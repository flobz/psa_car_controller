from typing import List
class Points():
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class Trips:
    def __init__(self):
        self.start_at = None
        self.end_at = None
        self.positions: List[Points] = []
        self.speed_average = None
        self.consumption = None
        self.consumption_km = None

    def add_points(self, longitude, latitude):
        self.positions.append(Points(longitude, latitude))

    def get_consumption(self):
        return {
            'date': self.start_at,
            'consumption': self.consumption_km,
        }


