from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plate_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    expected_consumption_l_per_100km: Mapped[float] = mapped_column(Float, nullable=False)
    tank_capacity_l: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)

    month_plans: Mapped[list["MonthPlan"]] = relationship(back_populates="vehicle")


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    license_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    month_plans: Mapped[list["MonthPlan"]] = relationship(back_populates="driver")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    address: Mapped[str] = mapped_column(String(256), nullable=False)
    distance_from_base_km: Mapped[float] = mapped_column(Float, nullable=False)
    active_for_generation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MonthPlan(Base):
    __tablename__ = "month_plans"
    __table_args__ = (UniqueConstraint("vehicle_id", "year", "month", name="uq_vehicle_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    base_address: Mapped[str] = mapped_column(String(256), nullable=False)
    start_odometer_km: Mapped[int] = mapped_column(Integer, nullable=False)
    end_odometer_km: Mapped[int] = mapped_column(Integer, nullable=False)

    vehicle: Mapped[Vehicle] = relationship(back_populates="month_plans")
    driver: Mapped[Driver] = relationship(back_populates="month_plans")
    refuels: Mapped[list["Refuel"]] = relationship(back_populates="month_plan", cascade="all,delete")
    trips: Mapped[list["Trip"]] = relationship(back_populates="month_plan", cascade="all,delete")


class Refuel(Base):
    __tablename__ = "refuels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    month_plan_id: Mapped[int] = mapped_column(ForeignKey("month_plans.id"), nullable=False)
    refuel_date: Mapped[date] = mapped_column(Date, nullable=False)
    liters: Mapped[float] = mapped_column(Float, nullable=False)
    odometer_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_price_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_foreign: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    month_plan: Mapped[MonthPlan] = relationship(back_populates="refuels")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    month_plan_id: Mapped[int] = mapped_column(ForeignKey("month_plans.id"), nullable=False)
    trip_date: Mapped[date] = mapped_column(Date, nullable=False)
    trip_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    start_address: Mapped[str] = mapped_column(String(256), nullable=False)
    end_address: Mapped[str] = mapped_column(String(256), nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    note: Mapped[str | None] = mapped_column(String(256), nullable=True)

    month_plan: Mapped[MonthPlan] = relationship(back_populates="trips")
    customer: Mapped[Customer | None] = relationship()


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    company_ico: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    company_logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    company_base_address: Mapped[str | None] = mapped_column(String(256), nullable=True)
