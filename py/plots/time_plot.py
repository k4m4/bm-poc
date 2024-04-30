from hashlib import sha256
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from bm_bls import BM_BLS
from bm_sb import BM_SB

from ec import from_ecc_py
import py_eth_pairing
BN128FQ, BN128Point = from_ecc_py('BN128', py_eth_pairing)

import time
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

RUNS = 10
SIGNERS_MAX_POWER=6

def compute_stats(data):
    means = [np.mean(run) for run in data]
    std_devs = [np.std(run) for run in data]
    return means, std_devs

sign_bm_bls_total = []
verify_bm_bls_total = []
sign_bm_sb_total = []
verify_bm_sb_total = []

verify_bm_bls_aggr_total = []

signers = np.array([2**i for i in range(SIGNERS_MAX_POWER+1)])
for num_signers in signers:
    hash = lambda x: sha256(x).digest()
    bm_bls = BM_BLS(BN128Point, BN128FQ, num_signers)
    bm_sb = BM_SB(BN128Point, BN128FQ, 32, hash, num_signers)

    sign_bm_bls = []
    verify_bm_bls = []
    sign_bm_sb = []
    verify_bm_sb = []

    verify_bm_bls_aggr = []

    for _ in range(RUNS):
        m = BN128FQ.rand()

        (pks, sks) = bm_bls.keygen()

        start_time = time.time()
        sigma = bm_bls.sign(sks, pks, m)
        end_time = time.time()
        sign_bm_bls.append((end_time - start_time) * 1000)

        start_time = time.time()
        bm_bls.verify(pks, m, sigma)
        end_time = time.time()
        verify_bm_bls.append((end_time - start_time) * 1000)

        num_messages = 32
        ms = [BN128FQ(i) for i in range(1, num_messages+1)]
        assert len(ms) == num_messages
        sigmas = [bm_bls.sign(sks, pks, m) for m in ms]
        start_time = time.time()
        bm_bls.verify_aggr(pks, ms, sigmas)
        end_time = time.time()
        verify_bm_bls_aggr.append(((end_time - start_time) * 1000) / num_messages)

        (sks, pks) = bm_sb.keygen()

        start_time = time.time()
        sigma = bm_sb.sign(pks, sks, m)
        end_time = time.time()
        sign_bm_sb.append((end_time - start_time) * 1000)

        start_time = time.time()
        bm_sb.verify(pks, m, sigma)
        end_time = time.time()
        verify_bm_sb.append((end_time - start_time) * 1000)

    sign_bm_bls_total.append(sign_bm_bls)
    verify_bm_bls_total.append(verify_bm_bls)
    verify_bm_bls_aggr_total.append(verify_bm_bls_aggr)
    sign_bm_sb.append(sign_bm_sb)
    verify_bm_sb.append(verify_bm_sb)

mean_sign_bm_bls, std_sign_bm_bls = compute_stats(sign_bm_bls_total)
mean_sign_bm_sb, std_sign_bm_sb = compute_stats(sign_bm_sb)
mean_verify_bm_bls, std_verify_bm_bls = compute_stats(verify_bm_bls_total)
mean_verify_bm_bls_aggr, std_verify_bm_bls_aggr = compute_stats(verify_bm_bls_aggr_total)
mean_verify_bm_sb, std_verify_bm_sb = compute_stats(verify_bm_sb)

plt.rcParams['text.latex.preamble'] = r"\usepackage{lmodern}"
rc('text', usetex=True)
rc(
    'font',
    family='serif',
    serif=['Computer Modern Roman'],
    monospace=['Computer Modern Typewriter'],
    size=25
)

plt.figure(figsize=(10, 9))

plt.errorbar(signers, mean_sign_bm_bls, yerr=std_sign_bm_bls, label='BM_BLS.Issue', fmt='-o', color='blue')
plt.errorbar(signers, mean_verify_bm_bls, yerr=std_verify_bm_bls, label='BM_BLS.Verify', fmt='--o', color='green')
plt.errorbar(signers, mean_verify_bm_bls_aggr, yerr=std_verify_bm_bls_aggr, label='BM_BLS.VerifyAggr', fmt='--*', color='orange')
plt.errorbar(signers, mean_sign_bm_sb, yerr=std_sign_bm_sb, label='BM_SB.Issue', fmt='-^', color='red')
plt.errorbar(signers, mean_verify_bm_sb, yerr=std_verify_bm_sb, label='BM_SB.Verify', fmt='--^', color='purple')

plt.xlabel('Number of issuers')
plt.ylabel('Execution time [ms]')
plt.xscale('log', base=2)
plt.yscale('log')
plt.grid(True)

plt.xticks(signers, [r'$2^{0}$'.format(i) for i in range(SIGNERS_MAX_POWER+1)])

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25), columnspacing=1, ncol=2, frameon=False)

plt.savefig("time.pdf", format="pdf", bbox_inches="tight")
plt.show()
