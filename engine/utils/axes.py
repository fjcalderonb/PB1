
# Axis mapper presets & sign flips
# Preset A (default): N ← F3, Vx ← F1, Vy ← F2, Mx ← M2, My ← M1
# Preset B: swap 1↔2 → Vx↔Vy and Mx↔My

def apply_preset(preset_label, F1, F2, F3, M1, M2):
    N  = F3
    Vx = F1
    Vy = F2
    Mx = M2
    My = M1
    if preset_label.startswith('Preset B'):
        Vx, Vy = Vy, Vx
        Mx, My = My, Mx
    return N, Vx, Vy, Mx, My

def flip_signs(N,Vx,Vy,Mx,My, flips):
    if 'N'  in flips: N  *= -1
    if 'Vx' in flips: Vx *= -1
    if 'Vy' in flips: Vy *= -1
    if 'Mx' in flips: Mx *= -1
    if 'My' in flips: My *= -1
    return N,Vx,Vy,Mx,My
