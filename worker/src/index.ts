/**
 * Time Vault Worker — Stateless Bitcoin funding intermediary.
 *
 * Monitors a donation address for incoming payments, parses OP_RETURN memos
 * (TV-{V_hex}-{P2WSH_address}), and constructs funding transactions:
 *   Output 0: P2WSH hashlock bounty (99% of received minus fees)
 *   Output 1: OP_RETURN with vault URL
 *   Output 2: Change back to Worker
 *
 * Triggered via cron (scheduled) or HTTP (manual trigger).
 * The blockchain is the only database — deduplication via OP_RETURN existence check.
 */

export interface Env {
  DONATION_ADDRESS: string;
  MEMPOOL_API: string;
  WORKER_PRIVATE_KEY: string; // WIF — set via `wrangler secret put`
}

const URL_PREFIX = "https://julioflima.github.io/timevault/v/";

interface UTXO {
  txid: string;
  vout: number;
  value: number;
  status: { confirmed: boolean };
}

interface TxDetail {
  vout: Array<{
    scriptpubkey: string;
    scriptpubkey_asm: string;
    scriptpubkey_type: string;
    value: number;
  }>;
}

/** Fetch UTXOs for the donation address. */
async function getUTXOs(env: Env): Promise<UTXO[]> {
  const res = await fetch(`${env.MEMPOOL_API}/address/${env.DONATION_ADDRESS}/utxo`);
  if (!res.ok) throw new Error(`mempool API error: ${res.status}`);
  return res.json() as Promise<UTXO[]>;
}

/** Fetch full transaction details. */
async function getTxDetails(env: Env, txid: string): Promise<TxDetail> {
  const res = await fetch(`${env.MEMPOOL_API}/tx/${txid}`);
  if (!res.ok) throw new Error(`mempool API error: ${res.status}`);
  return res.json() as Promise<TxDetail>;
}

/** Parse OP_RETURN memo from a transaction. Returns TV-{V}-{addr} or null. */
function parseOpReturnMemo(tx: TxDetail): string | null {
  for (const out of tx.vout) {
    if (out.scriptpubkey_type === "op_return") {
      // Decode hex data after OP_RETURN opcode (6a)
      const hex = out.scriptpubkey;
      // Skip 6a (OP_RETURN) + pushdata byte(s)
      const dataHex = hex.slice(4); // simplified — works for short memos
      try {
        const text = Buffer.from(dataHex, "hex").toString("utf8");
        if (text.startsWith("TV-")) return text;
      } catch {
        // not valid utf8
      }
    }
  }
  return null;
}

/** Check if a vault's funding tx already exists on-chain. */
async function isVaultFunded(env: Env, V: string): Promise<boolean> {
  // Search for transactions with our OP_RETURN URL pattern.
  // mempool.space doesn't have a direct OP_RETURN search API,
  // so we check our own address's transaction history.
  // For a production system, use an indexer or Electrum server.
  // This is a simplified check — scan Worker's recent txs.
  const res = await fetch(`${env.MEMPOOL_API}/address/${env.DONATION_ADDRESS}/txs`);
  if (!res.ok) return false;

  const txs = (await res.json()) as Array<{ vout: TxDetail["vout"] }>;
  const targetUrl = `${URL_PREFIX}${V}.vault.json`;

  for (const tx of txs) {
    for (const out of tx.vout) {
      if (out.scriptpubkey_type === "op_return") {
        const dataHex = out.scriptpubkey.slice(4);
        try {
          const text = Buffer.from(dataHex, "hex").toString("utf8");
          if (text.includes(targetUrl)) return true;
        } catch {
          // skip
        }
      }
    }
  }

  return false;
}

/** Process a single incoming UTXO. */
async function processUTXO(env: Env, utxo: UTXO): Promise<string | null> {
  // Get the transaction that created this UTXO
  const tx = await getTxDetails(env, utxo.txid);

  // Look for OP_RETURN memo in the user's payment
  const memo = parseOpReturnMemo(tx);
  if (!memo) return null; // not a Time Vault payment

  // Parse: TV-{V_hex_prefix}-{P2WSH_address}
  const parts = memo.split("-");
  if (parts.length < 3 || parts[0] !== "TV") return null;

  const V = parts[1];
  const p2wshAddress = parts.slice(2).join("-"); // address may theoretically contain dashes

  // Check if already funded (dedup)
  if (await isVaultFunded(env, V)) {
    console.log(`Vault ${V} already funded, skipping`);
    return null;
  }

  // Calculate amounts
  const totalSats = utxo.value;
  const feeSats = 250; // ~250 vBytes × 1 sat/vB
  const donationSats = Math.floor(totalSats * 0.01);
  const bountySats = totalSats - donationSats - feeSats;

  if (bountySats < 330) {
    console.log(`Payment too small: ${totalSats} sats, bounty would be ${bountySats}`);
    return null;
  }

  // TODO: Build and broadcast the funding transaction using bitcoinjs-lib.
  // This requires:
  // 1. Import the Worker's private key from WORKER_PRIVATE_KEY (WIF)
  // 2. Create a PSBT with:
  //    - Input: the UTXO we're spending
  //    - Output 0: bountySats to p2wshAddress
  //    - Output 1: OP_RETURN with vault URL
  //    - Output 2: donationSats change back to donation address
  // 3. Sign and broadcast via mempool.space POST /api/tx
  //
  // For now, log the intent:
  console.log(`Would fund vault ${V}: ${bountySats} sats → ${p2wshAddress}`);

  return V;
}

export default {
  /** HTTP trigger — manual processing. */
  async fetch(request: Request, env: Env): Promise<Response> {
    if (!env.DONATION_ADDRESS || !env.WORKER_PRIVATE_KEY) {
      return new Response("Worker not configured", { status: 503 });
    }

    try {
      const utxos = await getUTXOs(env);
      const results: string[] = [];

      for (const utxo of utxos) {
        if (!utxo.status.confirmed) continue; // wait for confirmation
        const v = await processUTXO(env, utxo);
        if (v) results.push(v);
      }

      return new Response(
        JSON.stringify({ processed: results.length, vaults: results }),
        { headers: { "Content-Type": "application/json" } },
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      return new Response(JSON.stringify({ error: message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  },

  /** Scheduled trigger — runs every 5 minutes. */
  async scheduled(event: ScheduledEvent, env: Env): Promise<void> {
    if (!env.DONATION_ADDRESS || !env.WORKER_PRIVATE_KEY) return;

    const utxos = await getUTXOs(env);
    for (const utxo of utxos) {
      if (!utxo.status.confirmed) continue;
      await processUTXO(env, utxo);
    }
  },
} satisfies ExportedHandler<Env>;
