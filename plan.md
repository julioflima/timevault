# Plan: Time Vault — Static Svelte Website with Client-Side Crypto

Build a static SvelteKit website deployed to **GitHub Pages** via GitHub Actions. The site implements the Time Vault protocol (from vault.py) running **entirely client-side** via PyScript/Pyodide. Users encrypt phrases/files with time-locked encryption, store ciphertexts in a separate GitHub repo (`time-vault-secrets`), and optionally create Bitcoin bounty wallets. Design: glassmorphism, minimalist black & white, utopia.png background.

---

## Phase 1: Reorganize Directory Structure

- Current flat structure is messy — reorganize files into logical directories:
  - `algorithm/` — `vault.py`, `fit_benchmark.py`, `store_phrase.py`, `requirements.txt`, `vault.json`
  - `docs/` — `idea.md`, `speech.md`, `table.md`, `diagram.mmd`
  - `assets/` — `utopia.png`, `time_lock_encryption.png`
  - `plan.md` stays at root

---

## Phase 2: Rename Repo + Create Subrepo

- **Rename repo** from `article-time-vault` to `timevault` (via GitHub settings or CLI)
- **Create `time-vault-secrets` repo** on GitHub (public, empty)
- **Add as git submodule**: `git submodule add git@github.com:{owner}/time-vault-secrets.git time-vault-secrets`
- **Configure submodule**: ensure `.gitmodules` is committed, submodule tracks `main` branch
- **Set permissions**: configure `time-vault-secrets` so collaborators can write (push encrypted files) but not delete — use branch protection rules (require PR for deletion, or use a GitHub App/bot for writes)

---

## Phase 3: Project Scaffolding + GitHub Actions

1. **Initialize SvelteKit project** — Svelte 5, TypeScript, Sass, `adapter-static`. Set `paths.base` for GitHub Pages. Move assets from `assets/` to `static/`.

2. **GitHub Actions CI/CD** — Create `.github/workflows/deploy.yml`:
   - Trigger on push to `main`
   - **Job 1**: Build site (`npm run build`)
   - **Job 2**: Convert idea.md → PDF via pandoc (placed in `static/whitepaper.pdf` before build)
   - **Job 3**: Deploy to GitHub Pages via `actions/deploy-pages@v4`
   - Add `.nojekyll` to `static/`

---

## Phase 4: Design System + Layout

3. **Global Sass styles** — Glassmorphism utilities (`backdrop-filter: blur`, semi-transparent cards), color palette (white/black only), utopia.png as `position: fixed` full-viewport background, clean sans-serif typography. The page background color should be derived from utopia.png repeated and heavily blurred (`background: repeat` + `filter: blur(~60px)`) so the dominant color bleeds through as an ambient backdrop behind the main image.

4. **UX pattern: Typeform-style step flow** — One action per screen, full viewport. Navigation via up/down arrow buttons (bottom-right corner) and keyboard arrows. Smooth vertical slide transitions between steps. Progress indicator optional (subtle dots or step count).

5. **Encrypt page** (`/` — home) — step-by-step flow:
   - **Step 1**: "Time Vault" title centered, subtitle "Encrypt a secret for the future". Arrow down to begin.
   - **Step 2**: Date picker — "When should this secret be unlockable?" Single date input, centered.
   - **Step 3**: Cost display — "Today it costs $1,000,000 to break this vault". Shows n bits, cost breakdown. Arrow buttons to adjust.
   - **Step 4**: Secret type — "What do you want to encrypt?" Two large buttons: "Phrase" or "File".
   - **Step 5a** (if phrase): Textarea — "Type your secret phrase".
   - **Step 5b** (if file): File upload dropzone — "Drop your file here".
   - **Step 6**: Bitcoin donation — QR code + wallet address input. "Support the project" (scrollable bottom section).
   - **Step 7**: Result — Encrypted output with download button (file) or copyable ciphertext (phrase). Link to decrypt page.

6. **Decrypt page** (`/decrypt`) — step-by-step flow:
   - **Step 1**: List all encrypted vaults from `time-vault-secrets` repo (via GitHub API). Click to select, or arrow down to manual entry.
   - **Step 2**: Input — paste encrypted phrase or upload encrypted file.
   - **Step 3**: Secret field — "Enter the secret S to decrypt".
   - **Step 4**: Result — revealed plaintext or decrypted file download.

