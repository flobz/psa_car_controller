import hashlib
from locale import atoi
from time import time

from Cryptodome.Cipher import AES

from .tokenizer import Tokenizer

DEFAULT_TOKEN = "0.2.11&&&&&&0&&0&&0&&9f13ba238fbabba08e85d93638e98ef5e48682a9d3e5bc325c3dd6fac8199a6ce09e9b4f373aa6a" \
                "75a905c3d690f6e3335d1e8e5b748ecec3020a794149033f6ada6896db6d73b8d43b8365bbe15b9ac66f49d4e684a3628f1e" \
                "9f3deda0c4e24aba771946e6085b92c5ad312477152acf8db01e6aea4b409d5ac1a05c2fd4e95&&0&&&&&&&&&&&&0&&0&&0&" \
                "&0&&0&&0&&0&&&&&&&&0&&0&&0&&0&&0&&2.0.0&&http://m.inwebo.com/&&"
DEFAULT_VERSION = "529"


def filter_load(string: str):
    return string.replace("&amp;", "&")


class IWData:
    # pylint: disable=invalid-name,too-many-branches,too-many-statements
    def __init__(self, IW):
        self.IW = IW
        self.tokenizer = Tokenizer(DEFAULT_TOKEN)
        self.tokenizer.nextToken()
        self.load1xx(int(DEFAULT_VERSION), self.tokenizer)

    def load1xx(self, j, tokenizer):
        self.iwid = tokenizer.nextToken()
        self.iwalea = tokenizer.nextToken()
        self.iwblocked = tokenizer.nextTokenI()
        if j >= 519:
            self.iwhasnopin = tokenizer.nextTokenI()
        self.iwTsync = tokenizer.nextTokenI()
        self.kfact = tokenizer.nextToken()
        if self.IW.isMac:
            self.iwconnected = tokenizer.nextTokenI()
            self.iwserver = tokenizer.nextToken()
        self.iwJ = tokenizer.nextToken()
        self.iwK = tokenizer.nextToken()
        self.iwK0 = tokenizer.nextToken()
        self.iwK1 = tokenizer.nextToken()
        self.iwTref = tokenizer.nextTokenI()
        self.iwcancelpin = tokenizer.nextTokenI()
        self.iwnboka = tokenizer.nextTokenI()
        self.iwlastt1 = tokenizer.nextTokenI()
        self.iwlastt2 = tokenizer.nextTokenI()
        self.iwlastt3 = tokenizer.nextTokenI()
        self.iwlastbp = tokenizer.nextTokenI()
        self.iwstackrand = tokenizer.nextToken()
        self.iwstack = tokenizer.nextToken()
        self.iwH = tokenizer.nextToken()
        nextTokenI = tokenizer.nextTokenI()
        self.iwsrvn = nextTokenI
        self.iwsrvid = [None] * (nextTokenI)
        self.iwsrvname = [None] * (nextTokenI)
        self.iwsrvlogo = [None] * (nextTokenI)
        self.iwsrvurl = [None] * (nextTokenI)
        self.iwsrvonlineotp = [None] * (nextTokenI)
        if self.IW.isMac:
            self.iwsrvconnected = [None] * (self.iwsrvn)
        j2 = self.iwsrvn
        self.iwsrvsecure = [None] * (j2)
        self.iwsrvksc = [None] * (j2)
        i = 0
        while i < self.iwsrvn:
            self.iwsrvid[i] = tokenizer.nextToken()
            self.iwsrvname[i] = filter_load(tokenizer.nextToken())
            self.iwsrvlogo[i] = filter_load(tokenizer.nextToken())
            if self.IW.isMac:
                self.iwsrvconnected[i] = tokenizer.nextTokenI()
            if j > 515:
                i2 = 1
            elif j == 515:
                i2 = 0
            else:
                i2 = -1
            if i2 < 0 or self.IW.isMac:
                self.iwsrvurl[i] = ""
            else:
                self.iwsrvurl[i] = filter_load(tokenizer.nextToken())
            if j < 520 or self.IW.isMac:
                self.iwsrvonlineotp[i] = 0
            else:
                self.iwsrvonlineotp[i] = tokenizer.nextTokenI()
            self.iwsrvsecure[i] = tokenizer.nextToken()
            if i2 < 0 or not self.IW.isMac:
                self.iwsrvksc[i] = ""
            else:
                self.iwsrvksc[i] = tokenizer.nextToken()
            i += 1
        nextTokenI2 = tokenizer.nextTokenI()
        self.iwsecn = nextTokenI2
        self.iwsecid = [None] * (nextTokenI2)
        self.iwsecval = [None] * (nextTokenI2)
        i3 = 0
        while ((i3)) < self.iwsecn:
            self.iwsecid[i3] = tokenizer.nextToken()
            self.iwsecval[i3] = tokenizer.nextToken()
            i3 += 1
        self.iwmsgn = tokenizer.nextTokenI()
        self.iwmsgtime = tokenizer.nextTokenI()
        self.iwmsgid = ""
        self.iwmsgtitle = ""
        self.iwmsgcontent = ""
        self.iwmsgack = ""
        i4 = 0
        while i4 < self.iwmsgn:
            self.iwmsgid += tokenizer.nextToken()
            self.iwmsgtitle += filter_load(tokenizer.nextToken())
            self.iwmsgcontent += filter_load(tokenizer.nextToken())
            self.iwmsgack += tokenizer.nextTokenI()
            i4 += 1
        self.iwmajorversion = tokenizer.nextTokenI()
        self.iwnewversion = filter_load(tokenizer.nextToken())
        self.iwnewversionurl = filter_load(tokenizer.nextToken())
        self.mustupgrade = False
        self.datatouch = 0

    def synchro(self, ixml: dict, key):
        aes_cipher = AES.new(bytes.fromhex(key), AES.MODE_ECB)
        value = ixml.get("id")
        if value is not None and len(value) > 0:
            self.iwid = value
        value = ixml.get("server")
        if value is not None and len(value) > 0:
            self.iwserver = value
        value = ixml.get("K0")
        if value is not None and len(value) > 0:
            self.iwK0 = aes_cipher.decrypt(bytes.fromhex(value)).hex()
        value = ixml.get("K1")
        if value is not None and len(value) > 0:
            self.iwK1 = aes_cipher.decrypt(bytes.fromhex(value)).hex()
        value = ixml.get("dK1")
        if value is not None and len(value) > 0:
            self.iwK1 = hashlib.sha256(("" + self.iwK1 + ";" + value).encode("utf-8")).hexdigest()[0:32]
        value = ixml.get("J")
        if value is not None and len(value) > 0:
            self.iwJ = value
            self.iwTref = int(time())
            self.IW.otpRetryService = -1
        value = ixml.get("K")
        if value is not None and len(value) > 0:
            self.iwK = value
        value = ixml.get("H")
        if value is not None and len(value) > 0:
            self.iwH = aes_cipher.decrypt(bytes.fromhex(value))
        value = ixml.get("connected")
        if value is not None and len(value) > 0:
            self.iwconnected = atoi(value) + int(time())
        value = ixml.get("s_n")
        if value is not None and len(value) > 0:
            self.iwcancelpin = 0
            self.iwnboka = 0
            self.iwlastt1 = 0
            self.iwlastt2 = 0
            self.iwlastt3 = 0
            self.iwlastbp = 0
            self.iwstackrand = ""
            self.iwstack = ""
            self.iwTsync = ixml.get("Tsync")
            self.iwsrvn = ixml.get("s_n")
            self.iwsrvid = ixml.get("s_id")
            self.iwsrvname = ixml.get("s_name")
            self.iwsrvlogo = ixml.get("s_icon")
            self.iwsrvconnected = ixml.get("s_connected")
            self.iwsrvksc = ixml.get("s_ksc")
            self.iwsrvsecure = ixml.get("s_secure")
            self.iwsrvurl = ixml.get("s_url")
            self.iwsrvonlineotp = ixml.get("s_onlineotp")
            self.IW.synchroJustDone = 1
        value = ixml.get("m_n")
        if value is not None and len(value) > 0:
            self.iwmsgtime = int(time())
            self.iwmsgn = ixml.get("m_n")
            self.iwmsgid = ixml.get("m_id")
            self.iwmsgtitle = ixml.get("m_title")
            self.iwmsgcontent = ixml.get("m_content")
            self.iwmsgack = ixml.get("m_ack")
        self.datatouch = 1
