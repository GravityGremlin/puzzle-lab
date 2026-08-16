#!/usr/bin/env python3
"""
gsmg_sweep.py — fresh candidate sweep of the GSMG.io final-gate small blob.

Pipeline (certified): X -> sha256(X).hex -> OpenSSL AES-256-CBC (EVP_BytesToKey/MD5)
decrypt of the published blob -> reduce plaintext to 32 bytes -> uncompressed secp256k1
pubkey -> HASH160 -> compare with escrow 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe.

Also supports a second convention seen earlier in the puzzle: some gates accepted the
sha256 hex directly as the OpenSSL password (password = sha256(X) hex used directly,
not re-hashed). Both conventions are swept here.

The 256-symbol object space was already swept (~335M negatives, ledger dated
2026-07-28). This sweep targets the OTHER half of the final gate — the small-blob
password route — which the ledger explicitly notes was never isolated and swept.
"""

import argparse
import base64
import hashlib
import itertools
import sys
import time

from Crypto.Cipher import AES
from ecdsa import SECP256k1, SigningKey

BLOB_B64 = (
    "U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
    "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ"
)
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"


def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int = 32, iv_len: int = 16):
    derived, prev = b"", b""
    while len(derived) < key_len + iv_len:
        prev = hashlib.md5(prev + password + salt).digest()
        derived += prev
    return derived[:key_len], derived[key_len:key_len + iv_len]


def try_decrypt(password: bytes) -> bytes | None:
    blob = base64.b64decode(BLOB_B64)
    salt = blob[8:16]
    ct = blob[16:]
    key, iv = evp_bytes_to_key(password, salt)
    pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    pad = pt[-1]
    if pad < 1 or pad > 16 or pt[-pad:] != bytes([pad]) * pad:
        return None
    return pt[:-pad]


def plaintext_reductions(pt: bytes):
    if not pt:
        return []
    out = {}
    out["raw-first32"] = pt[:32]
    out["sha256"] = hashlib.sha256(pt).digest()
    out["sha256-sha256"] = hashlib.sha256(hashlib.sha256(pt).digest()).digest()
    if len(pt) >= 32:
        out["last32"] = pt[-32:]
    if len(pt) >= 64:
        out["sha256-first64"] = hashlib.sha256(pt[:64]).digest()
    return list(out.items())


def privkey_to_address(priv_bytes: bytes) -> str | None:
    priv_int = int.from_bytes(priv_bytes, "big")
    if priv_int == 0 or priv_int >= SECP256k1.order:
        return None
    sk = SigningKey.from_secret_exponent(priv_int, curve=SECP256k1)
    pub = sk.get_verifying_key().to_string("uncompressed")
    h = hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()
    payload = b"\x00" + h
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = int.from_bytes(payload + checksum, "big")
    s = ""
    while n:
        n, r = divmod(n, 58)
        s = alphabet[r] + s
    return "1" * (len(payload + checksum) - len(s)) + s


def check_pw(password: bytes, tag: str) -> bool:
    pt = try_decrypt(password)
    if pt is None:
        return False
    for name, red in plaintext_reductions(pt):
        try:
            addr = privkey_to_address(red)
        except Exception:
            continue
        if addr == TARGET_ADDRESS:
            print(f"\n*** MATCH *** password_conv={tag} reading={name} "
                  f"priv_hex={red.hex()} plaintext={pt.hex()}")
            return True
    return False


# ---------- candidate corpus ----------

LORE = [
    # decoded strings from the published chain
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "ourfirsthintisyourlastcommand", "HASHTHETEXT", "hashthetext",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "causality", "Safenet", "Luna", "HSM", "11110",
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "THEMATRIXHASYOU", "thematrixhasyou",
    "GSMGIO5BTCPUZZLECHALLENGE", "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "gsmgio5btcpuzzlechallenge1gsmg1jc9wtdswfwapgj2xcmjpawnwx7prbe",
    "the seed is planted", "theseedisplanted", "the seed is planted",
    "salphaseion", "SALPHASEION", "dualite", "Dualite", "DUALITE",
    "follow the white rabbit", "followthewhiterabbit", "white rabbit", "whiterabbit",
    "the architect choice", "architect", "thearchitectchoice", "archichoice",
    "choice is an illusion", "choiceisanillusion",
    "in one of the valleys of phillip", "runtime-error.r00", "runtimeerror",
    "eps3.4", "magic keypads", "daughters hit magic keypads",
    "the keymaker", "keymaker", "keymakers",
    "worst gear", "on the highway", "the warning", "logic",
    "merovingian", "morpheus", "neo", "trinity", "the oracle", "oracle",
    "the matrix has you", "thematrixhasyou", "wake up neo", "wake up you",
    "why am i here", "am i here", "cheshire cat", "cheshire",
    "beautiful strategic position", "one for one four for one", "oneforonefourforone",
    "a fubcd king oracle queen thingky mvps", "fubcdoriginatingkeysmvps",
    "how long is forever", "sometimes just one second", "justonesecond",
    "heisenberg uncertainty principle", "heisenbergsuncertaintyprinciple",
    "the future is fluid", "thefutureisfluid", "jacque fresco", "jacquefresco",
    "giveit", "keyhole", "fall in the keyhole",
    "crypto finally to the latin moon", "how so mate",
    "the wise man above hinted", "hundred forty", "140", "hundred fourty",
    "ciao bella", "ciaobella", "ciao bella o",
    "private key", "privatekey", "the private keynote", "private keynote",
    "twenty three ciphers", "23 ciphers", "sixteen encryptions",
    "seven intertwined passwords", "7 intertwined passwords",
    "hash the text", "hash the text of the first puzzle", "hashthetextofthefirstpuzzle",
    "your life is the sum of a remainder", "youlifeisthesumofaremainder",
    "the sum of a remainder", "unbalanced equation",
    "a harmony of mathematical precision",
    "the eventualitiy of an anomaly", "theeventualityofananomaly",
    "scrypt", "secp256k1", "ecdsa", "brainwallet", "bip39",
    "gsmg", "GSMG", "Gsmg", "gsmg.io", "GSMG.io", "gsmg.io puzzle", "gsmgio",
    "gsmg io 5 btc puzzle challenge",
    "5btc", "5 btc", "five btc", "fivebitcoin",
    "2019-04-13", "20190413", "73e48ff571a7e9a4387574a50cf2fcb7b21b6ea5702c777a035664df57cbce02",
    "there is no spoon", "thereisnospoon", "red pill", "blue pill",
    "wake up", "wakeup", "the rabbit hole", "rabbit hole", "rabbithole",
    "down the rabbit hole", "downtherabbithole",
    "esrever", "esrever esrever",
]

