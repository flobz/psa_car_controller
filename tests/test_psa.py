import unittest
from unittest.mock import MagicMock, patch

from psa_car_controller.psa.RemoteClient import RemoteClient
from psa_car_controller.psa.connected_car_api import Vehicles, ApiClient
from psa_car_controller.psa.constants import DISCONNECTED
from psa_car_controller.psacc.model.car import Car
from tests.data.car_status import ELECTRIC_CAR_STATUS


class TestUnit(unittest.TestCase):

    def get_rc(self) -> RemoteClient:
        account_info = MagicMock()
        account_info.realm = ""
        return RemoteClient(account_info, Vehicles, None, None)

    @patch('time.sleep', return_value=None)
    def test_fix_not_updated_api(self, patched_time_sleep):
        # GIVEN
        remote_client = self.get_rc()
        vin = "myvin"
        car = Car("a", "b", "c")
        car.status = ApiClient()._ApiClient__deserialize(ELECTRIC_CAR_STATUS, "Status")
        car.status.get_energy('Electric').charging.status = DISCONNECTED
        remote_client.vehicles_list.get_car_by_vin = MagicMock(return_value=car)
        remote_client.wakeup = MagicMock()
        # WHEN
        remote_client._fix_not_updated_api({'remaining_time': 1}, vin)
        # THEN
        remote_client.wakeup.assert_called_once_with(vin)
