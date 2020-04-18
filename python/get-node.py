#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    https://github.com/brianddk/reddit ... python/get-node.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  https://github.com/brianddk/reddit/tipjar.txt
# [req]     pip3 install trezor

from trezorlib import btc, tools, ui
from trezorlib import MINIMUM_FIRMWARE_VERSION as min_version
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from sys import version_info as py_ver, exit
from time import perf_counter

count = 50

device = get_transport()
client = TrezorClient(transport=device, ui=ui.ClickUI())
fw_min = min_version[client.features.model]
py_min = (3,3,0)
if  fw_min > (client.features.major_version, client.features.minor_version, 
    client.features.patch_version) or py_min > py_ver:
    print(f"Requires FW rev {fw_min} and Python rev {py_min}")
    exit(1)
else:
    address_n = tools.parse_path("m/44'/0'/0'")
    start = perf_counter()
    for i in range(0,count):
        result = btc.get_public_node(
            client,
            address_n,
            coin_name="Testnet"
        )
        print(result.xpub)
        address_n[-1] += 1
    end = perf_counter()
    print(f"Timings: {count/(end-start)} nodes per second")
client.close()
