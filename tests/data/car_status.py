FUEL_CAR_STATUS = {
    'lastPosition': {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [9.65457, 49.96119, 21]},
                     'properties': {'updatedAt': '2021-03-29T05:16:10Z', 'heading': 126,
                                    'type': 'Estimated'}}, 'preconditionning': {
        'airConditioning': {'updatedAt': '2021-04-01T16:17:01Z', 'status': 'Disabled', 'programs': [
            {'enabled': False, 'slot': 1, 'recurrence': 'Daily', 'start': 'PT21H40M',
             'occurence': {'day': ['Sat']}}]}},
    'energy': [{'updatedAt': '2021-02-23T22:29:03Z', 'type': 'Fuel', 'level': 0},
               {'updatedAt': '2021-04-01T16:17:01Z', 'type': 'Electric', 'level': 70, 'autonomy': 192,
                'charging': {'plugged': True, 'status': 'InProgress', 'remainingTime': 'PT0S',
                             'chargingRate': 20, 'chargingMode': 'Slow', 'nextDelayedTime': 'PT21H30M'}}],
    'createdAt': '2021-04-01T16:17:01Z',
    'battery': {'voltage': 99, 'current': 0, 'createdAt': '2021-04-01T16:17:01Z'},
    'kinetic': {'createdAt': '2021-03-29T05:16:10Z', 'moving': False},
    'privacy': {'createdAt': '2021-04-01T16:17:01Z', 'state': 'None'},
    'service': {'type': 'Electric', 'updatedAt': '2021-02-23T21:10:29Z'},
    '_links': {'self': {
        'href': 'https://api.groupe-psa.com/connectedcar/v4/user/vehicles/myid/status'},
        'vehicles': {
            'href': 'https://api.groupe-psa.com/connectedcar/v4/user/vehicles/myid'}},
    'timed.odometer': {'createdAt': None, 'mileage': 1107.1}, 'updatedAt': '2021-04-01T16:17:01Z'}

ELECTRIC_CAR_STATUS = {
    "lastPosition": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-1.59008, 47.274, 30]},
                     "properties": {"updatedAt": "2021-03-29T06:22:51Z", "type": "Acquire", "signalQuality": 9}},
    "preconditionning": {"airConditioning": {"updatedAt": "2022-03-26T10:52:11Z", "status": "Disabled"}},
    "energy": [{"updatedAt": "2021-09-14T20:39:06Z", "type": "Fuel", "level": 0},
               {"updatedAt": "2022-03-26T11:02:54Z", "type": "Electric", "level": 59, "autonomy": 122,
                "charging": {"plugged": False, "status": "Disconnected", "remainingTime": "PT0S", "chargingRate": 0,
                             "chargingMode": "No", "nextDelayedTime": "PT22H31M"}}],
    "createdAt": "2022-03-26T11:02:54Z",
    "battery": {"voltage": 83.5, "current": 0, "createdAt": "2022-03-26T10:52:11Z"},
    "kinetic": {"createdAt": "2021-03-29T06:22:51Z", "moving": True},
    "privacy": {"createdAt": "2022-03-26T11:02:53Z", "state": "None"},
    "service": {"type": "Electric", "updatedAt": "2022-03-26T11:02:54Z"}, "_links": {"self": {
        "href": "https://api.groupe-psa.com/connectedcar/v4/user/vehicles/aa/status"},
        "vehicles": {
            "href": "https://api.groupe-psa.com/connectedcar/v4/user/vehicles/aa"}},
    "timed.odometer": {"createdAt": None, "mileage": 3196.5}, "updatedAt": "2022-03-26T11:02:54Z"}
