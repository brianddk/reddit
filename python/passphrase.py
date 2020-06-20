#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/passphrase.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/TREZOR/comments/hcv9ai/
# [req]     pip3 install mnemonic
# [usage]   python passphrase.py

from mnemonic import Mnemonic
from time import sleep
from random import randint

if __name__ == "__main__":
    wordlist = Mnemonic("english").wordlist
    l = 51
    while l > 50:
        m = [wordlist[n] for n in [randint(0,2047) for r in range(0,6)]]
        m = " ".join(m)
        l = len(m)
        sleep(0.1)
    print(m)
    