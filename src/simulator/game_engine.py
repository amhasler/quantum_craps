# src/simulator/game_engine.py

import re

def roll_dice(rng):
    # Simulate the roll of two fair dice
    return rng.integers(1, 7) + rng.integers(1, 7)

# --- Helpers to parse new-style bet labels ---

def parse_pass_line_odds_bet(bet_type: str):
    match = re.match(r'pass_line_odds_\$(\d+)', bet_type)
    return int(match.group(1)) if match else None

def parse_come_odds_bet(bet_type: str):
    match = re.match(r'come_odds_\$(\d+)_([4-6]|[8-9]|10)', bet_type)
    if match:
        amount = int(match.group(1))
        point = int(match.group(2))
        return amount, point
    return None, None

# --- Game State Builder for Agent ---

def build_game_state(agent):
    game_state = {
        'pass_line_odds_levels': sorted([
            parse_pass_line_odds_bet(bet['type'])
            for bet in agent.bets
            if bet['type'].startswith('pass_line_odds_')
        ]),
        'come_flat_active': any(
            bet['type'] == 'come_flat' for bet in agent.bets
        ),
        'active_come_points': sorted(agent.active_come_points),
        'come_odds_levels': {},
        'current_point': agent.current_point,
        'table_min': agent.table_min
    }

    for point in game_state['active_come_points']:
        levels = []
        for bet in agent.bets:
            if bet['type'].startswith('come_odds_'):
                amount, bet_point = parse_come_odds_bet(bet['type'])
                if bet_point == point:
                    levels.append(amount)
        game_state['come_odds_levels'][str(point)] = sorted(set(levels)) if levels else []

    return game_state

# --- Main Game Function ---

def play_game(agent, rng):
    agent.start_new_game()
    agent.point_established = False
    agent.current_point = None
    agent.active_come_points = set()
    agent.place_pass_line_bet()

    game_over = False

    # --- Come-Out Round ---
    while not agent.point_established and not game_over:
        roll = roll_dice(rng)
        if roll in (7, 11):
            agent.bankroll += agent.table_min
        elif roll in (2, 3, 12):
            game_over = True
        else:
            agent.point_established = True
            agent.current_point = roll

    # --- Point Round ---
    while not game_over:
        if not agent.can_continue():
            break

        agent.update_action_space()
        action = agent.choose_action()
        if action:
            agent.place_bets(action)

        roll = roll_dice(rng)

        if roll == 7:
            agent.resolve_game('seven_out')
            break

        # Pass Line win
        if roll == agent.current_point:
            agent.bankroll += agent.table_min
            for bet in agent.bets:
                if bet['type'].startswith('pass_line_odds_'):
                    amt = parse_pass_line_odds_bet(bet['type'])
                    if amt:
                        agent.bankroll += agent.lookup_payout(('pass_line_odds_$' + str(amt),), f'win_{roll}')

        # Come bet wins
        if roll in agent.active_come_points:
            for bet in agent.bets:
                if bet['type'] == 'come_flat' and bet.get('point') == roll:
                    agent.bankroll += bet['amount']
                elif bet['type'].startswith('come_odds_'):
                    amt, pt = parse_come_odds_bet(bet['type'])
                    if pt == roll:
                        key = ('come_odds_$' + str(amt) + '_' + str(pt),)
                        agent.bankroll += agent.lookup_payout(key, f'win_{roll}')

        # Come bet progression (bet becomes come point)
        for bet in agent.bets[:]:
            if bet['type'] == 'come_flat' and 'point' not in bet:
                if roll in (7, 11):
                    agent.bankroll += bet['amount']
                    agent.bets.remove(bet)
                elif roll in (2, 3, 12):
                    agent.bets.remove(bet)
                else:
                    bet['point'] = roll
                    agent.active_come_points.add(roll)

    return agent.bankroll
