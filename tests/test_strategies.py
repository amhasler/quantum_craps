# tests/test_strategies.py

import pytest
from agents.random_agent import RandomAgent
from agents.classical_agent import ClassicalAgent
from agents.quantum_agent import QuantumAgent
from agents.qbist_agent import QBistAgent

def test_random_agent_action_choice():
    agent = RandomAgent(starting_bankroll=1000, table_minimum=10)
    # Simulate legal actions manually
    agent.legal_actions = [('pass_line_flat',), ('come_flat',)]
    chosen = agent.choose_action()
    assert chosen in agent.legal_actions

def test_classical_agent_expected_value_computation():
    # Minimal setup for classical agent
    payouts = {
        (('pass_line_flat',), 'win'): 1.0,
        (('pass_line_flat',), 'lose'): -1.0,
    }
    outcome_probs = {'win': 0.4, 'lose': 0.6}
    flat_bets = [('pass_line_flat',)]
    agent = ClassicalAgent(payout_table=payouts, outcome_probs=outcome_probs,
                          flat_bets=flat_bets, starting_bankroll=1000, table_minimum=10)
    # Provide legal actions
    agent.legal_actions = [('pass_line_flat',)]
    ev = agent.compute_expected_value(agent.legal_actions[0])
    assert isinstance(ev, float)
    assert ev == pytest.approx(0.4 * 1.0 + 0.6 * -1.0)

def test_quantum_agent_legal_actions_update():
    agent = QuantumAgent(starting_bankroll=1000, table_minimum=10, max_combo_size=2)
    # Mock game state with atomic actions
    game_state = {
        'pass_line_odds_levels': [],
        'come_flat_active': False,
        'active_come_points': [],
        'come_odds_levels': {},
        'current_point': None,
        'table_min': 10
    }
    # Directly call update_action_space
    agent.bets = []
    agent.current_point = None
    agent.active_come_points = set()
    agent.update_action_space()
    # Should generate some legal actions (possibly empty if no atomic actions)
    assert isinstance(agent.legal_actions, list)

def test_qbist_agent_choose_action():
    agent = QBistAgent(starting_bankroll=1000, table_minimum=10)
    # Provide dummy legal actions
    agent.legal_actions = [('pass_line_flat',), ('come_flat',)]
    chosen = agent.choose_action()
    assert chosen in agent.legal_actions
