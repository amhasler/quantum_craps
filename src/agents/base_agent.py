# src/agents/base_agent.py

from abc import ABC, abstractmethod
import re

class BaseAgent(ABC):
    def __init__(
        self,
        starting_bankroll=1000,
        table_minimum=10,
        walkaway_threshold=None,
        payout_table=None,
        **kwargs
    ):
        self.initial_bankroll = starting_bankroll
        self.bankroll = starting_bankroll
        self.table_min = table_minimum
        self.walkaway_threshold = walkaway_threshold
        self.payout_table = payout_table or {}

        self.bets = []
        self.legal_actions = []
        self.point_established = False
        self.active_come_points = set()
        self.current_point = None

    def adjust_bankroll(self, delta):
        self.bankroll += delta

    def start_new_game(self):
        self.bankroll = self.initial_bankroll
        self.bets.clear()
        self.legal_actions.clear()
        self.point_established = False
        self.active_come_points = set()
        self.current_point = None

    def can_continue(self):
        return (
            self.bankroll >= self.table_min
            and (self.walkaway_threshold is None or self.bankroll < self.walkaway_threshold)
        )

    def lookup_payout(self, key, outcome):
        """
        Look up the payout for a given (bet_type, outcome) key from the payout table.
        """
        return self.payout_table.get((key, outcome), 0.0)

    def can_afford_action(self, action):
        total = sum(self._get_bet_amount(bet_str) for bet_str in action)
        return self.bankroll >= total

    @abstractmethod
    def place_pass_line_bet(self):
        pass

    @abstractmethod
    def update_action_space(self):
        pass

    @abstractmethod
    def choose_action(self):
        pass

    @abstractmethod
    def place_bets(self, action):
        pass

    def _get_bet_amount(self, bet_str):
        if bet_str.startswith('pass_line_odds_$'):
            match = re.match(r'pass_line_odds_\$(\d+)', bet_str)
            return int(match.group(1)) if match else self.table_min
        elif bet_str.startswith('come_odds_$'):
            match = re.match(r'come_odds_\$(\d+)_\d+', bet_str)
            return int(match.group(1)) if match else self.table_min
        else:
            return self.table_min

    def _extract_come_point(self, bet_str):
        import re
        match = re.match(r'come_odds_\$\d+_(\d+)', bet_str)
        return int(match.group(1)) if match else None
