# TuyaOS Link SDK for Python

- [TuyaOS Link SDK for Python](#tuyaos-link-sdk-for-python)
    - [Minimum Requirements](#minimum-requirements)
    - [Install from PyPI](#install-from-pypi)
    - [Install from source](#install-from-source)
  - [Examples](#examples)
- [License](#license)

### Minimum Requirements
*   Python 3.6+

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

[Examples README](examples)

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

# License

This library is licensed under the MIT License.
