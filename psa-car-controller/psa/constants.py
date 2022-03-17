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

DEFAULT_PRECONDITIONING_PROGRAM = {
    "program1": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
    "program2": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
    "program3": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
    "program4": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0}
}
AUTHORIZE_SERVICE = "https://api.mpsa.com/api/connectedcar/v2/oauth/authorize"
REMOTE_URL = "https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token?client_id="
BRAND = {"com.psa.mym.myopel": {"realm": "clientsB2COpel", "brand_code": "OP", "app_name": "MyOpel"},
         "com.psa.mym.mypeugeot": {"realm": "clientsB2CPeugeot", "brand_code": "AP", "app_name": "MyPeugeot"},
         "com.psa.mym.mycitroen": {"realm": "clientsB2CCitroen", "brand_code": "AC", "app_name": "MyCitroen"},
         "com.psa.mym.myds": {"realm": "clientsB2CDS", "brand_code": "DS", "app_name": "MyDS"},
         "com.psa.mym.myvauxhall": {"realm": "clientsB2CVauxhall", "brand_code": "VX", "app_name": "MyVauxhall"}
         }
