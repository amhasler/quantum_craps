import json

with open('src/simulator/parameters.json') as f:
    params = json.load(f)

n_games = params['n_games']
starting_bankroll = params['starting_bankroll']
agent_type = params['agent']