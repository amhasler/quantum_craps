import random

def roll_dice(rng):
    return rng.integers(1, 7) + rng.integers(1, 7)

def payout_pass_line_odds(amount, point):
    odds_table = {4: 2, 10: 2, 5: 1.5, 9: 1.5, 6: 1.2, 8: 1.2}
    return amount * odds_table.get(point, 0)

def payout_come_odds(amount, point):
    odds_table = {4: 2, 10: 2, 5: 1.5, 9: 1.5, 6: 1.2, 8: 1.2}
    return amount * odds_table.get(point, 0)

def play_game(agent, rng):
    agent.start_new_game()
    agent.place_pass_line_bet()
    agent.point_established = False
    agent.current_point = None
    agent.active_come_points = set()
    game_over = False

    # --- Come-Out Phase ---
    while not agent.point_established and not game_over:
        roll = roll_dice(rng)

        if roll in [7, 11]:
            agent.bankroll += agent.table_min  # Pass Line pays
            continue  # Same Pass Line bet remains active

        elif roll in [2, 3, 12]:
            game_over = True  # Pass Line bet lost
            break

        elif roll in [4, 5, 6, 8, 9, 10]:
            agent.point_established = True
            agent.current_point = roll
            break

    # --- Point Round ---
    while not game_over:
        if not agent.can_continue():
            game_over = True
            break

        agent.update_action_space()
        action = agent.choose_action()
        if action is None:
            break

        if isinstance(action, dict):  # For quantum agent: full action object
            agent.place_bets(action)
        else:  # For classical agent: action_id string
            agent.place_bets(action)

        roll = roll_dice(rng)

        if roll == 7:
            agent.resolve_game("seven_out")
            game_over = True
            break

        # Resolve Pass Line point hit
        if roll == agent.current_point:
            agent.bankroll += agent.table_min  # Flat bet pays 1:1
            for bet in agent.bets:
                if bet["type"] == "pass_line_odds":
                    agent.bankroll += payout_pass_line_odds(bet["amount"], agent.current_point)

        # Resolve Come point hits
        if roll in agent.active_come_points:
            for bet in agent.bets:
                if bet["type"] == "come_flat" and bet.get("point") == roll:
                    agent.bankroll += bet["amount"]
                elif bet["type"] == "come_odds" and bet.get("point") == roll:
                    agent.bankroll += payout_come_odds(bet["amount"], bet["point"])

        # Assign Come points (mini come-out logic)
        for bet in agent.bets:
            if bet["type"] == "come_flat" and "point" not in bet:
                if roll in [7, 11]:
                    agent.bankroll += bet["amount"]  # 1:1 payout on instant win
                elif roll in [2, 3, 12]:
                    continue  # Bet is lost
                elif roll in [4, 5, 6, 8, 9, 10]:
                    bet["point"] = roll
                    agent.active_come_points.add(roll)

    return agent.bankroll
