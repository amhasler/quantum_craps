# src/simulator/simulator.py

from simulator.game_engine import play_game

def simulate_agent(agent, rng, num_games=100):
    """
    Simulate a series of *complete* craps games for the agent,
    using the canonical play_game() for each one.
    """
    history = []
    for _ in range(num_games):
        # This runs come-out, point establishment, point rounds, etc.
        final_bankroll = play_game(agent, rng)
        history.append(final_bankroll)

        # stop early if bust or walkaway
        if not agent.can_continue():
            break

    return history
