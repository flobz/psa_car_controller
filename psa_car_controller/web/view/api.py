import logging

from flask import jsonify, request, Response as FlaskResponse
from pydantic import BaseModel

from psa_car_controller.common.utils import RateLimitException
from psa_car_controller.psacc.application.car_controller import PSACarController
from psa_car_controller.psacc.repository.db import Database
from psa_car_controller.web.app import app

from psa_car_controller.psacc.model.car import Cars
from psa_car_controller.psacc.repository.trips import Trips

from psa_car_controller.psacc.application.charging import Charging

import json

from psa_car_controller.web.tools.utils import convert_to_number_if_number_else_return_str

logger = logging.getLogger(__name__)

STYLE_CACHE = None
APP = PSACarController()


def json_response(json: str, status=200):
    return app.response_class(
        response=json,
        status=status,
        mimetype='application/json'
    )


@app.route('/get_vehicles')
def get_vehicules():
    response = app.response_class(
        response=json.dumps(APP.myp.get_vehicles(), default=lambda car: car.to_dict()),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/get_vehicleinfo/<string:vin>')
def get_vehicle_info(vin):
    from_cache = int(request.args.get('from_cache', 0)) == 1
    response = app.response_class(
        response=json.dumps(APP.myp.get_vehicle_info(vin, from_cache).to_dict(), default=str),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/style.json")
def get_style():
    global STYLE_CACHE
    if not STYLE_CACHE:
        with open(app.root_path + "/assets/style.json", "r", encoding="utf-8") as f:
            res = json.loads(f.read())
            STYLE_CACHE = res
    url_root = request.url_root
    STYLE_CACHE["sprite"] = url_root + "assets/sprites/osm-liberty"
    return jsonify(STYLE_CACHE)


@app.route('/charge_now/<string:vin>/<int:charge>')
def charge_now(vin, charge):
    return jsonify(APP.myp.remote_client.charge_now(vin, charge != 0))


@app.route('/charge_hour')
def change_charge_hour():
    return jsonify(APP.myp.remote_client.change_charge_hour(request.args['vin'],
                                                            request.args['hour'],
                                                            request.args['minute']))


@app.route('/wakeup/<string:vin>')
def wakeup(vin):
    try:
        return jsonify(APP.myp.remote_client.wakeup(vin))
    except RateLimitException:
        return jsonify({"error": "Wakeup rate limit exceeded"})


@app.route('/preconditioning/<string:vin>/<int:activate>')
def preconditioning(vin, activate):
    return jsonify(APP.myp.remote_client.preconditioning(vin, activate))


@app.route('/position/<string:vin>')
def get_position(vin):
    res = APP.myp.get_vehicle_info(vin)
    try:
        coordinates = res.last_position.geometry.coordinates
    except AttributeError:
        return jsonify({'error': 'last_position not available from api'})
    longitude, latitude = coordinates[:2]
    if len(coordinates) == 3:  # altitude is not always available
        altitude = coordinates[2]
    else:
        altitude = None
    return jsonify(
        {"longitude": longitude, "latitude": latitude, "altitude": altitude,
         "url": f"https://maps.google.com/maps?q={latitude},{longitude}"})


# Set a battery threshold and schedule an hour to stop the charge
@app.route('/charge_control')
def get_charge_control():
    logger.info(request)
    vin = request.args['vin']
    if APP.chc:
        charge_control = APP.chc.get(vin)
        if charge_control is None:
            return jsonify({"error": "VIN not in list"})
        if 'hour' in request.args and 'minute' in request.args:
            charge_control.set_stop_hour([int(request.args["hour"]), int(request.args["minute"])])
        if 'percentage' in request.args:
            charge_control.percentage_threshold = int(request.args['percentage'])
        APP.chc.save_config()
        return jsonify(charge_control.get_dict())
    error = "Charge control not setup check your PSACC configuration and logs"
    logger.error(error)
    return jsonify({"error": error})


@app.route('/positions')
def get_recorded_position():
    return FlaskResponse(Database.get_recorded_position(), mimetype='application/json')


@app.route('/abrp')
def abrp():
    vin = request.args.get('vin', None)
    enable = request.args.get('enable', None)
    token = request.args.get('token', None)
    if vin is not None and enable is not None:
        if enable == '1':
            APP.myp.abrp.abrp_enable_vin.add(vin)
        else:
            APP.myp.abrp.abrp_enable_vin.discard(vin)
    if token is not None:
        APP.myp.abrp.token = token
    return jsonify(dict(APP.myp.abrp))


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/horn/<string:vin>/<int:count>')
def horn(vin, count):
    try:
        return jsonify(APP.myp.remote_client.horn(vin, count))
    except RateLimitException:
        return jsonify({"error": "Horn rate limit exceeded"})


@app.route('/lights/<string:vin>/<int:duration>')
def lights(vin, duration):
    try:
        return jsonify(APP.myp.remote_client.lights(vin, duration))
    except RateLimitException:
        return jsonify({"error": "Lights rate limit exceeded"})


@app.route('/lock_door/<string:vin>/<int:lock>')
def lock_door(vin, lock):
    try:
        return jsonify(APP.myp.remote_client.lock_door(vin, lock))
    except RateLimitException:
        return jsonify({"error": "Locks rate limit exceeded"})


@app.route('/settings/<string:section>')
def settings_section(section: str):
    config_section: BaseModel = getattr(APP.config, section.capitalize())
    for key, value in request.args.items():
        typed_value = convert_to_number_if_number_else_return_str(value)
        setattr(config_section, key, typed_value)
        APP.config.write_config()
    return json_response(config_section.json())


@app.route('/vehicles/trips')
def get_trips():
    try:
        car = APP.myp.vehicles_list[0]
        trips_by_vin = Trips.get_trips(Cars([car]))
        trips = trips_by_vin[car.vin]
        trips_as_dict = trips.get_trips_as_dict()
        return jsonify(trips_as_dict)
    except (IndexError, TypeError, KeyError):
        logger.debug("Failed to get trips, there is probably not enough data yet:", exc_info=True)
        return jsonify([])


@app.route('/vehicles/chargings')
def get_chargings():
    try:
        chargings = Charging.get_chargings()
        return jsonify(chargings)
    except (IndexError, TypeError):
        logger.debug("Failed to get chargings, there is probably not enough data yet:", exc_info=True)
        return jsonify([])


@app.route('/settings')
def settings():
    return json_response(APP.config.json())


@app.route('/battery/soh/<string:vin>')
def db(vin: str):
    soh = Database.get_last_soh_by_vin(vin)
    return jsonify({"soh": soh})
