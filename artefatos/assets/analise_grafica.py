"""
Gera o gráfico da análise gráfica do problema de otimização (Seção 3).
Cenário reduzido com 2 clusters para visualização em 2D.
Salva em artefatos/assets/analise_grafica_otimizacao.png
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

# --- Parâmetros do cenário reduzido ---
PD1, PD2 = 0.002, 0.004
pi1, pi2 = 0.80, 0.70
CP1, CP2 = 4000, 1500
m1, m2 = 1.5, 0.8
n1, n2 = 500, 300
u_bar = 0.75
t = 0.0175
LGD = 0.60
PD_fin_atual = 0.0022

# Coeficientes de retorno líquido unitário
c1 = pi1 * (u_bar * t - PD1 * LGD)  # 0.00954
c2 = pi2 * (u_bar * t - PD2 * LGD)  # 0.00751

# Coeficientes da FO: max (n1*c1)*L1 + (n2*c2)*L2
fo_coef1 = n1 * c1  # 1.8
fo_coef2 = n2 * c2  # 0.27

# Bounds de R2 (capacidade de pagamento)
R2_L1 = m1 * CP1  # 6000
R2_L2 = m2 * CP2  # 1200

# R1 (inadimplência financeira): n1*(PD1-PD_fin)*L1 + n2*(PD2-PD_fin)*L2 <= 0
d1 = PD1 - PD_fin_atual  # -0.0002
d2 = PD2 - PD_fin_atual  # 0.0018
# => n1*d1*L1 + n2*d2*L2 <= 0
# => -0.1*L1 + 0.54*L2 <= 0
# => L2 <= (0.1/0.54)*L1 ≈ 0.185*L1
r1_slope = -n1 * d1 / (n2 * d2)  # 0.185...

# --- Região factível (vértices) ---
# Vértices do polígono factível:
# (0, 0)
# (R2_L1, 0) = (6000, 0)
# (R2_L1, r1_slope * R2_L1) = (6000, ~1111)  -- R1 binds antes de R2_L2
# Note: r1_slope * R2_L1 ≈ 1111 < R2_L2 = 1200, então R1 é a restrição ativa
vertices = np.array([
    [0, 0],
    [R2_L1, 0],
    [R2_L1, r1_slope * R2_L1],
    [0, 0],  # fecha
])

# --- Solução ótima ---
L1_opt = R2_L1
L2_opt = r1_slope * R2_L1
fo_opt = fo_coef1 * L1_opt + fo_coef2 * L2_opt

# --- Plot ---
fig, ax = plt.subplots(1, 1, figsize=(10, 7))

L1_max_plot = 8000
L2_max_plot = 2000

# Região factível (preenchida)
feasible = plt.Polygon(vertices[:-1], alpha=0.15, color='#2196F3', label='Região factível')
ax.add_patch(feasible)

# Contorno da região factível
ax.plot([0, R2_L1], [0, 0], color='#2196F3', linewidth=1.5)
ax.plot([R2_L1, R2_L1], [0, r1_slope * R2_L1], color='#2196F3', linewidth=1.5)
ax.plot([0, R2_L1], [0, r1_slope * R2_L1], color='#2196F3', linewidth=1.5)

# R1 - Inadimplência financeira: L2 = r1_slope * L1
L1_r1 = np.linspace(0, L1_max_plot, 300)
L2_r1 = r1_slope * L1_r1
ax.plot(L1_r1, L2_r1, color='#E53935', linewidth=2, linestyle='-',
        label=f'R1: Inadimplência financeira ($L_2 \\leq {r1_slope:.3f} \\cdot L_1$)')

# R2 - Capacidade de pagamento L1
ax.axvline(x=R2_L1, color='#43A047', linewidth=2, linestyle='--',
           label=f'R2: Cap. pagamento ($L_1 \\leq {R2_L1:,.0f}$)')

# R2 - Capacidade de pagamento L2
ax.axhline(y=R2_L2, color='#7CB342', linewidth=2, linestyle='--',
           label=f'R2: Cap. pagamento ($L_2 \\leq {R2_L2:,.0f}$)')

# Curvas de nível da FO (isoprofit lines)
fo_values = [fo_opt * 0.3, fo_opt * 0.6, fo_opt * 0.9, fo_opt]
for i, fo_val in enumerate(fo_values):
    L1_iso = np.linspace(0, L1_max_plot, 300)
    L2_iso = (fo_val - fo_coef1 * L1_iso) / fo_coef2
    alpha = 0.3 + 0.15 * i
    ax.plot(L1_iso, L2_iso, color='#FF9800', linewidth=1, linestyle=':', alpha=alpha)

# Label da última curva de nível (ótima)
L1_label_pos = L1_opt * 0.45
L2_label_pos = (fo_opt - fo_coef1 * L1_label_pos) / fo_coef2
ax.annotate('Curvas de nível da FO\n(isoprofit)', xy=(L1_label_pos, L2_label_pos),
            fontsize=8, color='#E65100', fontstyle='italic',
            ha='center', va='bottom')

# Gradiente da FO (seta)
grad_scale = 800
grad_origin = (2500, 200)
grad_dir = np.array([fo_coef1, fo_coef2])
grad_dir = grad_dir / np.linalg.norm(grad_dir) * grad_scale
ax.annotate('', xy=(grad_origin[0] + grad_dir[0], grad_origin[1] + grad_dir[1]),
            xytext=grad_origin,
            arrowprops=dict(arrowstyle='->', color='#E65100', lw=2.5))
ax.text(grad_origin[0] + grad_dir[0] * 0.5 - 100,
        grad_origin[1] + grad_dir[1] * 0.5 + 80,
        '∇FO', fontsize=10, color='#E65100', fontweight='bold')

# Ponto ótimo
ax.plot(L1_opt, L2_opt, 'o', color='#D32F2F', markersize=12, zorder=5,
        markeredgecolor='white', markeredgewidth=2)
ax.annotate(f'  Ótimo\n  $L_1^* = {L1_opt:,.0f}$\n  $L_2^* = {L2_opt:,.0f}$\n  FO = {fo_opt:,.1f}',
            xy=(L1_opt, L2_opt), xytext=(L1_opt + 300, L2_opt + 250),
            fontsize=9, fontweight='bold', color='#D32F2F',
            arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#D32F2F', alpha=0.9))

# Eixos
ax.set_xlabel('$L_1$ - Limite do Cluster 1 (baixo risco) [R\\$]', fontsize=11)
ax.set_ylabel('$L_2$ - Limite do Cluster 2 (risco moderado) [R\\$]', fontsize=11)
ax.set_title('Análise Gráfica - Região Factível e Solução Ótima\n(cenário reduzido com 2 clusters)',
             fontsize=13, fontweight='bold')

ax.set_xlim(-200, L1_max_plot)
ax.set_ylim(-100, L2_max_plot)
ax.set_aspect('auto')
ax.grid(True, alpha=0.3)
ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

# Linha de R$200 (piso pós-otimização)
ax.axhline(y=200, color='gray', linewidth=1, linestyle='-.', alpha=0.5)
ax.axvline(x=200, color='gray', linewidth=1, linestyle='-.', alpha=0.5)
ax.text(250, 50, 'Piso R\\$ 200\n(pós-otimização)', fontsize=7, color='gray', fontstyle='italic')

plt.tight_layout()

# Salvar
output_path = Path(__file__).parent / 'analise_grafica_otimizacao.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f"Gráfico salvo em: {output_path}")
