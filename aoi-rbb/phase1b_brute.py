#!/usr/bin/env python3
"""
phase1b_brute.py — brute-force the Stage One convention.

Space: flip-subset over first-letters {F,W,I,T,A,S,M} (or none/all) x
para-set (body, hal+body, body+edited, hal+body+edited) x joins
(\n, \r\n, \n\n, \r\n\r\n, \r\n\r\n\r\n) x trail ('' or join) x BIP44 index 0..9.
Target: 19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN.
"""
import sys, time, itertools
sys.path.insert(0, '/tmp/opencode/aoi-chapter')
from qc_engine import *

STAGE1 = '19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN'

body = [
 "I thought I'd write about the last four years, an eventful time for Bitcoin and me.",
 "For those who don't know me, I'm Hal Finney. I got my start in crypto working on an early version of PGP, working closely with Phil Zimmermann. When Phil decided to start PGP Corporation, I was one of the first hires. I would work on PGP until my retirement. At the same time, I got involved with the Cypherpunks. I ran the first cryptographically based anonymous remailer, among other activities.",
 "Fast forward to late 2008 and the announcement of Bitcoin. I've noticed that cryptographic graybeards (I was in my mid 50's) tend to get cynical. I was more idealistic; I have always loved crypto, the mystery and the paradox of it.",
 "When Satoshi announced Bitcoin on the cryptography mailing list, he got a skeptical reception at best. Cryptographers have seen too many grand schemes by clueless noobs. They tend to have a knee jerk reaction.",
 "I was more positive. I had long been interested in cryptographic payment schemes. Plus I was lucky enough to meet and extensively correspond with both Wei Dai and Nick Szabo, generally acknowledged to have created ideas that would be realized with Bitcoin. I had made an attempt to create my own proof of work based currency, called RPOW. So I found Bitcoin facinating.",
 "When Satoshi announced the first release of the software, I grabbed it right away. I think I was the first person besides Satoshi to run bitcoin. I mined block 70-something, and I was the recipient of the first bitcoin transaction, when Satoshi sent ten coins to me as a test. I carried on an email conversation with Satoshi over the next few days, mostly me reporting bugs and him fixing them.",
 "Today, Satoshi's true identity has become a mystery. But at the time, I thought I was dealing with a young man of Japanese ancestry who was very smart and sincere. I've had the good fortune to know many brilliant people over the course of my life, so I recognize the signs.",
 "After a few days, bitcoin was running pretty stably, so I left it running. Those were the days when difficulty was 1, and you could find blocks with a CPU, not even a GPU. I mined several blocks over the next days. But I turned it off because it made my computer run hot, and the fan noise bothered me. In retrospect, I wish I had kept it up longer, but on the other hand I was extraordinarily lucky to be there at the beginning. It's one of those glass half full half empty things.",
 "The next I heard of Bitcoin was late 2010, when I was surprised to find that it was not only still going, bitcoins actually had monetary value. I dusted off my old wallet, and was relieved to discover that my bitcoins were still there. As the price climbed up to real money, I transferred the coins into an offline wallet, where hopefully they'll be worth something to my heirs.",
 "Speaking of heirs, I got a surprise in 2009, when I was suddenly diagnosed with a fatal disease. I was in the best shape of my life at the start of that year, I'd lost a lot of weight and taken up distance running. I'd run several half marathons, and I was starting to train for a full marathon. I worked my way up to 20+ mile runs, and I thought I was all set. That's when everything went wrong.",
 "My body began to fail. I slurred my speech, lost strength in my hands, and my legs were slow to recover. In August, 2009, I was diagnosed with ALS, which is a fatal disease.",
 "ALS is a disease that kills moter neurons, which carry signals from the brain to the muscles. It causes first weakness, then paralysis. It usually kills within 2-5 years. There are no effective therapies. It is rarely even mentioned in the news; the Ice Bucket Challenge gained some attention for it, although it resulted in little actual benefit. Most people with this disease die within a few years of diagnosis.",
 "Today, I am essentially paralyzed. I am fed through a tube, and my breathing is assisted through another tube. I operate the computer with eye tracking, which has worked out quite well for me. I can even write code, slowly. It's a wonderful thing to have good health, and I try not to take it for granted. I've lived a very good life overall so far; I have no complaints.",
 "It has been an adjustment, but my life is not too bad. I can still read, listen to music, and watch TV and movies. I recently got to the point where I can even write code, and I'm improving. I communicate by writing and my words are spoken by a computer.",
 "And of course the price gyrations of bitcoins are entertaining to me. I have skin in the game. But I came by my bitcoins through luck, with little credit to me. I lived through the early days, maybe too long without paying attention. Regardless, my bitcoins are now as safe under my cold dead fingers as they can be.",
 "That's my story. I'm pretty lucky overall. Even with the ALS, my life is very satisfying. But my life expectancy is limited. I'm 61 years old, and I've lived a wonderful life. On the whole, I'm quite content with what I've gotten out of life, and with what I've been able to give back.",
]

para_sets = {
    'body': body,
    'hal+body': ['Hal:'] + body,
    'body+edited': body + ['[edited slightly]'],
    'hal+body+edited': ['Hal:'] + body + ['[edited slightly]'],
}
joins = ['\n', '\r\n', '\n\n', '\r\n\r\n', '\r\n\r\n\r\n']
letters = sorted({p[0] for p in body if p[0].isalpha()})
print('first letters present:', letters)

def flip_letter_set(paras, flip_set):
    out = []
    for p in paras:
        fl = next((c for c in p if c.isalpha()), '')
        if fl and fl.upper() in flip_set:
            out.append(flip_case(p))
        else:
            out.append(p)
    return out

t0 = time.time()
count = 0
found = None
# all subsets of letters (include empty set = no flip, full set = flip all)
subsets = []
for r in range(len(letters) + 1):
    subsets += list(itertools.combinations(letters, r))
print('flip subsets:', len(subsets))
for sel_name, paras in para_sets.items():
    for flip_set in subsets:
        fs = set(flip_set)
        ps = flip_letter_set(paras, fs)
        for join in joins:
            for trail in ('', join):
                text = join.join(ps) + trail
                e = md5_entropy(text)
                # hit any index?
                for idx in range(10):
                    count += 1
                    if address_from_entropy(e, idx) == STAGE1:
                        print(f'*** STAGE-ONE MATCH *** sel={sel_name} flip_set={sorted(fs)} join={join!r} trail={trail!r} index={idx}')
                        print('md5:', e.hex(), '| sha256:', hashlib.sha256(text.encode()).hexdigest())
                        found = (sel_name, sorted(fs), join, trail, idx, text)
                        break
                if found:
                    break
            if found:
                break
        if found:
            break
    if found:
        break
print(f'done: {count} derivations in {time.time()-t0:.1f}s')
if not found:
    print('NO MATCH in this space')
else:
    open('/tmp/opencode/aoi-chapter/stage1-convention.json', 'w').write(
        __import__('json').dumps({'sel': found[0], 'flip_set': found[1], 'join': repr(found[2]),
                                  'trail': repr(found[3]), 'index': found[4]}))
    print('convention saved to stage1-convention.json')
    print('winning text sha256:', hashlib.sha256(found[5].encode()).hexdigest())