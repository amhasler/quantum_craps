import os
import json
import importlib
import numpy as np
import pandas as pd
from simulator.simulator import simulate_agent

# --- Load configuration ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

NUM_GAMES = config["num_games"]
STARTING_BANKROLL = config["starting_bankroll"]
TABLE_MINIMUM = config["table_minimum"]
WALKAWAY_THRESHOLD = config["walkaway_threshold"]
SEED = config["fixed_seed"]
AGENT_SPECS = config["agents"]

# --- Output directory ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# --- Run simulations for all agents ---
def main():
    for agent_key, agent_info in AGENT_SPECS.items():
        print(f"\nSimulating: {agent_key.capitalize()} Agent")

        module = importlib.import_module(agent_info["module"])
        AgentClass = getattr(module, agent_info["name"])

        rng = np.random.default_rng(SEED)  # Same seed for each agent

        agent = AgentClass(
            starting_bankroll=STARTING_BANKROLL,
            table_minimum=TABLE_MINIMUM,
            walkaway_threshold=WALKAWAY_THRESHOLD
        )

        history = simulate_agent(agent, rng, num_games=NUM_GAMES)

        df = pd.DataFrame({
            'game': np.arange(len(history)),
            'bankroll': history
        })

        out_path = os.path.join(DATA_DIR, f"{agent_key}_bankrolls.csv")
        df.to_csv(out_path, index=False)
        print(f" → Saved to {out_path}")

if __name__ == "__main__":
    main()
