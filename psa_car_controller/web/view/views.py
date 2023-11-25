import json
from datetime import datetime
from typing import List
from urllib.parse import parse_qs, urlparse

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from flask import jsonify, request, Response as FlaskResponse
import time

from psa_car_controller.common.mylogger import CustomLogger
from psa_car_controller.psacc.application.car_controller import PSACarController
from psa_car_controller.psacc.model.car import Cars, Car
from psa_car_controller.common.utils import RateLimitException
from psa_car_controller.psacc.model.charge import Charge

from psa_car_controller.psacc.repository.trips import Trips

from psa_car_controller.psacc.application.charging import Charging
from psa_car_controller.web import figures

from psa_car_controller.web.app import app, dash_app
from psa_car_controller.psacc.repository.db import Database
from psa_car_controller.web.tools.utils import diff_dashtable, unix_time_millis, get_marks_from_start_end, create_card
from psa_car_controller.web.view.config_views import log_layout, config_layout

# pylint: disable=invalid-name
from psa_car_controller.web.tools.figurefilter import FigureFilter
from psa_car_controller.web.view.control import get_control_tabs

from psa_car_controller import __version__
logger = CustomLogger.getLogger(__name__)

EMPTY_DIV = "empty-div"
CALLBACK_CREATED = False

trips: Trips = Trips()
chargings: List[dict]
min_date = max_date = min_millis = max_millis = step = marks = cached_layout = None
APP = PSACarController()


def get_default_car() -> Car:
    return APP.myp.vehicles_list[0]


def add_header(el):
    version = "v" + __version__
    github_url= "https://github.com/flobz/psa_car_controller/releases/tag/"+version
    dbc_version = dbc.Button(html.I(version, className="m-1"),
                             size='sm',
                             color="secondary", 
                             className="me-1 bi bi-github",
                             external_link =True, href=github_url)
    return dbc.Row([dbc.Col(dcc.Link(html.H1('My car info'), href=dash_app.requests_pathname_external_prefix,
                                     style={"TextDecoration": "none"})),
                    dbc.Col(html.Div([dbc_version,
                                    dcc.Link(html.Img(src="assets/images/settings.svg", width="30veh"),
                                     href=dash_app.requests_pathname_external_prefix + "config",
                                     className="float-end")],
                                     className="d-grid gap-2 d-md-flex justify-content-md-end",))],
                                     className='align-items-center'), el


@dash_app.callback(Output('page-content', 'children'),
                   [Input('url', 'pathname'),
                    Input('url', 'search')])
def display_page(pathname, search):
    pathname = pathname[len(dash_app.requests_pathname_external_prefix) - 1:]
    query_params = parse_qs(urlparse(search).query)
    no_header = query_params.get("header", None) == ["false"]
    if pathname == "/config":
        page = config_layout()
    elif pathname == "/config_login":
        page = config_layout("login")
    elif pathname == "/log":
        page = log_layout()
    elif not APP.is_good:
        page = dcc.Location(pathname=dash_app.requests_pathname_external_prefix + "config_login", id="config_redirect")
    elif pathname == "/config_otp":
        page = config_layout("otp")
    elif pathname == "/control":
        page = get_control_tabs(APP)
    else:
        page = serve_layout()
    if no_header:
        return page
    return add_header(page)


