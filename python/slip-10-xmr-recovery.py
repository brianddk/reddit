#!/usr/bin/env python3
# [rights]  Copyright 2023 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/slip-10-xmr-recovery.py
# [ref]     github.com/satoshilabs/slips/blob/e9e52e8/slip-0010/testvectors.py
# [ref]     reddit.com/r/TREZOR/comments/1345rkr/
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip install trezor==0.13.7 monero==1.1.1 ed25519==1.5
# [note]    This script is for emergancy recovery of Monero funds from a
# [note]      Trezor-T hardware wallet.  User should change replace one of the
# [note]      pre-defined mnemonics and derivation if needed.

## INSTALL ##
#
# python -m venv xmr.venv
# xmr.venv\Scripts\activate.bat
# python -m pip install --upgrade pip setuptools wheel
# python -m pip install trezor monero ed25519

## REFERENCES ##
#
# See https://github.com/satoshilabs/slips/blob/e9e52e8/slip-0010.md
# See https://github.com/satoshilabs/slips/blob/e9e52e8/slip-0010/testvectors.py
# See https://github.com/satoshilabs/slips/blob/e9e52e8/slip-0014.md
# See https://github.com/trezor/trezor-firmware/blob/fee0d70/tests/common.py#L37
# See https://github.com/trezor/trezor-firmware/blob/fee0d70/tests/device_tests/monero/test_getaddress.py#L33
# See https://github.com/trezor/trezor-firmware/blob/fee0d70/docs/misc/coins-bip44-paths.md

## TODO ##
#
# - [x] Monero
# - [ ] Cardano 
# - [ ] Stellar 
# - [ ] NEM 
# - [ ] Tezos

import binascii
import hashlib
import hmac
import struct
import ecdsa
import ed25519
from mnemonic import Mnemonic
from trezorlib.tools import parse_path
import monero.seed

VERSION=0.2
privdev = 0x80000000
# See https://github.com/satoshilabs/slips/blob/e9e52e8/slip-0014.md
YOUR_MNEMONIC = "all all all all all all all all all all all all"
YOUR_PASSPHRASE = "hunter2"

# See https://github.com/trezor/trezor-firmware/blob/fee0d70/tests/common.py#L37
MNEMONIC12_TEST = "alcohol woman abuse must during monitor noble actual mixed trade anger aisle"


def int_to_string(x, pad):
    result = ['\x00'] * pad
    while x > 0:
        pad -= 1
        ordinal = x & 0xFF
        result[pad] = (chr(ordinal))
        x >>= 8
    return ''.join(result)


def string_to_int(s):
    result = 0
    for c in s:
        if not isinstance(c, int):
            c = ord(c)
        result = (result << 8) + c
    return result


# mode 0 - compatible with BIP32 private derivation
def seed2hdnode(seed, modifier, curve):
    k = seed
    while True:
        h = hmac.new(modifier.encode(), seed, hashlib.sha512).digest()
        key, chaincode = h[:32], h[32:]
        a = string_to_int(key)
        if (curve == 'ed25519'):
            break
        if (a < curve.order and a != 0):
            break
        seed = h
    return (key, chaincode)


def publickey(private_key, curve):
    if curve == 'ed25519':
        sk = ed25519.SigningKey(private_key)
        return b'\x00' + sk.get_verifying_key().to_bytes()
    else:
        Q = string_to_int(private_key) * curve.generator
        xstr = int_to_string(Q.x(), 32)
        parity = Q.y() & 1
        return chr(2 + parity) + xstr


def derive(parent_key, parent_chaincode, i, curve):
    assert len(parent_key) == 32
    assert len(parent_chaincode) == 32
    k = parent_chaincode
    if ((i & privdev) != 0):
        key = b'\x00' + parent_key
    else:
        key = publickey(parent_key, curve)
    d = key + struct.pack('>L', i)
    while True:
        h = hmac.new(k, d, hashlib.sha512).digest()
        key, chaincode = h[:32], h[32:]
        if curve == 'ed25519':
            break
        a = string_to_int(key)
        key = (a + string_to_int(parent_key)) % curve.order
        if (a < curve.order and key != 0):
            key = int_to_string(key, 32)
            break
        d = '\x01' + h[32:] + struct.pack('>L', i)                        
    return (key, chaincode)


def get_curve_info(curvename):
    if curvename == 'secp256k1':
        return (ecdsa.curves.SECP256k1, 'Bitcoin seed') 
    if curvename == 'nist256p1':
        return (ecdsa.curves.NIST256p, 'Nist256p1 seed') 
    if curvename == 'ed25519':
        return ('ed25519', 'ed25519 seed')
    raise BaseException('unsupported curve: '+curvename)


def get_keys(seedhex, derivationpath):
    curve, seedmodifier = get_curve_info('ed25519')
    master_seed = binascii.unhexlify(seedhex)
    k,c = seed2hdnode(master_seed, seedmodifier, curve)
    p = publickey(k, curve)
    depth = 0
    for i in derivationpath:
        i = i | privdev
        depth = depth + 1
        k,c = derive(k, c, i, curve)
        p = publickey(k, curve) 
    return p,k


def print_keys(derivation, mnemonic, passphrase = ""):
    bip39_seed = Mnemonic("English").to_seed(mnemonic, passphrase)
    pub, priv = get_keys(bip39_seed.hex(), parse_path(derivation))
    seed = monero.seed.Seed(priv.hex())
    pub_hex = '12' + seed.public_spend_key() + seed.public_view_key()
    chksum = monero.keccak.keccak_256(bytes.fromhex(pub_hex)).digest().hex()
    address = monero.base58.encode(pub_hex + chksum[:8])
    print("BIP39 Mnemonic:", mnemonic)
    print("BIP39 Seed:", bip39_seed.hex())
    print("SLIP10 Derivation:", derivation)
    print("SLIP10 Seed at Derivation:", priv.hex())
    print("Monero Mnemonic:\n    ", seed.phrase)
    print("Monero Address:", address)
    print("Monero Public Spend:", seed.public_spend_key())
    print("Monero Public View:", seed.public_view_key())
    print("Monero Private Spend:", seed.secret_spend_key())
    print("Monero Private View:", seed.secret_view_key())
    return address
    

derivation = "m/44h/128h/0h"
print("Version: ", VERSION)
print("\n\n### YOUR BROKEN SEED ###\n")
print_keys(derivation, YOUR_MNEMONIC, YOUR_PASSPHRASE)

print("\n\n### VERIFICATION TEST ###\n")
assert(print_keys(derivation, MNEMONIC12_TEST)
    # See https://github.com/trezor/trezor-firmware/blob/fee0d70/tests/device_tests/monero/test_getaddress.py#L33
    == "4Ahp23WfMrMFK3wYL2hLWQFGt87ZTeRkufS6JoQZu6MEFDokAQeGWmu9MA3GFq1yVLSJQbKJqVAn9F9DLYGpRzRAEXqAXKM")
