#!/usr/bin/env python3
"""
qc_engine.py — pure-Python implementation of the Aoi Nakamoto Quizchain transform:
MD5(bytes) -> BIP39 mnemonic -> BIP44 m/44'/0'/0'/0/i -> P2PKH address.

Certification targets:
  VECTOR_ENTROPY  @ index 1 -> WIF L5Z66qPmUkTAsWQywjRNHDxHrX6J1X1SQedp6V8QsbaXR7rGd6ex
  Hal Finney "Bitcoin and me" (stage-one source) + ITASM case-flip rule ->
      19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN
"""
import hashlib
import hmac
import struct

from ecdsa import SECP256k1, SigningKey

WORDLIST = [w.strip() for w in open('/tmp/opencode/aoi-chapter/english.txt')]

N = SECP256k1.order
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

TARGETS = {
    '14zMkTgaVXJcxdh4JdWi29MLRR44iUSG9W': 'RBB-current',
    '1EFojcAo2vbhRGCGCa7q8Wwvzss28mhQYC': 'RBB-superseded',
    '13Cv6SXUnzGDT8JHqzzJ8xMPtsSdhJA4wd': 'Block76',
    '19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN': 'StageOne-witness',
}


def md5_entropy(text: str) -> bytes:
    return hashlib.md5(text.encode('utf-8')).digest()


def mnemonic_from_entropy(entropy: bytes) -> str:
    assert len(entropy) == 16
    bits = int.from_bytes(entropy, 'big') << 4
    checksum = hashlib.sha256(entropy).digest()[0]
    bits |= checksum >> 4  # top 4 bits of sha256 appended as the checksum nibble
    # rebuild: entropy_bits(128) + checksum_bits(4) -> 12 x 11-bit words
    words = []
    for i in range(12):
        idx = (bits >> (11 * (11 - i))) & 0x7FF
        words.append(WORDLIST[idx])
    return ' '.join(words)


def seed_from_mnemonic(mnemonic: str, passphrase: str = '') -> bytes:
    return hashlib.pbkdf2_hmac(
        'sha512', mnemonic.encode('utf-8'),
        ('mnemonic' + passphrase).encode('utf-8'), 2048, dklen=64)


def hmac_sha512(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha512).digest()


def ckd_priv(k_par: int, c_par: bytes, index: int) -> tuple[int, bytes]:
    if index >= 0x80000000:
        data = b'\x00' + k_par.to_bytes(32, 'big') + struct.pack('>I', index)
    else:
        sk = SigningKey.from_secret_exponent(k_par, curve=SECP256k1)
        data = sk.get_verifying_key().to_string('compressed') + struct.pack('>I', index)
    I = hmac_sha512(c_par, data)
    I_L, I_R = I[:32], I[32:]
    k_i = (int.from_bytes(I_L, 'big') + k_par) % N
    if k_i == 0:
        raise ValueError('invalid child key')
    return k_i, I_R


def bip32_master(seed: bytes) -> tuple[int, bytes]:
    I = hmac_sha512(b'Bitcoin seed', seed)
    k = int.from_bytes(I[:32], 'big')
    return k, I[32:]


def derive(seed: bytes, path: list[int]) -> tuple[int, bytes]:
    k, c = bip32_master(seed)
    for idx in path:
        k, c = ckd_priv(k, c, idx)
    return k, c


HARD = 0x80000000


def pubkey_compressed(k: int) -> bytes:
    return SigningKey.from_secret_exponent(k, curve=SECP256k1).get_verifying_key().to_string('compressed')


def hash160(b: bytes) -> bytes:
    return hashlib.new('ripemd160', hashlib.sha256(b).digest()).digest()


def base58check(payload: bytes) -> str:
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    full = payload + checksum
    n = int.from_bytes(full, 'big')
    s = ''
    while n:
        n, r = divmod(n, 58)
        s = B58[r] + s
    z = 0
    for b in full:
        if b == 0:
            z += 1
        else:
            break
    return '1' * z + s


def p2pkh(k: int) -> str:
    return base58check(b'\x00' + hash160(pubkey_compressed(k)))


def address_from_entropy(entropy: bytes, index: int) -> str:
    mn = mnemonic_from_entropy(entropy)
    seed = seed_from_mnemonic(mn)
    k, _ = derive(seed, [44 + HARD, 0 + HARD, 0 + HARD, 0, index])
    return p2pkh(k)


def account_address_from_entropy(entropy: bytes) -> str:
    mn = mnemonic_from_entropy(entropy)
    seed = seed_from_mnemonic(mn)
    k, _ = derive(seed, [44 + HARD, 0 + HARD, 0 + HARD])
    return p2pkh(k)


def wif_index1(entropy: bytes) -> str:
    mn = mnemonic_from_entropy(entropy)
    seed = seed_from_mnemonic(mn)
    k, _ = derive(seed, [44 + HARD, 0 + HARD, 0 + HARD, 0, 1])
    payload = b'\x80' + k.to_bytes(32, 'big') + b'\x01'
    return base58check(payload)


# ---------- ITASM case-flip rule (certified on Stage One) ----------
NO_FLIP = set('ITASM')


def flip_case(paragraph: str) -> str:
    chars = list(paragraph)
    letters = [i for i, c in enumerate(chars) if c.isalpha()]
    if not letters:
        return paragraph
    first, last = letters[0], letters[-1]
    chars[first] = chars[first].lower()
    chars[last] = chars[last].upper()
    return ''.join(chars)


def apply_rule(paragraphs: list[str]) -> list[str]:
    out = []
    for p in paragraphs:
        if not p:
            out.append(p)
            continue
        fl = next((c for c in p if c.isalpha()), '')
        if fl and fl.upper() not in NO_FLIP:
            out.append(flip_case(p))
        else:
            out.append(p)
    return out