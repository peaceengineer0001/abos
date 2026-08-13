"""
abos.nostr.crypto
=================

Self-contained secp256k1 + BIP-340 Schnorr implementation used to give every
BOSS agent a **real** Nostr keypair. This is a vendored, dependency-free
reference implementation (pure Python, stdlib ``hashlib`` only) so ABOS can
generate valid Nostr keys and sign valid NIP-01 events with no native
extensions and no network access at import time.

It is deliberately additive to the peace-protocols Nostr conventions (see
``agents/raven/config.toml`` — ``nip05``, ``[nostr_kinds]``, ``channel``): the
same secp256k1 identity model, extended for the ABOS workspace bus.

The elliptic-curve / Schnorr routines follow the BIP-340 reference spec.
"""

from __future__ import annotations

import hashlib
import os
from typing import Tuple

# Optional fast backend. coincurve is a C-speed libsecp256k1 binding; when
# present ABOS uses it for key derivation + Schnorr sign/verify (~100x faster).
# The pure-Python BIP-340 implementation below is the always-available fallback
# and is fully wire-compatible (both produce/verify standard BIP-340 sigs).
try:  # pragma: no cover - availability depends on environment
    from coincurve import PrivateKey as _CCPrivateKey, PublicKeyXOnly as _CCXOnly
    _HAS_COINCURVE = True
except Exception:  # pragma: no cover
    _HAS_COINCURVE = False


def has_fast_backend() -> bool:
    """True if the native coincurve backend is active."""
    return _HAS_COINCURVE

# --------------------------------------------------------------------------- #
# secp256k1 curve parameters
# --------------------------------------------------------------------------- #
_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)

Point = Tuple[int, int]


def _tagged_hash(tag: str, msg: bytes) -> bytes:
    tag_hash = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(tag_hash + tag_hash + msg).digest()


def _point_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    if p1[0] == p2[0] and (p1[1] != p2[1]):
        return None
    if p1 == p2:
        lam = (3 * p1[0] * p1[0] * pow(2 * p1[1], _P - 2, _P)) % _P
    else:
        lam = ((p2[1] - p1[1]) * pow(p2[0] - p1[0], _P - 2, _P)) % _P
    x3 = (lam * lam - p1[0] - p2[0]) % _P
    y3 = (lam * (p1[0] - x3) - p1[1]) % _P
    return (x3, y3)


def _point_mul(p, n):
    r = None
    while n:
        if n & 1:
            r = _point_add(r, p)
        p = _point_add(p, p)
        n >>= 1
    return r


def _has_even_y(p: Point) -> bool:
    return p[1] % 2 == 0


