# plot_bankrolls.py

import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, 'data')

    agents = ['classical', 'quantum', 'qbist', 'random']
    label_map = {
        'classical': 'Classical',
        'quantum': 'Quantum',
        'qbist': 'QBist',
        'random': 'Random'
    }
    plt.figure(figsize=(10,6))

    for agent in agents:
        csv_path = os.path.join(data_dir, f'{agent}_bankrolls.csv')
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping.")
            continue

        # Read with header row, so pandas will use the first line as column names
        df = pd.read_csv(csv_path)

        # Ensure columns are named correctly
        df.columns = ['GameNumber', 'Bankroll']

        # Convert GameNumber to int (in case) and shift from 0-based → 1-based
        df['GameNumber'] = df['GameNumber'].astype(int) + 1

        plt.plot(df['GameNumber'], df['Bankroll'], label=label_map.get(agent, agent))

    plt.xlabel('Game Number')
    plt.ylabel('Bankroll')
    plt.title('Agent Bankrolls Over Games')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig("/Users/amhasler/Desktop/sine_wave.png", dpi=900)
    plt.show()

if __name__ == '__main__':
    main()
