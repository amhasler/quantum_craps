# src/agents/qbist_agent.py

import numpy as np
from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator
from simulator.payouts import PAYOUT_TABLE
from simulator.probabilities import get_bet_probs
from agents.utils import parse_atomic
from utils.sic_utils import load_sic # Check separately
import itertools

class QBistAgent(BaseAgent):
    # Included this in all agents to keep track of variables
    def __init__(self, max_combo_size=10, max_dim=10, **kwargs):
        super().__init__(**kwargs)
        self.max_combo_size = max_combo_size
        self.max_dim = max_dim
        self.action_gen = AtomicActionGenerator()

    # Landed on using the same basic EV for each agent, because probs and payouts the same
    def classical_ev(self, combo):
        ev = 0.0
        for bet_str in combo:
            bet_type, parsed_point = parse_atomic(bet_str)
            # For odds-type bets missing a point, fall back to current_point
            point = parsed_point if parsed_point is not None else self.current_point
            probs = get_bet_probs(bet_type, point)
            for outcome, p in probs.items():
                mult = PAYOUT_TABLE.get(((bet_str.lower(),), outcome), 0)
                ev += p * mult
        return ev

    def place_pass_line_bet(self):
        if self.bankroll >= self.table_min:
            self.bets.append({'type': 'pass_line_flat', 'amount': self.table_min})
            self.adjust_bankroll(-self.table_min)

    def update_action_space(self, game_state=None):
        # For tests
        if game_state is None:
            from simulator.game_engine import build_game_state
            game_state = build_game_state(self)

        atomic_actions = self.action_gen.generate_atomic_actions(game_state)
        self.legal_actions = []
        max_r = min(self.max_combo_size, len(atomic_actions))
        for r in range(1, max_r + 1):
            self.legal_actions.extend(itertools.combinations(atomic_actions, r))

    # Key differentiator. Updates dimensions based on legal bets
    # Although techincally this could go up to 22, I capped it at 10
    # because d=22 for SICs is insane
    # Credit to Matt Weiss for help here
    def choose_action(self):
        if not self.legal_actions:
            return None

        # Build atomic_set and cap dimension
        atomic_set = sorted({a for combo in self.legal_actions for a in combo})
        d = min(len(atomic_set), self.max_dim)

        # Load SIC POVM projectors (Qobj instances) and convert to numpy arrays
        sic_qobjs = load_sic(d)  # list of d^2 Qobj projectors
        sic = [H_i.full() for H_i in sic_qobjs]  # now each is a (d×d) ndarray

        rho = np.eye(d) / d  # maximally mixed state

        # Precompute p(H_i) = Tr(rho H_i)
        p_H = [np.real(np.trace(rho @ H_i)) for H_i in sic]

        scores = []
        for combo in self.legal_actions:
            # Build the action projector E_A
            action_vec = np.zeros(d, dtype=complex)
            for label in combo:
                idx = atomic_set.index(label)
                if idx < d:
                    action_vec[idx] = 1
            E_A = np.outer(action_vec, np.conj(action_vec))

            # QBist coherence via the urgleichung
            qscore = 0.0
            for H_i, p_i in zip(sic, p_H):
                overlap = np.real(np.trace(E_A @ H_i))
                qscore += ((d + 1) * overlap - 1 / d) * p_i

            # Classical EV
            ev = self.classical_ev(combo)

            scores.append(qscore * ev)

        # Normalize to probabilities
        total = sum(scores)
        if total > 0:
            probs = [s / total for s in scores]
        else:
            probs = [1 / len(scores)] * len(scores)

        return self.legal_actions[int(np.argmax(probs))]

    def place_bets(self, action):
        if not action:
            return
        # Distribute full table_min per new action
        amt = self.table_min
        for bet_str in action:
            if self.bankroll < amt:
                break
            bet = {'type': bet_str.lower(), 'amount': amt}
            self.bets.append(bet)
            self.adjust_bankroll(-amt)

    def resolve_game(self, outcome):
        remaining = []
        for bet in self.bets:
            key = ((bet['type'],), outcome)
            mult = PAYOUT_TABLE.get(key, 0)
            if mult < 0:
                continue
            if mult > 0:
                self.adjust_bankroll(bet['amount'] * mult)
            remaining.append(bet)
        self.bets = remaining
