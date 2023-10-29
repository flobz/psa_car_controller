from datetime import datetime
from enum import Enum


class ChargingMode(Enum):
    AC = "slow"
    DC = "fast"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value):
        return ChargingMode.UNKNOWN


class Charge:
    # pylint: disable=too-many-arguments
    def __init__(self, start_at: datetime, stop_at: datetime = None, vin=None, start_level=None, end_level=None,
                 co2=None, kw=None, price=None, charging_mode=None, mileage=None):
        assert isinstance(start_at, datetime)
        self.charging_mode: ChargingMode = ChargingMode(charging_mode)
        self.start_at = start_at
        self.stop_at = stop_at
        self.vin = vin
        self.start_level = start_level
        self.end_level = end_level
        self.co2 = co2
        self.kw = kw
        self.price = price
        self.mileage = mileage
