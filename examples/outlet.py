#!/usr/bin/env python
import time
import coloredlogs
from tuyalinksdk.client import TuyaClient
from tuyalinksdk.console_qrcode import qrcode_generate

coloredlogs.install(level='DEBUG')

client = TuyaClient(productid='ndo5dfkaiykh95dy',
                    uuid='tuyae53b389a45a00af0',
                    authkey='RUgfPmGAyv3J8nfQ75fPDDic1Tx4UeLW')

def on_connected():
    print('Connected.')

def on_qrcode(url):
    qrcode_generate(url)

def on_reset(data):
    print('Reset:', data)

def on_dps(dps):
    print('DataPoints:', dps)
    client.push_dps(dps)

client.on_connected = on_connected
client.on_qrcode = on_qrcode
client.on_reset = on_reset
client.on_dps = on_dps

client.connect()
client.loop_start()

while True:
    time.sleep(1)