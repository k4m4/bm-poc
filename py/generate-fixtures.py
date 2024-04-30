import os
import json
from hashlib import sha256
from ec import from_ecc_py
import py_eth_pairing
from bm_bls import BM_BLS
from bm_sb import BM_SB
BN128FQ, BN128Point = from_ecc_py('BN128', py_eth_pairing)

def write_bm_bls_aggr_fixture(apk, ms, sigmas):
    a, b = apk.p
    apk = [*a.coeffs, *b.coeffs]
    data = {
        "apk": list(map(lambda fq: fq.n, apk)), # TODO: clean up
        "messages": list(map(lambda x: x.n, ms)),
        "signatures": list(map(lambda x: x.p, sigmas)),
    }

    with open('data/input_aggr.json', 'w') as f:
        json.dump(data, f)

def write_bm_bls_aggr_hm_fixture(apk, hms, sigmas):
    hms_fmt = []
    for hm in hms:
        a, b = hm.p
        hms_fmt.append([a.n, b.n])

    a, b = apk.p
    apk = [*a.coeffs, *b.coeffs]
    data = {
        "apk": list(map(lambda fq: fq.n, apk)), # TODO: clean up
        "messageHashes": hms_fmt, # TODO: clean up
        "signatures": list(map(lambda x: x.p, sigmas)),
    }

    with open('data/input_aggr_hm.json', 'w') as f:
        json.dump(data, f)

def write_bm_sb_fixture(pks, m, sigma):
    (R_bar, y_bar, z_bar) = sigma
    data = {
        "R_bar": R_bar.p,
        "m": m.n,
        "pks": list(map(lambda x: x.p, pks)),
        "y_bar": y_bar.n,
        "z_bar": z_bar.n,
    }

    with open('data/input.json', 'w') as f:
        json.dump(data, f)

def generate_bm_sb_fixture(num_signers):
    m = BN128FQ.rand()
    hash = lambda x: sha256(x).digest()
    max_int_size = 32
    bm = BM_SB(BN128Point, BN128FQ, max_int_size, hash, num_signers)
    (sks, pks) = bm.keygen()
    sigma = bm.sign(pks, sks, m)
    assert bm.verify(pks, m, sigma)
    write_bm_sb_fixture(pks, m, sigma)

def generate_bm_bls_aggr_fixture(num_messages, num_signers):
    ms = [BN128FQ.rand() for _ in range(1, num_messages+1)]
    bm = BM_BLS(BN128Point, BN128FQ, num_signers)
    (pks, sks) = bm.keygen()
    apk = bm.keyaggr(pks)
    sigmas = [bm.sign(sks, pks, m) for m in ms]
    assert bm.verify_aggr(pks, ms, sigmas)
    write_bm_bls_aggr_fixture(apk, ms, sigmas)

def generate_bm_bls_aggr_hm_fixture(num_messages, num_signers):
    bm = BM_BLS(BN128Point, BN128FQ, num_signers)
    ms = [BN128FQ(i) for i in range(1, num_messages+1)]

    hms = [bm.H(m) for m in ms]

    (pks, sks) = bm.keygen()
    apk = bm.keyaggr(pks)
    sigmas = [bm.sign(sks, pks, m) for m in ms]
    assert bm.verify_aggr_hm(pks, hms, sigmas)

    write_bm_bls_aggr_hm_fixture(apk, hms, sigmas)

if __name__ == '__main__':
    num_messages = int(os.environ.get('NUM_MESSAGES', 1))
    num_signers = int(os.environ.get('NUM_SIGNERS', 1))
    generate_bm_bls_aggr_fixture(num_messages, num_signers)
    generate_bm_bls_aggr_hm_fixture(num_messages, num_signers)
    generate_bm_sb_fixture(num_signers)
