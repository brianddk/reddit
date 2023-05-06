TLDR; Read the warning below, then install trezorctl, then download the script.

* https://trezor.io/learn/a/trezorctl-on-windows
* https://github.com/brianddk/reddit/blob/master/python/mk_secret.py


# Trezor Secret Maker

This `mk_secret.py` utility is a simple python script to help users as Trezor Password Manager enters deprecation.  This utility will take a ascii key and generate 128 bit to 256 bit password with it.  This can be used as a very simple password manager until something more permanent comes around.  

## Single Password Storage

Here's a simple example for single passwords on the Windows console.  Very similar to the linux `pass` utility.

```
python mk_secret.py -k "reddit.com / brianddk" | clip
```

This produces a 128bit password and drops it into the Windows clipboard.  The KEY used is the string "reddit.com / brianddk" which will help the user remember that this password is for reddit, and the username on reddit this is for is u/brianddk.  The process is deterministic, so anytime you enter the same key, you will get the same secret.  Hopefully we all know that my reddit password isn't `828a...1f7a`.  I've been using [hunter2](https://i.kym-cdn.com/photos/images/facebook/001/065/965/989.png) for years now.

## Password Manager Launcher

Another use of this would be to allow you to launch your password manager from the console using a secret generated from your Trezor.  Since we may not like storing passwords on the clipboard, some password managers allow you to use console redirection create and unlock the database.  The following will create a new KeepassXC database with a generated password then launch the empty database for password entry.  Obviously the `db-create` command only needs to be run once to set the initial password.  The following assumes the Windows Console has KeepassXC installed and in the path:

```
python mk_secret.py -d -k "KeepassXC Database" | keepassxc-cli.exe db-create -p TrezorKeepass.kdbx 2> NUL
python mk_secret.py -k "KeepassXC Database" | keepassxc.exe --pw-stdin TrezorKeepass.kdbx
```

## Session Management

If you use a complex passphrase on your Trezor, you may wish to enable session management so you only need to enter the passphrase once, then use the session token thereafter.  Of course, tokens expire when the device is unplugged.  For example the following windows console commands would save off a session-id, then use it to place a password on the clipboard and launch the keepass database.

```
for /f %p in ('trezorctl get-session') do set session=%p
python mk_secret.py -s %session% -k "reddit.com / brianddk" | clip
python mk_secret.py -s %session% -k "KeepassXC Database" | keepassxc.exe --pw-stdin TrezorKeepass.kdbx
```

## Under The Hood

The utility will try to avoid showing secrets on the console unless verbosity (`-v`) is requested.  If EXTREME verbosity (`-e`) is requested you will see all the encodings I could think of.  This includes making BIP39 seeds and passwords of various forms.  Since some sites require symbols and numbers so encodings like base85 might be preferred.  The utility defaults to hex encoding.  The process of making a secret uses the Trezor `encrypt_keyvalue` command.  This is the same API as is used by `trezorctl crypto encrypt-keyvalue -n m/10016h/0 KEY VALUE`.  As you noticed, there is both a KEY and a VALUE mentioned in the arguments.  For simplicity, I simply use a padded version of the `KEY` for the `VALUE`.  The following two commands, one from `trezorctl` and the other with `mk_secret.py` will both produce the same secret.

```
trezorctl -s %session% crypto encrypt-keyvalue -n m/10016h/0 "test key" "test key        "
python mk_secret.py -v -s %session% -k "test key"
```

***NOTE:*** The extreme verbosity display will show a field called `fp`, this is the fingerprint of your current Trezor mnemonic+passphrase.  So long as you have the same fingerprint, you are guaranteed that a given input will produce the same secret.  Here's an example of the extreme verbosity display compared with the `get-public-node`.  Note that the `fp` and `node.fingerprint` fields match.

```
$ trezorctl -s "%session%" btc get-public-node -n "m/0"
Please confirm action on your Trezor device.
node.depth: 1
node.fingerprint: 5c44dd62
node.child_num: 0
node.chain_code: 5ffd052182dce6e2658544ccda9e1aac86bc39545837064eaac5a469bc929f56
node.public_key: 02c7af2fbcb7f6cb5c4d2befc69c71584cf9c83f62ab069136d0be87d282afb433
xpub: xpub68ZqGuoewpDF8TPKMYes2rT2ek7PiCAP6Z5guk8mQWXX4eQ57yCKQFHVrHwyr3Nc4CKbzxWVDLo1qrSD475xYqbep75A74GR9kEGJhFB4dw

$ python mk_secret.py -s "%session% -e -k "test key"                                                                                                                          
Please confirm action on your Trezor device.                                                                                                                               
input: [fp: 5c44dd62, path: "10016h/0", key: "test key", padded_value: "test key                "]                                                                         
encoded_b85: "4LpjOdgpPKS2StLw|U5="                                                                                                                                        
encoded_b64: "DTyKmXrncZVXNGnKt3nIpQ=="                                                                                                                                    
encoded_b58: "2doTDKguKQXv7XkmBtzFXA"                                                                                                                                      
encoded_hex: "0d3c8a997ae77195573469cab779c8a5"                                                                                                                            
encoded_4ch: "ArtwTonePlayVoluJackSkirFresMinoSkirRookImpuEnerStabEarnGrasFrieImmePrimSnacSqueProbRudeCardRebe"                                                            
encoded_b39: "artwork tone play volume jacket skirt fresh minor skirt rookie impulse energy stable earn grass friend immense primary snack squeeze problem rude card rebel"
```

## Requirements

To run this utility you need to have python 3 installed as well as the [trezorctl](https://trezor.io/learn/a/trezorctl-on-windows) utility.  The trezorctl install (`pip install trezor`) will install both the `trezorctl` utility as well as the `trezorlib` python libraries this utility relies on.  Assuming python 3 is already installed, doing the rest could be as simple as the following commands.  Do see the warnings below about running python from a stranger.

```
curl -o https://github.com/brianddk/reddit/blob/master/python/mk_secret.py
pip install trezor
python mk_secret.py -v -k "test key"
``` 

## Reproducibility

All these commands and outputs can be reproduced using the [SLIP-14](https://github.com/satoshilabs/slips/blob/master/slip-0014.md) seed-mnemonic and a passphrase of `mk_secret`.  Nothing up my sleeves.

```
slip-14-mnemonic: all all all all all all all all all all all all
passphrase: mk_secret
```

## Usage
```
usage: mk_secret.py [-h] [-s S] [-k K] [-c C] [-t] [-d] [-v] [-e] [-hex] [-58]
                    [-64] [-85] [-12] [-18] [-24] [-4]

Trezor Secret Maker

optional arguments:
  -h, --help  show this help message and exit
  -s S        session (hex) to use
  -k K        use key / secret from args (default is stdin)
  -c C        clip the the encoding down to NUM characters
  -t          trim linefeeds for keyfile use
  -d          two lines on stream for verify prompts
  -v          verbose will show the generated secret on stdout
  -e          extreme verbosity will show the key as well and ALL encodings
  -hex        (default) generate base16 (hex) encoding
  -58         generate base58 encoding
  -64         generate base64 encoding
  -85         generate base85 encoding
  -12         generate BIP39 12 word mnemonics
  -18         generate BIP39 18 word mnemonics
  -24         generate BIP39 24 word (default) mnemonics
  -4          4-character encoding of BIP39 mnemonic
```

## References

* https://trezor.io/learn/a/trezor-password-manager
* https://trezor.io/learn/a/trezorctl-on-windows
* https://docs.trezor.io/trezor-firmware/python/trezorlib.html
* https://github.com/satoshilabs/slips/blob/master/slip-0014.md
* https://github.com/satoshilabs/slips/blob/master/slip-0016.md
* https://github.com/brianddk/reddit/blob/master/python/mk_secret.py
* https://github.com/brianddk/reddit/blob/master/markdown/mk_secret.md

## BUGS

When I originally created this I had hoped to use the bash [process substitution](https://tldp.org/LDP/abs/html/process-sub.html) feature to let trezor work as a keyfile.  This would look something like:

```
keepassxc-cli db-create --set-key-file <(mk_secret.py -t -s %session% -k "Keepass Keyfile") example.kdbx
```

But unfortunately the filestream reader currently in use with `keepassxc-cli` doesn't support this type of FIFO reads.  There is already an [issue logged with KeepassXC](https://github.com/keepassxreboot/keepassxc/issues/1210#issuecomment-1537018034).  I had added the TRIM (`-t`) argument to the utility in anticipation of this.  Rational was to remove OS dependencies on EOL processing by stripping EOL characters from the stream.  I can verify that the trim feature works, but I can't verify it with KeepassXC till they fix KeepassXC.

# WARNINGS

If you don't read python then DONT download or run any of this code.  Python scripts can have fairly complete access to your filesystem.  It can't read secrets from the Trezor, but file system access is still a lot.  As a general rule of thumb, you should never trust internet strangers.  I may work on getting something like this added to one of the official repositories in the future, but for the most part, that is something up to the maintainers and not entirely within my control.  Hopefully this utility is simple enough to fully understand.

