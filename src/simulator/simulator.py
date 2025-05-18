import os
from game_engine.game_engine import play_game

def simulate_agent(agent, rng, num_games=100):
    history = []
    for _ in range(num_games):
        if not agent.can_continue():
            break  # Stop simulating if agent is broke or has walked away
        final_bankroll = play_game(agent, rng)
        history.append(final_bankroll)
    return history
