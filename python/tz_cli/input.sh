#!/bin/bash
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/tz_cli/input.sh
# [ref]     reddit.com/r/TREZOR/comments/j4lp9g/
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt

secho() {
  sleep 1
  echo $*
}
secho "Testnet"         # coin name
secho "tbtc1.trezor.io" # blockbook server and outpoint (below)
secho "e294c4c172c3d87991b0369e45d6af8584be92914d01e3060fad1ed31d12ff00:0"
secho "m/84'/1'/0'/0/0" # prev_out derivation to signing key
secho "4294967293"      # Sequence for RBF; hex(-3)
secho "segwit"          # Signature type on prev_out to use
secho ""                # NACK to progress to outs
secho "2MsiAgG5LVDmnmJUPnYaCeQnARWGbGSVnr3"        # out[0].addr
secho "10000000"                                   # out[1].amt
secho "tb1q9l0rk0gkgn73d0gc57qn3t3cwvucaj3h8wtrlu" # out[1].addr
secho "20000000"                                   # out[1].amt
secho "tb1qejqxwzfld7zr6mf7ygqy5s5se5xq7vmt96jk9x" # out[2].addr
secho "99999694"                                   # out[2].amt
secho ""                # NACK to progress to change
secho ""                # NACH to skip change
secho "2"               # txn.version
secho "0"               # txn.locktime
