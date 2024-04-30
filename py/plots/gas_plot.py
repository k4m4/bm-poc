import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib.ticker as ticker
import numpy as np

SIGNERS_MAX_POWER=6

num_issuers = np.array([2**i for i in range(SIGNERS_MAX_POWER+1)])
bm_bls_gas = np.full_like(num_issuers, 224534)
bm_sb_gas = np.array([66253, 80774, 111991, 183217, 361961, 879224, 2760507])

plt.rcParams['text.latex.preamble'] = r"\usepackage{lmodern}"
rc('text', usetex=True)
rc(
    'font',
    family='serif',
    serif=['Computer Modern Roman'],
    monospace=['Computer Modern Typewriter'],
    size=25
)

plt.figure(figsize=(10, 8))

plt.plot(num_issuers, bm_bls_gas, label='BM_BLS.Verify', marker='o', linestyle='dashed', color='green')
plt.plot(num_issuers, bm_sb_gas, label='BM_SB.Verify', marker='^', linestyle='dashed', color='purple')

def thousands_formatter(x, pos):
    return f'{int(x/1000)}'

plt.yscale('linear')
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(thousands_formatter))

plt.xlabel('Number of issuers')
plt.ylabel('Gas cost [x1K]')

plt.xscale('log', base=2)
plt.xticks(num_issuers, [r'$2^{0}$'.format(i) for i in range(SIGNERS_MAX_POWER+1)])

plt.grid(True)

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.125), ncol=2, frameon=False)

# Show the plot
plt.savefig("gas.pdf", format="pdf", bbox_inches="tight")
plt.show()
