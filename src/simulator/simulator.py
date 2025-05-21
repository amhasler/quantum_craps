# src/simulator/simulator.py

from simulator.game_engine import play_game

def simulate_agent(agent, rng, num_games=100):

    # grab the play game function from the play game and run
    history = []
    for _ in range(num_games):
        # This runs come-out, point establishment, point rounds, etc.
        final_bankroll = play_game(agent, rng)
        # This is the history from the run_simulator
        history.append(final_bankroll)

        # stop early if bust or walkaway (not used)
        if not agent.can_continue():
            break

    return history
