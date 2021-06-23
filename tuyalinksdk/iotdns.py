import requests
from base64 import b64decode

class Endpoint():
    @staticmethod
    def get(region=None, env='pro'):
        config = {
            "config": [
                {
                    "key": "httpsUrl",
                    "need_ca": False
                },
                {
                    "key": "mqttsUrl",
                    "need_ca": False
                }
            ]
        }

        if region:
            config['region'] = region
            config['env'] = env
        
        r = requests.post(url='https://h1.iot-dns.com/v1/url_config', json=config).json()

        mqtthost = r['mqttsUrl']['addr'].split(':')[0]
        mqttport = int(r['mqttsUrl']['addr'].split(':')[1])

        endpoint = {
            'mqtt': {
                'host':mqtthost,
                'port':mqttport
            },
            'atop': {
                'url':r['httpsUrl']['addr']
            }
        }

        return endpoint