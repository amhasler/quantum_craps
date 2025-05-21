# Base Agent....DRYing up by putting logic for each agent into basic agent file
# Sets  values that the simulator expects in the init file.
# Sets shared functions (e.g. start new game
# biggest interesting innovation here was the "abstract method" and ABC

from abc import ABC, abstractmethod

# Declaes that every instance of this MUST have these methods to be valid
# ABC = abstract base class
class BaseAgent(ABC):

    def __init__(self, starting_bankroll=1000, table_minimum=10, walkaway_threshold=None, **kwargs):
        self.initial_bankroll = starting_bankroll
        self.bankroll = starting_bankroll
        self.table_min = table_minimum
        self.walkaway_threshold = walkaway_threshold

        self.bets = []
        self.legal_actions = []
        self.point_established = False
        self.active_come_points = set()
        self.current_point = None

    def start_new_game(self):
        # Ensures that table clear of bets and point set to none
        self.bets.clear()
        self.legal_actions.clear()
        self.point_established = False
        self.active_come_points.clear()
        self.current_point = None

    # Must have place pass line bet to play
    @abstractmethod
    def place_pass_line_bet(self):

        pass

    # Make decision possible
    @abstractmethod
    def update_action_space(self):

        pass

    # Returns decision
    @abstractmethod
    def choose_action(self):

        pass

    # Support placing bets
    @abstractmethod
    def place_bets(self, action):

        pass

    # Requires all bets and bankroll resolved
    @abstractmethod
    def resolve_game(self, outcome):

        pass

    def can_continue(self):
        # Check. Stops playing if zero (addedd because of long line of zeros when
        # bankroll ran out before the total of games from config
        return (
            self.bankroll >= self.table_min #and
            # Didn't use this this time, but
            # keeping here if I want to extend
            # (self.walkaway_threshold is None or self.bankroll < self.walkaway_threshold)
        )

    # Optional helper method to adjust bankroll safely
    def adjust_bankroll(self, amount):
        # Edge case check (suggested)
        self.bankroll += amount
