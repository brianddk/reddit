@echo off
:: [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
:: [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
:: [repo]    github.com/brianddk/reddit/blob/master/batch/parseln.bat
:: [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
:: [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
:: [req]     pip3 bitstring base58

setlocal
set python=..\..\lightning-payencode\pyvenv\Scripts\python.exe
set paydecode=%python% ..\..\lightning-payencode\lightning-address.py decode
set parseln=%python% ..\python\parseln.py
set invoice="lnbc50u1p0tcly4pp5y5h78ltdhgxq3yps3ag0g0n9xmejqf2hq8azvc2np48jc9u7nn0qdqdw5hhxatdgf2yxxqr4rq9qy9qsqsp5rxhmfpp8hkn47x6d25u8ggxzwycqmk6m9h8r3uazg0jexks7d3fqrzjqwryaup9lh50kkranzgcdnn2fgvx390wgj5jd07rwr3vxeje0glc7zxlpyqqfpgqqqqqqqlgqqqqqeqqjqtkavq9crdtw3jxaf86xyx0ejyeky25v7k4lzpl23per354xpcz6pl5rxlsdqruzvg3pz0p8fste2p8dej2x2plh895m0dgk7mysudfsqjw6p7v"
if not "%1"=="" set invoice="%~1"
%paydecode% %invoice%
%parseln%   %invoice%