def _lift_x(x: int):
    if x >= _P:
        return None
    y_sq = (pow(x, 3, _P) + 7) % _P
    y = pow(y_sq, (_P + 1) // 4, _P)
    if pow(y, 2, _P) != y_sq:
        return None
    return (x, y if y % 2 == 0 else _P - y)


def _bytes_from_int(x: int) -> bytes:
    return x.to_bytes(32, "big")


def _int_from_bytes(b: bytes) -> int:
    return int.from_bytes(b, "big")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def generate_privkey() -> str:
    """Return a fresh 32-byte secp256k1 private key as 64-char hex."""
    while True:
        d = _int_from_bytes(os.urandom(32))
        if 1 <= d < _N:
            return _bytes_from_int(d).hex()


def _pubkey_point(privkey_int: int) -> Point:
    return _point_mul(_G, privkey_int)


def get_public_key(privkey_hex: str) -> str:
    """Derive the 32-byte x-only Nostr public key (hex) from a private key."""
    if _HAS_COINCURVE:
        return _CCPrivateKey(bytes.fromhex(privkey_hex)).public_key_xonly.format().hex()
    return _py_get_public_key(privkey_hex)


def _py_get_public_key(privkey_hex: str) -> str:
    d = _int_from_bytes(bytes.fromhex(privkey_hex))
    if not (1 <= d < _N):
        raise ValueError("invalid private key")
    p = _pubkey_point(d)
    return _bytes_from_int(p[0]).hex()


def schnorr_sign(msg32: bytes, privkey_hex: str, aux_rand: bytes | None = None) -> str:
    """BIP-340 Schnorr signature (fast backend if available)."""
    if len(msg32) != 32:
        raise ValueError("message must be 32 bytes")
    if _HAS_COINCURVE:
        return _CCPrivateKey(bytes.fromhex(privkey_hex)).sign_schnorr(msg32).hex()
    return _py_schnorr_sign(msg32, privkey_hex, aux_rand)


def _py_schnorr_sign(msg32: bytes, privkey_hex: str, aux_rand: bytes | None = None) -> str:
    """BIP-340 Schnorr signature over a 32-byte message; returns 64-byte hex."""
    if len(msg32) != 32:
        raise ValueError("message must be 32 bytes")
    d0 = _int_from_bytes(bytes.fromhex(privkey_hex))
    if not (1 <= d0 < _N):
        raise ValueError("invalid private key")
    P = _pubkey_point(d0)
    d = d0 if _has_even_y(P) else _N - d0
    if aux_rand is None:
        aux_rand = os.urandom(32)
    t = _int_from_bytes(_bytes_from_int(d) )
    t = d ^ _int_from_bytes(_tagged_hash("BIP0340/aux", aux_rand))
    t_bytes = _bytes_from_int(t)
    px = _bytes_from_int(P[0])
    rand = _tagged_hash("BIP0340/nonce", t_bytes + px + msg32)
    k0 = _int_from_bytes(rand) % _N
    if k0 == 0:
        raise RuntimeError("nonce is zero")
    R = _point_mul(_G, k0)
    k = k0 if _has_even_y(R) else _N - k0
    rx = _bytes_from_int(R[0])
    e = _int_from_bytes(_tagged_hash("BIP0340/challenge", rx + px + msg32)) % _N
    sig = rx + _bytes_from_int((k + e * d) % _N)
    return sig.hex()


def schnorr_verify(msg32: bytes, pubkey_hex: str, sig_hex: str) -> bool:
    """Verify a BIP-340 Schnorr signature (fast backend if available)."""
    if _HAS_COINCURVE:
        try:
            return _CCXOnly(bytes.fromhex(pubkey_hex)).verify(
                bytes.fromhex(sig_hex), msg32)
        except Exception:
            return False
    return _py_schnorr_verify(msg32, pubkey_hex, sig_hex)


def _py_schnorr_verify(msg32: bytes, pubkey_hex: str, sig_hex: str) -> bool:
    """Verify a BIP-340 Schnorr signature (pure Python)."""
    try:
        px = _int_from_bytes(bytes.fromhex(pubkey_hex))
        sig = bytes.fromhex(sig_hex)
        if len(sig) != 64:
            return False
        P = _lift_x(px)
        if P is None:
            return False
        r = _int_from_bytes(sig[:32])
        s = _int_from_bytes(sig[32:])
        if r >= _P or s >= _N:
            return False
        e = _int_from_bytes(
            _tagged_hash("BIP0340/challenge", sig[:32] + bytes.fromhex(pubkey_hex) + msg32)
        ) % _N
        R = _point_add(_point_mul(_G, s), _point_mul(P, _N - e))
        if R is None or not _has_even_y(R) or R[0] != r:
            return False
        return True
    except Exception:
        return False


# --- bech32 (NIP-19) encoding for npub/nsec human-readable identities ------- #
_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _bech32_polymod(values):
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def _bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def _bech32_create_checksum(hrp, data):
    values = _bech32_hrp_expand(hrp) + data
    polymod = _bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def _convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (tobits - bits)) & maxv)
    return ret


def to_bech32(hrp: str, hex_str: str) -> str:
    """Encode a hex key as a NIP-19 bech32 identity (e.g. npub…, nsec…)."""
    data = _convertbits(list(bytes.fromhex(hex_str)), 8, 5)
    combined = data + _bech32_create_checksum(hrp, data)
    return hrp + "1" + "".join([_CHARSET[d] for d in combined])
