# tests/test_game_engine.py

import pytest
import numpy as np
from simulator import game_engine

def test_roll_dice_distribution():
    rng = np.random.default_rng(seed=42)
    rolls = [game_engine.roll_dice(rng) for _ in range(10000)]
    assert all(2 <= roll <= 12 for roll in rolls)
    # Rough check of mean (~7)
    mean_roll = sum(rolls) / len(rolls)
    assert 6.5 < mean_roll < 7.5

def test_build_game_state_structure():
    class DummyAgent:
        def __init__(self):
            self.bets = [
                {'type': 'pass_line_odds', 'multiplier': 1},
                {'type': 'come_flat', 'amount': 10},
                {'type': 'come_odds', 'multiplier': 2, 'point': 6}
            ]
            self.active_come_points = {6}
            self.current_point = 5
            self.table_min = 10

    agent = DummyAgent()
    state = game_engine.build_game_state(agent)

    assert isinstance(state, dict)
    assert 'pass_line_odds_levels' in state
    assert state['pass_line_odds_levels'] == [1]
    assert state['come_flat_active'] is True
    assert state['active_come_points'] == [6]
    assert state['come_odds_levels'] == {6: [2]}
    assert state['current_point'] == 5
    assert state['table_min'] == 10