def create_callback():  # noqa: MC0001
    global CALLBACK_CREATED
    if not CALLBACK_CREATED:
        @dash_app.callback(Output(EMPTY_DIV, "children"),
                           [Input("battery-table", "data_timestamp")],
                           [State("battery-table", "data"),
                            State("battery-table", "data_previous")])
        def capture_diffs_in_battery_table(timestamp, data, data_previous):
            if timestamp is None:
                raise PreventUpdate
            diff_data = diff_dashtable(data, data_previous, "start_at")
            for changed_line in diff_data:
                if changed_line['column_name'] == 'price':
                    conn = Database.get_db()
                    charge = Charge(datetime.utcfromtimestamp(changed_line['start_at']/1000))
                    charge.price = changed_line['current_value']
                    charge.vin = get_default_car().vin
                    if not Database.set_chargings_price(conn, charge):
                        logger.error("Can't find line to update in the database")
                    else:
                        logger.debug("update price %s of %s", changed_line['current_value'], changed_line['start_at'])
                    conn.close()
            return ""  # don't need to update dashboard

        @dash_app.callback([Output("tab_battery_popup_graph", "children"), Output("tab_battery_popup", "is_open")],
                           [Input("battery-table", "active_cell"),
                            Input("tab_battery_popup-close", "n_clicks")],
                           [State('battery-table', 'data'),
                            State("tab_battery_popup", "is_open")])
        def get_battery_curve(active_cell, close, data, is_open):  # pylint: disable=unused-argument
            if is_open is None:
                is_open = False
            if active_cell is not None and active_cell["column_id"] in ["start_level", "end_level"] and not is_open:
                row = data[active_cell["row"]]
                return figures.get_battery_curve_fig(row, APP.myp.vehicles_list[0]), True
            return "", False

        @dash_app.callback([Output("tab_trips_popup_graph", "children"), Output("tab_trips_popup", "is_open"), ],
                           [Input("trips-table", "active_cell"),
                            Input("tab_trips_popup-close", "n_clicks")],
                           State("tab_trips_popup", "is_open"))
        def get_altitude_graph(active_cell, close, is_open):  # pylint: disable=unused-argument
            if is_open is None:
                is_open = False
            if active_cell is not None and active_cell["column_id"] in ["altitude_diff"] and not is_open:
                return figures.get_altitude_fig(trips[active_cell["row_id"] - 1]), True
            return "", False

        @dash_app.callback(Output("loading-output-trips", "children"), Input("export-trips-table", "n_clicks"))
        def export_trips_loading_animation(n_clicks): # pylint: disable=unused-argument
            time.sleep(3)

        @dash_app.callback(Output("loading-output-battery", "children"), Input("export-battery-table", "n_clicks"))
        def export_batt_loading_animation(n_clicks): # pylint: disable=unused-argument
            time.sleep(3)
        # Emulate click on original Export datatables button, since original button is hard to modify
        dash_app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0)
                    document.querySelector("#trips-table button.export").click()
                return ""
            }
            """,
            Output("trips-table", "data-dummy"),
            [Input("export-trips-table", "n_clicks")]
        )
        dash_app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0)
                    document.querySelector("#battery-table button.export").click()
                return ""
            }
            """,
            Output("battery-table", "data-dummy"),
            [Input("export-battery-table", "n_clicks")]
        )

        figures.CURRENCY = APP.config.General.currency
        figures.EXPORT_FORMAT = APP.config.General.export_format
        CALLBACK_CREATED = True


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


STYLE_CACHE = None


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
    charge_control = APP.chc.get(vin)
    if charge_control is None:
        return jsonify("error: VIN not in list")
    if 'hour' in request.args and 'minute' in request.args:
        charge_control.set_stop_hour([int(request.args["hour"]), int(request.args["minute"])])
    if 'percentage' in request.args:
        charge_control.percentage_threshold = int(request.args['percentage'])
    APP.chc.save_config()
    return jsonify(charge_control.get_dict())


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
        
def update_trips():
    global trips, chargings, cached_layout, min_date, max_date, min_millis, max_millis, step, marks
    logger.info("update_data")
    conn = Database.get_db(update_callback=False)
    Database.add_altitude_to_db(conn)
    conn.close()
    min_date = None
    max_date = None
    if APP.is_good:
        car = get_default_car()  # todo handle multiple car
        try:
            trips_by_vin = Trips.get_trips(Cars([car]))
            trips = trips_by_vin[car.vin]
            assert len(trips) > 0
            min_date = trips[0].start_at
            max_date = trips[-1].start_at
            figures.get_figures(trips[0].car)
        except (AssertionError, KeyError):
            logger.debug("No trips yet")
            figures.get_figures(Car("vin", "vid", "brand"))
        try:
            chargings = Charging.get_chargings()
            assert len(chargings) > 0
            if min_date:
                min_date = min(min_date, chargings[0]["start_at"])
                max_date = max(max_date, chargings[-1]["start_at"])
            else:
                min_date = chargings[0]["start_at"]
                max_date = chargings[-1]["start_at"]
        except AssertionError:
            logger.debug("No chargings yet")
            if min_date is None:
                return
        # update for slider
        try:
            logger.debug("min_date:%s - max_date:%s", min_date, max_date)
            min_millis = unix_time_millis(min_date)
            max_millis = unix_time_millis(max_date)
            step = (max_millis - min_millis) / 100
            marks = get_marks_from_start_end(min_date, max_date)
            cached_layout = None  # force regenerate layout
            figures.get_figures(car)
        except (ValueError, IndexError):
            logger.error("update_trips (slider): %s", exc_info=True)
        except AttributeError:
            logger.debug("position table is probably empty :", exc_info=True)
    return


