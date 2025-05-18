import os
import json
from .base_agent import BaseAgent

class ClassicalAgent(BaseAgent):
    """
    Classical rational agent that chooses from a predefined list of composite actions
    using expected value. Tie-breakers are resolved using effective house edge loss.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def place_pass_line_bet(self):
        if self.bankroll >= self.table_min:
            self.bankroll -= self.table_min
            self.bets.append({"type": "pass_line", "amount": self.table_min})

    def update_action_space(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'simulator', 'actions_classical.json')
        with open(path, 'r') as f:
            all_actions = json.load(f)

        legal = []
        for action in all_actions:
            total_cost = sum(bet["amount"] for bet in action["bets"])
            if self.bankroll < total_cost:
                continue

            legal_flag = True
            for bet in action["bets"]:
                if bet["type"] == "pass_line_odds":
                    if not self.point_established or any(b["type"] == "pass_line_odds" for b in self.bets):
                        legal_flag = False
                        break
                elif bet["type"] == "come_flat":
                    if not self.point_established:
                        legal_flag = False
                        break
                elif bet["type"] == "come_odds":
                    pt = bet["point"]
                    if pt not in self.active_come_points:
                        legal_flag = False
                        break
                    if any(b["type"] == "come_odds" and b.get("point") == pt for b in self.bets):
                        legal_flag = False
                        break

            if legal_flag:
                legal.append(action)

        self.legal_actions = legal

    def choose_action(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'simulator', 'actions_classical.json')
        with open(path, 'r') as f:
            all_actions = json.load(f)

        current_legal = [a for a in all_actions if a["id"] in [la["id"] for la in self.legal_actions]]

        def expected_value(action):
            ev = 0.0
            for bet in action["bets"]:
                amt = bet["amount"]
                if bet["type"] == "pass_line":
                    ev += amt * -0.0142
                elif bet["type"] == "come_flat":
                    ev += amt * -0.0101
                elif bet["type"] == "pass_line_odds":
                    ev += 0.0
                elif bet["type"] == "come_odds":
                    pt = bet.get("point")
                    if pt in {4, 10}:
                        ev += amt * (0.333 * 2.0 - 0.667)
                    elif pt in {5, 9}:
                        ev += amt * (0.4 * 1.5 - 0.6)
                    elif pt in {6, 8}:
                        ev += amt * (0.4545 * 1.2 - 0.5455)
            return ev

        def effective_loss(action):
            loss = 0.0
            edge_map = {1: 0.0085, 2: 0.0062, 3: 0.0046, 5: 0.0039, 10: 0.0027, 100: 0.0002}
            base = self.table_min

            for bet in action["bets"]:
                if bet["type"] in {"pass_line_odds", "come_odds"}:
                    odds_amt = bet["amount"]
                    total_wager = base + odds_amt
                    multiplier = round(odds_amt / base)
                    edge = edge_map.get(multiplier, 0.0046)
                    loss += total_wager * edge
            return loss

        evaluated = [(a, expected_value(a)) for a in current_legal]
        max_ev = max(ev for _, ev in evaluated)
        tied = [a for a, ev in evaluated if ev == max_ev]

        if len(tied) == 1:
            return tied[0]["id"]

        best_action = min(tied, key=effective_loss)
        return best_action["id"]

    def place_bets(self, action_id):
        path = os.path.join(os.path.dirname(__file__), '..', 'simulator', 'actions_classical.json')
        with open(path, 'r') as f:
            all_actions = json.load(f)

        action = next((a for a in all_actions if a["id"] == action_id), None)
        if action is None:
            return

        for bet in action["bets"]:
            self.bankroll -= bet["amount"]
            self.bets.append(bet)

    def resolve_game(self, outcome):
        winnings = 0
        for bet in self.bets:
            if bet["type"] == "pass_line":
                if outcome in ["pass_win", "point_win"]:
                    winnings += 2 * bet["amount"]
            elif bet["type"] == "pass_line_odds":
                if outcome == "point_win":
                    winnings += bet["amount"] + bet.get("odds_multiplier", 1) * self.table_min
            elif bet["type"] == "come_flat":
                if outcome in ["pass_win", "point_win"]:
                    winnings += 2 * bet["amount"]
            elif bet["type"] == "come_odds":
                if outcome == "point_win" and bet["point"] in self.active_come_points:
                    winnings += bet["amount"] + bet.get("odds_multiplier", 1) * self.table_min

        self.bankroll += winnings
        self.bets.clear()