# All known intermediate sha256 hexes (passwords used / URL hashes in the chain)
KNOWN_HASHES = [
    "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32",
    "250f37726d6862939f723edc4f993fde9d33c6004aab4f2203d9ee489d61ce4c",
    "1a57c572caf3cf722e41f5f9cf99ffacff06728a43032dd44c481c77d2ec30d5",
    "eb3efb5151e6255994711fe8f2264427ceeebf88109e1d7fad5b0a8b6d07e5bf",
]

# X values that yielded the known intermediate passwords, plus the puzzle's own
# first-page text (the "first hint" / "last command" family)
PHASE_X = [
    "causality",
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
]

SEVEN_PART = ("causality" "Safenet" "Luna" "HSM" "11110"
              "0x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E6972"
              "62206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D6954"
              "20656854"
              "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1")
SEVEN_PART_NOSPACE = SEVEN_PART.replace(" ", "")


def transforms(s: str):
    yield s
    yield s.lower()
    yield s.upper()
    yield s.title()
    yield s.replace(" ", "")
    yield s.replace(" ", "").lower()
    yield s.replace(" ", "").upper()
    yield s[::-1]
    yield s[::-1].replace(" ", "")
    yield s.replace("i", "1").replace("I", "1").replace("o", "0").replace("O", "0")
    yield s + "."
    yield s + "!"
    yield " " + s
    yield s + " "


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    args = ap.parse_args()

    candidates = []  # (password_bytes, label, conv)
    seen = set()

    def add_pw(pw: bytes, label: str, conv: str):
        if pw not in seen:
            seen.add(pw)
            candidates.append((pw, label, conv))

    # Conventional: password = sha256(X).hex where X is a plaintext answer string
    base = list(dict.fromkeys(LORE + PHASE_X + [SEVEN_PART, SEVEN_PART_NOSPACE]))
    for s in base:
        for t in transforms(s):
            add_pw(hashlib.sha256(t.encode()).hexdigest().encode(),
                   f"sha256({t!r})", "sha256(X)")

    # Direct-plaintext convention: some gates took a whole phrase as the password
    for s in base:
        for t in transforms(s):
            add_pw(t.encode(), f"plain({t!r})", "plaintext")

    # Known hexes used directly as password
    for h in KNOWN_HASHES:
        add_pw(h.encode(), f"hex-direct({h[:16]}...)", "hex-direct")
        add_pw(h.upper().encode(), f"hex-direct-upper({h[:16]}...)", "hex-direct")

    # Pairwise combos of short lore words (7 intertwined passwords motif)
    short = [s for s in base if len(s) < 32]
    for a, b in itertools.permutations(short[:24], 2):
        t = a + b
        add_pw(hashlib.sha256(t.encode()).hexdigest().encode(),
               f"sha256({t!r})", "sha256(pair)")
        for sep in (" ", "-", "_", "."):
            add_pw(hashlib.sha256((a + sep + b).encode()).hexdigest().encode(),
                   f"sha256({a}{sep}{b})", "sha256(pair-sep)")

    if args.limit:
        candidates = candidates[:args.limit]
    print(f"[sweep] {len(candidates)} candidates, {TARGET_ADDRESS}", flush=True)

    t0 = time.time()
    hit = 0
    for i, (pw, label, conv) in enumerate(candidates, 1):
        if check_pw(pw, conv):
            print(f"HIT at index {i}: {label} conv={conv}")
            hit += 1
            break
        if i % 50000 == 0:
            el = time.time() - t0
            print(f"  {i}/{len(candidates)} ({i/el:.0f}/s, {el:.0f}s)", flush=True)
    el = time.time() - t0
    print(f"[sweep] done in {el:.1f}s — {('HIT ' + str(hit)) if hit else 'no match'}")


if __name__ == "__main__":
    main()