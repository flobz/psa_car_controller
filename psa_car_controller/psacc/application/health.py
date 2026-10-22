from os import environ
from typing import Optional, Tuple

from psa_car_controller.psa.RemoteClient import RemoteClient

# about 10 minutes at paho's 2 minutes reconnect delay
DEFAULT_MAX_MQTT_AUTH_FAILURES = 5


def get_max_mqtt_auth_failures() -> int:
    return int(environ.get("PSACC_HEALTH_MAX_MQTT_AUTH_FAILURES", DEFAULT_MAX_MQTT_AUTH_FAILURES))


def get_health(remote_client: Optional[RemoteClient], remote_control: bool,
               max_auth_failures: int, api_authenticated: bool = True) -> Tuple[dict, int]:
    """Return the /health body and HTTP status.

    Only looks at state the mqtt callbacks already recorded: no PSA call, so it is cheap to poll.
    Unhealthy (503) once the broker refused the remote credentials max_auth_failures times in a row.
    api_authenticated is reported but never makes it unhealthy: a rejected refresh token needs a new
    login from the config web page, which restarting the container can't do.
    """
    if not remote_control or remote_client is None:
        return {"api_authenticated": api_authenticated, "remote_control": False}, 200
    last_connect = remote_client.mqtt_last_connect
    body = {
        "api_authenticated": api_authenticated,
        "remote_control": True,
        "mqtt_connected": remote_client.is_mqtt_connected(),
        "consecutive_auth_failures": remote_client.mqtt_auth_failures,
        "last_connect": last_connect.isoformat() if last_connect else None,
    }
    status = 503 if remote_client.mqtt_auth_failures >= max_auth_failures else 200
    return body, status
