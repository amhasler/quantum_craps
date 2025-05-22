# THANK YOU MATT WEISS!!
from qbism import sic_povm

def load_sic(d: int):
    from qbism import sic_povm
    sic_qobjs = sic_povm(d)
    return [H.full() for H in sic_qobjs]  # converts Qobj to np.ndarray
