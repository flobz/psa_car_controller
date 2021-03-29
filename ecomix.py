from datetime import datetime
from statistics import mean, StatisticsError
import xml.etree.cElementTree as ElT
import requests
import reverse_geocode

from MyLogger import logger


class Ecomix:
    @staticmethod
    def get_data_france(start, end):
        start_str = start.strftime("%d/%m/%Y")
        end_str = end.strftime("%d/%m/%Y")
        res = requests.get(
            f"https://eco2mix.rte-france.com/curves/eco2mixWeb?type=co2&&dateDeb={start_str}&dateFin={end_str}&mode=NORM",
            headers={
                "Origin": "https://www.rte-france.com",
                "Referer": "https://www.rte-france.com/eco2mix/les-emissions-de-co2-par-kwh-produit-en-france",
            }
        )

        etree = ElT.fromstring(res.text)
        period_start = (start.hour + int(start.minute / 30)) * 4
        period_end = (end.hour + int(end.minute / 30)) * 4

        valeurs = etree.iter("valeur")
        co2_per_kw = []

        valeur = next(valeurs)
        while int(valeur.attrib["periode"]) != period_start:
            valeur = next(valeurs)
        while int(valeur.attrib["periode"]) != period_end:
            co2_per_kw.append(int(valeur.text))
            valeur = next(valeurs)
        try:
            return mean(co2_per_kw)
        except StatisticsError:
            return None

    @staticmethod
    def get_co2_per_kw(start: datetime, end: datetime, latitude, longitude):
        try:
            location = reverse_geocode.search([(latitude, longitude)])[0]
            country_code = location["country_code"]
        except UnicodeDecodeError:
            logger.error("Can't find country for %s %s", latitude, longitude)
            country_code = None
        except IndexError:
            country_code = None
        # todo implement other countries
        if country_code == 'FR':
            co2_per_kw = Ecomix.get_data_france(start, end)
        else:
            co2_per_kw = None
        return co2_per_kw
