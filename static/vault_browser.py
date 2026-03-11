"""
Time Vault — Browser-adapted algorithm for Pyodide/PyScript
Same protocol as algorithm/vault.py, no CLI, no datetime dependency.
Exposes functions to JavaScript via global bindings.
"""

import hmac
import hashlib
import os
import math
import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Logistic benchmark: B(t) = L / (1 + exp(-k*(t - t_mid))) + b
BENCHMARK_L = 141.54
BENCHMARK_K = 0.0233
BENCHMARK_MID = 1925.9
BENCHMARK_B = -61.03


def get_benchmark(t0):
    exp_val = -BENCHMARK_K * (t0 - BENCHMARK_MID)
    exp_val = max(min(exp_val, 500), -500)
    return int(BENCHMARK_L / (1 + math.exp(exp_val)) + BENCHMARK_B)


def calc_n(t0, T_years):
    B = get_benchmark(t0)
    if T_years <= 0:
        T_years = 1 / 365
    n = B + math.floor(math.log2(T_years))
    return max(n, 8)


def calc_cost(n, t0):
    B = get_benchmark(t0)
    return 1_000_000 * (2 ** (n - B))


def generate_seed(n_bits):
    n_bytes = math.ceil(n_bits / 8)
    seed = os.urandom(n_bytes)
    if n_bits % 8 != 0:
        mask = (1 << (n_bits % 8)) - 1
        seed = bytes([seed[0] & mask]) + seed[1:]
    return seed


def compute_V(S, n):
    n_bytes = n.to_bytes(4, "big")
    return hmac.new(S, n_bytes, hashlib.sha256).digest()


def compute_K(S, V):
    return hmac.new(S, V, hashlib.sha256).digest()


def encrypt_data(K, plaintext_bytes):
    aesgcm = AESGCM(K)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
    return nonce + ciphertext


def decrypt_data(K, C):
    nonce = C[:12]
    ciphertext = C[12:]
    aesgcm = AESGCM(K)
    return aesgcm.decrypt(nonce, ciphertext, None)


def b64encode(data):
    return base64.b64encode(data).decode()


def b64decode(s):
    return base64.b64decode(s)


def vault_encrypt(plaintext_str, t0, T_years):
    """Full encrypt flow. Returns JSON string with vault data."""
    n = calc_n(t0, T_years)
    S = generate_seed(n)
    V = compute_V(S, n)
    K = compute_K(S, V)
    C = encrypt_data(K, plaintext_str.encode("utf-8"))

    return json.dumps({
        "C": b64encode(C),
        "n": n,
        "t0": t0,
        "T": T_years,
        "V": V.hex(),
        "S": S.hex(),
    })


def vault_encrypt_bytes(data_bytes, t0, T_years):
    """Encrypt raw bytes (for files). Returns JSON string."""
    n = calc_n(t0, T_years)
    S = generate_seed(n)
    V = compute_V(S, n)
    K = compute_K(S, V)
    C = encrypt_data(K, bytes(data_bytes))

    return json.dumps({
        "C": b64encode(C),
        "n": n,
        "t0": t0,
        "T": T_years,
        "V": V.hex(),
        "S": S.hex(),
    })


def vault_decrypt(vault_json_str, seed_hex):
    """Decrypt a vault given JSON string and seed hex. Returns plaintext string."""
    vault = json.loads(vault_json_str)
    S = bytes.fromhex(seed_hex)
    n = vault["n"]
    C = b64decode(vault["C"])

    V = compute_V(S, n)
    if V.hex() != vault["V"]:
        raise ValueError("Invalid seed: V does not match")

    K = compute_K(S, V)
    plaintext = decrypt_data(K, C)
    return plaintext.decode("utf-8")


def vault_decrypt_bytes(vault_json_str, seed_hex):
    """Decrypt to raw bytes (for files). Returns bytes."""
    vault = json.loads(vault_json_str)
    S = bytes.fromhex(seed_hex)
    n = vault["n"]
    C = b64decode(vault["C"])

    V = compute_V(S, n)
    if V.hex() != vault["V"]:
        raise ValueError("Invalid seed: V does not match")

    K = compute_K(S, V)
    return decrypt_data(K, C)
