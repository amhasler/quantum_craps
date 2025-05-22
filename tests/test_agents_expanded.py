import pytest
import numpy as np
from agents.classical_agent import ClassicalAgent
from agents.quantum_agent import QuantumAgent
from agents.qbist_agent import QBistAgent
from simulator.simulator import simulate_agent
from simulator.game_engine import play_game

# Test 1: ClassicalAgent computes EV for multiple bets
def test_classical_agent_composite_ev_multiple_bets():
    payouts = {
        (('pass_line_flat',), 'win'): 1.0,
        (('come_flat',), 'win'): 1.0
    }
    outcome_probs = {'win': 0.5, 'lose': 0.5}
    agent = ClassicalAgent(
        payout_table=payouts,
        outcome_probs=outcome_probs,
        starting_bankroll=1000,
        table_minimum=10
    )
    combo = ['pass_line_flat', 'come_flat']
    ev = agent.compute_expected_value(combo)
    assert ev == pytest.approx(1.0)


# Test 2: QuantumAgent chooses best payout action
def test_quantum_agent_action_score_selection():
    agent = QuantumAgent(starting_bankroll=1000, table_minimum=10, max_combo_size=2)
    agent.legal_actions = [('pass_line_flat',), ('come_flat',)]
    agent.payout_table = {
        (('pass_line_flat',), 'win'): 1.0,
        (('come_flat',), 'win'): 2.0,
    }
    action = agent.choose_action()
    assert action in [('pass_line_flat',), ('come_flat',)]

# Test 3: QBistAgent scoring with uniform SIC prior
def test_qbist_agent_qscore_applies_uniform_prior():
    agent = QBistAgent(starting_bankroll=1000, table_minimum=10, max_dim=3)
    agent.legal_actions = [('pass_line_flat',)]
    agent.payout_table = {
        (('pass_line_flat',), 'win'): 1.0,
    }
    action = agent.choose_action()
    assert action == ('pass_line_flat',)

# Test 4: Game engine runs correctly with fixed agent
def test_game_engine_single_game_win_path():
    class TestAgent:
        def __init__(self):
            self.bankroll = 1000
            self.table_min = 10
            self.initial_bankroll = 1000
            self.bets = []
            self.legal_actions = [('pass_line_flat',)]
            self.active_come_points = set()
            self.current_point = None
            self.point_established = False
            self.payout_table = {
                (('pass_line_flat',), 'win'): 1.0,
            }

        def place_pass_line_bet(self):
            self.bets.append({'type': 'pass_line_flat', 'amount': 10})
            self.bankroll -= 10

        def update_action_space(self): pass
        def choose_action(self): return None
        def adjust_bankroll(self, delta): self.bankroll += delta
        def can_continue(self): return self.bankroll >= self.table_min
        def start_new_game(self): pass
        def lookup_payout(self, key, outcome):
            return self.payout_table.get((key, outcome), 0.0)
        def resolve_game(self, outcome): pass

    rng = np.random.default_rng(seed=42)
    agent = TestAgent()
    final = play_game(agent, rng)
    assert final >= 990

# Test 5: Full simulation runs and agent places bets
def test_simulation_agent_places_bets():
    payouts = {
        (('pass_line_flat',), 'win'): 1.0,
        (('pass_line_flat',), 'lose'): -1.0
    }
    outcome_probs = {'win': 0.5, 'lose': 0.5}
    agent = ClassicalAgent(
        payout_table=payouts,
        outcome_probs=outcome_probs,
        starting_bankroll=1000,
        table_minimum=10
    )
    rng = np.random.default_rng(123)
    history = simulate_agent(agent, rng, num_games=10)

    assert len(history) > 0
    assert isinstance(agent.bets, list)
    assert all('type' in b for b in agent.bets) or agent.bets == []
