# TuyaOS Link SDK for Python

The TuyaOS Link SDK is built with C programming language, which provides interface encapsulation of basic services such as device activation, DP upstream and downstream, and firmware OTA upgrade. It is suitable for developers to connect the logic services of a self-developed device to the the cloud.

> **Time-limited activity**:
>
> Welcome to join in the [Tuya Beta Test](http://iot.tuya.com/?_source=9e2500920fe2275d1d1d5192dadd3f79) to get your development gifts and make the contribution to this Git repo. Your feedback is valuable to the whole Tuya community.

## Table of contents

- [Minimum Requirements](#minimum-requirements)
- [Library](#library)
    - [Install from PyPI](#install-from-pypi)
    - [Install from source](#install-from-source)
  - [Examples](#examples)
- [License](#license)

## Minimum requirements

Python 3.6+.

## Library

### Install from PyPI

```
python3 -m pip install tuyalinksdk
```

### Install from source

```
git clone https://github.com/tuya/tuyaos-link-sdk-python.git
python3 -m pip install ./tuyaos-link-sdk-python
```

## Examples

See [Examples](examples).

```python
from tuyalinksdk.client import TuyaClient

client = TuyaClient(productid='PID', uuid='UUID', authkey='AUTHKEY')

def on_connected():
    print('Connected.')

def on_dps(dps):
    print('DataPoints:', dps)
    client.push_dps(dps)

client.on_connected = on_connected
client.on_dps = on_dps
client.connect()
client.loop_start()
```

## License

This library is licensed under the MIT License.
