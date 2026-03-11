/**
 * Pyodide bridge — lazy-loads Pyodide + cryptography, exposes vault functions.
 */

import { base } from "$app/paths";

declare global {
    interface Window {
        loadPyodide: (config?: { indexURL?: string }) => Promise<PyodideInterface>;
    }
}

interface PyodideInterface {
    loadPackage: (packages: string | string[]) => Promise<void>;
    runPythonAsync: (code: string) => Promise<unknown>;
    globals: { get: (name: string) => unknown };
    micropip?: { install: (pkg: string | string[]) => Promise<void> };
    FS: {
        writeFile: (path: string, data: string | Uint8Array) => void;
    };
}

let pyodide: PyodideInterface | null = null;
let initPromise: Promise<PyodideInterface> | null = null;

export type VaultResult = {
    C: string;
    n: number;
    t0: number;
    T: number;
    V: string;
    S: string;
};

export type CalcResult = {
    n: number;
    cost: number;
};

async function init(): Promise<PyodideInterface> {
    if (pyodide) return pyodide;

    const py = await window.loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",
    });

    await py.loadPackage(["cryptography"]);

    // Fetch vault_browser.py from static/ and run it
    const resp = await fetch(`${base}/vault_browser.py`);
    const code = await resp.text();
    await py.runPythonAsync(code);

    pyodide = py;
    return py;
}

/** Start loading Pyodide eagerly (call on mount). */
export function preload(): void {
    if (!initPromise) {
        initPromise = init();
    }
}

async function getPyodide(): Promise<PyodideInterface> {
    if (!initPromise) {
        initPromise = init();
    }
    return initPromise;
}

/** Calculate n bits and cost for a given year and time horizon. */
export async function calcParams(
    t0: number,
    T_years: number,
): Promise<CalcResult> {
    const py = await getPyodide();
    const result = await py.runPythonAsync(`
import json
_n = calc_n(${t0}, ${T_years})
_cost = calc_cost(_n, ${t0})
json.dumps({"n": _n, "cost": _cost})
`);
    return JSON.parse(result as string);
}

/** Encrypt a text phrase. Returns vault JSON + seed. */
export async function encryptPhrase(
    plaintext: string,
    t0: number,
    T_years: number,
): Promise<VaultResult> {
    const py = await getPyodide();
    // Escape for Python string literal
    const escaped = plaintext.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, "\\n");
    const result = await py.runPythonAsync(
        `vault_encrypt('${escaped}', ${t0}, ${T_years})`,
    );
    return JSON.parse(result as string);
}

/** Encrypt raw file bytes. Returns vault JSON + seed. */
export async function encryptFile(
    data: Uint8Array,
    t0: number,
    T_years: number,
): Promise<VaultResult> {
    const py = await getPyodide();
    // Write file bytes to Pyodide FS, encrypt from there
    py.FS.writeFile("/tmp/_upload", data);
    const result = await py.runPythonAsync(`
with open("/tmp/_upload", "rb") as _f:
    _data = _f.read()
vault_encrypt_bytes(_data, ${t0}, ${T_years})
`);
    return JSON.parse(result as string);
}

/** Decrypt a vault given JSON string and seed hex. Returns plaintext. */
export async function decryptVault(
    vaultJson: string,
    seedHex: string,
): Promise<string> {
    const py = await getPyodide();
    const escaped = vaultJson.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
    const result = await py.runPythonAsync(
        `vault_decrypt('${escaped}', '${seedHex}')`,
    );
    return result as string;
}
