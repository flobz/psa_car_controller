from datetime import datetime

from typing import List


class BatterySoh:
    def __init__(self, vin, dates, levels):
        self.vin = vin
        self.dates: List[datetime] = dates
        self.levels: List[float] = levels
