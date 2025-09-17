
from engine.baseplate import compute_contact_pressures

def test_press_basic():
    p = compute_contact_pressures(500, 50, 80, 400, 500)
    assert 'sigma_max_kNmm2' in p and 'sigma_min_kNmm2' in p
