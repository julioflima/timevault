#!/usr/bin/env python3
"""
Protocolo de Encriptação Temporizada por Custo — Time Vault
Implementação baseada em HMAC-SHA256 + AES-256-GCM
"""

import hmac
import hashlib
import os
import json
import math
import base64
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# B(t0, $1M) — benchmark contínuo: bits alcançáveis com $1M no ano t0
# Função logística ajustada por mínimos quadrados à tabela histórica (1945–2025)
# Hardware: HMAC-SHA256 em GPUs (não ASICs)
# B(t) = L / (1 + exp(-k * (t - t_mid))) + b
# Parâmetros: L=141.54, k=0.0233, t_mid=1925.9, b=-61.03  (MSE=2.13)
BENCHMARK_L = 141.54
BENCHMARK_K = 0.0233
BENCHMARK_MID = 1925.9
BENCHMARK_B = -61.03


def get_benchmark(t0: float) -> int:
    """Retorna B(t0, $1M) — função logística contínua.

    Ajustada aos dados históricos de custo de hardware (1945–2025).
    Hardware: GPUs para HMAC-SHA256 (ASICs não se aplicam).
    Assíntota superior: ~80 bits.
    """
    exp_val = -BENCHMARK_K * (t0 - BENCHMARK_MID)
    # Clamp para evitar overflow
    exp_val = max(min(exp_val, 500), -500)
    return int(BENCHMARK_L / (1 + math.exp(exp_val)) + BENCHMARK_B)


def calc_n(t0: int, T_years: float) -> int:
    """Passo 1: n = B(t0, $1M) + floor(log2(T))

    B = bits que $1M em GPUs quebra em 1 ano.
    T em anos: >1 soma bits, <1 subtrai bits.
    """
    B = get_benchmark(t0)
    if T_years <= 0:
        T_years = 1 / 365
    n = B + math.floor(math.log2(T_years))
    return max(n, 8)  # mínimo 8 bits


def calc_cost(n: int, B: int) -> float:
    """Custo para quebrar em 1 ano com hardware atual.

    $1M compra 2^B tentativas/ano.
    Precisamos de 2^n tentativas.
    Custo = $1M × 2^(n - B)
    """
    return 1_000_000 * (2 ** (n - B))


def generate_seed(n_bits: int) -> bytes:
    """Passo 2: S ← {0,1}^n"""
    n_bytes = math.ceil(n_bits / 8)
    seed = os.urandom(n_bytes)
    # Mascara bits extras para ter exatamente n bits
    if n_bits % 8 != 0:
        mask = (1 << (n_bits % 8)) - 1
        seed = bytes([seed[0] & mask]) + seed[1:]
    return seed


def compute_V(S: bytes, n: int) -> bytes:
    """Passo 3: V ← HMAC-SHA256(S, n)"""
    n_bytes = n.to_bytes(4, "big")
    return hmac.new(S, n_bytes, hashlib.sha256).digest()


def compute_K(S: bytes, V: bytes) -> bytes:
    """Passo 4: K ← HMAC-SHA256(S, V)"""
    return hmac.new(S, V, hashlib.sha256).digest()


def encrypt(K: bytes, plaintext: bytes) -> bytes:
    """Passo 5: C ← AES-256-GCM(K, F)"""
    aesgcm = AESGCM(K)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    # C = nonce || ciphertext+tag
    return nonce + ciphertext


