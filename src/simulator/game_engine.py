# Full game engine, with logic for playing removed
# rom original code to agent files

# references to agent come from actually call of game_engine
# and "play game" function

def roll_dice(rng):
    # Roll. Sum of two dice.
    return rng.integers(1, 7) + rng.integers(1, 7)


def payout_pass_line_odds(amount, point):
    # Repeated to keep payouts between come and pass straight.
    # Possible opportunity to DRY up.
    odds_table = {4: 2, 10: 2, 5: 1.5, 9: 1.5, 6: 1.2, 8: 1.2}
    return amount * odds_table.get(point, 0)


def payout_come_odds(amount, point):
    # Repeated to keep payouts between come and pass straight.
    # Possible opportunity to DRY up.
    odds_table = {4: 2, 10: 2, 5: 1.5, 9: 1.5, 6: 1.2, 8: 1.2}
    return amount * odds_table.get(point, 0)


def build_game_state(agent):
    # Helper function to extract current game state. Agent needs this
    # at each decision point to make a decision
    game_state = {
        # Construct all the bets on the table
        # This is looped over/updated every roll

        # Loop over all bets, gives the multiplier (1x, 2x, 3x)
        # when multiplier bet found
        'pass_line_odds_levels': sorted(
            bet['multiplier'] for bet in agent.bets
            if bet['type'] == 'pass_line_odds'
        ),
        # Returns come_flat bet
        'come_flat_active': any(bet['type'] == 'come_flat' for bet in agent.bets),
        # Returns come points on table
        'active_come_points': sorted(agent.active_come_points),
        # Use dictionary here to make more complex object.
        # Works like objects in javascript
        'come_odds_levels': {},
        # Pass line point
        'current_point': agent.current_point,
        # Table minimum from agent (set originally in config)
        'table_min': agent.table_min
    }
    # Loop over all bets, gives the multiplier (1x, 2x, 3x)
    # when multiplier bet found, sets the come bet
    # and multiplier to that point
    for point in game_state['active_come_points']:
        multipliers = [
            bet['multiplier'] for bet in agent.bets
            if bet['type'] == 'come_odds' and bet.get('point') == point
        ]
        game_state['come_odds_levels'][point] = sorted(set(multipliers)) if multipliers else []

    return game_state


def play_game(agent, rng):
    # --- Initialize game ---
    # All of these live in the agent now, was part of
    # refactor to make most game play logic happen there
    agent.start_new_game()
    agent.point_established   = False # Come out round, so nothing
    agent.current_point       = None # Come out round, so empty
    # Come out round, so empty.

    # Not strictly necessary but I was geting confused and
    # this helped with debugging
    agent.active_come_points  = set()

    # Place the mandatory Pass Line flat bet (at table minimum
    # Lives lin player
    agent.place_pass_line_bet()

    # --- Come-Out Round ---
    game_over = False
    # Basic algorithm for come out round
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
        agent.update_action_space()

        # Agent selects and places bets (if any)
        # This is the heart of the simulator and the hardest part to
        # execute on, because it's the core difference between the agents
        action = agent.choose_action()
        # If it results in an action, play the bets the action contains
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
            # This logic moved to helper (odds amount times point payout
            for bet in agent.bets:
                if bet['type'] == 'pass_line_odds':
                    agent.bankroll += payout_pass_line_odds(
                        bet['amount'], agent.current_point
                    )

        # Come point hits. Basic win logic for  come point payouts
        if roll in agent.active_come_points:
            for bet in agent.bets:
                if bet['type'] == 'come_flat' and bet.get('point') == roll:
                    agent.bankroll += bet['amount']
                elif bet['type'] == 'come_odds' and bet.get('point') == roll:
                    agent.bankroll += payout_come_odds(
                        bet['amount'], bet['point']
                    )

        # If there's a come line bet, set the come point
        for bet in agent.bets[:]:  # iterate over a copy
            if bet['type'] == 'come_flat' and 'point' not in bet:
                # Restart mini game. I think this could be dried up
                # because it just follows the same logic as the
                # main game.
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
