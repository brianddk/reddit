@echo off
setlocal
set NC_CLI=C:\tools\msys64\usr\bin\nc.exe
set BTC_CLI=C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe
echo Using:
echo   [%NC_CLI%]
echo   [%BTC_CLI%]
if exist abort.lock (
  echo Removing [abort.lock]
  del abort.lock
)
python btc-herder.py
endlocal