def decrypt(K: bytes, C: bytes) -> bytes:
    """Decriptação: F ← AES-256-GCM.Dec(K, C)"""
    nonce = C[:12]
    ciphertext = C[12:]
    aesgcm = AESGCM(K)
    return aesgcm.decrypt(nonce, ciphertext, None)


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def main():
    t0 = datetime.now().year

    print("=" * 60)
    print("  TIME VAULT — Encriptação Temporizada por Custo")
    print("=" * 60)
    print()

    # --- Passo 1: Tempo alvo ---
    print("  Por quanto tempo a mensagem deve ficar protegida?")
    print()
    print("    1) 1 semana        5) 10 anos")
    print("    2) 1 mês           6) 50 anos")
    print("    3) 6 meses         7) 100 anos")
    print("    4) 1 ano           8) Personalizado")
    print()

    presets = {
        "1": ("1 semana",   1/52),
        "2": ("1 mês",      1/12),
        "3": ("6 meses",    0.5),
        "4": ("1 ano",      1.0),
        "5": ("10 anos",    10.0),
        "6": ("50 anos",    50.0),
        "7": ("100 anos",   100.0),
    }

    while True:
        choice = input("  Escolha [1-8]: ").strip()
        if choice in presets:
            label, T = presets[choice]
            print(f"  → {label} (T = {T:.4g} anos)")
            break
        elif choice == "8":
            while True:
                try:
                    T = float(input("  Tempo em anos (ex: 0.5, 2, 25): ").strip())
                    if T <= 0:
                        print("  Deve ser positivo.")
                        continue
                    break
                except ValueError:
                    print("  Valor inválido.")
            break
        else:
            print("  Opção inválida.")

    B = get_benchmark(t0)
    n = calc_n(t0, T)
    cost = calc_cost(n, B)
    time_bits = math.floor(math.log2(T)) if T > 0 else 0

    print()
    print(f"  t₀ (ano atual):       {t0}")
    print(f"  B(t₀, $1M):           {B} bits (quebrável em 1 ano com GPUs)")
    print(f"  Tempo alvo T:         {T:.4g} anos")
    print(f"  Bits temporais:       {time_bits:+d} bits (⌊log₂({T:.4g})⌋)")
    print(f"  Dificuldade:          n = {B} {time_bits:+d} = {n} bits")
    print(f"  Espaço de busca:      2^{n}")
    print(f"  Custo p/ quebrar:     ${cost:,.0f} (em 1 ano, hardware atual)")
    print()

    # --- Opção de trocar n ---
    change = input(f"  Deseja alterar o número de bits? (atual: {n}) [s/N]: ").strip().lower()
    if change == "s":
        while True:
            try:
                new_n = int(input(f"  Novo valor de n (bits): "))
                if new_n < 8:
                    print("  Mínimo 8 bits.")
                    continue
                n = new_n
                cost = calc_cost(n, B)
                print(f"  Dificuldade:          n = {n} bits")
                print(f"  Espaço de busca:      2^{n}")
                print(f"  Custo p/ quebrar:     ${cost:,.0f} (em 1 ano, hardware atual)")
                break
            except ValueError:
                print("  Valor inválido.")
    print()

    # --- Passo 2-5: Frase secreta ---
    F_text = input("Digite a frase secreta: ")
    F = F_text.encode("utf-8")

    # Passo 2: Gerar semente
    S = generate_seed(n)

    # Passo 3: V ← HMAC-SHA256(S, n)
    V = compute_V(S, n)

    # Passo 4: K ← HMAC-SHA256(S, V)
    K = compute_K(S, V)

    # Passo 5: C ← AES-256-GCM(K, F)
    C = encrypt(K, F)

    print()
    print("=" * 60)
    print("  VAULT CRIADO")
    print("=" * 60)
    print(f"  n  = {n} bits")
    print(f"  S  = {S.hex()}")
    print(f"  V  = {V.hex()}")
    print(f"  K  = {K.hex()}")
    print(f"  C  = {b64(C)}")
    print(f"  F  = {F_text}")
    print()

    # --- Verificação: decriptar para confirmar ---
    V_check = compute_V(S, n)
    K_check = compute_K(S, V_check)
    F_check = decrypt(K_check, C)
    assert F_check == F, "ERRO: verificação falhou!"
    print("  ✅ Verificação OK — decriptação confirmada.")
    print()

    # --- Salvar JSON ---
    vault = {
        "T": T,
        "t0": t0,
        "n": n,
        "S": S.hex(),
        "V": V.hex(),
        "K": K.hex(),
        "C": b64(C),
        "F": F_text,
    }

    filename = "vault.json"
    with open(filename, "w") as f:
        json.dump(vault, f, indent=2, ensure_ascii=False)

    print(f"  💾 Salvo em {filename}")
    print()

    # --- Info pública vs secreta ---
    print("  PÚBLICO (pode compartilhar):")
    print(f"    C  = {b64(C)[:40]}...")
    print(f"    n  = {n}")
    print(f"    V  = {V.hex()}")
    print()
    print("  SECRETO (não compartilhar):")
    print(f"    S  = {S.hex()}")
    print(f"    K  = {K.hex()}")
    print(f"    F  = {F_text}")
    print()


if __name__ == "__main__":
    main()
