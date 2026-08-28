#!/usr/bin/env node
/* jcs-js.mjs — canonicalize the same corpus with the `canonicalize` npm lib (RFC 8785),
   emit sha256 per case. Cross-language agreement = the cutover gate (roadmap item 1). */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import canonicalize from "canonicalize";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const corpus = JSON.parse(readFileSync(join(dir, "corpus.json"), "utf8"));
const out = { js_jcs: {} };
for (const c of corpus) {
  const jcs = canonicalize(c.value);
  out.js_jcs[c.name] = createHash("sha256").update(jcs, "utf8").digest("hex");
}
console.log(JSON.stringify(out, null, 1));
