@echo off
:: [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
:: [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
:: [repo]    github.com/brianddk/reddit/blob/master/batch/electrum_msys.cmd
:: [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
:: [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
:: [req]     https://chocolatey.org/install
setlocal

set electrum_repo=https://github.com/spesmilo/electrum.git
set electrum_tag=4.0.1
set trezor_repo=https://github.com/trezor/trezor-firmware.git
set trezor_tag=python/v0.12.0
set bld_script=%temp%\electrum_bld.sh
set base=auto{conf{,2.13},gen,make-wrapper} libtool make git
set ming=mingw-w64-x86_64-{gcc,libusb,python-{pip,pyqt5}}
set pip=.venv/bin/python -m pip
choco install -y msys2
call RefreshEnv.cmd 
(
  echo cd "%cd%"
  echo pacman -S --needed --noconfirm %base% %ming%
  echo git clone %electrum_repo%
  echo pushd electrum
  echo git fetch --all
  echo git checkout tags/%electrum_tag% -b tmp/%electrum_tag%
  echo git clone %trezor_repo%
  echo pushd trezor-firmware
  echo git fetch --all
  echo git checkout tags/%trezor_tag% -b tmp/%trezor_tag%
  echo rm common/defs/ethereum/aux.png
  echo popd
  echo GCC_TRIPLET_HOST="x86_64-w64-mingw32" contrib/make_libsecp256k1.sh
  echo cp /mingw64/bin/lib{gmp-10,usb-1.0}.dll electrum
  echo python -m pip install pyqt5
  echo python -m venv --system-site-packages .venv
  echo mv electrum/*.dll .venv/bin
  echo source .venv/bin/activate
  echo %pip% install --upgrade setuptools pip
  echo %pip% install -e trezor-firmware/python[hidapi] -e .[full]
  echo .venv/bin/python run_electrum
) > %bld_script%

for /f %%I in ('where mingw64.exe') do set env_cmd=%%~dpIusr\bin\env
REM No idea why an interactive shell is required
%env_cmd% MSYSTEM=MINGW64 /usr/bin/bash -l -c 'source "%bld_script%"'
