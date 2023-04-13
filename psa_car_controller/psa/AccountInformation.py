from psa_car_controller.psa.constants import MQTT_BRANDCODE


class AccountInformation:
    def __init__(self, client_id, customer_id: str, realm: str, country_code: str):
        self.client_id = client_id
        self.customer_id = customer_id
        self.realm = realm
        self.country_code = country_code

    def get_mqtt_customer_id(self):
        brand_code = self.customer_id[:2]
        return MQTT_BRANDCODE[brand_code] + self.customer_id[2:]
