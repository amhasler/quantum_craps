# src/agents/random_agent.py

import random
import itertools
import re
from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator
from simulator.payouts import PAYOUT_TABLE
from simulator.game_engine import build_game_state


class RandomAgent(BaseAgent):
    def __init__(self, max_combo_size=6, name="random", **kwargs,):
        super().__init__(**kwargs)
        self.action_gen = AtomicActionGenerator()
        self.max_combo_size = max_combo_size
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
        max_r = min(self.max_combo_size, n)
        for r in range(1, max_r + 1):
            self.legal_actions.extend(itertools.combinations(atomic_actions, r))

    def choose_action(self):
        if not self.legal_actions:
            return None

        legal = [a for a in self.legal_actions if self.can_afford_action(a)]
        if not legal:
            return None
        return random.choice(self.legal_actions)

    def place_bets(self, action):
        if not action or not self.can_afford_action(action):
            return


        for bet_str in action:
            amt = self._extract_bet_amount(bet_str)
            if self.bankroll >= amt:
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

    # --- Internal Utilities ---

    def _extract_bet_amount(self, bet_str):
        if bet_str.startswith('pass_line_odds_$'):
            match = re.match(r'pass_line_odds_\$(\d+)', bet_str)
            return int(match.group(1)) if match else self.table_min
        elif bet_str.startswith('come_odds_$'):
            match = re.match(r'come_odds_\$(\d+)_\d+', bet_str)
            return int(match.group(1)) if match else self.table_min
        else:
            return self.table_min

    def _extract_come_point(self, bet_str):
        match = re.match(r'come_odds_\$\d+_(\d+)', bet_str)
        return int(match.group(1)) if match else None
