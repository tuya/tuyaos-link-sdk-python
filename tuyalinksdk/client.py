import logging
import json
from base64 import b64encode
from tuyalinksdk.iotdns import Endpoint
from tuyalinksdk.atop import ATOPBootstrap
from tuyalinksdk.atop import ATOPService
from tuyalinksdk.mqtt_builder import TuyaMQTT
from tuyalinksdk.mqtt_bind import MQTTBind
from tuyalinksdk.console_qrcode import qrcode_generate

log = logging.getLogger('TuyaClient')
log.setLevel("DEBUG")

class TuyaClient():
    def __init__(self, productid, uuid, authkey, version='1.0.0', storage_path='./storage.json'):
        self.atop = None
        self.mqtt = None
        self._productid = productid
        self._uuid = uuid
        self._authkey = authkey
        self._version = version
        self._endpoint = {}
        self._storage_dict = {}
        self._storage_path = storage_path
        self._region = self.local_storage_read('region')
        self._regist = self.local_storage_read('regist')
        self._activated = self.local_storage_read('activated')
        self.on_qrcode = None
        self.on_activated = None
        self.on_dps = None
        self.on_reset = None
        self.on_connected = None
        self.on_disconnect = None

    """"""""""""""""" Local data storage """""""""""""""
    def local_storage_read(self, key):
        if not self._storage_dict:
            try:
                with open(self._storage_path, 'r') as f:
                    self._storage_dict = json.loads(f.read())
                    log.debug('storage dict:{}'.format(self._storage_dict))
            except:
                with open(self._storage_path, 'w') as f:
                    f.write(json.dumps(self._storage_dict, indent=4))
        log.debug('storage read({}):{}'.format(
            key, self._storage_dict.get(key)))
        return self._storage_dict.get(key)

    def local_storage_write(self, key, value):
        log.debug('storage write({}):{}'.format(key, value))
        self._storage_dict[key] = value
        with open(self._storage_path, 'w') as f:
            f.write(json.dumps(self._storage_dict, indent=4))

    def local_stogre_remove(self, key):
        log.debug('storage remove({})'.format(key))
        self._storage_dict.pop(key, None)
        with open(self._storage_path, 'w') as f:
            f.write(json.dumps(self._storage_dict, indent=4))

    """"""""""""""""" Event callback """""""""""""""
    def _on_mqtt_event(self, event, msg):
        log.info('MQTT EVENT:{}'.format(event))
        if event == 'CONNECTED':
            if self.on_connected:
                self.on_connected()
        elif event == 'DISCONNECT':
            if self.on_disconnect:
                self.on_disconnect()

    def _on_token(self, token, region, regist='pro'):
        log.info('token:{}, region:{}, regist:{}'.format(token, region, regist))
        self._region = region
        self._regist = regist
        self.local_storage_write('region', self._region)
        self.local_storage_write('regist', self._regist)
        self._endpoint = Endpoint.get(self._region, self._regist)
        log.debug('endpoint:{}'.format(json.dumps(self._endpoint)))

        self.atop = ATOPBootstrap(
            self._endpoint['atop']['url'], self._uuid, self._authkey)
        response = self.atop.activate(self._productid, token, self._version)
        log.debug('response:', response)

        if response and response.get('result'):
            self._activated = response['result']
        log.debug(self._activated)

    def _on_protocol_token(self, data):
        log.debug('data:', data)
        self._on_token(data['token'], data['region'])

    def _on_protocol_dps(self, data):
        if self.on_dps:
            self.on_dps(data['dps'])

    def _on_protocol_reset(self, data):
        self.local_stogre_remove('activated')
        self.mqtt.disconnect()
        if self.on_reset:
            self.on_reset(data)

    def push_dps(self, dps):
        self.mqtt.protocol_publish(self.mqtt.MQ_DPS_DATA_PUSH, {
                                   'devId': self._activated['devId'], 'dps': dps})

    def push_dp_raw(self, dpid, data):
        dps = {
            str(dpid): b64encode(data).decode('utf-8')
        }
        self.mqtt.protocol_publish(self.mqtt.MQ_DPS_DATA_PUSH, {
                                   'devId': self._activated['devId'], 'dps': dps})

    def _activate_process(self):
        self.mqtt = MQTTBind(host=self._endpoint['mqtt']['host'], port=self._endpoint['mqtt']['port'],
                             devid=self._uuid, secretkey=self._authkey, signkey=self._authkey)
        self.mqtt.protocol_register(self.mqtt.MQ_ACTIVE_TOKEN_ON, self._on_protocol_token)
        self.mqtt.enable_logger()
        self.mqtt.connect()

        qrcode_url = 'https://smartapp.tuya.com/s/p?p={}&uuid={}&v=2.0'.format(self._productid, self._uuid)
        log.info('>>> ' + qrcode_url)
        if self.on_qrcode:
            self.on_qrcode(qrcode_url)

        while not self._activated:
            self.mqtt.loop()
        log.info('Activated!')
        self.mqtt.disconnect()
        return self._activated

    def reset(self):
        self._on_protocol_reset(None)
        return self.atop.requset(api='tuya.device.reset', version='4.0')

    def connect(self, keepalive=100):
        '''IoTdns Endpoint get'''
        if not self._endpoint:
            self._endpoint = Endpoint.get(self._region, self._regist)
            log.debug(self._endpoint)

        '''If not activated, enter activate mode.'''
        if not self._activated:
            log.warning('not activated')
            self._activated = self._activate_process()
            self.local_storage_write('activated', self._activated)

        '''Event callback'''
        if self.on_activated:
            self.on_activated()

        '''ATOP service'''
        self.atop = ATOPService(self._endpoint['atop']['url'], self._activated['devId'], self._activated['secKey'])

        '''Create the MQTT client'''
        self.mqtt = TuyaMQTT(self._endpoint['mqtt']['host'], self._endpoint['mqtt']['port'],
                             self._activated['devId'], self._activated['localKey'], self._activated['secKey'])

        '''Default MQTT event callback register'''
        self.mqtt.event_callback = self._on_mqtt_event
        self.mqtt.protocol_register(self.mqtt.MQ_DPS_DATA_ON, self._on_protocol_dps)
        self.mqtt.protocol_register(self.mqtt.MQ_RESET_ON, self._on_protocol_reset)

        '''MQTT Connect'''
        return self.mqtt.connect(keepalive)

    def loop(self, timeout=1.0, max_packets=1):
        self.mqtt.loop(timeout=1.0, max_packets=1)

    def loop_forever(self, timeout=1.0, max_packets=1, retry_first_connection=False):
        self.mqtt.loop_forever(timeout, max_packets, retry_first_connection)

    def loop_start(self):
        self.mqtt.loop_start()

    def loop_stop(self, force=False):
        self.mqtt.loop_stop(force)
