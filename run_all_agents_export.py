import numpy as np
import csv
import os
import time
from src.agents.classical_agent import ClassicalAgent
from src.agents.quantum_agent import QuantumAgent
from src.agents.qbist_agent import QBistAgent
from src.agents.random_agent import RandomAgent
from src.simulator.payouts import PAYOUT_TABLE

OUTCOME_PROBS = {'win': 0.4929, 'lose': 0.5071}
FLAT_BETS = ['pass_line_flat', 'come_flat']

DATA_DIR = "data"

def save_bankroll_history(filename, bankroll_history):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['GameNumber', 'Bankroll'])
        for i, bankroll in enumerate(bankroll_history, start=1):
            writer.writerow([i, bankroll])

def run_and_export():
    rng = np.random.default_rng(seed=42)
    num_games = 100

    agents = {
        "Classical": ClassicalAgent(
            payout_table=PAYOUT_TABLE,
            outcome_probs=OUTCOME_PROBS,
            flat_bets=FLAT_BETS,
            starting_bankroll=1000,
            table_minimum=10),
        "Quantum": QuantumAgent(
            max_combo_size=10,
            max_dim=6,
            starting_bankroll=1000,
            table_minimum=10),
        "QBist": QBistAgent(
            max_combo_size=10,
            max_dim=4,
            starting_bankroll=1000,
            table_minimum=10),
        "Random": RandomAgent(
            max_combo_size=10,
            starting_bankroll=1000,
            table_minimum=10)
    }

    from src.simulator.simulator import simulate_agent

    for name, agent in agents.items():
        start_time = time.time()
        bankroll_history = simulate_agent(agent, rng, num_games)
        elapsed = time.time() - start_time

        print(f"{name} agent final bankroll after {num_games} games: ${bankroll_history[-1]:.2f}")
        print(f"{name} agent simulation time: {elapsed:.4f} seconds")

        save_bankroll_history(f"{name.lower()}_bankrolls.csv", bankroll_history)
        print(f"Saved bankroll history to {os.path.join(DATA_DIR, name.lower() + '_bankrolls.csv')}\n")

if __name__ == "__main__":
    run_and_export()
