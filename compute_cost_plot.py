#!/usr/bin/env python3
# plot_compute_cost.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullLocator

def compute_costs(d_range):
    """
    Theoretical computational cost estimates for each agent type.
    Assumes max composite size k = 3.
    """
    return {
        'Random':    np.ones_like(d_range),         # O(1)
        'Classical': d_range**3,                    # O(d^3)
        'Quantum':   d_range**5,                    # O(d^5)
        'QBist':     d_range**7                     # O(d^7)
    }

def plot_computational_complexity():
    d_range = np.arange(1, 11)  # Dimensions 1 to 10

    # Estimated cost models
    costs = compute_costs(d_range)

    # Plot styling
    fig, ax = plt.subplots(figsize=(9, 6))
    markers = {'Random': 'd', 'Classical': 'o', 'Quantum': 's', 'QBist': '^'}
    linestyles = {'Random': ':', 'Classical': '-', 'Quantum': '--', 'QBist': '-.'}
    complexity_orders = {'Random': 0, 'Classical': 3, 'Quantum': 5, 'QBist': 7}

    for label, y_vals in costs.items():
        ax.plot(
            d_range,
            y_vals,
            label=label,
            marker=markers[label],
            linestyle=linestyles[label],
            linewidth=1.8
        )

        # Annotate asymptotic order at final point
        order = complexity_orders[label]
        annotation = f"$\\mathcal{{O}}(d^{{{order}}})$"
        ax.text(
            d_range[-1] + 0.2, y_vals[-1],
            annotation,
            fontsize=9,
            verticalalignment='center'
        )

    # Axes formatting
    ax.set_yscale('log')
    ax.set_xlim(1, 10.5)
    ax.set_ylim(0.8, 1.2e7)
    ax.set_xlabel('Composite Action Dimension $d$', fontsize=12)
    ax.set_ylabel('Estimated Computational Cost', fontsize=12)
    ax.set_title('Computational Complexity by Agent Type', fontsize=14)

    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.grid(True, which='major', linestyle='--', linewidth=0.5)
    ax.legend(loc='upper left', fontsize=10)
    plt.tight_layout()

    # Save and display
    output_path = "compute_cost_plot.png"
    plt.savefig(output_path, dpi=300)
    print(f"✅ Saved plot to: {output_path}")
    plt.show()

if __name__ == '__main__':
    plot_computational_complexity()
