# src/agents/qbist_agent.py
import itertools
import numpy as np
from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator
from simulator.payouts import PAYOUT_TABLE
from simulator.game_engine import build_game_state
from utils.sic_utils import load_sic
import re

class QBistAgent(BaseAgent):
    def __init__(self, max_dim=6, name="qbist", **kwargs):
        super().__init__(**kwargs)
        self.max_dim = max_dim
        self.action_gen = AtomicActionGenerator()
        self.name = name

    def place_pass_line_bet(self):
        if self.bankroll >= self.table_min:
            self.bets.append({'type': 'pass_line_flat', 'amount': self.table_min})
            self.adjust_bankroll(-self.table_min)

    def update_action_space(self, game_state=None):
        if game_state is None:
            game_state = build_game_state(self)
        atomic_actions = self.action_gen.generate_atomic_actions(game_state)
        self.legal_actions = []
        n = len(atomic_actions)
        for r in range(1, min(n, 3) + 1):
            self.legal_actions.extend(list(itertools.combinations(atomic_actions, r)))

    def choose_action(self):
        if not self.legal_actions:
            return None

        atomic_set = sorted({a for combo in self.legal_actions for a in combo})
        d = max(2, min(len(atomic_set), self.max_dim))  # ensure d >= 2

        # Load SICs as numpy arrays
        sic = load_sic(d)

        # Apply uniform SIC prior
        p_H = [1 / d**2 for _ in range(d**2)]

        # ✅ Filter for affordable actions only
        legal = sorted(
            [a for a in self.legal_actions if self.can_afford_action(a)],
            key=lambda x: tuple(sorted(x))
        )

        if not legal:
            return None

        scores = []
        for combo in legal:
            action_vec = np.zeros((d, 1), dtype=float)
            for atomic_label in combo:
                if atomic_label in atomic_set:
                    idx = atomic_set.index(atomic_label)
                    if idx < d:
                        action_vec[idx, 0] = 1 / np.sqrt(len(combo))

            E_A = action_vec @ action_vec.T
            payout = self._lookup_composite_payout(combo)

            # QBist score via urgleichung (uniform prior)
            coeff = (d + 1) / d**2
            tr_sum = sum(np.trace(E_A @ H_i) for H_i in sic)
            q_A = coeff * tr_sum - 1
            score = q_A * payout
            scores.append(score)

        return legal[int(np.argmax(scores))] if scores else None

    def place_bets(self, action):
        if not action or not self.can_afford_action(action):
            return

        for bet_str in action:
            amt = self._get_bet_amount(bet_str)
            if amt is None or amt < self.table_min or self.bankroll < amt:
                continue

            bet = {'type': bet_str.lower(), 'amount': amt}

            if 'come_odds_' in bet_str:
                bet['point'] = self._extract_come_point(bet_str)

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

    def _lookup_composite_payout(self, combo):
        total = 0.0
        for bet_str in combo:
            key = ((bet_str.lower(),), 'win')
            payout = self.lookup_payout(key, 'win')
            total += payout
        return total
