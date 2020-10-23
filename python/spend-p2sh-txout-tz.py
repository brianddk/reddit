#!/usr/bin/env python3

# Copyright (C) 2014 The python-bitcoinlib developers
#
# This file is part of python-bitcoinlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoinlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

"""Low-level example of how to spend a P2SH/BIP16 txout"""

import sys
from os import environ
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

from bitcoin.core.key import use_libsecp256k1_for_signing
try:
    use_libsecp256k1_for_signing(True)
except:
    print("WARNING: Not using libsecp256k1 will introduce malleability")
    print("See: https://github.com/petertodd/python-bitcoinlib/issues/237")
    use_libsecp256k1_for_signing(False)

import hashlib
import time

from bitcoin import SelectParams
from bitcoin.core import b2x, b2lx, lx, x, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.script import CScript, OP_CHECKLOCKTIMEVERIFY, OP_CHECKSIG, OP_DROP, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.rpc import Proxy
try:
    from trezorlib.client import TrezorClient
    from trezorlib.transport import get_transport
    from trezorlib.ui import ClickUI
    from trezorlib.btc import get_public_node
    from trezorlib.misc import encrypt_keyvalue, decrypt_keyvalue
    from trezorlib.tools import parse_path
    trezor = True
except:
    trezor = False

# ########## Constants
coin = "Testnet"
path = "m/84'/1'/0'/0/0"
# nLockTime = 1602572140 # 10/13/2020 @ 6:55am (UTC)
nLockTime = 1602565200 # 10/13/2020
# ########## Constants

def get_actual_txn():
    return """
        0100000001e296627fff145212b64dfc998e90496e7e0d0ecf88412db0f2
        a5c09d30714fd10000000073473044022052b22153ad3c70c171d5dac2b9
        c6d5321a4287c876548f55f7003b72059d3f22022024451c5396c3f30fdd
        518fda68b1ec7078610c0a3c5d27b3084dd30c58c8da56012a045034855f
        b1752103998b9a8696e184125ae18e9c09d2ba26dde67779e6b76dd8e4cf
        87d21e0a8c0aacfdffffff01fe22000000000000160014f6e158d445313b
        b09563c4d4e73573ad514722cc5034855f
        """.replace('\n', '').replace(' ','')

# Bare minimum secp256k1 bounds check
# 
def is_valid(priv):
    n = 'FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141'
    assert len(priv) == 32
    priv = int(b2x(priv),16)
    n = int(n.replace(' ',''), 16)
    assert priv > 0
    assert priv < n

# Use AES to mix private and public key data to "export" a derived private key
# Likely kinda sketchy crypto voodoo, but seems to work
#    
def get_tz_priv(coin, path):    
    session_id = bytes.fromhex(environ.get('TZ_SESSIONID', ''))
    if trezor and len(session_id) == 32:
        device = get_transport()
        client = TrezorClient(transport=device, ui=ClickUI(), session_id=session_id)
        n_path = parse_path("m/10065'/0'") # Logical path for BIP0065 operation
        info = get_public_node(client, n_path, coin_name=coin)
        side, pubkey = (info.node.public_key[0], info.node.public_key[1:])
        left = True if side == 2 else False
        print("seed", b2x(pubkey), side)
        priv = encrypt_keyvalue(client, n_path, path, pubkey, ask_on_decrypt = side, ask_on_encrypt = False)
        client.close()
        print("priv", b2x(priv), left)
        is_valid(priv)
        return CBitcoinSecret.from_secret_bytes(priv)
    else:
        print("trezorlib must be available")
        print("see: https://pypi.org/project/trezor/")
        print("TZ_SESSIONID enviroinment variable required")
        print("See: trezorctl get-session --help")
        sys.exit(2)
    
def get_core_priv():
    proxy = Proxy()
    address = proxy.getnewaddress()
    # address = 'tb1qntuv4la0lh072jtr6ce3avrsghnc200dgamlpq'
    proxy._call("walletpassphrase", "P@55w0rd", 5)
    wif = proxy.dumpprivkey(address)    
    proxy._call("walletlock")
    print("address", address)
    return CBitcoinSecret(str(wif))

