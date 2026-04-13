from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator


def _parse_date_sk(value: Any) -> Any:
    if value is None or isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if "." in text:
            parts = text.split(".")
            if len(parts) == 3:
                day = parts[0].zfill(2)
                month = parts[1].zfill(2)
                year = parts[2]
                return f"{year}-{month}-{day}"
    return value


class VehicleCreate(BaseModel):
    plate_number: str = Field(min_length=2, max_length=32)
    model: str = Field(min_length=1, max_length=128)
    expected_consumption_l_per_100km: float = Field(gt=0)
    tank_capacity_l: float = Field(gt=0)
    default_driver_id: int | None = None
    use_custom_customer_catalog: bool = False


class VehicleUpdate(VehicleCreate):
    pass


class DriverCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=128)
    license_number: str = Field(min_length=2, max_length=64)


class DriverUpdate(DriverCreate):
    pass


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    address: str = Field(min_length=3, max_length=256)
    distance_from_base_km: float = Field(gt=0)
    active_for_generation: bool = True
    vehicle_id: int | None = None


class CustomerUpdate(CustomerCreate):
    pass


class MonthPlanCreate(BaseModel):
    vehicle_id: int
    driver_id: int
    year: int = Field(ge=2020, le=2100)
    month: int = Field(ge=1, le=12)
    base_address: str = Field(min_length=3, max_length=256)
    start_odometer_km: int | None = Field(default=None, ge=0)
    end_odometer_km: int = Field(ge=0)
    private_km_enabled: bool = False
    private_km_ratio_percent: float = Field(default=10.0, ge=0, le=90)

    @field_validator("start_odometer_km", mode="before")
    @classmethod
    def parse_start_odometer_km(cls, value: Any) -> Any:
        if value in (None, ""):
            return None
        return value


class MonthPlanUpdate(MonthPlanCreate):
    pass


class RefuelCreate(BaseModel):
    month_plan_id: int | None = None
    vehicle_id: int | None = None
    refuel_date: date
    liters: float = Field(gt=0)
    odometer_km: int | None = Field(default=None, ge=0)
    total_price_eur: float | None = Field(default=None, ge=0)
    location_city: str | None = Field(default=None, max_length=128)
    is_foreign: bool = False

    @field_validator("refuel_date", mode="before")
    @classmethod
    def parse_refuel_date(cls, value: Any) -> Any:
        return _parse_date_sk(value)


class RefuelUpdate(RefuelCreate):
    pass


class TripCreate(BaseModel):
    month_plan_id: int
    trip_date: date
    trip_end_date: date | None = None
    customer_id: int | None = None
    start_address: str = Field(min_length=3, max_length=256)
    end_address: str = Field(min_length=3, max_length=256)
    distance_km: float = Field(gt=0)
    note: str | None = Field(default=None, max_length=256)

    @field_validator("trip_date", "trip_end_date", mode="before")
    @classmethod
    def parse_trip_dates(cls, value: Any) -> Any:
        return _parse_date_sk(value)


class TripUpdate(TripCreate):
    pass


class GenerateResponse(BaseModel):
    generated_trips: int
    generated_km: float
    target_km: int
    service_target_km: float
    hidden_private_km: float
    recorded_service_km: float
    total_km_including_private: float
    total_trips_after_generation: int
    estimated_fuel_l: float
    refueled_l: float
    warning: str | None = None


class MonthReport(BaseModel):
    month_plan_id: int
    target_km: int
    total_km: float
    recorded_service_km: float
    hidden_private_km: float
    service_target_km: float
    refueled_l: float
    estimated_fuel_l: float
    fuel_difference_l: float
    average_consumption_l_per_100km: float | None = None
    trips_count: int


class GenerateOptions(BaseModel):
    private_km_enabled: bool = False
    private_km_ratio_percent: float = Field(default=10.0, ge=0, le=90)


class AppSettingsUpdate(BaseModel):
    company_name: str = Field(default="", max_length=128)
    company_ico: str = Field(default="", max_length=32)
    company_logo_url: str | None = Field(default=None, max_length=512)
    company_base_address: str | None = Field(default=None, max_length=256)


class BulkDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1)


class BulkCustomerGenerationUpdate(BaseModel):
    ids: list[int] = Field(min_length=1)
    active_for_generation: bool


class HolidayCreate(BaseModel):
    holiday_date: date
    name: str = Field(min_length=1, max_length=128)

    @field_validator("holiday_date", mode="before")
    @classmethod
    def parse_holiday_date(cls, value: Any) -> Any:
        return _parse_date_sk(value)
