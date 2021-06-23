import time
import json
import requests
from binascii import b2a_hex
from hashlib import md5
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tuyalinksdk.mqtt_builder import protocol_version

class ATOPBase:
    def __init__(self, enpoint, id, secretkey):
        self.enpoint = enpoint
        self.id = id
        self.secretkey = secretkey

    @staticmethod
    def encrypt(secretkey, data):
        cipher = AES.new(secretkey[:16].encode('utf-8'), AES.MODE_ECB)
        return cipher.encrypt(pad(data.encode("utf-8"), 16, 'pkcs7'))

    @staticmethod
    def decrypt(secretkey, data):
        cipher = AES.new(secretkey[:16].encode('utf-8'), AES.MODE_ECB)
        plaintext = cipher.decrypt(data)
        return json.loads(unpad(plaintext, 16, 'pkcs7'))

    def url_encode(self, params):
        uencode = lambda key,val : key + '=' + val + '&'
        sencode = lambda key,val : key + '=' + val + '||'
        encode  = lambda u,s,key,val : [u + uencode(key, val), s + sencode(key, val)]

        url = self.enpoint + '?'
        sbuf = ''
        url, sbuf = encode(url, sbuf, 'a', params['a'])
        if params.get('devId'):
            url, sbuf = encode(url, sbuf,'devId', params['devId'])
        url, sbuf = encode(url, sbuf, 'et', params['et'])
        url, sbuf = encode(url, sbuf, 't', params['t'])
        if params.get('uuid'):
            url, sbuf = encode(url, sbuf, 'uuid', params['uuid'])
        url, sbuf = encode(url, sbuf, 'v', params['v'])

        md5sign = md5((sbuf + self.secretkey).encode('utf-8'))
        url += 'sign=' + md5sign.digest().hex()
        return url

    def encode(self, data):
        encryptdata = self.encrypt(self.secretkey, json.dumps(data))
        return b"data=" + b2a_hex(encryptdata).upper()

    def decode(self, data):
        if not data.get('result'):
            return data
        encryptdata = b64decode(data['result'])
        return self.decrypt(self.secretkey, encryptdata)

    def post(self, params, data):
        """ inser t """
        t = int(time.time())
        params['t'] = str(t)
        data['t'] = t

        """ URL encode """
        url = self.url_encode(params)

        headers = {
            'User-Agent': 'TUYA_IOT_SDK',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        r = requests.post(url, headers=headers, data=self.encode(data))
        print('response:', r.json())
        return self.decode(r.json())


class ATOPBootstrap(ATOPBase):
    def activate(self, pid, token, verison, other=None):
        params = {
            "a": "tuya.device.active",
            "v": "4.3",
            "uuid": self.id,
            "et": "1"
        }

        data = {
            'token': token,
            'productKey': pid,
            'softVer': verison,
            'protocolVer': protocol_version.decode('utf-8'),
            'baselineVer': '40.00',
            'options': '{\"isFK\":false}',
            'cadVer': '1.0.3',
            'cdVer': '1.0.0'
        }

        if other and type(other) == dict:
            data.update(other)
        return self.post(params, data)


class ATOPService(ATOPBase):
    def requset(self, api, version, data={}):
        params = {
            "a": api,
            "v": version,
            "devId": self.id,
            "et": "1"
        }
        return self.post(params, data)