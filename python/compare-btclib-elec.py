#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/compare-btclib-elec.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt

# [txid]    a8110bbdd40d65351f615897d98c33cbe33e4ebedb4ba2fc9e8c644423dadc93
# [ref]     https://live.blockcypher.com/btc-testnet/tx/{txid}/
# [req]     python -m pip install bitcoinlib electrum

from bitcoin.core.key import use_libsecp256k1_for_signing
from bitcoin.core import x, b2x
from bitcoin.wallet import CBitcoinSecret
from electrum.ecc import ECPrivkey
from electrum.bitcoin import EncodeBase58Check

use_libsecp256k1_for_signing(True)

sechex  = '535b755a4c265772c4f6c7e0316bfd21e24c9e47441989e14e8133c7cb2f41a3'
hashhex = '9039c54c1c34aa12b69b4dda962f501bb6c9cdb6745014ef326f5d4d0472aa99'

seckey = CBitcoinSecret.from_secret_bytes(x(sechex))
sig    = seckey.sign(x(hashhex))
b_wif  = str(seckey)
b_pub  = b2x(seckey.pub)
b_sig  = b2x(sig)

seckey = ECPrivkey(x(sechex))
sig    = seckey.sign_transaction(x(hashhex))
e_wif  = EncodeBase58Check(b'\x80' + seckey.get_secret_bytes() + b'\x01')
e_pub  = seckey.get_public_key_hex(compressed=True)
e_sig  = b2x(sig)

assert b_wif == e_wif
assert b_pub == e_pub
print("wif:", b_wif)
print("pub:", b_pub)
print("sighash:", hashhex)
print("bitcoinlib sig:", b_sig)
print("electrum sig:  ", e_sig)