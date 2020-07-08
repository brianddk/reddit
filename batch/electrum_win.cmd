@echo off
:: [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
:: [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
:: [repo]    github.com/brianddk/reddit/blob/master/batch/electrum_win.cmd
:: [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
:: [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
:: [req]     https://chocolatey.org/install
setlocal

set electrum_repo=https://github.com/spesmilo/electrum.git
set electrum_tag=4.0.1
set trezor_repo=https://github.com/trezor/trezor-firmware.git
set trezor_tag=python/v0.12.0
set base=auto{conf{,2.13},gen,make-wrapper} libtool make git
set ming=mingw-w64-x86_64-{gcc,libusb}
set bld_script=%temp%\bld_libsecp256k1.sh
choco install -y python3 vcbuildtools protoc git msys2
call RefreshEnv.cmd 
git clone %electrum_repo%
pushd electrum
git fetch --all
git checkout tags/%electrum_tag% -b tmp/%electrum_tag%
(
  echo cd "%cd%"
  echo pacman -S --needed --noconfirm %base% %ming%
  echo GCC_TRIPLET_HOST="x86_64-w64-mingw32" contrib/make_libsecp256k1.sh
  echo cp /mingw64/bin/lib{gmp-10,usb-1.0}.dll electrum
  echo git clone %trezor_repo%
  echo pushd trezor-firmware
  echo git fetch --all
  echo git checkout tags/%trezor_tag% -b tmp/%trezor_tag%
  echo rm common/defs/ethereum/aux.png
) > %bld_script%
for /f %%I in ('where mingw64.exe') do set env_cmd=%%~dpIusr\bin\env
REM No idea why an interactive shell is required
%env_cmd% MSYSTEM=MINGW64 /usr/bin/bash -l -c 'source "%bld_script%"'
python -m venv .venv
call .venv\Scripts\activate.bat
set pip="%cd%\.venv\Scripts\python.exe" -m pip 
%pip% install --upgrade setuptools pip
%pip% install -e trezor-firmware\python[hidapi,ethereum] -e .[full]
move electrum\*.dll .venv\Lib\site-packages\pywin32_system32
.venv\Scripts\python run_electrum
