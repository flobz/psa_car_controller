class BatteryCurveDto:
    def __init__(self, date, level, rate, autonomy):
        self.autonomy = autonomy
        self.rate = rate
        self.level = level
        self.date = date
