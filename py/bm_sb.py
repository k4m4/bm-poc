from hashlib import sha256
from unittest import TestCase
from utils import serialize, controller, multi_controller
from ec import ECPoint, FQ

class BM_SBException(Exception):
    pass

class BM_SB:
    def __init__(self, ec_point: ECPoint, fq: FQ, max_int_size, hash, num_of_signers):
        self.ec_point = ec_point
        self.fq = fq
        self.max_int_size = max_int_size
        self.hash = hash
        self.domain = self.hash(b"DOMAIN_BM_SB")
        self.num_of_signers = num_of_signers
        self.g = ec_point.G1()
        #self.h = self.g * self.fq.rand()
        self.h = self.g * fq(3)

    def _H(self, *args) -> int:
        return int.from_bytes(
            self.hash(serialize(args)), # TODO: serialize(self.max_int_size, *args)
            'big'
        )

    def _H_FQ(self, *args) -> FQ:
        return self.fq(self._H(self.domain, *args))

    def H_sig(self, *args) -> FQ:
        #return self._H_FQ(b"sig", *args)
        return self._H_FQ(*args)

    def H_com(self, *args) -> FQ:
        #return self._H_FQ(b"com", *args)
        return self._H_FQ(*args)

    def rand(self) -> FQ: # TODO: random num in Z_q^*
        return self.fq.rand()

    def keygen(self):
        sks = []
        pks = []
        for _ in range(self.num_of_signers):
            sk = self.fq.rand()
            pk = self.g * sk
            sks.append(sk)
            pks.append(pk)

        return (sks, pks)

    def verify(self, pks, m, sigma):
        (R_bar, y_bar, z_bar) = sigma
        c_i_bar = [self.H_sig(pks, pk, m, R_bar) for pk in pks]

        LHS = R_bar + self.ec_point.sum(
            [pks[i] * (c_i_bar[i] + y_bar**3) for i in range(self.num_of_signers)]
        )
        RHS = self.g * z_bar + self.h * y_bar
        R_bar_check = LHS == RHS

        return y_bar != 0 and R_bar_check

    def U_sign(self, pks, m, S):
        A_i = []
        B_i = []
        com_i = []
        beta_i = []
        for s in S:
            (A, B, com) = s.send(())
            A_i.append(A)
            B_i.append(B)
            com_i.append(com)
            beta_i.append(self.fq.rand())

        alpha = self.rand()
        r = self.fq.rand()

        pk_sum = self.ec_point.sum(pks)
        A_sum = self.ec_point.sum(A_i)
        B_sum = self.ec_point.sum(B_i)
        alpha_cubed = alpha**3
        R_bar = self.ec_point.sum(
            [
                self.g * r,
                self.ec_point.sum([pks[i] * (alpha_cubed * beta_i[i]) for i in range(self.num_of_signers)]),
                A_sum * alpha_cubed,
                B_sum * alpha,
            ]
        )

        alpha_neg_cubed = alpha**(-3)

        c_j = []
        b_i = []
        y_i = []
        for i, s in enumerate(S):
            c_j.append(self.H_sig(pks, pks[i], m, R_bar) * alpha_neg_cubed + beta_i[i])
            com_ic = com_i.copy()
            com_ic[i] = b''
            b, y = s.send((c_j[i], com_ic))
            b_i.append(b)
            y_i.append(y)

        z_i = []
        for i, s in enumerate(S):
            y_ic = y_i.copy()
            y_ic[i] = b''
            z = s.send(y_ic)
            z_i.append(z)

        b_sum = self.fq.sum(b_i)
        y_sum = self.fq.sum(y_i)
        z_sum = self.fq.sum(z_i)

        B_check = B_sum == self.g * b_sum + self.h * y_sum
        A_check = self.g * z_sum == A_sum + self.ec_point.sum([pks[i] * (c_j[i] + y_sum**3) for i in range(self.num_of_signers)])
        if not A_check or not B_check:
            raise BM_SBException("ABORT")

        z_bar = (r + alpha_cubed * z_sum + alpha * b_sum)
        y_bar = alpha * y_sum
        sigma = (R_bar, y_bar, z_bar)

        if not self.verify(pks, m, sigma):
            raise BM_SBException("ABORT")

        yield sigma

    def S_sign(self, i, pk, sk):
        yield
        a = self.fq.rand()
        b = self.fq.rand()
        y = self.rand()

        A = self.g * a
        B = self.g * b + self.h * y
        com = self.H_com(i, y)

        c, com_i = yield (A, B, com)
        y_i = yield (b, y)

        com_i[i] = com
        y_i[i] = y

        if any(com_i[i] != self.H_com(i, y_i[i]) for i in range(self.num_of_signers)):
            raise BM_SBException("ABORT")

        y_sum = self.fq.sum(y_i)
        z = (a + (c + y_sum**3) * sk)
        yield z

    def sign(self, pks, sks, m):
        return multi_controller(
            lambda *args: self.U_sign(pks, m, *args),
            [(lambda i, pk, sk: lambda *args: self.S_sign(i, pk, sk, *args))(i, pks[i], sks[i]) for i in range(self.num_of_signers)]
        )

from ec import from_ecc_py
# from py_ecc import optimized_bn128 as bn128, optimized_bls12_381 as bls12_381
# from py_ecc import bn128, bls12_381
import py_eth_pairing
# BN128FQ, BN128Point = from_ecc_py('BN128', bn128)
BN128FQ, BN128Point = from_ecc_py('BN128', py_eth_pairing)
# BLS12381FQ, BLS12381Point = from_ecc_py('BLS12381', bls12_381)

class TestBM_SB(TestCase):
    def test(self):
        # for ec_point, fq, max_int_size in [(BLS12381Point, BLS12381FQ, 64), (BN128Point, BN128FQ, 32)]:
        for ec_point, fq, max_int_size in [(BN128Point, BN128FQ, 32)]:
            with self.subTest(msg=f"Testing with {ec_point.__name__} and {fq.__name__}"):
                m = BN128FQ.rand()
                num_of_signers = 1
                hash = lambda x: sha256(x).digest()
                bm = BM_SB(ec_point, fq, max_int_size, hash, num_of_signers)
                (sks, pks) = bm.keygen()
                sigma = bm.sign(pks, sks, m)
                self.assertTrue(bm.verify(pks, m, sigma))
