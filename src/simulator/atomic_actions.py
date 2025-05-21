# src/simulator/atomic_actions.py

from typing import List, Dict, Any

class AtomicActionGenerator:
    # Init for action generator. NEED TO IMPROVE THIS, 1X, 2X...etc. isn't quite right
    def __init__(self):
        # Betting templates
        self.pass_line_odds_options = ['PL_Odds_1x', 'PL_Odds_2x', 'PL_Odds_3x']
        self.come_flat_bet = 'Come_Flat'
        self.come_odds_templates = ['Come_Odds_1x_on_{}', 'Come_Odds_2x_on_{}', 'Come_Odds_3x_on_{}']

    def generate_atomic_actions(self, game_state: Dict[str, Any]) -> List[str]:
        # Generate legal bets given some game state
        atomic_actions: List[str] = []

        # Only allow odds and come bets once a point has been established
        if game_state.get('current_point') is None:
            return atomic_actions

        # Pass Line Odds: offer the next unused multiplier
        plo_levels = game_state.get('pass_line_odds_levels', [])
        for template in self.pass_line_odds_options:
            # Extract multiplier integer from template ending '1x', '2x', etc.
            mult = int(template.split('_')[-1][:-1])
            if mult not in plo_levels:
                atomic_actions.append(template)
                break

        # Come Flat bet: if none active yet
        if not game_state.get('come_flat_active', False):
            atomic_actions.append(self.come_flat_bet)

        # Come Odds bets: for each established come point
        active_points = game_state.get('active_come_points', [])
        come_odds_levels = game_state.get('come_odds_levels', {})
        for pt in active_points:
            used_levels = come_odds_levels.get(pt, [])
            for template in self.come_odds_templates:
                mult = int(template.split('_')[2][0])  # e.g. '2x' -> 2
                if mult not in used_levels:
                    atomic_actions.append(template.format(pt))
                    break

        return atomic_actions
