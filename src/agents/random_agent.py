# src/agents/random_agent.py

import random
import itertools
from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator
from simulator.payouts import PAYOUT_TABLE
from simulator.game_engine import build_game_state

class RandomAgent(BaseAgent):
    """
    Random agent picks one of the available composite actions uniformly at random.
    """

    def __init__(self, max_combo_size=3, **kwargs):
        """
        Args:
            max_combo_size (int): maximum number of atomic bets per composite action
            **kwargs: passed to BaseAgent (starting_bankroll, table_minimum, etc.)
        """
        super().__init__(**kwargs)
        self.action_gen = AtomicActionGenerator()
        self.max_combo_size = max_combo_size

    def place_pass_line_bet(self):
        """Always place the flat Pass Line bet on the come-out roll."""
        if self.bankroll >= self.table_min:
            self.bets.append({'type': 'pass_line_flat', 'amount': self.table_min})
            self.adjust_bankroll(-self.table_min)

    def update_action_space(self, game_state=None):
        """
        Update self.legal_actions to all combinations of legal atomic actions
        up to max_combo_size. Rebuilds game_state internally if not provided.
        """
        if game_state is None:
            game_state = build_game_state(self)

        atomic_actions = self.action_gen.generate_atomic_actions(game_state)
        self.legal_actions = []
        n = len(atomic_actions)
        max_r = min(self.max_combo_size, n)
        for r in range(1, max_r + 1):
            self.legal_actions.extend(itertools.combinations(atomic_actions, r))

    def choose_action(self):
        """Select one of the legal composite actions uniformly at random."""
        if not self.legal_actions:
            return None
        return random.choice(self.legal_actions)

    def place_bets(self, action):
        """
        For each atomic bet in the chosen composite action, place a wager
        equal to the table minimum (if funds allow).
        """
        if action is None:
            return

        for bet_str in action:
            if self.bankroll < self.table_min:
                break
            bet = {'type': bet_str.lower(), 'amount': self.table_min}
            self.bets.append(bet)
            self.adjust_bankroll(-self.table_min)

    def resolve_game(self, outcome):
        """
        Resolve all active bets according to the PAYOUT_TABLE.
        - Winning bets pay out and remain (you keep your chips on the table).
        - Losing bets are removed.
        - Bets with no matching entry stay on the table.
        """
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