SelectParams(coin.lower())

# Make a private key with Trezor if you have one
# seckey = get_tz_priv(coin, path)

# Otherwise pull a private key from Core
# seckey = get_core_priv()

# Or just hardcode it
seckey = CBitcoinSecret('cQNjiPwYKMBr2oB3bWzf3rgBsu198xb8Nxxe51k6D3zVTA98L25N')

print("wif", seckey)
print("pubk", b2x(seckey.pub))
expiry = lx(hex(nLockTime).replace('0x',''))

# Create a redeemScript. Similar to a scriptPubKey the redeemScript must be
# satisfied for the funds to be spent.
txin_redeemScript = CScript([expiry, OP_CHECKLOCKTIMEVERIFY, OP_DROP, seckey.pub, OP_CHECKSIG])
print("redeem", b2x(txin_redeemScript))

# Create the magic P2SH scriptPubKey format from that redeemScript. You should
# look at the CScript.to_p2sh_scriptPubKey() function in bitcoin.core.script to
# understand what's happening, as well as read BIP16:
# https://github.com/bitcoin/bips/blob/master/bip-0016.mediawiki
txin_scriptPubKey = txin_redeemScript.to_p2sh_scriptPubKey()

# Convert the P2SH scriptPubKey to a base58 Bitcoin address and print it.
# You'll need to send some funds to it to create a txout to spend.
txin_p2sh_address = CBitcoinAddress.from_scriptPubKey(txin_scriptPubKey)
print('Pay to:',str(txin_p2sh_address))

# Same as the txid:vout the createrawtransaction RPC call requires
#
# lx() takes *little-endian* hex and converts it to bytes; in Bitcoin
# transaction hashes are shown little-endian rather than the usual big-endian.
# There's also a corresponding x() convenience function that takes big-endian
# hex and converts it to bytes.
txid = lx('6d500966f9e494b38a04545f0cea35fc7b3944e341a64b804fed71cdee11d434')
vout = 1
amount = 0.00009999*COIN
amount_less_fees = amount - 200

# Create the txin structure, which includes the outpoint. The scriptSig
# defaults to being empty.
txin = CMutableTxIn(COutPoint(txid, vout))
binzero = 2**32
txin.nSequence = binzero - 3

# Create the txout. This time we create the scriptPubKey from a Bitcoin
# address.
txout = CMutableTxOut(amount_less_fees, CBitcoinAddress('tb1qv9hg20f0g08d460l67ph6p4ukwt7m0ttqzj7mk').to_scriptPubKey())

# Create the unsigned transaction.
tx = CMutableTransaction([txin], [txout])
tx.nLockTime = nLockTime

# Calculate the signature hash for that transaction. Note how the script we use
# is the redeemScript, not the scriptPubKey. That's because when the CHECKSIG
# operation happens EvalScript() will be evaluating the redeemScript, so the
# corresponding SignatureHash() function will use that same script when it
# replaces the scriptSig in the transaction being hashed with the script being
# executed.
sighash = SignatureHash(txin_redeemScript, tx, 0, SIGHASH_ALL)
print("hash:", b2x(sighash))
print(b2x(bytes([SIGHASH_ALL])))

# Now sign it. We have to append the type of signature we want to the end, in
# this case the usual SIGHASH_ALL.
sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])

print("sig:", b2x(sig))
# Set the scriptSig of our transaction input appropriately.
txin.scriptSig = CScript([sig, txin_redeemScript])

# Verify the signature worked. This calls EvalScript() and actually executes
# the opcodes in the scripts to see if everything worked out. If it doesn't an
# exception will be raised.
VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))

# Done! Print the transaction to standard output with the bytes-to-hex
# function.
txn = tx.serialize()
print("raw size:", len(txn))
print("txid:", b2lx(tx.GetTxid()))
txn = b2x(txn)
# txn = get_actual_txn()
print(txn)
