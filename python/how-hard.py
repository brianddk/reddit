from requests import get
from re import findall

def calc_msg(block_hash):
    Y = block_hash / (330*10**6) / 60 / 60 / 24 / 365
    M = Y * 12
    d = Y * 365
    W = d / 7
    h = d * 24
    m = h * 60
    s = m * 60
    if Y > 2: return f"{Y:,.2f} years"
    if M > 2: return f"{M:,.2f} months"
    if W > 2: return f"{W:,.2f} weeks"
    if d > 2: return f"{d:,.2f} days"
    if h > 2: return f"{h:,.2f} hours"
    if m > 2: return f"{m:,.2f} minutes"
    if s > 0.02: return f"{s:,.2f} seconds"
    return f"{s:,.8f} seconds"
    
r = get("https://blockchair.com/bitcoin")
content = str(r.content)
hashrate = findall('Hashrate:.*?<span>([0-9,.]+)</span>', content)[-1]
difficulty = findall('Difficulty:.*?<span>([0-9,.]+)</span>', content)[-1]
hashrate = float(hashrate.replace(",","_"))
difficulty = float(difficulty.replace(",","_"))

diff = difficulty * 2**32
d_msg = calc_msg(diff)
# h_msg = calc_msg(hashrate * 60 * 10)

print(f"difficulty: {d_msg}")
print(f"hashes: {diff:,.2f}")
# print(f"hashrate: {h_msg}")
