#!/usr/bin/env python3
"""
phase2_rbb.py — Real Big Block full-chapter sweep.

Source: the "Second" chapter, all 12 Wattpad pages, 273 paragraphs
(/tmp/opencode/aoi-chapter/paragraphs.json — local only, not redistributed).

Hypothesis space (all documented):
  selections x flips x joins x trails x nbsp x BIP44 index 0..9
  targets: RBB current 14zMk..., RBB superseded 1EFoj..., Block 76 13Cv...

Variant dimensions:
  selections:
    full / no_toc / story_a (p1[3]..p7[15]) / story_b (..p8[0]) /
    research (p8[2]..) / satoshi_code (p9[3]..) / 9 quote windows (p11[s]..p12[e]) /
    full_no_dialogue
  flips: none / ITASM rule / all-first-lower / all-last-upper
  joins:  \\n \\r\\n \\n\\n \\r\\n\\r\\n \\r\\n\\r\\n\\r\\n \\n\\n\\n
  trails: '' or join
  nbsp: raw or space-normalized
"""
import sys, json, time, itertools
sys.path.insert(0, '/tmp/opencode/aoi-chapter')
from qc_engine import *

PARAS = [tuple(x) for x in json.load(open('/tmp/opencode/aoi-chapter/paragraphs.json'))]  # (page, idx, text)

def sel(*ranges):
    out = []
    for (p, i, t) in PARAS:
        if any(lo <= (p, i) <= hi for lo, hi in ranges):
            out.append(t)
    return out

SELECTIONS = {
    'full': [t for (_, _, t) in PARAS],
    'no_toc': [t for (p, i, t) in PARAS if (p, i) > (1, 2)],
    'story_a': sel(((1, 3), (7, 15))),
    'story_b': sel(((1, 3), (8, 0))),
    'research': sel(((8, 2), (12, 39))),
    'satoshi_code': sel(((9, 3), (12, 39))),
    'full_no_dialogue': [t for (p, i, t) in PARAS if not t.startswith('"')],
}
for s in (13, 14, 15):
    for e in (0, 1, 2):
        SELECTIONS[f'quote_{s}_{e}'] = sel(((11, s), (12, e)))

JOINS = ['\n', '\r\n', '\n\n', '\r\n\r\n', '\r\n\r\n\r\n', '\n\n\n']
NO_FLIP = set('ITASM')

def itasm_flip(paras):
    out = []
    for p in paras:
        fl = next((c for c in p if c.isalpha()), '')
        if fl and fl.upper() not in NO_FLIP:
            out.append(flip_case(p))
        else:
            out.append(p)
    return out

def first_lower(paras):
    return [flip_case(p) for p in paras]

def last_upper(paras):
    out = []
    for p in paras:
        chars = list(p)
        letters = [i for i, c in enumerate(chars) if c.isalpha()]
        if letters:
            chars[letters[-1]] = chars[letters[-1]].upper()
        out.append(''.join(chars))
    return out

FLIPS = {'none': lambda ps: ps, 'itasm': itasm_flip, 'first_lower': first_lower, 'last_upper': last_upper}
TARGETS = {'current': '14zMkTgaVXJcxdh4JdWi29MLRR44iUSG9W',
           'superseded': '1EFojcAo2vbhRGCGCa7q8Wwvzss28mhQYC',
           'block76': '13Cv6SXUnzGDT8JHqzzJ8xMPtsSdhJA4wd'}

def variants_texts(paras):
    texts = set()
    for join in JOINS:
        for trail in ('', join):
            for nbsp_mode in (0, 1):
                ps = paras
                if nbsp_mode == 1:
                    ps = [t.replace('\xa0', ' ') for t in paras]
                texts.add((join, trail, nbsp_mode, join.join(ps) + trail))
    return texts

t0 = time.time()
total = 0
hits = []
for sel_name, paras in SELECTIONS.items():
    for flip_name, flip_fn in FLIPS.items():
        fparas = flip_fn(paras)
        variants = variants_texts(fparas)
        for (join, trail, nbsp_mode, text) in variants:
            e = md5_entropy(text)
            for idx in range(10):
                total += 1
                addr = address_from_entropy(e, idx)
                for tname, taddr in TARGETS.items():
                    if addr == taddr:
                        hits.append({'selection': sel_name, 'flip': flip_name, 'join': repr(join),
                                     'trail': repr(trail), 'nbsp': nbsp_mode, 'index': idx,
                                     'target': tname, 'md5': e.hex(),
                                     'sha256': hashlib.sha256(text.encode()).hexdigest()})
                        print('*** MATCH ***', hits[-1], flush=True)
        print(f'sel={sel_name} flip={flip_name} done, total={total} t={time.time()-t0:.0f}s', flush=True)

print(f'SWEEP COMPLETE: {total} derivations in {time.time()-t0:.0f}s, hits={len(hits)}')
json.dump({'total': total, 'secs': time.time() - t0, 'hits': hits},
          open('/tmp/opencode/aoi-chapter/phase2-results.json', 'w'))