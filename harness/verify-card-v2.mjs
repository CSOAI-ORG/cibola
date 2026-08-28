#!/usr/bin/env node
/* verify-card-v2.mjs — JCS-aware stranger verifier (RFC 8785 dispatch, move 1/9 of NEXT-100 v5).
 *
 * Three states, never two: VALID / INVALID(reason) / UNCHECKABLE.
 * Rule-aware preimage: canon == "jcs-rfc8785" -> RFC 8785 (JCS) bytes; absent -> legacy CPython v1.
 * Zero dependencies beyond node:crypto + the `canonicalize` lib for the JCS path (npm install
 * canonicalize, or swap in any RFC 8785 lib). Pins the published did:web key when given.
 *
 * Usage: node verify-card-v2.mjs card.json [expected_pubkey_b64]
 */
import { readFileSync } from "node:fs";
import canonicalize from "canonicalize";

const card = JSON.parse(readFileSync(process.argv[2], "utf8"));
const expectedKey = process.argv[3];

const sha256 = (b) =>
  crypto.subtle.digest("SHA-256", b).then((d) => [...new Uint8Array(d)].map((x) => x.toString(16).padStart(2, "0")).join(""));

// The v1 (CPython json.dumps) rule in JS needs two schema hints the site verifier uses:
// (1) FLOAT_FIELDS — keys whose integral values render with a trailing ".0" (CPython types);
// (2) ensure_ascii string escaping. JCS v2 removes both ambiguities by construction.
const FLOAT_FIELDS = new Set(["score", "latency_ms", "cost_usd", "value", "acc", "f1"]);

function jsonString(s) {
  let out = '"';
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (c === 34) out += "\\\"";
    else if (c === 92) out += "\\\\";
    else if (c < 0x20) out += "\\u" + c.toString(16).padStart(4, "0");
    else if (c < 0x80) out += ch;
    else out += "\\u" + c.toString(16).padStart(4, "0");
  }
  return out + '"';
}

function v1Canonical(obj) {
  const clean = { ...obj };
  delete clean.signature;  // canon absent on v1 cards
  function enc(value, key = null) {
    if (value === null) return "null";
    if (typeof value === "boolean") return value ? "true" : "false";
    if (typeof value === "number") {
      if (!Number.isFinite(value)) throw new Error("non-finite number");
      if (Number.isInteger(value) && FLOAT_FIELDS.has(key)) return value.toFixed(1);
      return String(value);
    }
    if (typeof value === "string") return jsonString(value);
    if (Array.isArray(value)) return "[" + value.map((v) => enc(v, key)).join(",") + "]";
    if (typeof value === "object") {
      const keys = Object.keys(value).sort();
      return "{" + keys.map((k) => jsonString(k) + ":" + enc(value[k], k)).join(",") + "}";
    }
    throw new Error("unserialisable");
  }
  return Buffer.from(enc(clean), "utf8");
}

function preimage(card) {
  if (card.canon === "jcs-rfc8785") {
    const clean = { ...card };
    delete clean.signature;   // canon stays: it is signed-in-body (the v2 rule)
    return Buffer.from(canonicalize(clean), "utf8");
  }
  return v1Canonical(card);
}

const s = card.signature;
if (!s || s.kind !== "ed25519") {
  console.log("UNCHECKABLE  ?  no Ed25519 signature (honestly-unsigned card)");
  process.exit(0);
}
let valid = false;
try {
  valid = await verifyEd25519(s.pubkey, s.sig, preimage(card));
} catch (e) {
  console.log(`UNCHECKABLE  ?  ${e.message}`);
  process.exit(0);
}

async function verifyEd25519(pubkeyB64, sigB64, msg) {
  const raw = Buffer.from(pubkeyB64, "base64");
  const sig = Buffer.from(sigB64, "base64");
  const key = await crypto.subtle.importKey("raw", raw, "Ed25519", false, ["verify"]);
  return crypto.subtle.verify("Ed25519", key, sig, msg);
}

if (valid) {
  if (expectedKey && s.pubkey !== expectedKey) {
    console.log("INVALID  !  signed by a key that is not the pinned identity");
    process.exit(1);
  }
  console.log(`VALID  ✓  (kid=${s.kid || "?"})  canon=${card.canon || "v1-legacy"}`);
  process.exit(0);
}
console.log("INVALID  !  signature does not verify — altered card or wrong key");
process.exit(1);
