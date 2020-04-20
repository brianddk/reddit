#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/get-node.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip3 install trezor

from trezorlib import btc, tools, ui, __version__ as lib_version
from trezorlib import MINIMUM_FIRMWARE_VERSION as min_version
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from sys import version_info as py_ver, exit
from time import perf_counter

count = 50

device = get_transport()
client = TrezorClient(transport=device, ui=ui.ClickUI())
fw = client.features
fw_min = min_version[fw.model]
py_min = (3,6,0)
tl_min = [0,12,0]
if (fw_min > (fw.major_version, fw.minor_version,fw.patch_version) or 
    tl_min > [int(i) for i in lib_version.split('.')] or py_min > py_ver):
    m = "Requires at least Python rev {}, trezorlib rev {}, and FW rev {}"
    print(m.format(py_min, tl_min, fw_min))
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
