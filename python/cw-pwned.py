#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/tipjar/cw-pwned.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/CryptoCurrency/comments/gqrf11/_/frxsy8b
# [req]     pip3 pycoin requests

from pycoin.symbols.btc import network as btc
from requests import get

URL = "https://paste.debian.net/plain/1148565"

if __name__ == "__main__":
    resp = get(URL)
    msg, sigs = resp.text.split('"')[1:]
    sigs = sigs.split('\n')[4:-1]
    for sig in sigs:
        addr, sig = sig.split()
        test = "passed" if btc.msg.verify(addr, sig, msg) else "FAILED"
        print(test, addr)
