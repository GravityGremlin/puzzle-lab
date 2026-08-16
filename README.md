# puzzle-lab

Autonomous crypto puzzle research lab. Certified engines, sweep results, and
negative ledgers for public treasure-hunt puzzles. Companion to the
`income-quest` journal (progress notes live there).

## Contents

- `aoi-rbb/qc_engine.py` — pure-Python MD5 -> BIP39 -> BIP44 -> P2PKH engine,
  certified against BIP39 vectors, the BIP32 spec vector, the author-published
  calibration WIF, and p2pkh(1). Used for the Aoi Nakamoto Quizchain Real Big
  Block (0.777 BTC) and Block 76 (0.077 BTC) puzzles.
  - Project page (public research + escrows): floflo777/open-crypto-puzzles,
    `1-big-prizes/aoi-nakamoto-quizchain-0-854btc/`.
- `gsmg/` — GSMG.io 5 BTC final-gate sweeps (OpenSSL AES-256-CBC blob decrypt,
  sha256(X).hex password conventions, KDF settling tests).

## Method notes

- No result is reported without a witness: engines are pinned against known
  vectors before any candidate run (a base58 leading-'1' bug was caught exactly
  this way on 2026-08-16).
- Puzzle source texts are NOT redistributed here (copyright). Link to sources.
- Sweeps log N, method, result, and date.

## Status (2026-08-16)

- GSMG: KDF settled (SHA-256 EVP KDF); 469 phase-text + 5,468 LORE candidates,
  0 matches.
- Aoi RBB: full 12-page chapter (273 paragraphs) identified as the untested
  source; serialization sweep in progress.
