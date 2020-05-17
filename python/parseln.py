from json import dumps
from sys import argv

BECHSET  = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
PYB32SET = "0123456789abcdefghijklmnopqrstuv"

def str_split(s, l):
    lst = []
    for i in range(0, len(s), l):
        lst += [ s[i:i+l] ]
    return lst

def bech32_decode(bech, hex=False):
    rtn = 0
    data = [PYB32SET[BECHSET.find(x)] for x in bech]
    rtn = int(''.join(data), base=32)    # int data is big-endian
    if hex:               # hex data is little-endian (shift required)
        l = len(data)
        bwi = 5 * l
        bwo = bwi // 8 * 8
        num = rtn >> (bwi - bwo)
        hex = f"{num:x}"
        pad = "0" * (bwo // 4 - len(hex))
        rtn = pad + hex
    return rtn

class ParseInv:
    def __init__(self, invoice):
        self._broke = self._done = self._currentTag = self._lastTag = None
        self._inv = invoice[0:-110]
        self.signature = invoice[-110:-6]
        self.checksum = invoice[-6:]
        self.hrp = self.hrp()
        self.timestamp = self.timestamp()

        # "psdnhxcfr"
        for tag in "psh":   # parse these tags as hex
            setattr(self, 'case_' + tag, self.default_hex)

        for tag in "n": # parse these tags as raw bech
            setattr(self, 'case_' + tag, self.default_bech)

        for tag in "xc":   # parse these tags as int
            setattr(self, 'case_' + tag, self.default_int)

        while(not self._done):
            self.bite()

    def dequeue(self, len):
        rtn = self._inv[0:len]
        self._inv = self._inv[len:]
        return rtn

    def hrp(self):
        i = self._inv.rfind('1')
        rtn = self.dequeue(i)
        self.dequeue(1)
        return rtn

    def timestamp(self):
        bech = self.dequeue(7)
        return bech32_decode(bech)

    def done(self):
        self._done = True

    def bite(self):
        self._lastTag = self._currentTag
        if len(self._inv):
            self._currentTag = self.dequeue(1)
            bech = self.dequeue(2)
            l = bech32_decode(bech)
            bech = self.dequeue(l)
            fnc = getattr(self, 'case_' + self._currentTag, self.broke)
            fnc(bech, l, self._currentTag)
        else:
            self.done()

    def case_d(self, bech, l, tag): # 'd' requires a shift operand
        h = bech32_decode(bech, hex=True)
        self.d = bytes.fromhex(h).decode('utf-8')

    def case_9(self, bech, l, tag): # can't have a class prop called '9'
        self.nine = bech

    def default_int(self, bech, l, tag):
        i = bech32_decode(bech)
        setattr(self, tag, i) # just set prop to data as int

    def default_hex(self, bech, l, tag):
        h = bech32_decode(bech, hex=True)
        setattr(self, tag, h) # just set prop to data as hex

    def case_f(self, bech, l, tag):
        self.f = getattr(self, tag, []) + str_split(bech, 33)

    def case_r(self, bech, l, tag):        
        hx = bech32_decode(bech, hex=True)
        nl = 66
        lst = [
            dict(
                node = r[0:nl],
                short_chid = [int(r[b:e],16) for b,e in ((nl+0,  nl+6),
                                                         (nl+6,  nl+12), 
                                                         (nl+12, nl+16))],
                fee_base  = int(r[nl+16: nl+24],16),
                fee_mills = int(r[nl+24: nl+32],16),
                cltv_exp  = int(r[nl+32: nl+36],16)
            )
            for r in str_split(hx, 102)
        ]
        self.r = getattr(self, tag, []) + lst

    def default_bech(self, bech, l, tag):
        setattr(self, tag, bech) # just set prop to bech data

    def broke(self, bech, l, tag, msg = "ERROR: Tag {} of len {} is invalid"):
        self._broke = msg.format(tag, l)
        self._inv = bech + self._inv
        print("Incorrect tag:", self._currentTag)
        self.done()

    def __str__(self):
        keys = ['hrp', 'timestamp']+[i for i in "psdnhxcfr"]+['nine', 'signature', 'checksum']
        if(self._broke):
            keys += ['_lastTag', '_inv', '_broke']
        d = {}
        for k in keys:
            v = getattr(self, k, None)
            if v:
                d[k] = getattr(self, k, None)
        return dumps(d, indent=4)

if __name__ == '__main__':
    print(ParseInv(argv[1]))
