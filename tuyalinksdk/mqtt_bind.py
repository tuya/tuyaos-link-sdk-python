from hashlib import md5
from tuyalinksdk.mqtt_builder import TuyaMQTT

class MQTTBind(TuyaMQTT):
    def login_sign(self):
        self.clientid_ = 'acon_' + self._devid
        self.usermane_ = 'acon_' + self._devid
        self.password_ = md5(self._signkey).hexdigest()[8:8+8*2]
        self._topic_in = 'd/ai/' + self._devid