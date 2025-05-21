# src/agents/classical_agent.py

from agents.base_agent import BaseAgent
from simulator.atomic_actions import AtomicActionGenerator # Separate shared script. Keys to the kingdom.
from simulator.payouts import PAYOUT_TABLE
# from simulator.probabilities import get_bet_probs
# from agents.utils import parse_atomic
from simulator.probabilities import OUTCOME_PROBS
# This was particularly interesting -
import itertools
import numpy as np

class ClassicalAgent(BaseAgent):
    # Included this in all agents to keep track of variables
    def __init__(
        # Old habits
        self,
        payout_table=None,
        outcome_probs=None,       # <- accept a custom dict
        flat_bets=None,
        max_combo_size=10,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.payout_table  = payout_table or PAYOUT_TABLE
        # Use injected outcome_probs, or default to full-craps OUTCOME_PROBS
        self.outcome_probs = outcome_probs or OUTCOME_PROBS
        self.flat_bets     = flat_bets or ['pass_line_flat', 'come_flat']
        self.max_combo_size= max_combo_size

        self.action_gen    = AtomicActionGenerator()

    # Required
    def place_pass_line_bet(self):
        if self.bankroll >= self.table_min:
            bet = {'type': 'pass_line_flat', 'amount': self.table_min}
            self.bets.append(bet)
            self.adjust_bankroll(-self.table_min)

    # Particularly difficult but reusable. Indexes over total legal bets and returns)
    def update_action_space(self, game_state=None):
        from simulator.game_engine import build_game_state
        # For tests
        if game_state is None:
            game_state = build_game_state(self)
        # Very crucial line that required
        atomic = self.action_gen.generate_atomic_actions(game_state)
        self.legal_actions = []
        n = len(atomic)
        max_r = min(self.max_combo_size, n)
        for r in range(1, max_r + 1):
            self.legal_actions.extend(itertools.combinations(atomic, r))

    # Ultimately the same for each
    def compute_expected_value(self, combo):
        ev = 0.0
        # Loop over all possible outcomes in self.outcome_probs
        for outcome, prob in self.outcome_probs.items():
            # Sum up the payout from every atomic bet in the combo
            payout = 0.0
            for bet_str in combo:
                payout += self.payout_table.get(((bet_str.lower(),), outcome), 0)
            ev += prob * payout
        return ev

    # Key differentiator
    def choose_action(self):
        if not self.legal_actions:
            return None
        best_ev = -np.inf
        best_actions = []
        for action in self.legal_actions:
            ev = self.compute_expected_value(action)
            if ev > best_ev:
                best_ev, best_actions = ev, [action]
            elif ev == best_ev:
                best_actions.append(action)
        if len(best_actions) == 1:
            return best_actions[0]
        # Tie-break by minimal flat-bet exposure
        def expected_loss(action):
            return sum(self.table_min for b in action if b in self.flat_bets)
        return sorted(best_actions, key=expected_loss)[0]

    # Actually exeecute on action
    def place_bets(self, action):
        if not action:
            return
        for bet_str in action:
            if self.bankroll < self.table_min:
                break
            parts = bet_str.lower().split('_')
            if parts[0] == 'pass' and parts[1] == 'line':
                if len(parts) == 2:
                    bet = {'type': 'pass_line_flat', 'amount': self.table_min, 'multiplier': 1}
                else:
                    mult = int(parts[-1][0])
                    bet = {'type': 'pass_line_odds', 'amount': self.table_min, 'multiplier': mult}
            elif parts[0] == 'come' and parts[1] == 'flat':
                bet = {'type': 'come_flat', 'amount': self.table_min}
            elif parts[0] == 'come' and parts[1] == 'odds':
                mult = int(parts[2][0])
                pt = int(parts[3])
                bet = {'type': 'come_odds', 'amount': self.table_min, 'multiplier': mult, 'point': pt}
            else:
                bet = {'type': bet_str.lower(), 'amount': self.table_min}
            self.bets.append(bet)
            self.adjust_bankroll(-self.table_min)

    # Resolution
    def resolve_game(self, outcome):
        remaining = []
        for bet in self.bets:
            key = ((bet['type'],), outcome)
            mult = self.payout_table.get(key, 0)
            if mult < 0:
                continue
            if mult > 0:
                self.adjust_bankroll(bet['amount'] * mult)
            remaining.append(bet)
        self.bets = remaining
