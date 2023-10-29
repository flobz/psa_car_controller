import hashlib
import logging
import pickle
from secrets import token_hex, token_bytes
from math import ceil
from collections import defaultdict
from xml.etree import cElementTree as ElT

import requests
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
from Cryptodome import Hash

from . import oaep
from .load import IWData

# pylint: disable=invalid-name
CONFIG_NAME = "otp.bin"
TIMEOUT_IN_S = 10

logger = logging.getLogger(__name__)


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


base36 = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
          "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


def number_to_base36(n):
    b = 36
    if n == 0:
        return [0]
    digits = ""
    while n:
        digits += base36[int(n % b)]
        n //= b
    return digits


class ConfigException(Exception):
    """Raise exception if otp config isn't correct"""


class Otp:
    OTP_TWICE = 10
    OK = 0
    NOK = -1
    KPub = "11"
    exponent = int(KPub, 16)
    ACTIVATE_MODE = "activate"
    OTP_MODE = "otp"
    MS_MODE = "ms"
    iw_host = "https://otp.mpsa.com"
    proxies = None

    def __init__(self, inwebo_access_id, device_id=token_hex(8)):
        self.Kiw = None
        self.pinmode = None
        self.Kfact = None
        self.pinmode = None
        self.needsync = None
        self.serviceid = None
        self.alias = None
        self.iwalea = token_hex(16)
        self.device_id = device_id
        self.codepin = None
        self.challenge = ""
        self.action = ""
        self.s_id = None
        self.version = "0.2.11"
        self.isMac = True
        self.data = IWData(self)
        self.cipher = None
        self.macid = inwebo_access_id
        self.smsCode = None
        self.mode = Otp.ACTIVATE_MODE
        self.defi = 0
        self.otp_count = 0

    def init(self, Kfact=None, Kiw=None, pinmode=None):
        self.Kfact = Kfact
        self.pinmode = pinmode
        self.Kiw = self.decode_oaep(Kiw, self.Kfact)
        key = RSA.construct((int(self.Kiw, 16), Otp.exponent))
        self.cipher = oaep.new(key, hash_algo=Hash.SHA256)

    def get_serial(self):
        return self.device_id + "/_/" + self.iwalea

    def generate_kma(self, codepin):
        serial = self.get_serial()
        kma_str = codepin + ";" + serial
        kma = hashlib.sha256(kma_str.encode("utf-8")).hexdigest()[:32]
        return kma

    def get_r(self):
        if self.action == "upgrade":
            iw = self.data.iwK1
            # not correctly implemented
        else:
            iw = self.data.iwK0
        if self.action == "synchro":
            R2 = self.challenge + ";" + iw + ";" + self.codepin
        else:
            R2 = self.challenge + ";" + iw + ";"

        R0 = self.challenge + ";" + iw + ";" + self.get_serial()
        R1 = self.challenge + ";" + iw + ";" + self.data.iwK1
        logger.debug("%s\n%s\n%s", R0, R1, R2)
        return {"R0": hashlib.sha256(R0.encode("utf-8")).hexdigest(),
                "R1": hashlib.sha256(R1.encode("utf-8")).hexdigest(),
                "R2": hashlib.sha256(R2.encode("utf-8")).hexdigest()}

    @staticmethod
    def decode_oaep(enc, key):
        modulus = int(key, 16)
        key = RSA.construct((modulus, Otp.exponent))
        cipher = oaep.new(key, hash_algo=Hash.SHA256)
        block_size = 128
        dec_string = ""
        enc_b = bytes.fromhex(enc)
        nb_block = ceil(len(enc_b) / block_size)

        for x in range(0, nb_block):
            if x == nb_block - 1:
                maxi = len(enc_b)
            else:
                maxi = (1 + x) * 128
            mini = x * 128
            ciphertext = cipher.decrypt(enc_b[mini:maxi])
            dec_string += ciphertext.hex()
        logger.debug(dec_string)
        return dec_string

    def request(self, param, setup=False):
        raw_xml = requests.get(
            f"{self.iw_host}/iwws/MAC",
            headers={
                "Connection": "Keep-Alive",
                "Host": "otp.mpsa.com",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.0.0; Android SDK built for x86_64 "
                              "Build/OSR1.180418.004) "
            },
            params=param,
            proxies=self.proxies,
            verify=self.proxies is None,
            timeout=TIMEOUT_IN_S
        ).text
        try:
            raw_xml = raw_xml[raw_xml.index("?>") + 2:]
            if setup:
                return etree_to_dict(ElT.XML(raw_xml))["ActionSetup"]
            return etree_to_dict(ElT.XML(raw_xml))["ActionFinalize"]
        except KeyError:
            logger.debug(raw_xml)
            raise ValueError("Bad response from server") from KeyError

    def activation_start(self):
        param = {"action": "ActionSetup", "mode": self.mode, "id": self.data.iwid, "lastsync": self.data.iwTsync,
                 "version": "Generator-1.0/0.2.11", "macid": self.macid}
        if self.mode == Otp.OTP_MODE:
            param.update({"sid": self.data.iwsecid})
        elif self.mode == Otp.ACTIVATE_MODE:
            param.update({"code": self.smsCode})

        xml = self.request(param, setup=True)
        if xml["err"] == "OK":
            if self.mode == Otp.ACTIVATE_MODE:
                xml_filtred = {key: xml[key] for key in ["Kiw", "Kfact", "pinmode"]}
                self.init(**xml_filtred)
            elif self.mode == Otp.OTP_MODE:
                self.challenge = xml["challenge"]
            return True
        raise ConfigException(xml)

    def activation_finalyze(self, random_bytes=None):
        R = self.get_r()
        params = {"action": "ActionFinalize", "mode": self.mode, "id": self.data.iwid, "lastsync": self.data.iwTsync,
                  "version": "Generator-1.0/0.2.11",
                  "lang": "fr", "ack": "", "macid": self.macid}
        if self.mode == Otp.OTP_MODE:
            params.update({"keytype": '0', "sid": self.data.iwsecid})

        elif self.mode == Otp.ACTIVATE_MODE:
            kma_crypt = self.cipher.encrypt(bytes.fromhex(self.generate_kma(self.codepin))).hex()
            pin_crypt = self.cipher.encrypt(self.codepin.encode("utf-8")).hex()
            params.update({"serial": self.get_serial(), "code": self.smsCode,
                           "Kma": kma_crypt, "pin": pin_crypt, "name": "Android SDK built for x86_64 / UNKNOWN", })

        params.update(R)
        xml = self.request(params)
        if xml["err"] != "OK":
            logger.error("Error during activation: %s", xml)
            return Otp.NOK
        self.data.synchro(xml, self.generate_kma(self.codepin))

        if self.mode == Otp.OTP_MODE:
            try:
                self.defi = str(xml["defi"])
            except KeyError:
                raise ConfigException from KeyError
            if "J" in xml:
                logger.debug("Need another otp request")
                return Otp.OTP_TWICE
            return Otp.OK

        if "ms_n" not in xml or xml["ms_n"] == 0:
            logger.debug("no ms_n request needed")
            return Otp.OK

        if int(xml["ms_n"]) > 1:
            raise NotImplementedError
        ms_n = "0"

        self.challenge = xml["challenge"]
        self.action = "synchro"
        res = self.decode_oaep(xml["ms_key"], self.Kfact)
        temp_key = RSA.construct((int(res, 16), self.exponent))
        temp_cipher = oaep.new(temp_key, hash_algo=Hash.SHA256)
        if random_bytes is None:
            random_bytes = token_bytes(16)
        kpub_encode = temp_cipher.encrypt(random_bytes)

        aes_cipher = AES.new(bytes.fromhex(self.generate_kma(self.codepin)), AES.MODE_ECB)
        encode_aes_from_hex = aes_cipher.encrypt(random_bytes).hex()
        self.data.iwsecval = encode_aes_from_hex
        self.data.iwsecid = xml["s_id"]
        self.data.iwsecn = 1

        req_param = {"action": "ActionFinalize", "mode": Otp.MS_MODE, "ms_id" + ms_n: xml["ms_id"],
                     "ms_val" + ms_n: kpub_encode.hex(), "macid": self.macid}
        req_param.update({"id": self.data.iwid, "lastsync": self.data.iwTsync, "ms_n": 1})
        req_param.update(self.get_r())
        xml = self.request(req_param)
        self.data.synchro(xml, self.generate_kma(self.codepin))
        return Otp.OK

    def _get_otp_code(self):
        password = self.data.iwK1 + ":" + str(self.defi) + ":" + self.data.iwsecval
        res = bytes(hashlib.sha256(password.encode("utf-8")).digest())
        nb = ((int.from_bytes(res[:4], byteorder="big") & 0xfffffff) * 1024) + (
            int.from_bytes(res[4:8], byteorder="big") & 1023)
        otp = number_to_base36(nb)
        return otp

    def get_otp_code(self):
        self.mode = Otp.OTP_MODE
        otp_code = None
        if self.activation_start():
            res = self.activation_finalyze()
            if res != Otp.NOK:
                if res == Otp.OTP_TWICE:
                    self.mode = Otp.OTP_MODE
                    self.activation_start()
                    self.activation_finalyze()
                otp_code = self._get_otp_code()
                logger.debug("otp code: %s", otp_code)
        if otp_code is None:
            raise ConfigException("Can't get otp code")
        return otp_code

    def __getstate__(self):
        odict = self.__dict__.copy()
        if 'cipher' in odict:
            del odict['cipher']  # don't pickle this
        return odict

    def __setstate__(self, dict_param):
        self.__dict__.update(dict_param)
        if self.Kiw is not None:
            key = RSA.construct((int(self.Kiw, 16), Otp.exponent))
            self.cipher = oaep.new(key, hash_algo=Hash.SHA256)

    @staticmethod
    def set_proxies(proxies):
        Otp.proxies = proxies


def encode_oeap(text, key):
    cipher = oaep.new(bytes.fromhex(key), hash_algo=Hash.SHA256)
    return cipher.encrypt(text)


def save_otp(obj, filename="otp.bin"):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output)


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        renamed_module = "psa_car_controller.psa." + module.lower()
        return super().find_class(renamed_module, name)


def load_otp(filename=CONFIG_NAME):
    try:
        with open(filename, 'rb') as input_file:
            try:
                return pickle.load(input_file)
            except ModuleNotFoundError as ex:
                logger.debug(ex, exc_info=True)
                return RenameUnpickler(input_file).load()
    except FileNotFoundError:
        logger.debug("", exc_info=True)
    return None


def new_otp_session(smscode, codepin, old_otp_session: Otp = None, ):
    if old_otp_session is None:
        otp = Otp("bb8e981582b0f31353108fb020bead1c")
    else:
        otp = Otp("bb8e981582b0f31353108fb020bead1c", device_id=old_otp_session.device_id)
    otp.smsCode = smscode
    otp.codepin = codepin
    if otp.activation_start():
        otp.activation_finalyze()
        save_otp(otp)
        return otp
    return None
