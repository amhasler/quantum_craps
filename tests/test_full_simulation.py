# tests/test_full_simulation.py

import pytest
import numpy as np

from simulator.simulator import simulate_agent
from agents.random_agent import RandomAgent
from agents.classical_agent import ClassicalAgent
from agents.quantum_agent import QuantumAgent
from agents.qbist_agent import QBistAgent


@pytest.mark.parametrize("AgentClass", [
    RandomAgent,
    ClassicalAgent,
    QuantumAgent,
    QBistAgent,
])
def test_full_simulation(AgentClass):
    """
    Integration test running a full simulation of 100 games per agent,
    verifying no crashes and reasonable bankroll evolution.
    """
    rng = np.random.default_rng(seed=12345)
    starting_bankroll = 1000
    table_minimum = 10
    num_games = 100

    agent = AgentClass(starting_bankroll=starting_bankroll, table_minimum=table_minimum)

    bankroll_history = simulate_agent(agent, rng, num_games=num_games)

    # Basic assertions:

    # Check simulation ran full or until bankruptcy
    assert len(bankroll_history) > 0, "Bankroll history is empty"

    # Bankroll should never be negative
    assert all(b >= 0 for b in bankroll_history), "Bankroll went negative"

    # Final bankroll should be a reasonable number (not NaN or infinite)
    final_bankroll = bankroll_history[-1]
    assert np.isfinite(final_bankroll), "Final bankroll is not finite"

    # At least one bet placed (bankroll should change if betting)
    assert bankroll_history[0] != bankroll_history[-1] or len(agent.bets) > 0

    # Agent should not have invalid bets after simulation
    for bet in agent.bets:
        assert bet['amount'] >= table_minimum, "Bet amount less than table minimum"
        assert isinstance(bet['type'], str), "Bet type is not string"
