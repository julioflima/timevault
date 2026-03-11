/**
 * Bitcoin integration — P2WSH hashlock address generation + BIP21 QR.
 *
 * Given a seed S (from vault encryption), computes:
 *   - SHA256(S) as the hashlock target
 *   - P2WSH address from script: OP_SHA256 <SHA256(S)> OP_EQUAL
 *   - BIP21 URI for the Worker's donation address
 *   - QR code data URL
 */

import * as bitcoin from "bitcoinjs-lib";
import { sha256 } from "@noble/hashes/sha2.js";
import QRCode from "qrcode";

// Worker's donation address — all payments go here first.
// The Worker forwards 99% to the P2WSH bounty address.
const DONATION_ADDRESS = ""; // TODO: set Worker's Bitcoin address

// OP_RETURN URL prefix
const URL_PREFIX = "https://julioflima.github.io/timevault/v/";

/**
 * Build the hashlock redeem script: OP_SHA256 <SHA256(S)> OP_EQUAL
 */
function buildHashlockScript(seedBytes: Uint8Array): Buffer {
  const hash = sha256(seedBytes);
  return bitcoin.script.compile([
    bitcoin.opcodes.OP_SHA256,
    Buffer.from(hash),
    bitcoin.opcodes.OP_EQUAL,
  ]);
}

/**
 * Derive the P2WSH address from a seed S.
 * This is the address where the bounty will be locked.
 */
export function getP2WSHAddress(seedHex: string): string {
  const seedBytes = Uint8Array.from(Buffer.from(seedHex, "hex"));
  const redeemScript = buildHashlockScript(seedBytes);
  const p2wsh = bitcoin.payments.p2wsh({
    redeem: { output: redeemScript },
    network: bitcoin.networks.bitcoin,
  });
  return p2wsh.address!;
}

/**
 * Build OP_RETURN data for the funding transaction.
 * Format: URL pointing to the vault file.
 */
export function buildOpReturnData(V: string): Buffer {
  const url = `${URL_PREFIX}${V}.vault.json`;
  return Buffer.from(url, "utf8");
}

/**
 * Build a BIP21 URI for payment to the Worker's donation address.
 * The memo contains routing info: TV-{V_hex}-{P2WSH_address}
 */
export function buildBIP21URI(
  V: string,
  seedHex: string,
  amountBTC?: number,
): string {
  if (!DONATION_ADDRESS) {
    return "";
  }

  const p2wshAddr = getP2WSHAddress(seedHex);
  const memo = `TV-${V.slice(0, 16)}-${p2wshAddr}`;

  let uri = `bitcoin:${DONATION_ADDRESS}`;
  const params: string[] = [];

  if (amountBTC && amountBTC > 0) {
    params.push(`amount=${amountBTC.toFixed(8)}`);
  }
  params.push(`message=${encodeURIComponent(memo)}`);

  if (params.length > 0) {
    uri += "?" + params.join("&");
  }

  return uri;
}

/**
 * Generate a QR code data URL for a BIP21 URI.
 */
export async function generateQRDataURL(
  bip21URI: string,
): Promise<string> {
  if (!bip21URI) return "";
  return QRCode.toDataURL(bip21URI, {
    width: 256,
    margin: 2,
    color: { dark: "#000000", light: "#ffffff" },
  });
}

/** Check if the donation address is configured. */
export function isDonationConfigured(): boolean {
  return DONATION_ADDRESS.length > 0;
}

export type BitcoinInfo = {
  p2wshAddress: string;
  bip21URI: string;
  qrDataURL: string;
  opReturnURL: string;
};

/**
 * Compute all Bitcoin info for a vault.
 * Returns P2WSH address, BIP21 URI, QR data URL, and OP_RETURN URL.
 */
export async function computeBitcoinInfo(
  V: string,
  seedHex: string,
  amountBTC?: number,
): Promise<BitcoinInfo> {
  const p2wshAddress = getP2WSHAddress(seedHex);
  const bip21URI = buildBIP21URI(V, seedHex, amountBTC);
  const qrDataURL = bip21URI ? await generateQRDataURL(bip21URI) : "";
  const opReturnURL = `${URL_PREFIX}${V}.vault.json`;

  return { p2wshAddress, bip21URI, qrDataURL, opReturnURL };
}
