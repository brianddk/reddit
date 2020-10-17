#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/spend-p2wsh-hodl-tz.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip3 install trezor python-bitcoinlib
import hashlib
import time

from bitcoin import SelectParams
from bitcoin.core import b2x, b2lx, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, CTxInWitness, CTxWitness
from bitcoin.core.script import CScript, CScriptWitness, OP_0, OP_CHECKLOCKTIMEVERIFY, OP_CHECKSIG, OP_DROP, OP_CHECKSIG, SignatureHash, SIGHASH_ALL, SIGVERSION_WITNESS_V0
from bitcoin.wallet import CBitcoinSecret, CBitcoinAddress, P2WSHBitcoinAddress
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from trezorlib.ui import ClickUI
from trezorlib.btc import get_public_node
from trezorlib.misc import decrypt_keyvalue
from trezorlib.tools import parse_path

# ########## Constants
coin = "Testnet"
path = "m/84'/1'/0'/0/0"
nLockTime = 1602572140 # 10/13/2020 @ 6:55am (UTC)
# ########## Constants

def is_valid(priv):
    n = 'FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141'
    priv = int(b2x(priv),16)
    n = int(n.replace(' ',''), 16)
    assert priv > 0
    assert priv < n

device = get_transport()
client = TrezorClient(transport=device, ui=ClickUI())

n_path = parse_path(path)
info = get_public_node(client, n_path, coin_name=coin)
side, pubkey = (info.node.public_key[0], info.node.public_key[1:])
left = True if side == 2 else False
print("seed", b2x(pubkey), side)
priv = decrypt_keyvalue(client, n_path, path, pubkey, ask_on_decrypt = False, ask_on_encrypt = side)
is_valid(priv)
print("priv", b2x(priv), left)

client.close()

SelectParams(coin.lower())
seckey = CBitcoinSecret.from_secret_bytes(priv)

# Create a witnessScript and corresponding redeemScript. Similar to a scriptPubKey
# the redeemScript must be satisfied for the funds to be spent.
txin_witnessScript = CScript([seckey.pub, OP_CHECKSIG])
expiry = lx(hex(nLockTime).replace('0x',''))

# Use OP_HODL to lock the funds in this UTXO until expiry
txin_witnessScript = CScript([expiry, OP_CHECKLOCKTIMEVERIFY, OP_DROP, seckey.pub, OP_CHECKSIG])
txin_scriptHash = hashlib.sha256(txin_witnessScript).digest()
txin_redeemScript = CScript([OP_0, txin_scriptHash])

# Convert the P2WSH scriptPubKey to a base58 Bitcoin address and print it.
# You'll need to send some funds to it to create a txout to spend.
txin_p2wsh_address = P2WSHBitcoinAddress.from_scriptPubKey(txin_redeemScript)
print('Pay to:', str(txin_p2wsh_address))
print('Witness Script:', b2x(txin_witnessScript))
print('PubKey Script:', b2x(txin_redeemScript))
print('Expiry', int(b2lx(expiry), 16))

# Same as the txid:vout the createrawtransaction RPC call requires
# lx() takes *little-endian* hex and converts it to bytes; in Bitcoin
# transaction hashes are shown little-endian rather than the usual big-endian.
txid = lx('ef3fad03b7fd4fe42956e41fccb10ef1a95d98083d3b9246b6c17a88e51c8def')
vout = 1

# Specify the amount send to your P2WSH address.
amount = int(0.0001 * COIN)

# Calculate an amount for the upcoming new UTXO. Set a high fee (5%) to bypass
# bitcoind minfee setting.
amount_less_fee = amount * 0.95

# Create the txin structure, which includes the outpoint. The scriptSig
# defaults to being empty as is necessary for spending a P2WSH output.
# Set nSequence so nLockTime rules can take effect
txin = CMutableTxIn(COutPoint(txid, vout))
txin.nSequence = 0

# Specify a destination address and create the txout.
destination_address = CBitcoinAddress(
    'tb1q5rn69avl3ganw3cmhz5ldcxpash2kusq7sncfl').to_scriptPubKey()
txout = CMutableTxOut(amount_less_fee, destination_address)

# Create the unsigned transaction.
# Set the nLockTime so that OP_HODL will work
tx = CMutableTransaction([txin], [txout])
tx.nLockTime = nLockTime

# Calculate the signature hash for that transaction. Note how the script we use
# is the witnessScript, not the redeemScript.
sighash = SignatureHash(script=txin_witnessScript, txTo=tx, inIdx=0,
                        hashtype=SIGHASH_ALL, amount=amount, sigversion=SIGVERSION_WITNESS_V0)

# Now sign it. We have to append the type of signature we want to the end, in
# this case the usual SIGHASH_ALL.
sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])

# Construct a witness for this P2WSH transaction and add to tx.
witness = CScriptWitness([sig, txin_witnessScript])
tx.wit = CTxWitness([CTxInWitness(witness)])

# Done! Print the transaction to standard output with the bytes-to-hex
# function.
print(b2x(tx.serialize()))
