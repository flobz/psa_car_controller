import json
import threading
from datetime import datetime, timezone
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html

from MyLogger import logger
from flask import jsonify, request, Response as FlaskResponse

from web import figures

from MyPSACC import MyPSACC

dash_app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server
myp = None
chc = None


@dash_app.callback(Output('trips_map', 'figure'),
                   Output('consumption_fig', 'figure'),
                   Output('consumption_fig_by_speed', 'figure'),
                   Output('consumption', 'children'),
                   Input('date-slider', 'value'))
def display_value(value):
    min = datetime.fromtimestamp(value[0], tz=timezone.utc)
    max = datetime.fromtimestamp(value[1], tz=timezone.utc)
    filtered_trips = []
    for trip in trips:
        if min <= trip.start_at <= max:
            filtered_trips.append(trip)
    print(len(filtered_trips))
    figures.get_figures(filtered_trips)
    consumption = "Average consumption: {:.1f} kW/100km".format(float(figures.consumption_df.mean()))
    return figures.trips_map, figures.consumption_fig, figures.consumption_fig_by_speed, consumption


@app.route('/getvehicles')
def getvehicules():
    return jsonify(myp.getVIN())


@app.route('/get_vehicleinfo/<string:vin>')
def get_vehicle_Info(vin):
    response = app.response_class(
        response=json.dumps(myp.get_vehicle_info(vin).to_dict(), default=str),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/charge_now/<string:vin>/<int:charge>')
def charge_now(vin, charge):
    return jsonify(myp.charge_now(vin, charge != 0))


@app.route('/charge_hour')
def change_charge_hour():
    return jsonify(myp.change_charge_hour(request.form['vin'], request.form['hour'], request.form['minute']))


@app.route('/wakeup/<string:vin>')
def wakeup(vin):
    return jsonify(myp.wakeup(vin))


@app.route('/preconditioning/<string:vin>/<int:activate>')
def preconditioning(vin, activate):
    return jsonify(myp.preconditioning(vin, activate))


@app.route('/position/<string:vin>')
def get_position(vin):
    res = myp.get_vehicle_info(vin)
    longitude, latitude = res.last_position.geometry.coordinates
    return jsonify(
        {"longitude": longitude, "latitude": latitude, "url": f"http://maps.google.com/maps?q={latitude},{longitude}"})


# Set a battery threshold and schedule an hour to stop the charge
@app.route('/charge_control')
def charge_control():
    logger.info(request)
    vin = request.args['vin']
    charge_control = chc.get(vin)
    if charge_control is None:
        return jsonify("error: VIN not in list")
    if 'hour' in request.args or 'minute' in request.args:
        charge_control.set_stop_hour([int(request.args["hour"]), int(request.args["minute"])])
    if 'percentage' in request.args:
        charge_control.percentage_threshold = int(request.args['percentage'])
    save_config()
    return jsonify(charge_control.get_dict())


@app.route('/positions')
def get_recorded_position():
    return FlaskResponse(myp.get_recorded_position(), mimetype='application/json')


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


def save_config(my_peugeot: MyPSACC):
    my_peugeot.save_config()
    threading.Timer(30, save_config, args=[my_peugeot]).start()


trips = MyPSACC.get_trips()
figures.get_figures(trips)
dash_app.layout = dbc.Container([
    html.H1('My car info'),
    html.Hr(),
    html.Div([
        dcc.RangeSlider(
            id='date-slider',
            min=figures.unix_time_millis(figures.consumption_df["date"].min()),
            max=figures.unix_time_millis(figures.consumption_df["date"].max()),
            step=None,
            marks=figures.get_marks_from_start_end(figures.consumption_df["date"].min(),
                                                   figures.consumption_df["date"].max()),
            value=[figures.unix_time_millis(figures.consumption_df["date"].min()),
                   figures.unix_time_millis(figures.consumption_df["date"].max())],
        ),
        html.Div(id='updatemode-output-container', style={'margin-top': 20})
    ],
        style={'margin-left': 20}
    ),
    html.Div([
        html.Div([
            dcc.Graph(figure=figures.trips_map, id="trips_map")
        ]),
        html.Div([
            dcc.Graph(figure=figures.consumption_fig, id="consumption_fig")
        ]),
        html.H2(id="consumption",
                children="Average consumption: {:.1f} kW/100km".format(float(figures.consumption_df.mean()))),
        html.Div([
            dcc.Graph(figure=figures.consumption_fig_by_speed, id="consumption_fig_by_speed")
        ]),
    ], id="data-div"),
])
