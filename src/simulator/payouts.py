# src/simulator/payouts.py

PAYOUT_TABLE = {
    # Pass Line Flat Bet
    (('pass_line_flat',), 'win'): 1.0,     # 1:1 payout
    (('pass_line_flat',), 'lose'): -1.0,

    # Pass Line Odds Bets (multiples)
    (('pass_line_odds_1x',), 'win_4'): 2.0,  # 2:1 payout on point 4
    (('pass_line_odds_2x',), 'win_4'): 4.0,
    (('pass_line_odds_3x',), 'win_4'): 6.0,

    (('pass_line_odds_1x',), 'win_10'): 2.0,
    (('pass_line_odds_2x',), 'win_10'): 4.0,
    (('pass_line_odds_3x',), 'win_10'): 6.0,

    (('pass_line_odds_1x',), 'win_5'): 1.5,  # 3:2 payout on 5
    (('pass_line_odds_2x',), 'win_5'): 3.0,
    (('pass_line_odds_3x',), 'win_5'): 4.5,

    (('pass_line_odds_1x',), 'win_9'): 1.5,
    (('pass_line_odds_2x',), 'win_9'): 3.0,
    (('pass_line_odds_3x',), 'win_9'): 4.5,

    (('pass_line_odds_1x',), 'win_6'): 1.2,  # 6:5 payout on 6
    (('pass_line_odds_2x',), 'win_6'): 2.4,
    (('pass_line_odds_3x',), 'win_6'): 3.6,

    (('pass_line_odds_1x',), 'win_8'): 1.2,
    (('pass_line_odds_2x',), 'win_8'): 2.4,
    (('pass_line_odds_3x',), 'win_8'): 3.6,

    # Come Flat Bet
    (('come_flat',), 'win'): 1.0,
    (('come_flat',), 'lose'): -1.0,

    # Come Odds Bets (multiples)
    (('come_odds_1x_4',), 'win_4'): 2.0,
    (('come_odds_2x_4',), 'win_4'): 4.0,
    (('come_odds_3x_4',), 'win_4'): 6.0,

    (('come_odds_1x_10',), 'win_10'): 2.0,
    (('come_odds_2x_10',), 'win_10'): 4.0,
    (('come_odds_3x_10',), 'win_10'): 6.0,

    (('come_odds_1x_5',), 'win_5'): 1.5,
    (('come_odds_2x_5',), 'win_5'): 3.0,
    (('come_odds_3x_5',), 'win_5'): 4.5,

    (('come_odds_1x_9',), 'win_9'): 1.5,
    (('come_odds_2x_9',), 'win_9'): 3.0,
    (('come_odds_3x_9',), 'win_9'): 4.5,

    (('come_odds_1x_6',), 'win_6'): 1.2,
    (('come_odds_2x_6',), 'win_6'): 2.4,
    (('come_odds_3x_6',), 'win_6'): 3.6,

    (('come_odds_1x_8',), 'win_8'): 1.2,
    (('come_odds_2x_8',), 'win_8'): 2.4,
    (('come_odds_3x_8',), 'win_8'): 3.6,
}

# Add losing payouts for all bets (lose = lose bet amount)
for bet_key in list(PAYOUT_TABLE.keys()):
    bet_type = bet_key[0][0]
    outcome = bet_key[1]
    if 'win' in outcome:
        lose_outcome = 'lose'
        if 'come_odds' in bet_type or 'pass_line_odds' in bet_type:
            PAYOUT_TABLE[(bet_key[0], lose_outcome)] = -1.0
        elif 'flat' in bet_type:
            PAYOUT_TABLE[(bet_key[0], lose_outcome)] = -1.0

# Seven out loses all point and come bets
PAYOUT_TABLE[(('pass_line_flat',), 'seven_out')] = -1.0
PAYOUT_TABLE[(('come_flat',), 'seven_out')] = -1.0
for multiplier in ['1x', '2x', '3x']:
    for point in ['4', '5', '6', '8', '9', '10']:
        PAYOUT_TABLE[(('pass_line_odds_' + multiplier,), 'seven_out')] = -1.0
        PAYOUT_TABLE[(('come_odds_' + multiplier + '_' + point,), 'seven_out')] = -1.0
