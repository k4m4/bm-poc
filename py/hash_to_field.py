#!/usr/bin/python
#
# pure Python implementation of hash-to-field as specified in
#     https://github.com/pairingwg/bls_standard/blob/master/minutes/spec-v1.md

# SOURCE (MODIFIED): https://github.com/algorand/bls_sigs_ref/blob/master/python-impl/hash_to_field.py

import hashlib
import hmac
from random import randint

from py_ecc.optimized_bn128 import field_modulus as p

# defined in RFC 3447, section 4.1
def I2OSP(val, length):
    if val < 0 or val >= (1 << (8 * length)):
        raise ValueError("bad I2OSP call: val=%d length=%d" % (val, length))
    ret = [0] * length
    val_ = val
    for idx in reversed(range(0, length)):
        ret[idx] = val_ & 0xff
        val_ = val_ >> 8
    ret = bytes(ret)
    assert ret == int(val).to_bytes(length, 'big'), "oops: %s %s" % (str(ret), str(int(val).to_bytes(length, 'big')))
    return ret

# defined in RFC 3447, section 4.2
def OS2IP(octets):
    ret = 0
    for o in octets:
        ret = ret << 8
        ret += o
    assert ret == int.from_bytes(octets, 'big')
    return ret

# per RFC5869
def hkdf_extract(salt, ikm, hash_fn):
    if salt is None:
        salt = bytes((0,) * hash_fn().digest_size)
    return hmac.HMAC(salt, ikm, hash_fn).digest()
def hkdf_expand(prk, info, length, hash_fn):
    digest_size = hash_fn().digest_size
    if len(prk) < digest_size:
        raise ValueError("length of prk must be at least Hashlen")
    nreps = (length + digest_size - 1) // digest_size
    if nreps == 0 or nreps > 255:
        raise ValueError("length arg to hkdf_expand cannot be longer than 255 * Hashlen")
    if info is None:
        info = b''
    last = okm = b''
    for rep in range(0, nreps):
        last = hmac.HMAC(prk, last + info + I2OSP(rep + 1, 1), hash_fn).digest()
        okm += last
    return okm[:length]

# expand_message_xmd from draft-irtf-cfrg-hash-to-curve-06
_strxor = lambda str1, str2: bytes( s1 ^ s2 for (s1, s2) in zip(str1, str2) )
def expand_message_xmd(msg, DST, len_in_bytes, hash_fn):
    # input and output lengths for hash_fn
    b_in_bytes = hash_fn().digest_size
    r_in_bytes = hash_fn().block_size

    # ell, DST_prime, etc
    ell = (len_in_bytes + b_in_bytes - 1) // b_in_bytes
    if ell > 255:
        raise ValueError("expand_message_xmd: ell=%d out of range" % ell)
    DST_prime = DST + I2OSP(len(DST), 1)
    Z_pad = I2OSP(0, r_in_bytes)
    l_i_b_str = I2OSP(len_in_bytes, 2)

    b_0 = hash_fn(Z_pad + msg + l_i_b_str + I2OSP(0, 1) + DST_prime).digest()
    b_vals = [None] * ell
    b_vals[0] = hash_fn(b_0 + I2OSP(1, 1) + DST_prime).digest()
    for idx in range(1, ell):
        b_vals[idx] = hash_fn(_strxor(b_0, b_vals[idx - 1]) + I2OSP(idx + 1, 1) + DST_prime).digest()
    pseudo_random_bytes = b''.join(b_vals)
    return pseudo_random_bytes[0 : len_in_bytes]

def expand_message_xof(msg, DST, len_in_bytes, hash_fn):
    DST_prime = DST + I2OSP(len(DST), 1)
    msg_prime = msg + I2OSP(len_in_bytes, 2) + DST_prime
    return hash_fn(msg_prime).digest(len_in_bytes)

# hash_to_field from draft-irtf-cfrg-hash-to-curve-06
def hash_to_field(msg, count, DST, modulus, degree, blen, expand_fn, hash_fn):
    # get pseudorandom bytes
    len_in_bytes = count * degree * blen
    pseudo_random_bytes = expand_fn(msg, DST, len_in_bytes, hash_fn)

    u_vals = [None] * count
    for idx in range(0, count):
        e_vals = [None] * degree
        for jdx in range(0, degree):
            elm_offset = blen * (jdx + idx * degree)
            tv = pseudo_random_bytes[elm_offset : elm_offset + blen]
            e_vals[jdx] = OS2IP(tv) % modulus
        u_vals[idx] = e_vals
    return u_vals

def Hp_shake(msg, count, dst):
    if not isinstance(msg, bytes):
        raise ValueError("Hp can't hash anything but bytes")
    return hash_to_field(msg, count, dst, p, 1, 64, expand_message_xof, hashlib.shake_128)

def Hp2_shake(msg, count, dst):
    if not isinstance(msg, bytes):
        raise ValueError("Hp2 can't hash anything but bytes")
    return hash_to_field(msg, count, dst, p, 2, 64, expand_message_xof, hashlib.shake_128)

def Hp(msg, count, dst):
    if not isinstance(msg, bytes):
        raise ValueError("Hp can't hash anything but bytes")
    #return hash_to_field(msg, count, dst, p, 1, 64, expand_message_xmd, hashlib.sha256)
    return hash_to_field(msg, count, dst, p, 1, 48, expand_message_xmd, hashlib.sha256)

def Hp2(msg, count, dst):
    if not isinstance(msg, bytes):
        raise ValueError("Hp2 can't hash anything but bytes")
    return hash_to_field(msg, count, dst, p, 2, 64, expand_message_xmd, hashlib.sha256)

def _random_string(strlen):
    return bytes( randint(65, 65 + 25) for _ in range(0, strlen) )

def test_xmd():
    msg = _random_string(48)
    dst = _random_string(16)
    ress = {}
    for l in range(16, 8192):
        result = expand_message_xmd(msg, dst, l, hashlib.sha512)
        assert l == len(result)
        key = result[:16]
        ress[key] = ress.get(key, 0) + 1
    assert all( x == 1 for x in ress.values() )

if __name__ == "__main__":
    test_xmd()
