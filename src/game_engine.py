import random
import time

# Use current time in nanoseconds as seed
seed_value = time.time_ns()
random.seed(seed_value)

starting_bankroll = 1000
min_bet = 10
max_bet = 1000
max_odds = 0
strategy = "classical"

def roll():
    # PRNG for dice roll
    return random.randint(1, 6) + random.randint(1, 6)

def point_round(point, bankroll, pass_line_bet):
    # Point round of game
    # This is where you can place pass line bet (odds)
    # 3x pass line bet when the point is 4 or 10
    # 4x pass line bet when the point is 5 or 9
    # 5x pass line bet when the point is 6 or 8

    # This is where you can set come line bet, acts as new come out roll
    # If come bet placed, 7 or 11 you win, 2, 3, 12 you lose
    # Same max/min
    while True:
        roll_result = roll()
        print(f"Rolled: {roll_result}")
        if roll_result == point:
            # Payout pays pass line bet
            bankroll = bankroll + pass_line_bet
            return True, bankroll
        elif roll_result == 7:
            # Game over "seven out". Pass line bet lost. Come line pays.
            print("Seven out. Lost.")
            return False, bankroll
        else:
            print("Neither point or seven. Reroll.")
            # Reroll
            continue

def play(starting_bankroll):
    pass_line_bet = min_bet # This should vary with params (house rules)
    # This is the minimum requirement to play
    bankroll = starting_bankroll - pass_line_bet # Bet can vary with params (choice)
    while True:
        come_out_roll = roll()
        print(f"Come-out roll: {come_out_roll}")
        if come_out_roll in (7, 11):
            # Update bankroll 1:1 pass line bet
            bankroll = bankroll + min_bet
            print("Win on come-out roll. Pay out pass line bet.")
            continue  # Reroll
        elif come_out_roll in (2, 3, 12):
            # Bankroll stays the same because first bet lost
            # Craps. Game over
            print("Lose on come-out roll.")
            print(f"Game over. New bankroll: {bankroll}\n")
            break  # End the game
        else:
            # Bankroll carries over to next round
            print(f"Point established: {come_out_roll}")
            result, value = point_round(come_out_roll, bankroll, pass_line_bet)
            if result:
                print("Win. Starting new round.\n")
                continue  # Start a new come-out roll
            else:
                print(f"Game over. New bankroll: {bankroll}\n")
                break  # End the game


# Start the game
play(starting_bankroll)
