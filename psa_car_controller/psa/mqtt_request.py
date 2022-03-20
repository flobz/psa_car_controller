import json
from datetime import datetime, timedelta
from uuid import uuid4

from psa_car_controller.psa.constants import PSA_DATE_FORMAT, PSA_CORRELATION_DATE_FORMAT

MQTT_REQ_TOPIC = "psa/RemoteServices/from/cid/"


class MQTTRequest:
    TIME_BEFORE_EXPIRATION = 30

    def __init__(self, topic, vin, req_parameters, customer_id):
        self.customer_id = customer_id
        self.topic = MQTT_REQ_TOPIC + self.customer_id + topic
        self.vin = vin
        self.req_parameters = req_parameters
        self.date = datetime.now()
        self.data = {}

    def get_message_to_json(self, remote_access_token):
        return json.dumps(self.get_message(remote_access_token))

    def get_message(self, remote_access_token):
        date = datetime.utcnow()
        date_str = date.strftime(PSA_DATE_FORMAT)
        self.data = {"access_token": remote_access_token, "customer_id": self.customer_id,
                     "correlation_id": self.__gen_correlation_id(date), "req_date": date_str, "vin": self.vin,
                     "req_parameters": self.req_parameters}
        return self.data

    def is_expired(self):
        return self.date < datetime.now() - timedelta(seconds=self.TIME_BEFORE_EXPIRATION)

    @staticmethod
    def __gen_correlation_id(date):
        date_str = date.strftime(PSA_CORRELATION_DATE_FORMAT)[:-3]
        uuid_str = str(uuid4()).replace("-", "")
        correlation_id = uuid_str + date_str
        return correlation_id

    def __str__(self):
        return "topic: " + self.topic + ": " + str(self.req_parameters)
