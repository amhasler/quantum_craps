class Simulator:

    # Load the run params
    def __init__(self, agent, starting_bankroll, n_games):
        self.agent = agent
        self.starting_bankroll = starting_bankroll
        self.n_games = n_games
        self.bankroll_history = []

    # Run many games
    def run(self):

        bankroll = self.starting_bankroll

        for _ in range(self.n_games):
            bankroll = self.agent.play_round(bankroll)
            self.bankroll_history.append(bankroll)

        return self.bankroll_history