6. **Glassmorphism components** — Frosted glass Card, black Button, glass Input, QR display. Everything in strict black & white over the utopia background.

---

## Phase 5: PyScript Integration (Client-Side Crypto)

7. **Adapt vault.py for browser** → `static/vault_browser.py`. **Using Option A: `cryptography` in Pyodide** — import `cryptography` directly in Pyodide (available since v0.24+). vault.py runs nearly unchanged, no JS bridge code needed. Tradeoff: ~17MB total first load (Pyodide ~12MB + `cryptography` ~5MB), all cached after first visit. Simpler code, zero bridge bugs, same exact algorithm as the Python CLI.

8. **PyScript setup** — Load PyScript in `app.html` with `packages = ["cryptography"]` in the Pyodide config. Create Svelte wrapper component, expose Python functions (`calc_n`, `generate_seed`, `compute_V`, `compute_K`, `encrypt`, `decrypt`) to JavaScript via global bindings.

9. **Offline capability** — After initial PyScript load (~3-10s), all crypto runs locally. User can disconnect and still encrypt/decrypt. Show loading spinner during init.

---

## Phase 6: GitHub Storage (`time-vault-secrets`)

10. **Storage structure (GitHub repo as database)** — Separate public repo `time-vault-secrets` acts as a flat-file database. Each vault is stored as `{V_hex}.vault.json` containing `{ "C", "n", "t0", "T" }`. V (the public verification value) is the filename — guarantees uniqueness and enables lookup by V.

11. **Write via GitHub API** (TypeScript, `src/lib/github.ts`) — A **public fine-grained PAT** is hardcoded in the client with `Contents:write` scope on `time-vault-secrets` only. Anyone can add vault files — this is intentional (the repo is an append-only public database). Deletion is prevented via GitHub branch protection rules (require PR for deletion, restrict force-push). On "Proceed" after encryption:
    - `PUT /repos/{owner}/time-vault-secrets/contents/{V_hex}.vault.json` with Base64-encoded JSON body
    - Commit message: `"vault: {V_hex_short} | n={n} | unlock={T}"`
    - If the file already exists (409 conflict), the vault V is a duplicate — show error

12. **Read / List via GitHub API (no auth)** — Since `time-vault-secrets` is public:
    - `GET /repos/{owner}/time-vault-secrets/contents/` returns all vault files (no token needed)
    - Display scrollable list on Decrypt page: V (truncated), creation date (from `t0`), n value, unlock date (from `T`)
    - Click a vault to auto-populate the decrypt form with its `C` and `n`
    - For repos with many files, paginate using GitHub Trees API: `GET /repos/{owner}/time-vault-secrets/git/trees/main`

---

## Phase 7: Bitcoin Integration

13. **Bitcoin bounty + on-chain proof (combined design)** — A single funding transaction registers the vault on the blockchain and locks the bounty:

    **Funding transaction (created by vault creator):**
    - **Output 0 — P2WSH hashlock bounty**: Script = `OP_SHA256 <SHA256(S)> OP_EQUAL`. The bounty amount (any amount above 330 sats dust limit). Can only be spent by revealing S.
    - **Output 1 — OP_RETURN** (all ASCII, ~108 bytes): `https://julioflima.github.io/timevault/v/{V_hex}`. Clickable URL on block explorers, links directly to the vault's decrypt page. `n` is stored in the vault JSON file. `t0` comes from the block timestamp (free). Since Bitcoin Core v30 (Oct 2025), OP_RETURN supports up to ~100KB.
    - Minimum total cost: ~550 sats (~$0.55) — 330 sats bounty + ~220 sats fee (slightly larger tx due to OP_RETURN data).

    **Spending transaction (when vault is cracked):**
    - Witness data: `<S>` — the cracker must reveal S on-chain to claim the bounty.
    - S is permanently recorded on the blockchain.
    - Anyone can verify: `HMAC-SHA256(S, n) == V` (the V from the OP_RETURN in the funding tx).

    **On-chain narrative:**
    | Event | On-chain data | Verifiable |
    |-------|--------------|------------|
    | Vault created | OP_RETURN: URL with V | Clickable link to vault. `n` from vault file. `t0` from block timestamp. |
    | Bounty locked | P2WSH output with hashlock | Funds locked until S is found |
    | Vault cracked | S revealed in witness | `HMAC-SHA256(S, n) == V` ✓ |

    **Implementation** (`src/lib/bitcoin.ts`):
    - Use `bitcoinjs-lib` (TypeScript, runs in browser) for P2WSH address generation
    - Compute `SHA256(S)` as the hashlock target
    - Generate the P2WSH address from the hashlock script
    - Display: BIP21 QR code pointing to the Worker's donation address

