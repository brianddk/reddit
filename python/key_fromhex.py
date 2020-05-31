#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/key_fromhex.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/BitcoinBeginners/comments/gtuyha/_/fsemaic/
# [req]     pip3 install pycoin mnemonic
# [usage]   python key_fromhex.py 0660cc198330660cc198330660cc1983

from mnemonic import Mnemonic
from pycoin.symbols.btc import network as btc
from pycoin.networks.bitcoinish import create_bitcoinish_network as btcnet
from sys import argv
from string import hexdigits

ACCT44 = '44H/0H/0H'
ACCT49 = '49H/0H/0H'
ACCT84 = '84H/0H/0H'
HW49 = dict(bip32_pub_prefix_hex="049d7cb2", bip32_prv_prefix_hex="049d7878")
HW84 = dict(bip32_pub_prefix_hex="04b24746", bip32_prv_prefix_hex="04b2430c")

def print_keys(seed, path, kw):
    if kw:
        net = btcnet("", "", "", **dict(wif_prefix_hex="80", **kw))
    else:
        net = btc
    acct = net.keys.bip32_seed(seed).subkey_for_path(path)
    key  = acct.subkey_for_path('0/0')
    hash = key.hash160(is_compressed=True)
    wif  = key.wif()
    if path[0:2] == "44":
        addr = key.address()
    if path[0:2] == "49":
        script = btc.contract.for_p2pkh_wit(hash)
        addr   = btc.address.for_p2s(script)
    if path[0:2] == "84":
        addr   = btc.address.for_p2pkh_wit(hash)   
    xpub = acct.hwif(as_private=False)
    xprv = acct.hwif(as_private=True)
    path += '0/0'
    print(f"\n{xprv}\n{xpub}\nwif @ {path}: {wif}\naddr @ {path}: {addr}")

def main(entropy):
    mnemo = Mnemonic("english")
    mnemonic = mnemo.to_mnemonic(entropy)
    seed = mnemo.to_seed(mnemonic)
    print("Entropy:", f'"{entropy.hex()}"')
    print("Seed:", f'"{seed.hex()}"')
    print(mnemonic)
    print_keys(seed, ACCT44, None)
    print_keys(seed, ACCT49, HW49)
    print_keys(seed, ACCT84, HW84)

if __name__ == "__main__":
    if len(argv) < 2:
        print(f"Usage:\t{argv[0]}", "<hex_string>")
    else:
        hex = argv[1].replace("0x","").strip()
        if all(c in hexdigits for c in hex):
            main(bytes.fromhex(hex))
