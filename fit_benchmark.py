"""
Ajuste de curva logística ao benchmark HMAC-SHA256 (GPU) com $1M.
Dados desde 1945 (ENIAC) até 2025 (RTX 5090).
"""
import numpy as np
from scipy.optimize import curve_fit

# Dados históricos: HMAC-SHA256 equivalente com orçamento $1M
years = np.array([
    1945, 1950, 1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990,
    1995, 2000, 2005, 2008, 2010, 2012, 2014, 2016, 2018, 2020,
    2022, 2024, 2025
])
bits = np.array([
    24, 31, 33, 36, 40, 44, 46, 48, 50, 55,
    59, 63, 58, 60, 63, 64, 65, 66, 66, 67,
    67, 67, 67
])

# ── Logística: B(t) = L / (1 + exp(-k*(t - t_mid))) + b ──
def logistic(t, L, k, t_mid, b):
    return L / (1 + np.exp(-k * (t - t_mid))) + b

popt, pcov = curve_fit(logistic, years, bits, p0=[45, 0.08, 1985, 22], maxfev=50000)
L, k, t_mid, b = popt
pred = logistic(years, *popt)
residuals = bits - pred
mse = np.mean(residuals**2)

print("=" * 55)
print("  AJUSTE LOGÍSTICO — HMAC-SHA256 / GPU / $1M")
print("=" * 55)
print()
print(f"  B(t) = {L:.2f} / (1 + exp(-{k:.4f} * (t - {t_mid:.1f}))) + {b:.2f}")
print()
print(f"  L     = {L:.2f}   (amplitude)")
print(f"  k     = {k:.4f}  (taxa de crescimento)")
print(f"  t_mid = {t_mid:.1f} (ponto de inflexão)")
print(f"  b     = {b:.2f}  (offset base)")
print()
print(f"  Assíntota inferior: {b:.1f} bits")
print(f"  Assíntota superior: {L + b:.1f} bits")
print(f"  MSE: {mse:.2f}")
print(f"  RMSE: {np.sqrt(mse):.2f}")
print(f"  Erro máx: {np.max(np.abs(residuals)):.1f} bits")
print()

# ── Validação ──
print("  Ano  | Real | Modelo | Erro")
print("  -----|------|--------|------")
for y, real, p in zip(years, bits, pred):
    err = p - real
    flag = " ⚠️" if abs(err) > 3 else ""
    print(f"  {y} | {real:4d} | {p:6.1f} | {err:+5.1f}{flag}")

# ── Extrapolação ──
print()
print("  Previsões futuras:")
print("  Ano  | Bits")
print("  -----|-----")
for y in [2026, 2028, 2030, 2035, 2040, 2050, 2075, 2100]:
    p = logistic(y, *popt)
    print(f"  {y} | {p:5.1f} → {int(p)} bits")

# ── Saída para vault.py ──
print()
print("  " + "─" * 40)
print("  Para vault.py:")
print(f"    BENCHMARK_L   = {L:.2f}")
print(f"    BENCHMARK_K   = {k:.4f}")
print(f"    BENCHMARK_MID = {t_mid:.1f}")
print(f"    BENCHMARK_B   = {b:.2f}")
