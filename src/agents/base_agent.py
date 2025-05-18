# src/agents/base_agent.py

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Abstract base class for all craps-playing agents.
    Defines the standard interface that the game engine expects.
    """

    def __init__(self, starting_bankroll=1000, table_minimum=10, walkaway_threshold=None):
        self.initial_bankroll = starting_bankroll
        self.bankroll = starting_bankroll
        self.table_min = table_minimum
        self.walkaway_threshold = walkaway_threshold

        self.bets = []                 # Active bets (to be resolved)
        self.legal_actions = []        # List of composite actions (dicts from JSON)
        self.point_established = False
        self.active_come_points = []   # e.g., [5, 9]

    def start_new_game(self):
        """
        Reset state for a new game. Clear bets and point status.
        """
        self.bets.clear()
        self.legal_actions.clear()
        self.point_established = False
        self.active_come_points = []

    @abstractmethod
    def place_pass_line_bet(self):
        """
        Mandatory first action of any game. All agents must implement this.
        """
        pass

    @abstractmethod
    def update_action_space(self):
        """
        Called between rolls during the point round.
        Update self.legal_actions based on game state.
        """
        pass

    @abstractmethod
    def choose_action(self):
        """
        Return the agent's chosen action ID from self.legal_actions.
        """
        pass

    @abstractmethod
    def place_bets(self, action_id):
        """
        Process the agent's chosen action (via its ID) and commit bets.
        Deduct from bankroll and update self.bets.
        """
        pass

    @abstractmethod
    def resolve_game(self, outcome):
        """
        Resolve all active bets based on the game outcome.
        Update bankroll and internal state.
        """
        pass

    def can_continue(self):
        """
        Returns True if the agent is allowed to keep betting:
        - Has enough bankroll for a base bet
        - Has not exceeded walkaway threshold
        """
        return (
            self.bankroll >= self.table_min and
            (self.walkaway_threshold is None or self.bankroll < self.walkaway_threshold)
        )
