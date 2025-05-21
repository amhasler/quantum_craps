# THANK YOU MATT WEISS!!
from qbism import sic_povm

def load_sic(d):
    if 2 <= d <= 10:
        return sic_povm(d)
    else:
        raise NotImplementedError(f"SIC-POVMs for d={d} not supported.")
