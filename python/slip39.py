#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/slip39.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/TREZOR/comments/gswh86/_/fs91czu/
# [req]     pip3 install pycoin mnemonic shamir_mnemonic

from mnemonic import Mnemonic
from pycoin.symbols.btc import network as btc
from pycoin.networks.bitcoinish import create_bitcoinish_network as btcnet
from shamir_mnemonic import combine_mnemonics, generate_mnemonics

# Nonsense Passphrase and Master-Seed
PP     = "Pa55w0rd"
MSEC   = "0660cc198330660cc198330660cc1983" # SLIP-14 entryopy for fun

ACCT44 = '44H/0H/0H'
ACCT49 = '49H/0H/0H'
ACCT84 = '84H/0H/0H'
HW49 = dict(bip32_pub_prefix_hex="049d7cb2", bip32_prv_prefix_hex="049d7878")
HW84 = dict(bip32_pub_prefix_hex="04b24746", bip32_prv_prefix_hex="04b2430c")

# Can be done MS -> shamir-mnemonic or shamir-mnemonic -> MS
SSS  = generate_mnemonics(1, [(1,1)], bytes.fromhex(MSEC), PP.encode(), 0)
#SSS = [["armed husband academic academic document aquatic wisdom " +
#        "pleasure lilac response axle parking shaft crazy cargo " +
#        "dish diet dramatic together unfold"]]
seed = combine_mnemonics(SSS[-1],PP.encode())

print(seed.hex())
print(SSS[-1][-1], "\n")

# BIP44 derivations and xpub/xprv prefix
acct44 = btc.keys.bip32_seed(seed).subkey_for_path(ACCT44)
key44  = acct44.subkey_for_path('0/0')
addr44 = key44.address()
xprv44 = acct44.hwif(as_private=True)
xpub44 = acct44.hwif(as_private=False)
print(xprv44)
print(xpub44)
print(addr44, "\n")

# BIP49 derivations and ypub/yprv prefix
btc49  = btcnet("", "", "", **HW49)
acct49 = btc49.keys.bip32_seed(seed).subkey_for_path(ACCT49)
key49  = acct49.subkey_for_path('0/0')
hash49 = key49.hash160(is_compressed=True)
scpt49 = btc.contract.for_p2pkh_wit(hash49)
addr49 = btc.address.for_p2s(scpt49)
xprv49 = acct49.hwif(as_private=True)
xpub49 = acct49.hwif(as_private=False)
print(xprv49)
print(xpub49)
print(addr49, "\n")

# BIP84 derivations and zpub/zprv prefix
btc84  = btcnet("", "", "", **HW84)
acct84 = btc84.keys.bip32_seed(seed).subkey_for_path(ACCT84)
key84  = acct84.subkey_for_path('0/0')
hash84 = key84.hash160(is_compressed=True)
addr84 = btc.address.for_p2pkh_wit(hash84)
xprv84 = acct84.hwif(as_private=True)
xpub84 = acct84.hwif(as_private=False)
print(xprv84)
print(xpub84)
print(addr84)
