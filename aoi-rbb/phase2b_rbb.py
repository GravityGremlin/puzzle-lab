#!/usr/bin/env python3
"""
phase2b_rbb.py — round 2 of the full-chapter sweep.

New dimensions after phase2's 15,360 negatives:
  A. page-level prefixes: byline ("AoiNakamoto"), reader header title (2019
     reader showed the section titles as copyable text), title duplication.
  B. punctuation normalization: curly apostrophes/quotes, en/em dashes, ellipsis.
  C. bounded single-char-class edits on the strongest bases (full / no_toc /
     story_a) with joins \n\n and \r\n\r\n: NBSP<->space, ' vs U+2019,
     '-' vs U+2013/U+2014, first-alpha case toggle per paragraph boundary.
  D. trailing paragraph separators: extra blank line runs at the end (how a
     copy of the rendered page ends: with/without a final blank paragraph).
Targets: 14zMk...(current), 1EFoj...(superseded), 13Cv...(block 76).
"""
import sys, json, time, itertools
sys.path.insert(0, '/tmp/opencode/aoi-chapter')
from qc_engine import *

PARAS = [tuple(x) for x in json.load(open('/tmp/opencode/aoi-chapter/paragraphs.json'))]
TARGETS = {'current': '14zMkTgaVXJcxdh4JdWi29MLRR44iUSG9W',
           'superseded': '1EFojcAo2vbhRGCGCa7q8Wwvzss28mhQYC',
           'block76': '13Cv6SXUnzGDT8JHqzzJ8xMPtsSdhJA4wd'}

full = [t for (_, _, t) in PARAS]
no_toc = [t for (p, i, t) in PARAS if (p, i) > (1, 2)]
story_a = [t for (p, i, t) in PARAS if (1, 3) <= (p, i) <= (7, 15)]

JOINS = ['\n\n', '\r\n\r\n']
t0 = time.time()
total = 0
hits = []
results = {}

def check(text, tag):
    global total
    e = md5_entropy(text)
    for idx in range(10):
        total += 1
        addr = address_from_entropy(e, idx)
        for tname, taddr in TARGETS.items():
            if addr == taddr:
                hits.append({'tag': tag, 'index': idx, 'target': tname, 'md5': e.hex(),
                             'sha256': hashlib.sha256(text.encode()).hexdigest()})
                print('*** MATCH ***', hits[-1], flush=True)

# A. page-level prefixes
PREFIXES = ['AoiNakamoto', 'by AoiNakamoto', 'Second', 'Second\nAoiNakamoto']
for pref in PREFIXES:
    for join in JOINS:
        for trail in ('', join):
            for body in (full, no_toc):
                if pref == 'Second' and body is full:
                    continue  # title already present as paragraph 0
                check(pref + join + join.join(body) + trail, f'A:prefix={pref!r} body={len(body)} join={join!r}')
print(f'A done, total={total} t={time.time()-t0:.0f}s', flush=True)

# B. punctuation normalization over the full text
def norm(text, mode):
    repl = {
        'curly': [("'", '\u2019'), ('"', '\u201d')],
        'straight': [('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'), ('\u201d', '"')],
        'dash': [('\u2013', '-'), ('\u2014', '-')],
        'ellipsis': [('\u2026', '...')],
    }[mode]
    for a, b in repl:
        text = text.replace(a, b)
    return text

bases = {'full': full, 'no_toc': no_toc}
for bname, body in bases.items():
    for join in JOINS:
        for trail in ('', join):
            text = join.join(body) + trail
            for mode in ('curly', 'straight', 'dash', 'ellipsis'):
                check(norm(text, mode), f'B:{bname} join={join!r} norm={mode}')
print(f'B done, total={total} t={time.time()-t0:.0f}s', flush=True)

# C. char-class edits on the strongest bases
def edits(body, join):
    """Generate single char-class edits of the joined text."""
    text = join.join(body) + join
    out = set()
    # NBSP<->space at every position
    for i, ch in enumerate(text):
        if ch == '\xa0':
            out.add(text[:i] + ' ' + text[i+1:])
        elif ch == ' ':
            out.add(text[:i] + '\xa0' + text[i+1:])
    # apostrophe class swap
    for i, ch in enumerate(text):
        if ch == "'":
            out.add(text[:i] + '\u2019' + text[i+1:])
        elif ch == '\u2019':
            out.add(text[:i] + "'" + text[i+1:])
    return out

for bname in ('full', 'no_toc', 'story_a'):
    body = {'full': full, 'no_toc': no_toc, 'story_a': story_a}[bname]
    for join in JOINS:
        for t in edits(body, join):
            check(t, f'C:{bname} join={join!r} charclass-edit')
print(f'C done, total={total} t={time.time()-t0:.0f}s', flush=True)

# D. trailing blank-paragraph runs (0..3 extra empty paragraphs at the end)
for bname, body in bases.items():
    for join in JOINS:
        for trail in ('', join, join + join, join * 3):
            check(join.join(body) + trail, f'D:{bname} join={join!r} trail-x{len(trail)//max(len(join),1)}')
print(f'D done, total={total} t={time.time()-t0:.0f}s', flush=True)

json.dump({'total': total, 'secs': time.time() - t0, 'hits': hits},
          open('/tmp/opencode/aoi-chapter/phase2b-results.json', 'w'))
print(f'PHASE2B COMPLETE: {total} derivations in {time.time()-t0:.0f}s, hits={len(hits)}')