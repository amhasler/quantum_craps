# src/agents/random_agent.py

import random
import itertools
from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator
from simulator.payouts import PAYOUT_TABLE
from simulator.game_engine import build_game_state

class RandomAgent(BaseAgent):
    # Included this in all agents to keep track of variables
    def __init__(self, max_combo_size=3, **kwargs):
        super().__init__(**kwargs)
        self.action_gen = AtomicActionGenerator()
        self.max_combo_size = max_combo_size

    def place_pass_line_bet(self):
        if self.bankroll >= self.table_min:
            self.bets.append({'type': 'pass_line_flat', 'amount': self.table_min})
            self.adjust_bankroll(-self.table_min)

    def update_action_space(self, game_state=None):
        # For tests
        if game_state is None:
            game_state = build_game_state(self)

        atomic_actions = self.action_gen.generate_atomic_actions(game_state)
        self.legal_actions = []
        n = len(atomic_actions)
        max_r = min(self.max_combo_size, n)
        for r in range(1, max_r + 1):
            self.legal_actions.extend(itertools.combinations(atomic_actions, r))

    def choose_action(self):
        if not self.legal_actions:
            return None
        return random.choice(self.legal_actions)

    def place_bets(self, action):
        if action is None:
            return

        for bet_str in action:
            if self.bankroll < self.table_min:
                break
            bet = {'type': bet_str.lower(), 'amount': self.table_min}
            self.bets.append(bet)
            self.adjust_bankroll(-self.table_min)

    def resolve_game(self, outcome):
        remaining = []
        for bet in self.bets:
            key = ((bet['type'],), outcome)
            mult = PAYOUT_TABLE.get(key, 0)
            if mult < 0:
                # lost wager, remove
                continue
            if mult > 0:
                # win: add payout (mult * wager)
                self.adjust_bankroll(bet['amount'] * mult)
            # keep the bet on the table if it wasn't lost
            remaining.append(bet)

        self.bets = remaining
