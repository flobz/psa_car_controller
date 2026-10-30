import unittest
from sqlite3.dbapi2 import IntegrityError
from unittest.mock import patch

from psa_car_controller.psacc.model.battery_soh import BatterySoh
from psa_car_controller.psacc.repository.db import Database
from tests.utils import get_new_test_db, compare_dict, get_date, vehicule_list


class TestUnit(unittest.TestCase):
    def test_record_soh(self):
        get_new_test_db()
        car = vehicule_list[0]
        soh_list = [99.0, 96.0, 90.2]
        for x in range(len(soh_list)):
            Database.record_battery_soh(car.vin, get_date(x), soh_list[x])
        compare_dict(vars(BatterySoh(car.vin,
                                     [get_date(0), get_date(1), get_date(2)],
                                     soh_list)),
                     vars(Database.get_soh_by_vin(car.vin))
                     )
        self.assertEqual(soh_list[-1], Database.get_last_soh_by_vin(car.vin))

    def test_record_same_soh(self):
        get_new_test_db()
        car = vehicule_list[0]
        Database.record_battery_soh(car.vin, get_date(0), 99.0)
        self.assertRaises(IntegrityError, Database.record_battery_soh, car.vin, get_date(0), 99.0)

    def test_record_soh_already_seen(self):
        get_new_test_db()
        car = vehicule_list[0]
        soh_list = [91.0, 100.0, 91.0]
        for x, soh in enumerate(soh_list):
            Database.record_battery_soh(car.vin, get_date(x), soh)
        self.assertEqual(soh_list, Database.get_soh_by_vin(car.vin).levels)
        self.assertEqual(91.0, Database.get_last_soh_by_vin(car.vin))

    @patch("psa_car_controller.psacc.repository.db.Database.backup")
    def test_migrate_soh_unique_level(self, mock_backup):
        conn = get_new_test_db()
        car = vehicule_list[0]
        conn.execute("DROP TABLE battery_soh;")
        conn.execute("CREATE TABLE battery_soh(date DATETIME, VIN TEXT, level FLOAT, UNIQUE(VIN, level));")
        conn.execute("INSERT INTO battery_soh VALUES(?,?,?)", (get_date(0), car.vin, 91.0))
        conn.execute("INSERT INTO battery_soh VALUES(?,?,?)", (get_date(1), car.vin, 100.0))
        conn.commit()
        Database.init_db(conn)
        mock_backup.assert_called_once()
        Database.record_battery_soh(car.vin, get_date(2), 91.0)
        self.assertEqual([91.0, 100.0, 91.0], Database.get_soh_by_vin(car.vin).levels)
        self.assertEqual(91.0, Database.get_last_soh_by_vin(car.vin))
