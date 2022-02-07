# [begin]   Document Hash Starts at the beginning of this line { EOL=`\n` }
# [rights]  Copyright 2022 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/signed-md.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [refA]    github.com/brianddk/reddit/blob/master/markdown/trusting-trust.md
# [refB]    reddit.com/r/Bitcoin/comments/smj1ep/
# [version] 1.0
# [usageA]  <msg.md pgm.py stripGpg | pgm.py stripUnderscore
# [usageB]  <msg.md pgm.py stripGpg | pgm.py setHash | gpg2 --clear-sign \
# [usageB.]    | pgm.py fixupGpg | pgm.py prepGpg | gpg2 --verify
# [verify]  re1='s@(^\[#\]:\x5f\[strip\]\x5f+)' re2='([^\x5f]*)\x5f?' \
# [verify.]    re3='@\2\x20\3\x20\4\x20@g' sh -c \
# [verify.]    'sed -E "$re1$re2$re2$re2$re3" msg.md' | gpg2 --verify

import re
from hashlib import sha256
from requests import get
from sys import stdin, stderr, stdout, argv, exit
from html import unescape
from time import sleep

rStrip  = re.compile(r"^\[#\]:_\[strip\]_{1,}")
rBegin  = re.compile(r"^\[#\]:_\[begin\]_{1,}")
rEnd    = re.compile(r"^\[#\]:_\[end\]_{1,}")
rHash   = re.compile(r"^\[#\]:_\[hash\]_{1,}([0-9a-f]{64})")

encodeLines = lambda l: ("\n".join(l)+"\n").encode()
    
def setHash(lines):
    hash = "hi mom"
    midlines = []
    inMid = False
    for i in range(0, len(lines)):
        line = lines[i]
        if rBegin.match(line): 
            inMid = True
        if inMid:  
            midlines.append(line)
        if rEnd.match(line):
            inMid = False
            data = encodeLines(midlines)
            hash = sha256(data).hexdigest()
        mHash = rHash.match(line)
        if mHash:
            lines[i] = line.replace(mHash.group(1), hash)
            break

    # print(hash, file=stderr)
    # stdout.buffer.write(data)
    return lines

def stripUnderscore(lines):
    for i in range(0, len(lines)):
        line = lines[i]        
        if line.startswith("[#]:"):
            lines[i] = line.replace('_', ' ')
    return lines
    
def stripGpg(lines):
    strippedLines = []
    inMid = False
    for i in range(0, len(lines)):
        line = lines[i]        
        if line.startswith("[#]:"):
            line = line.replace(' ', '_')
        if rBegin.match(line): 
            inMid = True           
        if rEnd.match(line):
            inMid = False
        if inMid:
            strippedLines.append(line)
        else:
            if line == "" or rStrip.match(line):
                pass
            else:
                strippedLines.append(line)
 
    return strippedLines + ['']

def prepGpg(lines):
    for i in range(0, len(lines)):
        line = lines[i]
        if rStrip.match(line):
            line = rStrip.sub("", line)            
            lines[i] = line.replace('_', ' ')

    return lines

def fixupGpg(lines):
    inMid = False
    for i in range(0, len(lines)):
        line = lines[i]
        if rBegin.match(line): 
            inMid = True
        if inMid and line.startswith("-----BEGIN"):
            inMid = False
        if not inMid and line:
            line = line.replace(' ', '_')
            lines[i] = "[#]:_[strip]___" + line

    return lines
    
def getPost(lines):
    sub = argv[2]
    id  = argv[3]
    href = f"https://www.reddit.com/r/{sub}/comments/{id}/.json"
    status = 0
    while True:
        res = get(href)
        status = res.status_code
        if status == 200:
            break
        print(status, file=stderr)
        sleep(3)
    lines = (res.json()[0]['data']['children'][0]['data']['selftext']).split("\n")
    for i in range(0, len(lines)):
        line = lines[i]
        lines[i] = unescape(line)
    return lines

def main():            
    fn = eval(argv[1])
    lines = []
    file = stdin
    # with open('sample_markdown.md', "r") as file:
    if argv[1] != "getPost":
        for line in file:
            lines.append(line.rstrip('\r\n'))
   
    lines = fn(lines)
    stdout.buffer.write(encodeLines(lines))

if __name__ == "__main__":
    main()
    
"""
# Procedure

1. Faucet some Testnet: https://testnet-faucet.mempool.co/
2. Checksum and sign your file
3. OP_RETURN your checksum (max fee)
4. Wait for confirmation
5. Archive the TXN on archive.org
6. Make your doc footer
7. Resign
7. Post doc on reddit
8. Push doc to github
9. Return to tipjar


Samples


< ..\markdown\trusting-trust.md python signed-md.py stripGpg | python signed-md.py stripUnderscore > edit.md

<  python signed-md.py getPost brianddk skzv04 | python signed-md.py stripGpg | python signed-md.py stripUnderscore > edit.md

< ..\markdown\trusting-trust.md python signed-md.py stripGpg | python signed-md.py setHash | gpg2 --clear-sign | python signed-md.py fixupGpg > post.md

< posted.md python signed-md.py prepGpg | gpg2 --verify

< posted.md env re1='s@(^\[#\]:\x5f\[strip\]\x5f+)' re2='([^\x5f]*)\x5f?' re3='@\2\x20\3\x20\4\x20@g' sh -c 'sed -E "$re1$re2$re2$re2$re3"' | gpg2 --verify

< ..\markdown\trusting-trust.md python signed-md.py stripGpg | python signed-md.py setHash | gpg2 --clear-sign | python signed-md.py fixupGpg | python signed-md.py prepGpg | gpg2 --verify

< ..\markdown\trusting-trust.md python signed-md.py stripGpg | python signed-md.py setHash | gpg2 --clear-sign | python signed-md.py fixupGpg | env re1='s@(^\[#\]:\x5f\[strip\]\x5f+)' re2='([^\x5f]*)\x5f?' re3='@\2\x20\3\x20\4\x20@g' sh -c 'sed -E "$re1$re2$re2$re2$re3"' | gpg2 --verify

"""