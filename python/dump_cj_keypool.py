#!/usr/bin/env python3
# [rights]  Copyright 2023 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/dump_cj_keypool.py
# [ref]     github.com/trezor/blockbook/issues/921
# [ref]     reddit.com/r/TREZOR/comments/1311ekf/
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip install bip-utils==2.7.0 trezor==0.13.5
# [note]    This script will modify the device settings for safety-checks 
# [note]      and passphrase.  This is intentional to allow different
# [note]      configs.  To control this behavior, modify the defines in
# [note]      the "#CONFIG" block of this script below.  You can also reset
# [note]      these settings using the following two trezorctl commands
# [note]        trezorctl set passphrase --help
# [note]        trezorctl set safety-checks --help

# tbtc2.trezor.io/xpub/{descriptor}?tokens=derived

from sys import stderr
from bip_utils import Bip44, Bip44Changes, Bip44Coins, Bip86, Bip86Coins
from bip_utils import Bip32Slip10Secp256k1, Bip39SeedGenerator
from trezorlib import btc, messages
from trezorlib.device import apply_settings
from trezorlib.tools import b58check_encode, b58decode
from trezorlib.client import TrezorClient, get_default_client
from trezorlib.tools import parse_path
from trezorlib.ui import ClickUI

#CONFIG - Modify these settings as needed
NUM_ACCOUNTS = 2                                       # Number of accounts to enumerate
NUM_ADDRESSES = 200                                    # Number of addresses to enumerate
USE_PASSPHRASE = True                                  # On or off... you choose
PASSPHRASE_ON_DEVIE = True                             # Only possible on Trezor-T
COIN_NAME = "Testnet"                                  # "Testnet" or "Bitcoin"
PATH_TEMPLATE = "m/10025'/1'/{}'/1'"                   # Coinjoin path
# PATH_TEMPLATE = "m/86'/1'/{}'"                         # Standard BIP86 path
# SAFETY_CHECKS = messages.SafetyCheckLevel.PromptAlways # Required for exotic path
# SAFETY_CHECKS = messages.SafetyCheckLevel.Strict       # Default setting 

def initialize_device() -> TrezorClient:
    client = get_default_client(ui=ClickUI(passphrase_on_host=not PASSPHRASE_ON_DEVIE))
    # if client.features.safety_checks != SAFETY_CHECKS:
        # stderr.write("Modifying Safety Checks per #CONFIG block\n")
        # apply_settings(client, safety_checks=SAFETY_CHECKS)
    if bool(client.features.passphrase_protection) != USE_PASSPHRASE:
        stderr.write("Modifying Passphrase enablement per #CONFIG block\n")
        apply_settings(client, use_passphrase=USE_PASSPHRASE)
    client.ensure_unlocked()
    return client

def set_depth(xpub, s_path) -> tuple:
    # bip_utils / blockbook hack which requires xpub depth after account to be 3
    bytes = b58decode(xpub)
    depth = bytes[4]                                         # depth is held in byte #5
    if depth > 3:
        depth = 3
        l_path = s_path.split("/")
        s_path = "_".join(l_path[:2]).replace("'", "h") + "/" + "/".join(l_path[2:])
    mod = bytes[:4] + depth.to_bytes(1, 'big') + bytes[5:78] # trim off checksum
    xpub = b58check_encode(mod)
    return (xpub, s_path)                                    # return modified xpub

def main() -> None:
    client = initialize_device()
    cj_path = PATH_TEMPLATE
    bip_coin = Bip86Coins.BITCOIN_TESTNET if COIN_NAME == "Testnet" else Bip86Coins.BITCOIN
    accts = []
    for acct in range(NUM_ACCOUNTS):
        s_path = cj_path.format(acct)
        n_path = parse_path(s_path)
        stderr.write("Grabbing XPUB at {} approval may be required\n".format(s_path))
        try:
            # Some paths need to be unlocked, others don't, lazy, so just try both ways
            xpub = btc.get_public_node(client, n=n_path, coin_name=COIN_NAME, unlock_path=[n_path[0]]).xpub
        except:
            xpub = btc.get_public_node(client, n=n_path, coin_name=COIN_NAME).xpub
        r_xpub, r_path = set_depth(xpub, s_path)
        stderr.write("orig: tr([{}]{}/<0;1>/*)\n".format(s_path, xpub))
        stderr.write("mod:  tr([{}]{}/<0;1>/*)\n".format(r_path, r_xpub))
        accts += [(s_path, r_xpub)]

    for acct in accts:
        s_path, xpub = acct
        for chng in range(2):
            for indx in range(NUM_ADDRESSES):
                bip86_obj = Bip86.FromExtendedKey(xpub, bip_coin)
                node = bip86_obj.Change(Bip44Changes(chng)).AddressIndex(indx)
                addr = node.PublicKey().ToAddress()
                print("{}/{}/{}\t".format(s_path, chng, indx), addr)

if __name__ == "__main__":
    main()
    
