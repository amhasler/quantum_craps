import random
import time

# Use current time in nanoseconds as seed
seed_value = time.time_ns()
random.seed(seed_value)

starting_bankroll = 1000 # Very variable. If it's higher table minimum this should be higher to avoid running out of money
min_bet = 10 # This should be a variable. What if it's a $25 minimum bet table (very common)
play_odds = True  # Set to false to disable odds betting on pass bets.
play_come_odds = True # Set to false to disable odds betting on come bets. Probably not going to be variable, but just in case.

def roll():
    # Roll and sum six sided dice
    return random.randint(1, 6) + random.randint(1, 6)

def format_currency(amount):
    # Easy formatting for dollar amount, only necessary for early stages where I want
    # to display results
    if amount == int(amount):
        return f"${int(amount)}"
    else:
        return f"${amount:.2f}"

def decide_come_bet_amount(bankroll):
    # Come bet amount. Pass line bets and come line bets are generally the same.
    # Although it's possible to bet more, it's not advised given the odds.
    if bankroll >= min_bet:
        return min_bet
    return 0

def get_max_odds(point, flat_bet):
    # Basic odds bets, based on what's available for the pass line or come line point values
    if point in (4, 10):
        return 3 * flat_bet
    elif point in (5, 9):
        return 4 * flat_bet
    elif point in (6, 8):
        return 5 * flat_bet
    else:
        return 0

def decide_odds_bet_amount(bankroll, max_odds):
    # This is a place holder. This will vary based on strategy used.
    return min(bankroll, max_odds)

def resolve_odds_bet(point, odds_bet, bankroll):
    # This decides the payout based on the odds bet. See max odds logic above.
    if point in (4, 10):
        payout = odds_bet * 2
    elif point in (5, 9):
        payout = odds_bet * 1.5
    elif point in (6, 8):
        payout = odds_bet * 1.2
    else:
        payout = 0
    bankroll += odds_bet + payout
    # Print statement here for debugging/checking logic. I'll comment out once I'm
    # running many games.
    print(f"Odds bet wins {format_currency(payout)}.")
    return bankroll

def resolve_come_bets(come_bets, roll_result, bankroll, come_odds_bets):
    updated_come_bets = []
    unresolved_wins = 0
    unresolved_losses = 0

    # This decides the payout based on the bets on the come line, and whether the
    # come point was hit.
    updated_come_bets = []
    established_points = []

    for cp, bet in come_bets:
        # Come bets is a list of tuples (come point (cp) and
        # bet is the bet placed (usually table minimum)

        # Come bet has come-out roll when placed, just like on pass line.

        # If a come bet/s already exist/s
        if cp is not None:
            # Win logic, same as pass line logic...is come point hit before 7?
            if roll_result == cp:
                bankroll += bet
                print(f"Come point {cp} hit. Come bet wins {format_currency(bet)}.")
                # Resolve odds bet if exists
                if cp in come_odds_bets:
                    odds_bet = come_odds_bets[cp]
                    bankroll = resolve_odds_bet(cp, odds_bet, bankroll)
                    del come_odds_bets[cp]
            # If 7 hit before point hit (same as pass logic)
            elif roll_result == 7:
                print(f"Come bet on point {cp} lost.")
                # Lose odds bet if exists
                if cp in come_odds_bets:
                    print(f"Odds bet on point {cp} lost.")
                    del come_odds_bets[cp]
            else:
                # Do nothing
                break
            #   updated_come_bets.append((cp, bet))
        # Come-out roll on come bet. Same logic as pass line bet.
        elif cp is None:
            if roll_result in (7, 11):
                bankroll += bet
                unresolved_wins += 1
            elif roll_result in (2, 3, 12):
                unresolved_losses += 1
            else:
                updated_come_bets.append((roll_result, bet))
                established_points.append(roll_result)

    if established_points:
        unique_points = sorted(set(established_points))
        if len(unique_points) == 1:
            print(f"Come point established at {unique_points[0]}.")
        else:
            points_str = ', '.join(str(p) for p in unique_points)
            print(f"Come points established at: {points_str}.")
    if unresolved_wins > 0:
        print(f"{unresolved_wins} come bet(s) win on come-out number {roll_result}.")
    if unresolved_losses > 0:
        print(f"{unresolved_losses} come bet(s) lose on come-out number {roll_result}.")

    return updated_come_bets, bankroll

def display_active_come_points(come_bets):
    # This whole function is here just to verify the code is working.
    # will be unused once I'm sure about the logic and
    # and written the different strategies. Then I'll comment it out when
    # I'm running many many games. I borrowed this because it's not core
    # program logic.

    active_come_points = sorted(set(cp for cp, _ in come_bets if cp is not None))
    if active_come_points:
        points_str = ', '.join(str(cp) for cp in active_come_points)
        print(f"Come line points are: {points_str}")

