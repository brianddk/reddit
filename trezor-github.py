#!/usr/bin/env python3
# [rights]  Copyright 2021 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/trezor-github.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     python -m pip install trezor

print("Spinning up Trezor runtime and hardware... standby")
from trezorlib.misc import encrypt_keyvalue, decrypt_keyvalue
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from trezorlib.ui import ClickUI
from trezorlib.tools import parse_path
from sys import exit, stdin
from json import dump, dumps
from requests import get
from re import search
from base64 import b85encode, b85decode

enc_with_pad = lambda c: (c+(' '*16))[:0-(16+len(c))%16].encode()
    
token_store = dict(
    key       = "Github API Token",
    path      = "m/6'/9'/42'/0",    # HHGG path since 6 * 9 = 42 # lol"
    cipherB85 = "qWxi1+KR+C*fY=TI!SxL6UjY{dy;}pwvu66A64u^K1N9~(F}Dz>Yqf;%RCs?"
)

class NoPassphraseUi(ClickUI):
    def __init__(self):
        super().__init__(passphrase_on_host = True)
    def get_passphrase(self, available_on_device = False):
        return ""

class TokenStore():
    def __init__(self, key, path):
        self.client = TrezorClient(transport=get_transport(), ui=NoPassphraseUi())
        self.path = parse_path(path)
        self.key = key

    def encrypt(self, cleartext):
        return b85encode(self._crypt(enc_with_pad(cleartext))).decode()
                
    def decrypt(self, cipherB85):
        return self._crypt(b85decode(cipherB85), True).decode().strip()
                
    def _crypt(self, value, decrypt = False):
        method = decrypt_keyvalue if decrypt else encrypt_keyvalue
        return method(self.client, self.path, self.key, value, False)
    
store = TokenStore(token_store['key'], token_store['path'])

# To produce cipherB85
# print("Please enter your secret in STDIN for encoding")
# apikey = stdin.readline().strip()
# print(f"cipherB85: [{store.encrypt(apikey)}]")
# exit(1)

apikey = store.decrypt(token_store['cipherB85'])
print(f"Got {token_store['key']}, fetching data over REST... standby")
head = {'Authorization': f"token {apikey}"}
req = get("https://api.github.com/rate_limit", headers=head)
if req.json()['resources']['core']['limit'] >= 5000:
    print("Github API Token verified")
else:
    print("Your API token was rejected for some reason")
