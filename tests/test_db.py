import os
import tempfile
import unittest
from sqlite3.dbapi2 import IntegrityError

from psa_car_controller.psacc.model.battery_soh import BatterySoh
from psa_car_controller.psacc.repository.db import CustomSqliteConnection, Database, WAL_SIZE_LIMIT_IN_BYTES
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

    def test_wal_size_is_limited(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = CustomSqliteConnection(os.path.join(tmp, "info.db"))
            try:
                self.assertEqual("wal", conn.execute("PRAGMA journal_mode;").fetchone()[0])
                self.assertEqual(WAL_SIZE_LIMIT_IN_BYTES, conn.execute("PRAGMA journal_size_limit;").fetchone()[0])
            finally:
                conn.close_db()
