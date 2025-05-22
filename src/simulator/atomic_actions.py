# src/simulator/atomic_actions.py

from typing import List, Dict, Any

POINT_DENOMINATORS = {
    '4': 1,
    '5': 2,
    '6': 5,
    '8': 5,
    '9': 2,
    '10': 1,
}

MAX_MULTIPLIER = 3

def legal_odds_bet_amounts(point: str, max_mult: int = MAX_MULTIPLIER) -> List[int]:
    denom = POINT_DENOMINATORS.get(str(point))
    if denom is None:
        return []
    return [denom * m for m in range(1, max_mult + 1)]


class AtomicActionGenerator:
    def __init__(self):
        self.come_flat_bet = 'come_flat'
        self.latest_atomic_actions = []

    def generate_atomic_actions(self, game_state):
        atomic_actions = []

        point = game_state.get('current_point')
        if point is None:
            return atomic_actions  # No odds or come bets allowed during come-out roll

        # --- Pass Line Odds ---
        existing_plo_levels = game_state.get('pass_line_odds_levels', [])
        available_plo = legal_odds_bet_amounts(point)
        for amt in available_plo:
            if amt not in existing_plo_levels:
                atomic_actions.append(f'pass_line_odds_${amt}')

        # --- Come Flat Bet ---
        # Allow placement of come bet if one is not already pending
        if not game_state.get('come_flat_active', False):
            atomic_actions.append(self.come_flat_bet)

        # --- Come Odds Bets ---
        active_points = game_state.get('active_come_points', [])
        come_odds_levels = game_state.get('come_odds_levels', {})  # {pt: [amt1, amt2, ...]}

        for pt in active_points:
            pt_str = str(pt)
            available_amt = legal_odds_bet_amounts(pt_str)
            used = come_odds_levels.get(pt_str, [])
            for amt in available_amt:
                if amt not in used:
                    label = f'come_odds_${amt}_{pt_str}'
                    atomic_actions.append(label)

        self.latest_atomic_actions = atomic_actions

        return atomic_actions
