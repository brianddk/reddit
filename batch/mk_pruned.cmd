@echo off
:: [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
:: [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
:: [repo]    github.com/brianddk/reddit/blob/master/batch/mk_pruned.cmd
:: [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
:: [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
:: [req]     https://bitcoin.org/en/download
:: [usage]   Please edit the suggested block below
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM ############################################### MER
REM ### Please edit the section below as needed ### MER
REM ############################################### MER

REM Give the location of your full block data
set _full_=%APPDATA%\Bitcoin

REM Tell where you want to put your pruned data
set _pruned_=S:\Bitcoin

REM Are you runing Testnet or Mainnet?
set mainnet=\
set testnet=\testnet3\
set _network_=%testnet%

REM How many MB do you want to reduce block data to?
set /a "pruned_mb=550"

REM ################################################# MER
REM ### No more edits should be needed below here ### MER
REM ################################################# MER

set /a "pruned_mb=550"

set mainnet=\
set testnet=\testnet3\
set _network_=%testnet%

set full_blk=%_full_%%_network_%blocks
set full_blk_idx=%_full_%%_network_%blocks\index
set full_chainstates=%_full_%%_network_%chainstate
set pruned_blk=%_pruned_%%_network_%blocks
set pruned_blk_idx=%_pruned_%%_network_%blocks\index
set pruned_chainstate=%_pruned_%%_network_%chainstate

mkdir %pruned_blk%
mkdir %pruned_blk_idx%
mkdir %pruned_chainstate%

(
  echo prune=%pruned_mb%
) > %_pruned_%\bitcoin.conf

robocopy /s %full_blk_idx% %pruned_blk_idx%
robocopy /s %full_chainstates% %pruned_chainstate%

set /a "sum=0"
for /f %%I in ('dir /s /b /o:-n %full_blk%\blk*.dat') do (
  set size=%%~zI
  set blkdat=%%~nxI
  set revdat=!blkdat:blk=rev!
  if !sum! GTR !pruned_mb! (
    echo.> %pruned_blk%\!blkdat!
    echo.> %pruned_blk%\!revdat!
  ) else (
    copy %full_blk%\!blkdat! %pruned_blk%\!blkdat!
    copy %full_blk%\!revdat! %pruned_blk%\!revdat!
  )
  set /a "sum=!sum! -1 + !size!/(1024*1024)"
)

if "%_network_%"=="%testnet%" set tnarg=-testnet
echo A pruned clone of your existing block data has been copied.
echo   To complete the pruning process run:
echo.
echo "%PROGRAMFILES%\Bitcoin\bitcoin-qt.exe" %tnarg% ^^
echo   -datadir=%_pruned_% ^^
echo   -conf=%_pruned_%\bitcoin.conf

endlocal