def display_active_odds_bets(*odds_dicts):
    # Same notes as above, but for odds bets. Odds bets are on different points,
    # So slightly more complicated formatting.

    for label, odds_bets in odds_dicts:
        if odds_bets:
            print(f"{label} odds bets:")
            for point in sorted(odds_bets):
                bet = odds_bets[point]
                print(f"\tPoint {point}: {format_currency(bet)}")
            print()

# Core game algorithm
def play(starting_bankroll):
    bankroll = starting_bankroll
    come_bets = []
    odds_bets = {}
    come_odds_bets = {}
    print("New game starting.")

    while True:
        # Place pass line bet if bankroll allows. This check is more relevant when I'm playing many games.
        if bankroll < min_bet:
            print("Insufficient funds to place a pass line bet.")
            print(f"Final bankroll: {format_currency(bankroll)}")
            return bankroll
        pass_line_bet = min_bet
        bankroll -= pass_line_bet

        print(f"\nPlaced pass line bet of {format_currency(pass_line_bet)}.")

        # Come-out round logic
        come_out_roll = roll()
        print(f"\nCome-out roll: {come_out_roll}")
        if come_out_roll in (7, 11):
            bankroll += pass_line_bet
            print("\nWin on come-out roll. Pass line bet wins.")
            continue  # Shooter continues with a new come-out roll
        elif come_out_roll in (2, 3, 12):
            print("Lose on come-out roll. Pass line bet lost.")
            print(f"\nFinal bankroll: {format_currency(bankroll)}")
            return bankroll
        else:
            point = come_out_roll
            print(f"Point established: {point}\n")
            # Place odds bet on pass line if enabled
            # Max odds you can play depends on pass line point value
            max_odds = get_max_odds(point, pass_line_bet)
            # This bet will vary based on strategy. Defaults here to playing the max odds for demonstration purposes.
            odds_bet = decide_odds_bet_amount(bankroll, max_odds)
            if odds_bet > 0:
                bankroll -= odds_bet  # Substract odds bet from payroll
                odds_bets[point] = odds_bet  # Add odds bet as point and bet to list as tuple
                print(f"Placed pass line odds bet.")

        # Point round logic
        while True:
            # Optionally, place a new come bet (only during point phase). This places a come bet every roll until seven out.
            new_come_bet = decide_come_bet_amount(bankroll) # This defaults to true and min_bet
            if new_come_bet > 0:
                bankroll -= new_come_bet # Subtract come bet from payroll. Amount variable, defaults to min_bet.
                come_bets.append((None, new_come_bet)) # Add to list of come bets (The point set later)
                print(f"Placed new come bet.")

            # Place odds bets on come points if enabled
            if play_come_odds:
                for cp, bet in come_bets:
                    if cp is not None and cp not in come_odds_bets: # Place odds bet on come point if set
                        max_odds = get_max_odds(cp, bet)
                        odds_bet = decide_odds_bet_amount(bankroll, max_odds)
                        if odds_bet > 0:
                            bankroll -= odds_bet # Deduct odds bet from bankroll
                            come_odds_bets[cp] = odds_bet # Add odds bet to list of odds bets
                            print(f"Placed odds bet on come point {cp}.")

            # Point round roll after pass line odds bet and come line bet
            roll_result = roll()
            print(f"\nRoll: {roll_result}")

            # Check for Pass line bet resolution
            if roll_result == point: # Win
                bankroll += pass_line_bet
                print(f"Point hit. Pass line bet wins.")
                # Resolve odds bet on Pass line
                if point in odds_bets: # If an odds bet on pass line bet placed, resolve payout
                    bankroll = resolve_odds_bet(point, odds_bets[point], bankroll)
                    del odds_bets[point]
                print(f"New bankroll: {format_currency(bankroll)}\n")
                break  # Exit to start a new come-out roll
            elif roll_result == 7: # Lose
                print("Seven out.\n")
                # Lose odds bet on Pass line
                if point in odds_bets:
                    print(f"Odds bet on pass line bet lost.")
                    del odds_bets[point]
                # Lose all other come bet odds bets
                for cp, bet in come_bets:
                    if cp is not None:
                        print(f"Come bet on point {cp} lost.")
                        if cp in come_odds_bets:
                            print(f"Odds bet on point {cp} lost.")
                            del come_odds_bets[cp]

                come_bets.clear()  # Clear all come bets
                print(f"\nFinal bankroll: {format_currency(bankroll)}")
                return bankroll

            # Check all come bets and resolve based on roll above
            come_bets, bankroll = resolve_come_bets(come_bets, roll_result, bankroll, come_odds_bets)

            # When display active, remind of active come bets
            display_active_come_points(come_bets)

            # When display active, display all odds bets and amounts
            display_active_odds_bets(
                ("Pass line", odds_bets),
                ("Come", come_odds_bets)
            )

        print("New come-out roll")


play(starting_bankroll)

