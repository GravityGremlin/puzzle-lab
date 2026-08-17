#!/usr/bin/env python3
"""
phase2c_rbb.py — final round for Real Big Block.

Dimensions added after phase2 (15,360) + phase2b (394,820) negatives:
  - 13 extra paragraph selections (dialogue/prose splits, section cuts)
  - BIP44 index extended to 0..20
  - encodings: utf-8, latin-1, cp1252 (2019 browser copies could be legacy)
  - the certified-rule flip + one/two-break joins as the primary hypothesis
"""
import sys, json, time
sys.path.insert(0, '/tmp/opencode/aoi-chapter')
from qc_engine import *

PARAS = [tuple(x) for x in json.load(open('/tmp/opencode/aoi-chapter/paragraphs.json'))]
TARGETS = {'current': '14zMkTgaVXJcxdh4JdWi29MLRR44iUSG9W',
           'superseded': '1EFojcAo2vbhRGCGCa7q8Wwvzss28mhQYC',
           'block76': '13Cv6SXUnzGDT8JHqzzJ8xMPtsSdhJA4wd'}

def sel(*ranges):
    return [t for (p, i, t) in PARAS if any(lo <= (p, i) <= hi for lo, hi in ranges)]

full = [t for (_, _, t) in PARAS]
story = sel(((1, 3), (7, 15)))
# where does the story end / research begin? p8[0] opens the Grycoin part.
story_prose = [t for t in story if t and not t.startswith('"')]
story_dialogue = [t for t in story if t and t.startswith('"')]
early = sel(((1, 3), (5, 16)))
mid_story = sel(((3, 0), (7, 15)))
research_all = sel(((8, 0), (12, 39)))
research_no_satoshi = sel(((8, 0), (9, 2)))
satoshi_only = sel(((9, 4), (12, 39)))
gycoin_part = sel(((5, 6), (9, 2)))
quote_embed = sel(((11, 14), (12, 0)))

SELECTIONS = {
    'full': full,
    'story': story,
    'story_prose': story_prose,
    'story_dialogue': story_dialogue,
    'early': early,
    'mid_story': mid_story,
    'research_all': research_all,
    'research_no_satoshi': research_no_satoshi,
    'satoshi_only': satoshi_only,
    'gycoin_part': gycoin_part,
    'quote_embed': quote_embed,
    'story_plus_quote': story + quote_embed,
    'early_plus_quote': early + quote_embed,
}

JOINS = ['\n', '\r\n', '\n\n', '\r\n\r\n', '\n\n\n', '\r\n\r\n\r\n']
NO_FLIP = set('ITASM')
ENCODINGS = ['utf-8', 'latin-1', 'cp1252']

def itasm_flip(paras):
    out = []
    for p in paras:
        fl = next((c for c in p if c.isalpha()), '')
        if fl and fl.upper() not in NO_FLIP:
            out.append(flip_case(p))
        else:
            out.append(p)
    return out

t0 = time.time()
total = 0
hits = []

def check(text_bytes, tag):
    global total
    e = hashlib.md5(text_bytes).digest()
    for idx in range(21):
        total += 1
        addr = address_from_entropy(e, idx)
        for tname, taddr in TARGETS.items():
            if addr == taddr:
                hits.append({'tag': tag, 'index': idx, 'target': tname, 'md5': e.hex()})
                print('*** MATCH ***', hits[-1], flush=True)

for sel_name, paras in SELECTIONS.items():
    for flip_name, ps in (('none', paras), ('itasm', itasm_flip(paras))):
        for join in JOINS:
            for trail in ('', join, '\n', '\r\n'):
                text = join.join(ps) + trail
                for enc in ENCODINGS:
                    try:
                        b = text.encode(enc)
                    except UnicodeEncodeError:
                        continue
                    check(b, f'{sel_name}/{flip_name}/{join!r}/{trail!r}/{enc}')
    print(f'done {sel_name}, total={total} t={time.time()-t0:.0f}s', flush=True)

json.dump({'total': total, 'secs': time.time() - t0, 'hits': hits},
          open('/tmp/opencode/aoi-chapter/phase2c-results.json', 'w'))
print(f'PHASE2C COMPLETE: {total} derivations in {time.time()-t0:.0f}s, hits={len(hits)}')