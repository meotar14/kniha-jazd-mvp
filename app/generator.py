import calendar
from datetime import date, timedelta
from random import Random

from sqlalchemy.orm import Session

from . import models


def plan_private_km(month_plan: models.MonthPlan) -> float:
    target_km = max(0, month_plan.end_odometer_km - month_plan.start_odometer_km)
    if not month_plan.private_km_enabled:
        return 0.0
    ratio = max(0.0, min(float(month_plan.private_km_ratio_percent or 0.0), 90.0))
    return round(target_km * (ratio / 100.0), 1)


def plan_service_target_km(month_plan: models.MonthPlan) -> float:
    target_km = max(0, month_plan.end_odometer_km - month_plan.start_odometer_km)
    return round(target_km - plan_private_km(month_plan), 1)


def generate_missing_trips(db: Session, month_plan: models.MonthPlan) -> tuple[int, float]:
    target_km = plan_service_target_km(month_plan)
    target_private_km = plan_private_km(month_plan)
    existing_service_km = sum(t.distance_km for t in month_plan.trips if not t.is_private)
    existing_private_km = sum(t.distance_km for t in month_plan.trips if t.is_private)
    remaining = round(target_km - existing_service_km, 1)

    customers = db.query(models.Customer).all()
    if remaining > 0 and not customers:
        return 0, 0.0
    base_normalized = (month_plan.base_address or "").strip().casefold()
    eligible_customers = [
        c
        for c in customers
        if c.active_for_generation
        and c.distance_from_base_km > 0
        and (c.address or "").strip().casefold() != base_normalized
    ]
    if remaining > 0 and not eligible_customers:
        return 0, 0.0

    days_in_month = calendar.monthrange(month_plan.year, month_plan.month)[1]
    rng = Random(month_plan.year * 100 + month_plan.month + month_plan.vehicle_id)
    blocked_dates: set[date] = set()
    for trip in month_plan.trips:
        if trip.generated:
            continue
        start = trip.trip_date
        end = trip.trip_end_date or trip.trip_date
        cur = start
        while cur <= end:
            if cur.year == month_plan.year and cur.month == month_plan.month:
                blocked_dates.add(cur)
            cur = cur + timedelta(days=1)
    weekday_dates = [
        date(month_plan.year, month_plan.month, d)
        for d in range(1, days_in_month + 1)
        if date(month_plan.year, month_plan.month, d).weekday() < 5 and date(month_plan.year, month_plan.month, d) not in blocked_dates
    ]
    day_pool = weekday_dates if weekday_dates else [
        date(month_plan.year, month_plan.month, d)
        for d in range(1, days_in_month + 1)
        if date(month_plan.year, month_plan.month, d) not in blocked_dates
    ]
    if not day_pool and remaining > 0:
        return 0, 0.0

    # Existing cumulative km by date.
    existing_by_date: dict[date, float] = {}
    for trip in sorted(month_plan.trips, key=lambda t: (t.trip_date, t.id)):
        existing_by_date[trip.trip_date] = existing_by_date.get(trip.trip_date, 0.0) + trip.distance_km

    generated: list[models.Trip] = []
    tolerance = 0.20
    generated_km_by_day: dict[date, float] = {d: 0.0 for d in day_pool}

    def cumulative_km_until(end_date: date) -> float:
        existing = sum(km for d, km in existing_by_date.items() if d <= end_date)
        planned = sum(t.distance_km for t in generated if t.trip_date <= end_date)
        return round(existing + planned, 1)

    def pick_balanced_day(candidates: list[date]) -> date | None:
        if not candidates:
            return None
        min_day_km = min(generated_km_by_day.get(d, 0.0) for d in candidates)
        near_min = [d for d in candidates if generated_km_by_day.get(d, 0.0) <= min_day_km + 1.0]
        return rng.choice(near_min)

    def customer_real_roundtrip(customer: models.Customer) -> float:
        return round(customer.distance_from_base_km * 2, 1)

    def customer_min_km(customer: models.Customer) -> float:
        return round(customer_real_roundtrip(customer) * (1 - tolerance), 1)

    def customer_max_km(customer: models.Customer) -> float:
        return round(customer_real_roundtrip(customer) * (1 + tolerance), 1)

    def pick_trip_km(customer: models.Customer, max_allowed: float) -> float | None:
        min_km = customer_min_km(customer)
        max_km = min(customer_max_km(customer), round(max_allowed, 1))
        if max_km < min_km:
            return None
        km = round(customer_real_roundtrip(customer) * rng.uniform(1 - tolerance, 1 + tolerance), 1)
        km = max(min_km, min(km, max_km))
        return round(km, 1)

    def create_generated_trip(trip_date: date, trip_km: float, customer: models.Customer | None) -> None:
        selected_customer = customer or rng.choice(eligible_customers)
        if selected_customer.distance_from_base_km <= 0:
            return
        if (selected_customer.address or "").strip().casefold() == base_normalized:
            return
        generated.append(
            models.Trip(
                month_plan_id=month_plan.id,
                trip_date=trip_date,
                customer_id=selected_customer.id,
                start_address=month_plan.base_address,
                end_address=selected_customer.address,
                distance_km=round(trip_km, 1),
                generated=True,
                is_private=False,
                note="Automaticky generovana jazda",
            )
        )
        generated_km_by_day[trip_date] = round(generated_km_by_day.get(trip_date, 0.0) + trip_km, 1)

    # Fuel-aware milestones: ensure enough km before refuel dates.
    consumption_per_km = month_plan.vehicle.expected_consumption_l_per_100km / 100.0
    refuels = sorted(month_plan.refuels, key=lambda r: (r.refuel_date, r.id))
    cumulative_refueled = 0.0
    for refuel in refuels:
        cumulative_refueled += refuel.liters
        required_km = round(cumulative_refueled / consumption_per_km, 1) if consumption_per_km > 0 else 0.0
        required_km = min(required_km, float(target_km))
        current_km = cumulative_km_until(refuel.refuel_date)
        deficit = round(required_km - current_km, 1)
        if deficit <= 0:
            continue

        eligible_days = [d for d in day_pool if d <= refuel.refuel_date]
        if not eligible_days:
            continue

        while deficit > 0 and remaining > 0:
            max_allowed = min(deficit, remaining)
            candidates = [c for c in eligible_customers if customer_min_km(c) <= max_allowed]
            if not candidates:
                break
            customer = rng.choice(candidates)
            trip_km = pick_trip_km(customer, max_allowed)
            if trip_km is None:
                break
            trip_date = pick_balanced_day(eligible_days)
            if trip_date is None:
                break
            create_generated_trip(trip_date, trip_km, customer)
            deficit = round(deficit - trip_km, 1)
            remaining = round(remaining - trip_km, 1)
            if remaining <= 0:
                break

    # Fill the rest of monthly target.
    while remaining > 0:
        candidates = [c for c in eligible_customers if customer_min_km(c) <= remaining]
        if not candidates:
            break
        customer = rng.choice(candidates)
        trip_km = pick_trip_km(customer, remaining)
        if trip_km is None:
            break
        trip_date = pick_balanced_day(day_pool)
        if trip_date is None:
            break
        create_generated_trip(trip_date, trip_km, customer)
        remaining = round(remaining - trip_km, 1)

    # If a small remainder stays, try to distribute it to existing generated trips
    # without exceeding +20% of each trip's real roundtrip distance.
    if remaining > 0:
        for trip in generated:
            if remaining <= 0:
                break
            if not trip.customer:
                continue
            max_km = customer_max_km(trip.customer)
            possible_add = round(max_km - trip.distance_km, 1)
            if possible_add <= 0:
                continue
            add_km = min(possible_add, remaining)
            trip.distance_km = round(trip.distance_km + add_km, 1)
            remaining = round(remaining - add_km, 1)

    private_remaining = round(target_private_km - existing_private_km, 1)
    if private_remaining > 0:
        source_dates = [trip.trip_date for trip in sorted(month_plan.trips + generated, key=lambda t: (t.trip_date, t.id or 0)) if not trip.is_private]
        private_dates = source_dates if source_dates else day_pool
        if private_dates:
            total_tenths = max(0, int(round(private_remaining * 10)))
            slots = len(private_dates)
            base_units, remainder = divmod(total_tenths, slots)
            for index, trip_date in enumerate(private_dates):
                units = base_units + (1 if index < remainder else 0)
                distance_km = round(units / 10.0, 1)
                if distance_km <= 0:
                    continue
                generated.append(
                    models.Trip(
                        month_plan_id=month_plan.id,
                        trip_date=trip_date,
                        customer_id=None,
                        start_address=month_plan.base_address or "-",
                        end_address=month_plan.base_address or "-",
                        distance_km=distance_km,
                        generated=True,
                        is_private=True,
                        note="Sukromna jazda",
                    )
                )

    for trip in generated:
        db.add(trip)
    db.commit()
    generated_km = round(sum(t.distance_km for t in generated if not t.is_private), 1)
    return len(generated), generated_km
