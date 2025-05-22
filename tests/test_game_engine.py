from simulator import game_engine

def test_build_game_state_structure():
    class DummyAgent:
        def __init__(self):
            self.bets = [
                {'type': 'pass_line_odds_$2', 'amount': 2},
                {'type': 'come_flat', 'amount': 10},
                {'type': 'come_odds_$10_6', 'amount': 10, 'point': 6}
            ]
            self.active_come_points = {6}
            self.current_point = 5
            self.table_min = 10

    agent = DummyAgent()
    state = game_engine.build_game_state(agent)

    assert isinstance(state, dict)
    assert 'pass_line_odds_levels' in state
    assert state['pass_line_odds_levels'] == [2]          # updated from [1]
    assert state['come_flat_active'] is True
    assert state['active_come_points'] == [6]
    assert state['come_odds_levels'] == {'6': [10]}       # updated from {6: [2]}
    assert state['current_point'] == 5
    assert state['table_min'] == 10