14. **Payment flow — Worker (Option A: Intermediary)** — A stateless Worker handles transaction construction so the user only needs to scan a single QR code from any Bitcoin wallet.

    **User flow (client-side):**
    - Site generates a BIP21 QR code: `bitcoin:{donation_address}?amount={amount}`
    - The user's payment includes an OP_RETURN memo: `TV-{V_hex}-{P2WSH_address}`
    - User scans QR with any Bitcoin wallet and pays. Done — zero complexity.

    **Worker flow (server-side, `worker/src/index.ts`):**
    1. Monitors the donation address for incoming transactions (via mempool.space WebSocket or polling API)
    2. Parses the OP_RETURN memo from the user's tx to extract `V_hex` and `P2WSH_address`
    3. **Deduplication via blockchain (no database):** queries blockchain API for any existing OP_RETURN containing `timevault/v/{V_hex}`. If found → already processed, skip.
    4. Builds the **funding transaction** with 3 outputs:
       - **Output 0 — P2WSH hashlock bounty**: sends 99% of received amount (minus fees) to the P2WSH address from the memo
       - **Output 1 — OP_RETURN**: `https://julioflima.github.io/timevault/v/{V_hex}`
       - **Output 2 — Change**: any remaining sats back to the Worker's address
    5. The 1% kept by the donation address **is** the project donation — no separate output needed
    6. Broadcasts the funding tx via blockchain API

    **Worker is stateless:**
    - No database — the blockchain is the source of truth for deduplication (OP_RETURN existence check) and balance (UTXO query)
    - Worker can crash and restart without losing state
    - Needs only: a private key (Worker secret) + blockchain API endpoint (mempool.space)

    **Cost breakdown (user pays):**
    | Component | Value |
    |-----------|-------|
    | User's tx to donation address | user-chosen amount |
    | Worker keeps 1% as donation | ~1% of amount |
    | Worker sends 99% to P2WSH bounty | ~99% minus fees |
    | Worker tx fee (~250 vBytes × 1 sat/vB) | ~250 sats |
    | OP_RETURN | 0 sats |
    | **Minimum user payment** | **~600 sats** (330 bounty + 250 fee + ~20 donation) |

---

## Phase 8: Whitepaper + Article

15. **PDF in CI** — `pandoc idea.md -o static/whitepaper.pdf --pdf-engine=xelatex`. Serve at `/whitepaper.pdf`.

16. **Article section** — Title: "Bitcoin is a Time Vault". First paragraph: the consequence — if cryptography breaks, all wallets are vulnerable. Reference Satoshi Nakamoto's early wallets being gradually broken and funds stolen. Link to PDF download.

---

## Relevant Files

**Existing (reuse/reference):**
- `vault.py` — Core algorithm: `get_benchmark()`, `calc_n()`, `generate_seed()`, `compute_V()`, `compute_K()`, `encrypt()`, `decrypt()`
- `store_phrase.py` — Bitcoin OP_RETURN pattern via `bit` library
- `diagram.mmd` — Mermaid protocol flowchart (could render on site)
- `idea.md` — Whitepaper source → PDF
- `utopia.png` — Background image
- `time_lock_encryption.png` — Protocol diagram

**New files to create:**
- `.github/workflows/deploy.yml`
- `svelte.config.js`, `package.json`, `tsconfig.json`
- `src/app.html` — PyScript loader
- `src/routes/+page.svelte` — Encrypt page
- `src/routes/+layout.svelte` — Shared layout
- `src/routes/decrypt/+page.svelte` — Decrypt page
- `src/lib/styles/` — Sass globals, glassmorphism
- `src/lib/components/` — Card, Button, DatePicker, FileUpload, QRCode
- `src/lib/github.ts` — GitHub API client
- `src/lib/bitcoin.ts` — Address derivation, QR generation
- `static/vault_browser.py` — Browser-adapted vault algorithm
- `worker/src/index.ts` — Worker: monitors donations, builds funding txs
- `worker/wrangler.toml` — Worker config

---

## Verification

