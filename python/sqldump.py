#!/usr/bin/env python3
# [rights]  Copyright 2021 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/sqldump.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     python -m pip install sqlite-utils
# [note]    This requires a descriptor wallet from v0.21 or v22.0

from sqlite_utils import Database

def snip(data):
    slen = 10
    if len(data) > 3+2*slen:
        return f"{data[:slen]}...{data[(0-slen):]}"
    else:
        return data

def fmt_key(key):
    klen = key[0] + 1
    try:
        ktxt = key[1:klen].decode()
        if ktxt.isprintable():
            ktxt = snip(ktxt)
        else:
            klen = 0
    except:
        klen = 0
        
    if klen > len(key) or klen < 2:
        return snip(key.hex())
    kbin = snip(key[klen:].hex())
    if len(kbin) == 0:
        return ktxt
    return f"{ktxt}, {kbin}"

if __name__ == "__main__":
    db=Database("wallet.dat")
    for row in db['main'].rows:
        key = fmt_key(row['key'])
        value = fmt_key(row['value'])
        
        pref = "{wallet.dat}.main."
        print(f"{pref}{{{key}}} = {value}")
