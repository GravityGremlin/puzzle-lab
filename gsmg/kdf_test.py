#!/usr/bin/env python3
"""
kdf_test.py — settle the KDF question for the GSMG blobs.

Blob 1 (656 ct bytes, salt 06286612d43ed7ed): phase 2/3, known password
    sha256('causality').hex  -> plaintext "The ironic 2name of the keymakers..."
Blob 2 (4096 ct bytes, salt 9fbc451d13d071f4): phase 3, known password
    sha256(7-part concat).hex -> plaintext "What if the merovingian is wrong..."

If a blob decrypts with valid PKCS7 padding under one KDF but not the other,
the convention is settled. Print which KDF each blob accepts.
"""
import base64, hashlib
from Crypto.Cipher import AES

def evp_kdf(password: bytes, salt: bytes, kdf: str, key_len=32, iv_len=16):
    digest = hashlib.md5 if kdf == "md5" else hashlib.sha256
    derived, prev = b"", b""
    while len(derived) < key_len + iv_len:
        prev = digest(prev + password + salt).digest()
        derived += prev
    return derived[:key_len], derived[key_len:key_len + iv_len]

def try_decrypt(b64: str, password: bytes, kdf: str):
    blob = base64.b64decode(b64)
    salt, ct = blob[8:16], blob[16:]
    key, iv = evp_kdf(password, salt, kdf)
    pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    pad = pt[-1]
    if 1 <= pad <= 16 and pt[-pad:] == bytes([pad]) * pad:
        return pt[:-pad]
    return None

cases = [
    ("phase2/3", "blob_656_a089144531c6.b64", "causality"),
    ("phase3", "blob_4096_9163a38d8c49.b64", None),  # 7-part from sweep module
]
import sys
sys.path.insert(0, "/home/user/puzzle-lab")
from gsmg_sweep import SEVEN_PART  # reuse exact concatenation

blobs = {
    "656": open("/tmp/opencode/gsmg-analysis/corpus/blob_656_a089144531c6.b64").read(),
    "4096": open("/tmp/opencode/gsmg-analysis/corpus/blob_4096_9163a38d8c49.b64").read(),
    "salphaseion": open("/tmp/opencode/gsmg-analysis/corpus/blob_1328_b18950551a4d.b64").read(),
    "trailing": open("/tmp/opencode/gsmg-analysis/corpus/blob_p32trailing.b64").read(),
}
pws = {
    "656": hashlib.sha256(b"causality").hexdigest().encode(),
    "4096": hashlib.sha256(SEVEN_PART.encode()).hexdigest().encode(),
}
for name, pw in pws.items():
    for kdf in ("md5", "sha256"):
        pt = try_decrypt(blobs[name], pw, kdf)
        status = "DECRYPTED" if pt else "pad-fail"
        snippet = pt[:48].decode("latin1") if pt else ""
        print(f"[{name}] kdf={kdf}: {status} {snippet!r}")

# also try trailing-password candidate seen in the wild for the blob
for bname in ("salphaseion", "trailing"):
    for pw_name, pw in pws.items():
        for kdf in ("md5", "sha256"):
            pt = try_decrypt(blobs[bname], pw, kdf)
            if pt:
                print(f"[{bname}] kdf={kdf} pw={pw_name}: DECRYPTED {pt[:32].hex()}")
print("done")