import numpy as np

def get_legal_atomic_bets(agent, odds_multipliers=[1, 2, 3]):
    """
    Returns a list of legal atomic bets available to the agent at this point in the game.
    Filters based on game state: point status, existing bets, and come points.
    """
    legal_atomic_bets = []
    base = agent.table_min

    # Pass Line Odds: only one set allowed, and only after point is established
    if agent.point_established and not any(b["type"] == "pass_line_odds" for b in agent.bets):
        for mult in odds_multipliers:
            legal_atomic_bets.append({
                "type": "pass_line_odds",
                "amount": mult * base
            })

    # Come Flat Bet: legal only after point is established
    if agent.point_established:
        legal_atomic_bets.append({
            "type": "come_flat",
            "amount": base
        })

    # Come Odds: only allowed if a come point is active and not already backed
    for pt in agent.active_come_points:
        if not any(b["type"] == "come_odds" and b.get("point") == pt for b in agent.bets):
            for mult in odds_multipliers:
                legal_atomic_bets.append({
                    "type": "come_odds",
                    "amount": mult * base,
                    "point": pt
                })

    return legal_atomic_bets

def construct_density_matrix(d):
    """
    Returns a maximally mixed density matrix of dimension d.
    """
    return np.identity(d) / d

def construct_povm_element(indices, dim):
    """
    Constructs a diagonal POVM element as a matrix of shape (dim, dim).
    Each index corresponds to a +1 on the diagonal.
    """
    E = np.zeros((dim, dim))
    for i in indices:
        E[i, i] = 1.0
    return E
