#!/usr/bin/env python3
"""Position-based flip subsets on the 16-body-paragraph Finney text (k=3,4,5),
joins subset, BIP44 index 0..5. Logs a hit or exhaustion to a file."""
import sys, time, itertools, json
sys.path.insert(0, '/tmp/opencode/aoi-chapter')
from qc_engine import *
exec(open('/tmp/opencode/aoi-chapter/phase1b_brute.py').read().split("para_sets = {")[0].split("# ---")[0])  # reuse 'body'

STAGE1 = '19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN'
joins = ['\n', '\r\n', '\n\n', '\r\n\r\n']
t0 = time.time()
count = 0
for k in (3, 4, 5):
    for combo in itertools.combinations(range(16), k):
        ps = [flip_case(p) if i in combo else p for i, p in enumerate(body)]
        for join in joins:
            for trail in ('', join):
                text = join.join(ps) + trail
                e = md5_entropy(text)
                for idx in range(6):
                    count += 1
                    if address_from_entropy(e, idx) == STAGE1:
                        out = {'match': True, 'k': k, 'positions': combo, 'join': repr(join),
                               'trail': repr(trail), 'index': idx, 'md5': e.hex(),
                               'sha256': hashlib.sha256(text.encode()).hexdigest()}
                        print('*** MATCH ***', out)
                        json.dump(out, open('/tmp/opencode/aoi-chapter/stage1-position-match.json', 'w'))
                        sys.exit(0)
        if count % 50000 < 4800:
            print(f'k={k} combo {combo} count={count} t={time.time()-t0:.0f}s', flush=True)
print(f'NO MATCH: {count} derivations in {time.time()-t0:.0f}s')
open('/tmp/opencode/aoi-chapter/stage1-position-negative.json', 'w').write(json.dumps({'count': count, 'secs': time.time()-t0}))
