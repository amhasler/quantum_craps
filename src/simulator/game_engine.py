# src/simulator/game_engine.py

"""
Core game engine for simulating a single game of craps.
Includes dice rolls, bet resolution, and integration with agents.
"""

def roll_dice(rng):
    """Roll two six-sided dice using the provided RNG and return the sum."""
    return rng.integers(1, 7) + rng.integers(1, 7)


def payout_pass_line_odds(amount, point):
    """Compute Pass Line odds payout for a given amount and point."""
    odds_table = {4: 2, 10: 2, 5: 1.5, 9: 1.5, 6: 1.2, 8: 1.2}
    return amount * odds_table.get(point, 0)


def payout_come_odds(amount, point):
    """Compute Come odds payout for a given amount and point."""
    odds_table = {4: 2, 10: 2, 5: 1.5, 9: 1.5, 6: 1.2, 8: 1.2}
    return amount * odds_table.get(point, 0)


def build_game_state(agent):
    """
    Build a snapshot of the current game state for agent decision-making.
    Returns a dict consumed by agents' update_action_space().
    """
    game_state = {
        'pass_line_odds_levels': sorted(
            bet['multiplier'] for bet in agent.bets
            if bet['type'] == 'pass_line_odds'
        ),
        'come_flat_active': any(bet['type'] == 'come_flat' for bet in agent.bets),
        'active_come_points': sorted(agent.active_come_points),
        'come_odds_levels': {},
        'current_point': agent.current_point,
        'table_min': agent.table_min
    }
    # Populate come odds levels for each active point
    for point in game_state['active_come_points']:
        multipliers = [
            bet['multiplier'] for bet in agent.bets
            if bet['type'] == 'come_odds' and bet.get('point') == point
        ]
        game_state['come_odds_levels'][point] = sorted(set(multipliers)) if multipliers else []

    return game_state


def play_game(agent, rng):
    """
    Simulate one full craps game for the given agent.
    Returns the agent's bankroll after the game.

    Args:
        agent: Instance of BaseAgent or its subclass.
        rng:   numpy.random.Generator for reproducible rolls.
    """
    # --- Initialize game ---
    agent.start_new_game()
    agent.point_established   = False
    agent.current_point       = None
    agent.active_come_points  = set()

    # Place the mandatory Pass Line flat bet
    agent.place_pass_line_bet()

    # --- Come-Out Phase ---
    game_over = False
    while not agent.point_established and not game_over:
        roll = roll_dice(rng)
        if roll in (7, 11):
            # Pass Line wins flat bet 1:1
            agent.bankroll += agent.table_min
            # Bet remains active
        elif roll in (2, 3, 12):
            # Pass Line loses
            game_over = True
        else:
            # Point is established
            agent.point_established = True
            agent.current_point     = roll

    # --- Point Round ---
    while not game_over:
        # Check if agent can continue betting
        if not agent.can_continue():
            break

        # Provide state to agent and let it update its action space
        state = build_game_state(agent)
        agent.update_action_space()

        # Agent selects and places bets (if any)
        action = agent.choose_action()
        if action:
            agent.place_bets(action)

        # Roll dice for this round
        roll = roll_dice(rng)

        # Seven out: lose all point and come bets
        if roll == 7:
            agent.resolve_game('seven_out')
            break

        # Pass Line point hit: pays flat + odds
        if roll == agent.current_point:
            agent.bankroll += agent.table_min
            for bet in agent.bets:
                if bet['type'] == 'pass_line_odds':
                    agent.bankroll += payout_pass_line_odds(
                        bet['amount'], agent.current_point
                    )

        # Come point hits
        if roll in agent.active_come_points:
            for bet in agent.bets:
                if bet['type'] == 'come_flat' and bet.get('point') == roll:
                    agent.bankroll += bet['amount']
                elif bet['type'] == 'come_odds' and bet.get('point') == roll:
                    agent.bankroll += payout_come_odds(
                        bet['amount'], bet['point']
                    )

        # Resolve and assign new come points for come flat bets
        for bet in agent.bets[:]:  # iterate over a copy
            if bet['type'] == 'come_flat' and 'point' not in bet:
                if roll in (7, 11):
                    # Instant win on come
                    agent.bankroll += bet['amount']
                    agent.bets.remove(bet)
                elif roll in (2, 3, 12):
                    # Come flat loses
                    agent.bets.remove(bet)
                else:
                    # Assign come point
                    bet['point'] = roll
                    agent.active_come_points.add(roll)

    return agent.bankroll
