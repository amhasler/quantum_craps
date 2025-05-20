#!/usr/bin/env python3
# plot_compute_cost.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullLocator

def main():
    # Dimensions from 1 to 10
    d = np.arange(1, 11)

    # Approximated compute costs
    random_cost    = np.clip(d, None, 10)
    classical_cost = np.clip(d, None, 10)
    quantum_cost   = np.clip(d**3, None, 1000)
    qbist_cost     = np.clip(d**5, None, 100000)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(d, random_cost,    marker='d', linestyle=':', label='Random')
    ax.plot(d, classical_cost, marker='o', label='Classical')
    ax.plot(d, quantum_cost,   marker='s', label='Quantum')
    ax.plot(d, qbist_cost,     marker='^', label='QBist')

    ax.set_yscale('log')
    ax.set_xlim(0, 10)
    ax.set_xlabel('Dimension $d$')
    ax.set_ylabel('Compute Cost (arb. units, log scale)')
    ax.set_title('Estimated Computational Cost vs Dimension (1–10)')

    # Show only major y‐ticks at powers of 10
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=10))
    ax.yaxis.set_minor_locator(NullLocator())

    ax.grid(True, which='major', ls='--', lw=0.5)
    ax.legend(loc='best')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
