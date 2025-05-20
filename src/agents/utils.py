def parse_atomic(bet_str: str):
    """
    Turn 'PL_Odds_2x_on_5' → ('pass_line_odds', None)
         'Come_Odds_3x_on_8' → ('come_odds', 8)
         'Pass_Line_Flat'     → ('pass_line_flat', None)
         'Come_Flat'          → ('come_flat', None)
    """
    parts = bet_str.lower().split('_')
    if parts[0] == 'pl' and parts[1] == 'odds':
        return 'pass_line_odds', None
    if parts[0] == 'come' and parts[1] == 'odds':
        return 'come_odds', int(parts[-1])
    if parts[0] == 'pass' and parts[1] == 'line':
        return 'pass_line_flat', None
    if parts[0] == 'come' and parts[1] == 'flat':
        return 'come_flat', None
    raise ValueError(f"Unknown bet_str: {bet_str}")
