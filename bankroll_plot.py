#!/usr/bin/env python3
# plot_bankrolls.py

import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, 'data')
    output_dir = os.path.join(base_dir, 'plots')

    # ✅ Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    agents = ['classical', 'quantum', 'qbist', 'random']
    label_map = {
        'classical': 'Classical',
        'quantum': 'Quantum',
        'qbist': 'QBist',
        'random': 'Random'
    }

    starting_bankroll = 1000
    plt.figure(figsize=(10, 6))

    for agent in agents:
        csv_path = os.path.join(data_dir, f'{agent}_bankrolls.csv')
        if not os.path.exists(csv_path):
            print(f"⚠️  Warning: {csv_path} not found, skipping.")
            continue

        df = pd.read_csv(csv_path)
        df.columns = ['GameNumber', 'Bankroll']
        df['GameNumber'] = df['GameNumber'].astype(int) + 1

        label = label_map.get(agent, agent.title())
        plt.plot(df['GameNumber'], df['Bankroll'], label=label)

        final = df['Bankroll'].iloc[-1]
        plt.text(df['GameNumber'].iloc[-1], final, f'{final:.0f}', fontsize=8, ha='left', va='center')
        print(f"{label} final bankroll: ${final:.2f}")

    plt.axhline(y=starting_bankroll, color='gray', linestyle='--', linewidth=0.8, label='Starting Bankroll')

    plt.xlabel('Game Number')
    plt.ylabel('Bankroll')
    plt.title('Agent Bankrolls Over Games')
    plt.legend(loc='best')
    plt.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.6)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'bankroll_plot.png')
    plt.savefig(output_path, dpi=900)
    print(f"\n✅ Saved plot to: {output_path}")
    plt.show()

if __name__ == '__main__':
    main()
