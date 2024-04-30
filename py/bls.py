from hashlib import sha256
from hash_to_point import hash_to_point
from ec import ECPoint, FQ
from utils import serialize

from py_ecc.bn128 import FQ12, multiply, neg # TODO: remove

class BLS:
    def __init__(self, ec_point: ECPoint, fq: FQ):
        self.ec_point = ec_point
        self.fq = fq
        self.g1 = ec_point.G1()
        self.g2 = ec_point.G2()
        self.neg_g2 = self.ec_point(neg(ec_point.G2().p))

        self.hash = lambda x: sha256(x).digest()
        self.domain = self.hash(b"DOMAIN_BLS")

    def keygen(self):
        sk = self.fq.rand()
        pk = (self.g1 * sk, self.ec_point(multiply(self.g2.p, sk.n)))
        return (sk, pk)

    def H(self, *args):
        return self.ec_point(hash_to_point(serialize(args), self.domain))

    def sign(self, m, sk):
        return self.H(m) * sk

    def verify(self, sigma, pk: (ECPoint, ECPoint), m):
        return self.ec_point.pairing(sigma, self.neg_g2, self.H(m), pk[1])

import unittest
from ec import from_ecc_py
import py_eth_pairing
#from py_ecc import optimized_bn128
#BN128FQ, BN128Point = from_ecc_py('BN128', optimized_bn128)
BN128FQ, BN128Point = from_ecc_py('BN128', py_eth_pairing)

class TestBLS(unittest.TestCase):
    def test(self):
        bls = BLS(BN128Point, BN128FQ)
        (sk, pk) = bls.keygen()
        m = BN128FQ.rand()
        sigma = bls.sign(m, sk)
        self.assertTrue(bls.verify(sigma, pk, m))
