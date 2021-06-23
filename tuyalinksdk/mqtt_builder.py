import json
import time
import logging
import struct
from hashlib import md5
from binascii import crc32
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import paho.mqtt.client as mqtt

protocol_version = b'2.2'
PV22_HEADERLEN = 3 + 4 + 4 + 4

log = logging.getLogger('TuyaMQTT')
log.setLevel("DEBUG")

class TuyaMQTT(mqtt.Client):
    def __init__(self, host, port, devid, secretkey, signkey):
        self.host_ = host
        self.port_ = port
        self.clientid_ = ''
        self.usermane_ = ''
        self.password_ = ''
        self._devid = devid
        self._secretkey = secretkey.encode('utf-8')
        self._signkey = signkey.encode('utf-8')
        self._topic_in = ''
        self._topic_out = ''
        self._sequence = 0
        self.protocol_list = {}
        self.login_sign()
        self.event_callback = None
        super().__init__(client_id=self.clientid_, protocol=mqtt.MQTTv311)

        '''Protocol ID'''
        self.MQ_DPS_DATA_PUSH = 4
        self.MQ_DPS_DATA_ON = 5
        self.MQ_RESET_ON = 11
        self.MQ_ACTIVE_TOKEN_ON = 46

    @staticmethod
    def decode(key, data):
        """ unpack """
        protocol, crc32, sequence, source = struct.unpack('!3sIII', data[:PV22_HEADERLEN])
        if protocol != protocol_version:
            log.error("version error:", protocol)
            return None

        encryptdata = data[PV22_HEADERLEN:]
        if len(encryptdata) % 16 != 0:
            log.error("data len error:", len(encryptdata))
            return None

        """ AES DECRYPT """
        cipher = AES.new(key[:16], AES.MODE_ECB)
        plaintext = unpad(cipher.decrypt(encryptdata), 16).decode('utf-8')
        return [sequence, source, json.loads(plaintext)]

    @staticmethod
    def encode(key, sequence, source, data):
        """ AES ENCRYPT """
        cipher = AES.new(key[:16], AES.MODE_ECB)
        paddata = pad(json.dumps(data).encode('utf-8'), 16)
        encryptdata = cipher.encrypt(paddata)
        """ pack """
        buffer = bytearray(protocol_version) # 2.2
        ssbytes = struct.pack("!II", sequence, source)
        buffer += struct.pack('!I', crc32(ssbytes + encryptdata)) # crc32
        buffer += ssbytes # sequence, source
        buffer += encryptdata # data
        return buffer

    def login_sign(self):
        self.clientid_ = self._devid
        self.usermane_ = self._devid
        self.password_ = md5(self._signkey).hexdigest()[8:8+8*2]
        self._topic_in = 'smart/device/in/' + self._devid
        self._topic_out = 'smart/device/out/' + self._devid

    def on_connect(self, client, userdata, flags, rc):
        log.info("Connected:{}".format(flags))
        log.debug("Subscribing:" + self._topic_in)
        self.subscribe(self._topic_in, qos=1)

    def on_disconnect(self, client, userdata, rc):
        log.info("Disconnect")
        if self.event_callback:
            self.event_callback('DISCONNECT', None)

    def on_message(self, mqttc, obj, msg):
        log.debug(msg.topic+" "+str(msg.qos)+" "+ msg.payload.hex())
        if msg.topic == self._topic_in:
            raw = self.decode(self._secretkey, msg.payload)
            self._sequence = raw[0]
            payload = raw[2]
            protocol_id = payload['protocol']
            log.debug('message decode:{}'.format(payload))
            if self.protocol_list.get(protocol_id):
                self.protocol_list[protocol_id](payload['data'])

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        log.debug("Subscribed: "+str(mid)+" "+str(granted_qos))
        if self.event_callback:
            self.event_callback('CONNECTED', None)

    def on_log(self, mqttc, obj, level, string):
        log.debug('log >>>> ' + string)

    def connect(self, keepalive=100):
        self.tls_set()
        self.username_pw_set(self.usermane_, self.password_)
        log.debug('self.host_:' + self.host_)
        log.debug('self.port_:' + str(self.port_))
        log.debug('self.clientid_:' + self.clientid_)
        log.debug('self.usermane_:' + self.usermane_)
        log.debug('self.password_:' + self.password_)
        return super().connect(self.host_, self.port_, keepalive)

    def protocol_register(self, protocol_id, func):
        self.protocol_list[protocol_id] = func

    def protocol_publish(self, protocol_id, data):
        payload = {
            "protocol":protocol_id,
            "t":int(time.time()),
            "data":data
        }
        log.debug('Publish payload:{}'.format(payload))
        self._sequence = self._sequence + 1
        buffer = self.encode(self._secretkey, self._sequence, 1, payload)
        self.publish(self._topic_out, buffer, qos=1)
    