1. `npm run build` produces static files in `build/`
2. Open locally → vault encryption/decryption works in browser
3. **Offline test**: disconnect internet after page load → encrypt/decrypt still works
4. GitHub API: test file listing and upload against `time-vault-secrets`
5. Bitcoin: generate address from known S → verify valid BTC address + QR scans
6. PDF: `whitepaper.pdf` accessible at published URL
7. Design: visual check — glassmorphism, utopia background, black/white, responsive
8. GitHub Actions: push to main → auto-deploys to Pages

---

## Decisions

- **Sass** (CSS preprocessor), confirmed
- **GitHub Pages** for hosting, confirmed
- **Separate repo** `time-vault-secrets` for storage, confirmed
- **Scope includes**: encrypt page, decrypt page, GitHub storage, Bitcoin address, PDF, CI/CD
- **Scope excludes**: no traditional backend server (Worker is the only server-side component)

---

## Resolved Decisions

1. **PyScript loading UX** — Using **Option A** (`cryptography` in Pyodide). Slower first load (~17MB) but simpler code, zero bridge bugs, same algorithm as CLI. Show loading spinner ("Initializing cryptographic engine..."), disable buttons until ready. All cached after first visit.

2. **GitHub token (public, append-only)** — The PAT is public and hardcoded in the client. It can only create/update files in `time-vault-secrets` — it cannot delete files, force-push, or access other repos. Branch protection rules on `time-vault-secrets` enforce append-only behavior (no deletion, no force-push). If the token is revoked/rotated, update the hardcoded value and redeploy. No user login or token input — zero friction.

3. **Bitcoin address standard** — **P2WSH** (SegWit) for the hashlock bounty. Uses script `OP_SHA256 <SHA256(S)> OP_EQUAL` which forces the cracker to reveal S on-chain when spending. Combined with OP_RETURN in the same funding transaction for full on-chain correlation.

4. **OP_RETURN format** — All ASCII, single clickable URL: `https://julioflima.github.io/timevault/v/{V_hex}`. Block explorers auto-linkify it. `n` is read from the vault JSON file at the URL. `t0` is derived from the block timestamp (free, no need to store). Since Bitcoin Core v30 (Oct 2025), OP_RETURN supports up to ~100KB — the ~108 byte URL fits easily. The URL prefix `julioflima.github.io/timevault` acts as both protocol identifier and direct link.

5. **Satoshi's wallets as precedent** — The article references Satoshi Nakamoto's ~1.1M BTC held in P2PK (Pay-to-Public-Key) addresses, identified by researcher Sergio Lerner via the "Patoshi Pattern" (extraNonce fingerprinting in blocks 1–36,000). These addresses expose the raw public key on-chain, making them vulnerable to quantum attacks via Shor's algorithm. Bitcoin developers proposed BIP-360 (quantum-resistant address migration). Time Vault makes this same pattern intentional and quantifiable: encryption that is secure today but will eventually be breakable as hardware improves.

6. **On-chain data lifecycle** — A vault's complete lifecycle is recorded on the Bitcoin blockchain:
   - **Funding tx**: Output 0 = P2WSH hashlock bounty (locked by `SHA256(S)`), Output 1 = OP_RETURN with clickable URL containing V. `n` is in the vault JSON file. `t0` comes from the block timestamp.
   - **Spending tx**: Witness data reveals S. Anyone can verify `HMAC-SHA256(S, n) == V`. The vault is publicly and permanently "cracked."
   - **Minimum cost**: ~600 sats — 330 sats bounty (P2WSH dust limit) + ~250 sats fee + ~20 sats donation.
   - **The blockchain becomes a proof-of-crack ledger**: vault exists (V in OP_RETURN) → bounty locked (P2WSH) → vault broken (S in witness).

7. **Payment UX — Worker intermediary** — The user scans a single BIP21 QR code from any Bitcoin wallet. Payment goes to a project donation address with an OP_RETURN memo (`TV-{V_hex}-{P2WSH_address}`). A stateless Worker monitors the donation address, parses the memo, and builds the funding tx (P2WSH + OP_RETURN + change) in one transaction. The Worker uses the **blockchain as its database**: deduplication is done by checking if an OP_RETURN with the vault's V already exists on-chain. No external database, no state — the Worker can crash and restart without data loss. The 1% donation is simply the amount kept by the donation address. Minimum user payment: ~600 sats.
