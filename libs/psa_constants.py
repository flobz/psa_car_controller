DELAYED_CHARGE = "delayed"
IMMEDIATE_CHARGE = "immediate"
PSA_CORRELATION_DATE_FORMAT = "%Y%m%d%H%M%S%f"
PSA_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
realm_info = {
    "clientsB2CPeugeot": {"oauth_url": "https://idpcvs.peugeot.com/am/oauth2/access_token", "app_name": "MyPeugeot"},
    "clientsB2CCitroen": {"oauth_url": "https://idpcvs.citroen.com/am/oauth2/access_token", "app_name": "MyCitroen"},
    "clientsB2CDS": {"oauth_url": "https://idpcvs.driveds.com/am/oauth2/access_token", "app_name": "MyDS"},
    "clientsB2COpel": {"oauth_url": "https://idpcvs.opel.com/am/oauth2/access_token", "app_name": "MyOpel"},
    "clientsB2CVauxhall": {"oauth_url": "https://idpcvs.vauxhall.co.uk/am/oauth2/access_token",
                           "app_name": "MyVauxhall"}
}
MQTT_BRANDCODE = {"AP": "AP",
                  "AC": "AC",
                  "DS": "AC",
                  "VX": "OV",
                  "OP": "OV"
                  }
DISCONNECTED = "Disconnected"
INPROGRESS = "InProgress"
FAILURE = "Failure"
STOPPED = "Stopped"
FINISHED = "Finished"