# src/simulator/payouts.py

PAYOUT_TABLE = {
    # Flat bets
    (('pass_line_flat',), 'win'): 1.0,
    (('pass_line_flat',), 'lose'): -1.0,
    (('come_flat',), 'win'): 1.0,
    (('come_flat',), 'lose'): -1.0,
    (('pass_line_flat',), 'seven_out'): -1.0,
    (('come_flat',), 'seven_out'): -1.0,
}

# Odds payout ratios: point → (numerator, denominator)
POINTS = {
    '4': (2, 1),
    '5': (3, 2),
    '6': (6, 5),
    '8': (6, 5),
    '9': (3, 2),
    '10': (2, 1),
}

MAX_MULTIPLIER = 3

for point, (num, denom) in POINTS.items():
    for m in range(1, MAX_MULTIPLIER + 1):
        bet_amount = m * denom
        payout = m * num

        # Create labels based on dollar amount
        label = f'${bet_amount}'

        # Keys
        key_pass_win = (('pass_line_odds_' + label,), f'win_{point}')
        key_come_win = (('come_odds_' + label + '_' + point,), f'win_{point}')
        key_pass_lose = (('pass_line_odds_' + label,), 'lose')
        key_come_lose = (('come_odds_' + label + '_' + point,), 'lose')
        key_pass_seven = (('pass_line_odds_' + label,), 'seven_out')
        key_come_seven = (('come_odds_' + label + '_' + point,), 'seven_out')

        # Wins
        PAYOUT_TABLE[key_pass_win] = payout
        PAYOUT_TABLE[key_come_win] = payout

        # Losses
        PAYOUT_TABLE[key_pass_lose] = -bet_amount
        PAYOUT_TABLE[key_come_lose] = -bet_amount
        PAYOUT_TABLE[key_pass_seven] = -bet_amount
        PAYOUT_TABLE[key_come_seven] = -bet_amount
