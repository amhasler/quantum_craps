# This is what actually runs the simulation, and updates the agents.
# Necessary for running many agents.

import os
import json
import importlib
import numpy as np
import pandas as pd
from simulator.simulator import simulate_agent

# Load config files
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Set config values
NUM_GAMES = config["num_games"]
STARTING_BANKROLL = config["starting_bankroll"]
TABLE_MINIMUM = config["table_minimum"]
# WALKAWAY_THRESHOLD = config["walkaway_threshold"] # Not currently using this, because no one profitable.
SEED = config["fixed_seed"]
AGENT_SPECS = config["agents"]

# Output directory (This is just the csv's to export to)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    # Populate all
    for agent_key, agent_info in AGENT_SPECS.items():
        # Debug
        print(f"\nSimulating: {agent_key.capitalize()} Agent")

        # Grab agent to update
        module = importlib.import_module(agent_info["module"])
        # Get actual agent by name
        AgentClass = getattr(module, agent_info["name"])

        rng = np.random.default_rng(SEED)

        # Update the specs for that agent (needed when running through
        agent = AgentClass(
            starting_bankroll=STARTING_BANKROLL,
            table_minimum=TABLE_MINIMUM
            # walkaway_threshold=WALKAWAY_THRESHOLD unused right now
        )

        # Update history
        history = simulate_agent(agent, rng, num_games=NUM_GAMES)

        # Get data to put in CSV (two columns)
        df = pd.DataFrame({
            'game': list(range(len(history))),
            'bankroll': history
        })

        # Basic CSV update
        out_path = os.path.join(DATA_DIR, f"{agent_key}_bankrolls.csv")
        df.to_csv(out_path, index=False)
        print(f" → Saved to {out_path}")

# Run main when when file called
if __name__ == "__main__":
    main()