def serve_layout():
    global cached_layout
    if cached_layout is None:
        logger.debug("Create new layout")
        fig_filter = FigureFilter()
        try:
            range_slider = dcc.RangeSlider(
                id='date-slider',
                min=min_millis,
                max=max_millis,
                step=step,
                marks=marks,
                value=[min_millis, max_millis],
            )
            summary_tab = [
                dbc.Container(dbc.Row(id="summary-cards",
                                      children=create_card(figures.SUMMARY_CARDS)), fluid=True),
                fig_filter.add_graph(dcc.Graph(id="consumption_fig"), "start_at", ["consumption_km"],
                                     figures.consumption_fig),
                fig_filter.add_graph(dcc.Graph(id="consumption_fig_by_speed"), "speed_average",
                                     ["consumption_km"] * 2, figures.consumption_fig_by_speed),
                fig_filter.add_graph(dcc.Graph(id="consumption_graph_by_temp"), "consumption_by_temp",
                                     ["consumption_km"] * 2, figures.consumption_fig_by_temp)]
            maps = fig_filter.add_map(dcc.Graph(id="trips_map", style={"height": '90vh'}), "lat",
                                      ["long", "start_at"], figures.trips_map)
            fig_filter.add_table("trips", figures.table_fig)
            fig_filter.add_table("chargings", figures.battery_table)
            fig_filter.src = {"trips": trips.get_trips_as_dict(), "chargings": chargings}
            fig_filter.set_clientside_callback(dash_app, {"minimumLength": APP.config.General.minimum_trip_length})
            create_callback()
        except (IndexError, TypeError, NameError, AssertionError, NameError, AttributeError):
            summary_tab = figures.ERROR_DIV
            maps = figures.ERROR_DIV
            logger.warning("Failed to generate figure, there is probably not enough data yet", exc_info_debug=True)
            range_slider = html.Div()
            figures.battery_table = figures.ERROR_DIV

        data_div = html.Div([
            *fig_filter.get_store(),
            html.Div([
                range_slider,
                dbc.Tabs([
                    dbc.Tab(label="Summary", tab_id="summary", children=summary_tab),
                    dbc.Tab(label="Trips", tab_id="trips", id="tab_trips",
                            children=[dbc.Row(
                                        dbc.Col([
                                            dcc.Loading(
                                                id="loading-div-trips",
                                                children=[html.Div([html.Div(id="loading-output-trips")])],
                                                type="circle",
                                                className="export-load-anim"
                                            ),
                                            dbc.Button("Export trips data",
                                                       id="export-trips-table",
                                                       n_clicks=0,
                                                       size="sm",
                                                       color="light",
                                                       className="m-1 w-200"
                                            )],
                                            className="d-grid gap-2 d-md-flex justify-content-md-end"
                                        )
                                      ),
                                      html.Div(id="tab_trips_fig", children=figures.table_fig),
                                      dbc.Modal(
                                          [
                                              dbc.ModalHeader("Altitude"),
                                              dbc.ModalBody(html.Div(
                                                  id="tab_trips_popup_graph")),
                                              dbc.ModalFooter(
                                                  dbc.Button("Close",
                                                             id="tab_trips_popup-close",
                                                             className="ml-auto")
                                              ),
                                          ],
                                          id="tab_trips_popup",
                                          size="xl",
                            )
                            ]),
                    dbc.Tab(label="Charge", tab_id="charge", id="tab_charge",
                            children=[dbc.Row(
                                        dbc.Col([
                                            dcc.Loading(
                                                id="loading-div-battery",
                                                children=[html.Div([html.Div(id="loading-output-battery")])],
                                                type="circle",
                                                className="export-load-anim"
                                            ),
                                            dbc.Button("Export charging data",
                                                       id="export-battery-table",
                                                       n_clicks=0,
                                                       size="sm",
                                                       color="light",
                                                       className="m-1 w-200"
                                            )],
                                            className="d-grid gap-2 d-md-flex justify-content-md-end"
                                        )
                                      ),
                                      figures.battery_table,
                                      dbc.Modal(
                                          [
                                              dbc.ModalHeader(
                                                  "Charging speed"),
                                              dbc.ModalBody(html.Div(
                                                  id="tab_battery_popup_graph")),
                                              dbc.ModalFooter(
                                                  dbc.Button("Close",
                                                             id="tab_battery_popup-close",
                                                             className="ml-auto")
                                              ),
                                          ],
                                          id="tab_battery_popup",
                                          size="xl",
                                      )
                                      ]),
                    dbc.Tab(label="Map", tab_id="map", children=[maps]),
                    dbc.Tab(label="Control", tab_id="control", children=html.Iframe(
                        src=request.url_root + "control?header=false",
                        style={"position": "absolute",
                               "height": "100%",
                               "width": "100%",
                               "border": "none"}))
                ],
                    id="tabs",
                    active_tab="summary",
                    persistence=True),
                html.Div(id=EMPTY_DIV)
            ])])
        cached_layout = data_div
    return cached_layout


try:
    if APP.is_good:
        Charging.set_default_price(APP.myp.vehicles_list)
    Database.set_db_callback(update_trips)
    figures.CURRENCY = APP.config.General.currency
    figures.EXPORT_FORMAT = APP.config.General.export_format
    update_trips()
except (IndexError, TypeError):
    logger.debug("Failed to get trips, there is probably not enough data yet:", exc_info=True)

dash_app.layout = dbc.Container(fluid=True, children=[dcc.Location(id='url', refresh=False),
                                                      html.Div(id='page-content')],
                                style={"height": "100vh"})
