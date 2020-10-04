#!/bin/bash
# [rights]  Copyright 2020 brianddk at github https:# github.com/brianddk
# [license] Apache 2.0 License https:# www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/tz_cli/csign.sh
# [ref]     reddit.com/r/TREZOR/comments/j4lp9g/
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt

source <(gpg2 -dq environ.asc)
# source ... (python venv)
# build_tx=... (path to build script)

test_version() {
  echo "$(md5sum <<DOC
    major_version: 2,
    minor_version: 3,
    patch_version: 0,
DOC
)"
}

verify_version() {
  trezorctl get-features | grep version | md5sum --check <( test_version ) > /dev/null
}

if verify_version then
then
  stxn="$((./input.sh | $build_tx | trezorctl btc sign-tx -) 2> /dev/null)"
fi
deactivate

echo "$stxn"