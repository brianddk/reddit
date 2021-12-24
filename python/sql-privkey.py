#!/usr/bin/env python3
# [rights]  Copyright 2021 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/sql-privkey.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     python -m pip install sqlite-utils pycoin
# [req]     bitcoin\test\functional directory from bitcoin source (v22.0)
# [note]    This requires a descriptor wallet from v0.21 or v22.0

from pycoin.symbols.xtn import network as tbtc
from pycoin.encoding.b58 import a2b_hashed_base58
from sqlite_utils import Database
from os.path import expandvars, abspath, dirname
from json import dumps
from sys import path
from re import search

testpath = abspath(dirname(__file__) + r'\..\..\bitcoin\test\functional')
path.insert(0, testpath)
from test_framework.script import taproot_construct
from test_framework.descriptors import descsum_create
from test_framework.segwit_addr import Encoding, bech32_encode, convertbits

# filepath = r"%appdata%\Bitcoin\testnet3\wallets\wallet.dat"
filepath = "wallet.dat"

def snip(data):
    enabled = False
    slen = 10
    if enabled and len(data) > 3+2*slen:
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

def print_p2pkh(tprv, path, start=0, end=2):
    root = tbtc.parse(tprv)
    for i in range(start, 1+end):
        npath = path + f"/{i}"
        node  = root.subkey_for_path(npath)
        addr  = node.address()
        print(npath, addr)

def print_p2sh_segwit(tprv, path, start=0, end=2):
    root = tbtc.parse(tprv)
    for i in range(start, 1+end):
        npath  = path + f"/{i}"
        node   = root.subkey_for_path(npath)
        hash   = node.hash160(is_compressed=True)
        script = tbtc.contract.for_p2pkh_wit(hash)
        addr   = tbtc.address.for_p2s(script)
        print(npath, addr)

def print_segwit(tprv, path, start=0, end=2):
    root = tbtc.parse(tprv)
    for i in range(start, 1+end):
        npath = path + f"/{i}"
        node  = root.subkey_for_path(npath)
        hash  = node.hash160(is_compressed=True)
        addr  = tbtc.address.for_p2pkh_wit(hash)
        print(npath, addr)

def print_p2tr(tprv, path, start=0, end=2):
    root = tbtc.parse(tprv)
    for i in range(start, 1+end):
        npath = path + f"/{i}"
        node  = root.subkey_for_path(npath)
        pk    = node.sec()
        p2tr  = taproot_construct(pk[1:])
        words = [1] + convertbits((list(p2tr.output_pubkey)), 8, 5)
        addr  = bech32_encode(Encoding.BECH32M, 'tb', words)
        print(npath, addr)

def main():
    wallet = {}
    db=Database(expandvars(filepath))
    for row in db['main'].rows:
        key = fmt_key(row['key'])
        value = fmt_key(row['value'])

        ktxt = key.split(',')[0].strip()
        kbin = key.split(',')[-1].strip()
        data = { kbin: value }
        if kbin != ktxt:
            data = { ktxt: data }
        if wallet.get(ktxt, False):
            wallet[ktxt].update(data[ktxt])
        else:
            wallet.update(data)
    # print(dumps(wallet, indent=2))

    assert wallet["walletdescriptor"] and wallet["walletdescriptorkey"]
    for dkey in wallet["walletdescriptor"].keys():
        for kkey in wallet["walletdescriptorkey"].keys():
            if kkey.startswith(dkey):
                print()
                desc = wallet["walletdescriptor"][dkey].split('#')[0]
                der  = wallet["walletdescriptorkey"][kkey]
                assert der.startswith('d63081d30201010420')
                m    = search('\(([A-z0-9]*)/', desc)
                pub  = m.group(1)
                path = '/'.join(desc.split('/')[1:-1])
                sec  = bytes.fromhex('00') + bytes.fromhex(der)[9:][:32]
                tpub = a2b_hashed_base58(pub)
                blob = tpub[4:-33] + sec
                prv  = tbtc.bip32_as_string(blob, as_private = True)
                hwif = tbtc.parse(prv).hwif()
                assert hwif == pub
                print(descsum_create(desc))
                desc = desc.replace(pub,prv)
                print(descsum_create(desc))
                if   desc.startswith("pkh(tprv"):
                    print_p2pkh(prv, path)
                elif desc.startswith("sh(wpkh(tprv"):
                    print_p2sh_segwit(prv, path)
                if desc.startswith("wpkh(tprv"):
                    print_segwit(prv, path)
                if desc.startswith("tr(tprv"):
                    print_p2tr(prv, path)

if __name__ == "__main__":
    main()