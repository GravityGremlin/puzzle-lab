# Aoi Nakamoto Quizchain — Real Big Block (0.777 BTC) — session results 2026-08-17

All derivations use `qc_engine.py` (certified: author WIF vector, BIP39 tv1/tv2,
BIP32 spec vector, p2pkh(1)).

## Stage One witness (Hal Finney "Bitcoin and me" -> 19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN)

| sweep | space | count | result |
|---|---|---|---|
| flip-letter-subsets x para-sets x joins x trails x idx 0..9 | 128 x 4 x 5 x 2 x 10 | 51,200 | no match |
| position-flip subsets k=3..5 x joins x trails x idx 0..6 | 6,748 x 4 x 2 x 6 | 323,904 | no match |

Conclusion: today's bitcointalk capture differs in content from the 2019-era
text (the repo author's capture produces 4 case-flip-eligible paragraphs, ours
3). Archive capture diff queued (Wayback CDX was 503 during the session).

## Full-chapter sweeps (source: "Second" chapter, 12 Wattpad pages, 273 paragraphs)

Targets: current `14zMkTgaVXJcxdh4JdWi29MLRR44iUSG9W`,
superseded `1EFojcAo2vbhRGCGCa7q8Wwvzss28mhQYC`, Block 76 `13Cv6SXUnzGDT8JHqzzJ8xMPtsSdhJA4wd`.

| sweep | space | count | result |
|---|---|---|---|
| phase2: 13 selections x 4 flips x 6 joins x 2 trails x 2 nbsp x idx 0..9 | — | 15,360 | no match |
| phase2b: page prefixes, punctuation norms, char-class edits, trailing blank runs | — | 394,820 | no match |
| phase2c: prose/dialogue splits, idx 0..20, utf-8/latin-1/cp1252 | — | 39,312 | no match |
| TOTAL | | 449,492 | 0 hits |

Line-break timeline from the author's own posts: v1 (superseded) = ONE break
between paragraphs; v2 (current) = TWO breaks. Both joins were swept.

## Next steps

- 2019-era capture diff (bitcointalk topic 155054, Wattpad chapter) when archive APIs are up.
- Bounded 2-char paragraph-boundary edit sweep (~12.5M derivations, background compute).
- Re-read author's final 27 posts (Reddit JSON blocked from this VM; try HTML route).
