# src/simulator/simulator.py

from simulator.game_engine import play_game
from utils.diagnostics import initialize_diagnostics_file, append_diagnostics_row
import time
import os

def simulate_agent(agent, rng, num_games=100):
    history = []

    # Step 3: Initialize diagnostics file
    diagnostics_path = os.path.join("data", f"{agent.name}_diagnostics.csv")
    diagnostics_headers = [
        "agent", "game_number", "bankroll",
        "atomic_action_count", "composite_action_count",
        "bets_placed", "total_wager",
        "compute_cost_estimate", "decision_time_sec"
    ]
    initialize_diagnostics_file(diagnostics_path, diagnostics_headers)

    for game_number in range(num_games):
        # Time the decision phase
        start_time = time.perf_counter()
        action = agent.choose_action()
        decision_time = time.perf_counter() - start_time

        # Play the game and get final bankroll
        final_bankroll = play_game(agent, rng)
        history.append(final_bankroll)

        # Step 4: Collect diagnostics
        atomic_count = (
            len(agent.action_gen.latest_atomic_actions)
            if hasattr(agent.action_gen, "latest_atomic_actions")
            else None
        )
        composite_count = len(agent.legal_actions)
        bets_placed = len(agent.bets)
        total_wager = sum(bet['amount'] for bet in agent.bets)

        d = min(composite_count, getattr(agent, "max_dim", 10))
        if agent.name == "qbist":
            compute_cost = d**5
        elif agent.name == "quantum":
            compute_cost = d**3
        else:
            compute_cost = d

        append_diagnostics_row(diagnostics_path, [
            agent.name,
            game_number,
            final_bankroll,
            atomic_count,
            composite_count,
            bets_placed,
            total_wager,
            compute_cost,
            round(decision_time, 6)
        ])

        # stop early if bust or walkaway
        if not agent.can_continue():
            break

    return history
