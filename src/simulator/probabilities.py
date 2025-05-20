# src/simulator/probabilities.py

"""
Craps outcome probabilities for both come-out and point rounds.
These are used by all agents when computing expected value.
"""

# Come-out roll probabilities (out of 36 equally likely dice outcomes)
P2, P3, P4, P5, P6 = 1/36, 2/36, 3/36, 4/36, 5/36
P8, P9, P10, P11, P12 = 5/36, 4/36, 3/36, 2/36, 1/36
P7  = 6/36

# Come-out aggregated events
P_WIN_CO  = P7 + P11           # pass-line wins on 7 or 11
P_LOSE_CO = P2 + P3 + P12      # pass-line loses on 2, 3, 12

# Point-establishment probabilities
POINT_PROBS = {
    4:  P4,
    5:  P5,
    6:  P6,
    8:  P8,
    9:  P9,
    10: P10
}

# Conditional point-round probabilities
def _p_hit_before_7(pn):   return pn / (pn + P7)
def _p_seven_before_n(pn): return P7 / (pn + P7)

# Build the full outcome-prob dictionary
OUTCOME_PROBS = {
    # Come-out outcomes
    'win':     P_WIN_CO,
    'lose':    P_LOSE_CO,
    # Seven-out in point round (aggregate)
    'seven_out': 1 - (P_WIN_CO + P_LOSE_CO),
}

# Add “point_n” outcomes (establishing each point)
for n, pn in POINT_PROBS.items():
    OUTCOME_PROBS[f'point_{n}'] = pn

# Add win_n and seven_out for each point round
for n, pn in POINT_PROBS.items():
    OUTCOME_PROBS[f'win_{n}']       = pn * _p_hit_before_7(pn)
    OUTCOME_PROBS[f'seven_out_{n}'] = pn * _p_seven_before_n(pn)

# Flat‐bet probabilities (come-out)
PASS_LINE_PROBS = {
    'win':  P_WIN_CO,     # ≈0.4929
    'lose': P_LOSE_CO     # ≈0.5071
}

# Conditional “hit before 7” probabilities for odds bets
_ODDS_P = {
    n: POINT_PROBS[n] / (POINT_PROBS[n] + P7)
    for n in POINT_PROBS
}

def get_bet_probs(bet_type: str, point: int = None) -> dict:
    """
    Return {'win': p, 'lose': 1-p} for the given bet_type.
    - bet_type: 'pass_line_flat', 'come_flat', 'pass_line_odds', 'come_odds'
    - point: required for odds bets
    """
    if bet_type in ('pass_line_flat', 'come_flat'):
        return PASS_LINE_PROBS.copy()

    if bet_type in ('pass_line_odds', 'come_odds'):
        if point is None:
            raise ValueError("Odds bets require a point")
        p = _ODDS_P[point]
        return {'win': p, 'lose': 1 - p}

    # Fallback: 50/50
    return {'win': 0.5, 'lose': 0.5}