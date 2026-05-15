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
T = 22
LGD = 0.80
PD_fin_atual = 0.0022

# Coeficientes de retorno líquido unitário
c1 = pi1 * (T * u_bar * t - PD1 * LGD)
c2 = pi2 * (T * u_bar * t - PD2 * LGD)

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
CONSTRAINT_COLOR = '#1565C0'
FO_COLOR = '#D32F2F'

fig, ax = plt.subplots(1, 1, figsize=(10, 7), facecolor='white')

L1_max_plot = 8000
L2_max_plot = 1600

# Região factível (preenchida)
feasible = plt.Polygon(vertices[:-1], alpha=0.12, color=CONSTRAINT_COLOR, label='Região factível')
ax.add_patch(feasible)

# R1 - Inadimplência financeira: L2 = r1_slope * L1
L1_r1 = np.linspace(0, L1_max_plot, 300)
L2_r1 = r1_slope * L1_r1
ax.plot(L1_r1, L2_r1, color=CONSTRAINT_COLOR, linewidth=2, linestyle='-',
        label=f'R1: Inadimplência financeira ($L_2 \\leq {r1_slope:.3f} \\cdot L_1$)')

# R2 - Capacidade de pagamento L1
ax.axvline(x=R2_L1, color=CONSTRAINT_COLOR, linewidth=2, linestyle='--',
           label=f'R2: Cap. pagamento ($L_1 \\leq {R2_L1:,.0f}$)')

# R2 - Capacidade de pagamento L2
ax.axhline(y=R2_L2, color=CONSTRAINT_COLOR, linewidth=2, linestyle='--',
           label=f'R2: Cap. pagamento ($L_2 \\leq {R2_L2:,.0f}$)')

# Reta da FO passando pelo ótimo (isoprofit no ponto ótimo)
L1_fo = np.linspace(0, L1_max_plot, 300)
L2_fo = (fo_opt - fo_coef1 * L1_fo) / fo_coef2
mask = (L2_fo >= 0) & (L2_fo <= L2_max_plot)
ax.plot(L1_fo[mask], L2_fo[mask], color=FO_COLOR, linewidth=2, linestyle='-.',
        label=f'FO = {fo_opt:,.1f} (reta ótima)')

# Gradiente da FO (seta perpendicular à reta, partindo de um ponto sobre ela)
# Escolher ponto na reta da FO que esteja visível no gráfico
grad_L2_start = 400  # ponto baixo na reta onde há espaço horizontal
grad_L1_start = (fo_opt - fo_coef2 * grad_L2_start) / fo_coef1  # x correspondente na reta
grad_scale = 300
grad_dir = np.array([fo_coef1, fo_coef2])
grad_dir = grad_dir / np.linalg.norm(grad_dir) * grad_scale
ax.annotate('', xy=(grad_L1_start + grad_dir[0], grad_L2_start + grad_dir[1]),
            xytext=(grad_L1_start, grad_L2_start),
            arrowprops=dict(arrowstyle='->', color=FO_COLOR, lw=2.5))
ax.text(grad_L1_start + grad_dir[0] + 80,
        grad_L2_start + grad_dir[1],
        '$\\nabla$ FO', fontsize=10, color=FO_COLOR, fontweight='bold')

# Ponto ótimo
ax.plot(L1_opt, L2_opt, 'o', color=FO_COLOR, markersize=12, zorder=5,
        markeredgecolor='white', markeredgewidth=2)
ax.annotate(f'Ótimo\n$L_1^* = {L1_opt:,.0f}$\n$L_2^* = {L2_opt:,.0f}$\nFO = {fo_opt:,.1f}',
            xy=(L1_opt, L2_opt), xytext=(L1_opt + 400, L2_opt + 200),
            fontsize=9, fontweight='bold', color=FO_COLOR,
            arrowprops=dict(arrowstyle='->', color=FO_COLOR, lw=1.5),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=FO_COLOR, alpha=0.9))

# Eixos
ax.set_xlabel('$L_1$ - Limite do Cluster 1 (baixo risco) [R\\$]', fontsize=11)
ax.set_ylabel('$L_2$ - Limite do Cluster 2 (risco moderado) [R\\$]', fontsize=11)
ax.set_title('Análise Gráfica - Região Factível e Solução Ótima\n(cenário reduzido com 2 clusters)',
             fontsize=13, fontweight='bold')

ax.set_xlim(0, L1_max_plot)
ax.set_ylim(0, L2_max_plot)
ax.set_aspect('auto')
ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

# Remover spines superiores e direitas para visual limpo
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# Salvar
output_path = Path(__file__).parent.parent / 'artefatos' / 'assets' / 'analise_grafica_otimizacao.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f"Gráfico salvo em: {output_path}")
