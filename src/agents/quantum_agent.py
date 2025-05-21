# src/agents/quantum_agent.py

from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator
from simulator.probabilities import get_bet_probs
from agents.utils import parse_atomic
from simulator.payouts import PAYOUT_TABLE
from simulator.game_engine import build_game_state
import itertools
import numpy as np

class QuantumAgent(BaseAgent):
    # Included this in all agents to keep track of variables
    def __init__(self, max_combo_size=10, max_dim=None, **kwargs):
        super().__init__(**kwargs)
        self.max_combo_size = max_combo_size
        self.max_dim = max_dim
        self.action_gen = AtomicActionGenerator()

    def place_pass_line_bet(self):
        if self.bankroll >= self.table_min:
            bet = {'type': 'pass_line_flat', 'amount': self.table_min}
            self.bets.append(bet)
            self.adjust_bankroll(-self.table_min)

    def update_action_space(self, game_state=None):
        # For tests
        if game_state is None:
            game_state = build_game_state(self)
        atomic_actions = self.action_gen.generate_atomic_actions(game_state)
        self.legal_actions = []
        max_r = min(self.max_combo_size, len(atomic_actions))
        for r in range(1, max_r + 1):
            self.legal_actions.extend(itertools.combinations(atomic_actions, r))

    # Landed on using the same basic EV for each agent, because probs and payouts the same
    def classical_ev(self, combo):
        ev = 0.0
        for bet_str in combo:
            bet_type, parsed_point = parse_atomic(bet_str)
            # For odds bets without explicit point, use the current point
            point = parsed_point if parsed_point is not None else self.current_point
            probs = get_bet_probs(bet_type, point)
            for outcome, p in probs.items():
                mult = PAYOUT_TABLE.get(((bet_str.lower(),), outcome), 0)
                ev += p * mult
        return ev

    # Critical distinguishing function. Expands rho dimensions by available bets.
    def choose_action(self):
        if not self.legal_actions:
            return None

        # Build list of atomic actions & determine dimension
        atomic_set = sorted({a for combo in self.legal_actions for a in combo})
        d = min(len(atomic_set), self.max_dim or len(atomic_set))
        rho = np.eye(d) / d

        scores = []
        for combo in self.legal_actions:
            # build rank-1 projector E_A from combo
            action_vec = np.zeros(d, dtype=complex)
            for a in combo:
                if a in atomic_set:
                    idx = atomic_set.index(a)
                    if idx < d:
                        action_vec[idx] = 1
            E_A = np.outer(action_vec, np.conj(action_vec))
            # score = Tr(rho E_A)
            qscore = np.real(np.trace(rho @ E_A))
            scores.append(qscore)

        total = sum(scores)
        if total > 0:
            probs = [s / total for s in scores]
        else:
            probs = [1 / len(scores)] * len(scores)

        best_idx = int(np.argmax(probs))
        return self.legal_actions[best_idx]

    def place_bets(self, action):
        if not action:
            return
        for bet_str in action:
            if self.bankroll < self.table_min:
                break
            bet = {'type': bet_str.lower(), 'amount': self.table_min}
            self.bets.append(bet)
            self.adjust_bankroll(-self.table_min)

    def resolve_game(self, outcome):
        remaining_bets = []
        for bet in self.bets:
            key = ((bet['type'],), outcome)
            mult = PAYOUT_TABLE.get(key, 0)
            if mult < 0:
                continue
            if mult > 0:
                self.adjust_bankroll(bet['amount'] * mult)
            remaining_bets.append(bet)
        self.bets = remaining_bets
