from hashlib import sha256
from functools import reduce
from ec import ECPoint, FQ
from hash_to_point import hash_to_point
from utils import serialize, multi_controller, timing_decorator, byte_count_decorator

from py_ecc.bn128 import neg, add, multiply, FQ12 # TODO: remove

class BM_BLS:
    def __init__(self, ec_point: ECPoint, fq: FQ, num_signers):
        self.ec_point = ec_point
        self.fq = fq
        self.g1 = ec_point.G1()
        self.g2 = ec_point.G2()
        self.neg_g2 = ec_point(neg(ec_point.G2().p))

        self.num_signers = num_signers # TODO: inconsistent naming across implementations
        self.hash = lambda x: sha256(x).digest()
        self.domain = self.hash(b"DOMAIN_BM_BLS")

    def H(self, *args):
        return self.ec_point(hash_to_point(serialize(args), self.domain))

    def _H(self, *args):
        return int.from_bytes(
            self.hash(serialize(args)),
            'big'
        )

    def H_agg(self, *args):
        return self.fq(self._H('agg', *args))

    def keygen(self):
        sks = []
        pks = []
        for _ in range(self.num_signers):
            sk = self.fq.rand()
            sks.append(sk)
            pk = (self.g1 * sk, self.ec_point(multiply(self.g2.p, sk.n)))
            pks.append(pk)

        return (pks, sks) # TODO: inconsistent order (sks, pks) / (pks, sks)

    def _a(self, pks):
        a = [
            self.H_agg(
                list(map(lambda pk: pk[1], pks)),
                pks[signer_index][1]
            )
            for signer_index in range(self.num_signers)
        ]
        return a

    def keyaggr(self, pks):
        a = self._a(pks)
        apk = self.ec_point(reduce(add, [
            multiply(pks[signer_index][1].p, a[signer_index].n)
            for signer_index in range(self.num_signers)
        ]))
        return apk

    #@byte_count_decorator
    def S(self, sk):
        m = yield
        s_bar = m * sk
        yield s_bar

    def U(self, m, pks, S):
        sigma_bars = []
        for i, s in enumerate(S):
            r = self.fq.rand()
            m_bar = self.H(m) + self.g1 * r
            s_bar = s.send(m_bar)
            sigma_bar = s_bar + self.ec_point.neg(pks[i][0] * r)
            sigma_bars.append(sigma_bar)

        a = self._a(pks)
        sigma = self.ec_point.sum([sigma_bars[s] * a[s] for s in range(self.num_signers)])
        yield sigma

    def verify(self, pks, m, sigma):
        apk = self.keyaggr(pks)
        return self.ec_point.pairing(sigma, self.neg_g2, self.H(m), apk)

    def verify_aggr(self, pks, ms, sigmas):
        apk = self.keyaggr(pks)
        sigma = self.ec_point.sum(sigmas)
        hs = self.ec_point.sum([self.H(m) for m in ms])
        return self.ec_point.pairing(sigma, self.neg_g2, hs, apk)

    def verify_aggr_hm(self, pks, hms, sigmas):
        apk = self.keyaggr(pks)
        sigma = self.ec_point.sum(sigmas)
        hs = self.ec_point.sum(hms)
        return self.ec_point.pairing(sigma, self.neg_g2, hs, apk)

    def sign(self, sks, pks, m):
        return multi_controller(
            lambda *args: self.U(m, pks, *args),
            [(lambda sk: lambda *args: self.S(sk, *args))(sks[i]) for i in range(self.num_signers)]
        )

import unittest
from ec import from_ecc_py
# from py_ecc import bn128
# BN128FQ, BN128Point = from_ecc_py('BN128', bn128)
import py_eth_pairing
BN128FQ, BN128Point = from_ecc_py('BN128', py_eth_pairing)

class TestBM_BLS(unittest.TestCase):
    def test(self):
        m = BN128FQ(1337)
        num_signers = 2
        bm = BM_BLS(BN128Point, BN128FQ, num_signers)
        (pks, sks) = bm.keygen()
        apk = bm.keyaggr(pks)
        sigma = bm.sign(sks, pks, m)
        self.assertTrue(bm.verify(pks, m, sigma))

    def test_aggr(self):
        num_messages = 16
        num_signers = 4

        ms = [BN128FQ.rand() for _ in range(1, num_messages+1)]
        bm = BM_BLS(BN128Point, BN128FQ, num_signers)
        (pks, sks) = bm.keygen()
        apk = bm.keyaggr(pks)
        sigmas = [bm.sign(sks, pks, m) for m in ms]
        for (m, sigma) in zip(ms, sigmas):
            self.assertTrue(bm.verify(pks, m, sigma))

        self.assertTrue(bm.verify_aggr(pks, ms, sigmas))

    def test_aggr_hm(self):
        num_messages = 8
        num_signers = 2

        bm = BM_BLS(BN128Point, BN128FQ, num_signers)
        ms = [BN128FQ.rand() for _ in range(1, num_messages+1)]

        hms = [bm.H(m) for m in ms]

        (pks, sks) = bm.keygen()
        apk = bm.keyaggr(pks)
        sigmas = [bm.sign(sks, pks, m) for m in ms]
        for (m, sigma) in zip(ms, sigmas):
            self.assertTrue(bm.verify(pks, m, sigma))

        self.assertTrue(bm.verify_aggr_hm(pks, hms, sigmas))
