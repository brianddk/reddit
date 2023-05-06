#!/usr/bin/env python3
# [rights]  Copyright 2023 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/mk_secret.py
# [ref]     github.com/brianddk/reddit/blob/master/markdown/mk_secret.md
# [ref]     reddit.com/r/TREZOR/comments/1345rkr/
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip install mnemonic==0.20 trezor==0.13.5
# [note]    This script is intended to generate secure 128bit secrets
# [note]      provided simple plaintext by using the Trezor API.  See  
# [note]      mk_secret.md in the comment block above for more information

from os import isatty
from sys import stderr, stdout
from getpass import getpass
from argparse import ArgumentParser
from base64 import b64encode, b85encode
from mnemonic import Mnemonic
from trezorlib.btc import get_public_node
from trezorlib.misc import encrypt_keyvalue
from trezorlib.tools import parse_path, b58encode
from trezorlib.client import get_default_client, TrezorClient
from trezorlib.transport import get_transport
from trezorlib.ui import ClickUI

VERSION = "1.0"
PATH = "10016h/0"
BIP32_PATH = parse_path(PATH)
PADDING = "                "

def parse_args():
    parser = ArgumentParser(description='Trezor Secret Maker')
    parser.add_argument('-s', help='session (hex) to use')
    parser.add_argument('-k', help='use key / secret from args (default is stdin)')
    parser.add_argument('-c', type=int, help='clip the the encoding down to NUM characters')
    parser.add_argument('-t', action='store_true', help='trim linefeeds for keyfile use')
    parser.add_argument('-d', action='store_true', help='two lines on stream for verify prompts')
    parser.add_argument('-v', action='store_true', help='verbose will show the generated secret on stdout')
    parser.add_argument('-e', action='store_true', help='extreme verbosity will show the key as well and ALL encodings')
    parser.add_argument('-hex', action='store_true', help='(default) generate base16 (hex) encoding')
    parser.add_argument('-58', action='store_true', help='generate base58 encoding')
    parser.add_argument('-64', action='store_true', help='generate base64 encoding')
    parser.add_argument('-85', action='store_true', help='generate base85 encoding')
    parser.add_argument('-12', action='store_true', help='generate BIP39 12 word mnemonics')
    parser.add_argument('-18', action='store_true', help='generate BIP39 18 word mnemonics')
    parser.add_argument('-24', action='store_true', help='generate BIP39 24 word (default) mnemonics')
    parser.add_argument('-4', action='store_true', help='4-character encoding of BIP39 mnemonic')
    options = parser.parse_args()
    return (parser, options)

def b39encode(encsec, options):
    nemo = Mnemonic("english")
    encsec = encsec + encsec
    if getattr(options, '18'):
        encsec = encsec[:24]
    if getattr(options, '12'):
        encsec = encsec[:16]
    encb39 = nemo.to_mnemonic(encsec[:32])
    enc4ch = []
    for word in encb39.split():
        ch4 = word[0].upper()
        ch4 += (word + " ")[1:4]
        enc4ch += [ch4]
    return (encb39, "".join(enc4ch))

def main():
    try:
        parser, options = parse_args()
    except:
        exit(1)

    if isatty(stdout.fileno()):
        if (options.v or options.e):
            pass
        else:
            print("ERROR2: Won't dump secrets to the console without -v or -e")
            parser.print_help()
            exit(2)

    session = bytes.fromhex(options.s) if options.s else None
    try:
        client = TrezorClient(get_transport(), ClickUI(), session)
        if options.s:
            assert session == client.session_id
    except:
        print("ERROR3: Missing Trezor, or bad session hex")
        exit(3)

    client.ensure_unlocked()
    key = options.k if options.k else getpass('Key / Secret: ', stderr)
    padsec = key + PADDING
    secret = padsec[:(0-len(padsec) % 16)]
    encsec = encrypt_keyvalue(client, BIP32_PATH, key, secret.encode(), True, True)

    enchex = encsec.hex()
    encb58 = b58encode(encsec)
    encb64 = b64encode(encsec).decode()
    encb85 = b85encode(encsec).decode()
    encb39, enc4ch = b39encode(encsec, options)

    msg = enchex
    if getattr(options, '12') or getattr(options, '18') or getattr(options, '24') or getattr(options, '4'):
        msg = enc4ch if getattr(options, '4') else encb39
    elif getattr(options, '58'):
        msg = encb58
    elif getattr(options, '64'):
        msg = encb64
    elif getattr(options, '85'):
        msg = encb85

    if options.c:
        msg = msg[:options.c]

    if options.e:
        fingerprint = hex(get_public_node(client, [0]).root_fingerprint)[2:]
        print('version:', VERSION)
        print('input: [fp: {}, path: "{}", key: "{}", padded_value: "{}"]'.format(fingerprint, PATH, key, padsec))
        print('encoded_b85: "{}"'.format(encb85))
        print('encoded_b64: "{}"'.format(encb64))
        print('encoded_b58: "{}"'.format(encb58))
        print('encoded_hex: "{}"'.format(enchex))
        print('encoded_4ch: "{}"'.format(enc4ch))
        print('encoded_b39: "{}"'.format(encb39))

    elif options.t:
        stdout.write(msg)
    elif options.d:
        print(msg)
        print(msg)
    else:
        print(msg)

if __name__ == "__main__":
    main()
