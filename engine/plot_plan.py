import io
import matplotlib.pyplot as plt

def render_plan_png(B, L, bolts, d_col, bf_col):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.add_patch(plt.Rectangle((-B/2,-L/2), B, L, fill=False, lw=1.5))
    ax.add_patch(plt.Rectangle((-bf_col/2,-d_col/2), bf_col, d_col, fill=False, ls='--', lw=1.0))
    ax.axhline(0,color='k',lw=0.5); ax.axvline(0,color='k',lw=0.5)
    for b in bolts:
        ax.add_patch(plt.Circle((b['x'], b['y']), 6, color='tab:blue'))
        ax.text(b['x']+8, b['y']+8, b.get('id',''), fontsize=7)
    ax.set_aspect('equal', 'box')
    ax.set_xlim(-B*0.65, B*0.65); ax.set_ylim(-L*0.65, L*0.65)
    ax.set_xlabel('x (mm)'); ax.set_ylabel('y (mm)')
    buf = io.BytesIO()
    plt.tight_layout(); plt.savefig(buf, format='png', dpi=180)
    plt.close(fig); buf.seek(0)
    return buf.read()