# src/agents/classical_agent.py

from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator
from itertools import combinations
import re


class ClassicalAgent(BaseAgent):
    def __init__(self, payout_table=None, name="classical", outcome_probs=None, flat_bets=None, max_combo_size=6, **kwargs):
        super().__init__(payout_table=payout_table, **kwargs)

        self.outcome_probs = outcome_probs or {
            'win': 0.4929,
            'lose': 0.5071
        }

        self.flat_bets = flat_bets or ['pass_line_flat', 'come_flat']
        self.max_combo_size = max_combo_size
        self.action_gen = AtomicActionGenerator()
        self.name = name

    def place_pass_line_bet(self):
        if self.bankroll >= self.table_min:
            bet = {'type': 'pass_line_flat', 'amount': self.table_min}
            self.bets.append(bet)
            self.adjust_bankroll(-self.table_min)

    def update_action_space(self):
        game_state = {
            'pass_line_odds_levels': sorted([
                self._extract_odds_amount(bet['type'])
                for bet in self.bets
                if bet['type'].startswith('pass_line_odds_')
            ]),
            'come_flat_active': any(b['type'] == 'come_flat' and 'point' not in b for b in self.bets),
            'active_come_points': sorted(self.active_come_points),
            'come_odds_levels': {},
            'current_point': self.current_point,
            'table_min': self.table_min,
        }

        for bet in self.bets:
            if bet['type'].startswith('come_odds_'):
                _, pt = self._parse_come_odds(bet['type'])
                pt_str = str(pt)
                if pt_str not in game_state['come_odds_levels']:
                    game_state['come_odds_levels'][pt_str] = []
                game_state['come_odds_levels'][pt_str].append(bet['amount'])

        atomic = self.action_gen.generate_atomic_actions(game_state)
        self.legal_actions = self._enumerate_composites(atomic)

    def choose_action(self):
        if not self.legal_actions:
            return None
        legal = [a for a in self.legal_actions if self.can_afford_action(a)]
        if not legal:
            return None

        max_ev = float('-inf')
        best_actions = []

        for combo in self.legal_actions:
            ev = self.compute_expected_value(combo)
            if ev > max_ev:
                max_ev = ev
                best_actions = [combo]
            elif ev == max_ev:
                best_actions.append(combo)

        # Break ties by minimizing total wager
        def total_wager(action):
            wager = sum(self._get_bet_amount(bet) for bet in action)
            committed = sum(b['amount'] for b in self.bets if b['type'] in ('pass_line_flat', 'come_flat'))
            return wager + committed

        return min(best_actions, key=total_wager)

    def compute_expected_value(self, combo):
        ev = 0.0
        for outcome, prob in self.outcome_probs.items():
            payout = 0.0
            for bet_str in combo:
                payout += self.payout_table.get(((bet_str.lower(),), outcome), 0.0)
            ev += prob * payout
        return ev

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

    # --- Internal Utilities ---

    def _enumerate_composites(self, atomic):
        all_combos = []
        for r in range(1, min(len(atomic), self.max_combo_size) + 1):
            all_combos.extend(combinations(atomic, r))
        return [list(combo) for combo in all_combos]

    def _extract_odds_amount(self, bet_type):
        match = re.match(r'pass_line_odds_\$(\d+)', bet_type)
        return int(match.group(1)) if match else None

    def _parse_come_odds(self, bet_type):
        match = re.match(r'come_odds_\$(\d+)_([4-6]|[8-9]|10)', bet_type)
        if match:
            amt = int(match.group(1))
            pt = int(match.group(2))
            return amt, pt
        return None, None

    def resolve_game(self, outcome):
        remaining = []
        for bet in self.bets:
            key = ((bet['type'],), outcome)
            mult = self.lookup_payout(key, outcome)
            if mult < 0:
                continue  # lost
            if mult > 0:
                self.adjust_bankroll(bet['amount'] * mult)
            remaining.append(bet)
        self.bets = remaining

