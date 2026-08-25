#!/usr/bin/env python3
"""build_rwa_target_list.py — build the tokenized-RWA target-list corpus (register).

Maps the XRPL (~42-asset) + EVM universe tokenized-RWA research into a structured,
measurement-ready target list for the attestation engine. Each record is a *target* for a
future signed attestation — it is a MEASUREMENT TARGET LIST, not a certification, and never
records a score. The register + neutrality verbatim ride every record.

Doctrine (verbatim from canon):
  REGISTER = "This is a measurement target list. It is not a certification, endorsement, or
             conformity mark, and must not be presented as one."
  NEUTRALITY = "records the measured target, never certifies it"

HONEST SCOPE: r-addresses and outstanding figures are *reported* from the cited sources
(Blockworks State of XRP Q2 2026; XRP Dashboard/xrpl.fi Aug 2026) and must be re-verified on
XRPScan before publication. `value_usd` is the REPORTED figure, not independently verified.
Represented vs distributed value is flagged explicitly (e.g. Justoken JMWH $2.23B is
held entirely by the issuer — represented, not distributed). This is opportunity-mapping for
strategic planning, not execution or investment advice.
"""
import json
import os
import time

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
OUT_DIR = os.path.join(HOME, "assets", "registers", "rwa")

REGISTER = ("This is a measurement target list. It is not a certification, endorsement, or "
            "conformity mark, and must not be presented as one.")
NEUTRALITY = "records the measured target, never certifies it"
SOURCE = ("Blockworks, State of XRP Q2 2026 (42-asset XRPL registry, $4.46B tokenized RWA); "
          "RWA.xyz / CoinGecko RWA Report 2026; XRP Dashboard / xrpl.fi (Aug 2026); "
          "industry announcements.")

# XRPL instruments (verified r-address where published): [name, ticker, asset_class,
#   issuer, r_address|None, structure, value_rep_usd|None, value_distributed_usd|None, note]
XRPL = [
    ["Ondo Short-Term US Gov Treasuries", "OUSG", "treasury", "Ondo Finance",
     "rHuiXXjHLpMP8ZE9sSQU5aADQVWDwv6h5p", "tokenized treasury fund (BUIDL-backed)", 183_000_000, None,
     "~1.83M OUSG outstanding (~$183M), XRPL 11 Jun 2025; QP only; multi-chain"],
    ["Ripple USD", "RLUSD", "stablecoin", "Ripple (NYDFS trust charter)",
     "rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De", "tokenized USD stablecoin", 963_000_000, None,
     "~962.78M on XRPL, ~$1.7B XRPL+ETH; Deloitte-attested reserves"],
    ["Archax x abrdn USD Liquidity Fund", "ABRDN-MMF", "institutional-fund", "Archax/abrdn",
     "rKCu4CucpepQ6N89c8T5GuX2jkxzCST18Q", "tokenized money-market fund (Lux MMF)", None, None,
     "first tokenized MMF on XRPL 25 Nov 2024; professional investors; no active on-ledger issue at fetch"],
    ["OpenEden TBILL", "TBL", "treasury", "OpenEden", "rJNE2NNz83GJYtWVLwMvchDWEon3huWnFn",
     "tokenized US T-bills", None, None, "~9.92B fractional units; second tokenized treasury on XRPL"],
    ["Aviva Investors USD Liquidity Fund", "AVIVA", "institutional-fund", "Aviva Investors",
     None, "tokenized UCITS MMF (BNY Mellon custody; Komainu digital custody)", None, None,
     "first Aviva fund tokenization, XRPL 29 Jul 2026; RLUSD cash leg"],
    ["Guggenheim Digital Commercial Paper", "DCP", "commercial-paper", "Guggenheim Treasury Services",
     None, "tokenized commercial paper via SPV (Great Bridge Capital)", None, None,
     "Prime-1 Moody's; QIB/QP; $280M+ volume"],
    ["Braza Bank USDB", "USDB", "stablecoin", "Braza Group/Braza Bank", "rB3y9EPnq1ZrZP3aXgfyfdXQThzdXMrLMc",
     "USD stablecoin (US/Brazil bonds)", 21_580_000, None, "~21.58M USDB (Aug 2026)"],
    ["Braza Bank BBRL", "BBRL", "stablecoin", "Braza Group", "rH5CJsqvNqZGxrMyGaqLEoMWRYcVTAPZMt",
     "BRL stablecoin", 8_270_000, None, "~41.35M BBRL at ~$0.20 (Aug 2026)"],
    ["Justoken JMWH", "JMWH", "commodity", "Justoken", None,
     "energy-backed commodity token", 2_230_000_000, None,
     "REPRESENTED value $2.23B held entirely by issuer (NOT distributed); ~half of XRPL RWA total"],
    ["GateHub XAU", "XAU", "commodity", "GateHub", None,
     "tokenized gold (1 g/token)", None, None, "settles on XRPL DEX"],
    ["Schuman Financial EURØP", "EURP", "stablecoin", "Schuman Financial", None,
     "MiCA-compliant EUR stablecoin", None, None, "first MiCA euro stablecoin natively on XRPL; KPMG-audited"],
    ["Societe Generale-FORGE EURCV", "EURCV", "stablecoin", "SG-FORGE", None,
     "MiCA euro stablecoin", None, None, "EURCV on XRPL; Euro settlement asset"],
    ["Ctrl Alt / Dubai Land Dept real estate", "DLD-RE", "real-estate", "Ctrl Alt (VARA)/Dubai Land Dept",
     None, "Asset-Referenced Virtual Asset + ownership tokens", 5_000_000, None,
     "Phase 1 10 properties >$5M; Phase 2 2026 secondary trading; target AED 60bn by 2033"],
    ["SBI START Bond", "SBI-ST", "bond", "SBI Holdings", None,
     "security-token bond (¥10bn, BOOSTRY ibet for Fin)", 64_500_000, None,
     "Japan first retail security-token bond; XRP rewards; Osaka Digital Exchange START"],
    ["Kyobo Life tokenized gov-bond pilot", "KYOBO", "bond", "Kyobo Life Insurance", None,
     "tokenized government-bond settlement pilot", None, None, "directly relevant to tokenized insurance"],
    ["Ctrl Alt / Billiton diamonds", "DIA", "commodity", "Ctrl Alt/Billiton", None,
     "tokenized diamonds", None, None, "~$280M announced"],
    ["Circle USDC", "USDC", "stablecoin", "Circle", None, "USD stablecoin (xrpl native)", None, None,
     "Circle USDC issues natively on XRPL"],
]

# EVM clusters (issuer -> instruments), aggregated not contract-exhaustive.
EVM_CLUSTERS = [
    {"cluster": "Securitize", "issuer": "Securitize", "count": "130+ tokens, $4.6B+ administered",
     "flagships": ["BlackRock BUIDL ($2.1B+ across 8 chains; BNY custody, PwC auditor)",
                   "Apollo Diversified Credit (ACRED)", "VanEck VBILL",
                   "Hamilton Lane / KKR tokenized private-market feeders"],
     "note": "DS Token standard (ERC-20 ext); 2026 per-investor on-chain vault; 2,000-investor cap"},
    {"cluster": "Ondo Finance", "issuer": "Ondo Finance", "count": "OUSG + USDY + Ondo Stocks 438+",
     "flagships": ["OUSG ($690M+ historically; BUIDL-backed)", "USDY (yield-bearing stablecoin)",
                   "Ondo Stocks 438+ tokenized US stocks/ETFs across ETH/SOL/BNB; $1B+ TVL"],
     "note": "daily attestations at regulated US entities; SPV + independent director; Broadridge proxy-vote"},
    {"cluster": "Backed Finance", "issuer": "Backed Finance", "count": "60+ tokenized equities/ETFs",
     "flagships": ["bCSPX (Core S&P 500)", "bIB01 (iShares 0-1yr Treasury)", "bNVDA", "bCOIN",
                   "bTSLA", "bMSFT", "bGME", "bMSTR", "bGOOGL"],
     "note": "ERC-20 tracker certificates 1:1; Swiss/Jersey SPV; xStocks line 55+ on Kraken/Solana"},
    {"cluster": "Franklin Templeton", "issuer": "Franklin Templeton", "count": "BENJI (FOBXX)",
     "flagships": ["Franklin OnChain US Government Money Fund (FOBXX)"], "note": "tokenized MMF, yield pass-through"},
    {"cluster": "Superstate", "issuer": "Superstate", "count": "USTB + USCC",
     "flagships": ["USTB (Short Duration US Gov Securities)", "USCC (Crypto Carry Fund)"],
     "note": "managed-whitelist model"},
    {"cluster": "Hashnote", "issuer": "Hashnote", "count": "USYC",
     "flagships": ["USYC (tokenized Treasury/money-market)"], "note": "institutional"},
    {"cluster": "Centrifuge", "issuer": "Centrifuge", "count": "tokenized private-credit pools",
     "flagships": ["Tinlake successor pools"], "note": "protocol-level KYC"},
    {"cluster": "Commodity/other", "issuer": "Paxos / Tether / Dinari", "count": "PAXG, XAUT, dShares",
     "flagships": ["Paxos Gold (PAXG ~$1B+)", "Tether Gold (XAUT ~$1B+)", "Dinari dShares"],
     "note": "tokenized gold + tokenized US equities"},
]

def record(name, ticker, ac, issuer, addr, struct, v_rep, v_dist, note):
    return {
        "schema": "csoai.rwa-target/0.1",
        "kind": "target-list-record",
        "name": name, "ticker": ticker, "asset_class": ac, "issuer": issuer,
        "r_address": addr, "structure": struct,
        "value_usd_reported": v_rep,
        "value_usd_distributed": v_dist,
        "note": note,
        "register": REGISTER, "neutrality": NEUTRALITY,
        "_provenance": {"source": SOURCE, "verified": False,
                        "verify_note": "re-verify r-address on XRPScan before publication"},
    }

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = [record(*r) for r in XRPL]
    # index payload
    index = {
        "schema": "csoai.rwa-target-list/0.1",
        "kind": "measurement target list",
        "counts": {
            "xrpl": len(XRPL),
            "evm_clusters": len(EVM_CLUSTERS),
            "total": len(XRPL) + len(EVM_CLUSTERS),
        },
        "note": "target list for future signed attestations; NOT a certification of any issuer",
        "register": REGISTER, "neutrality": NEUTRALITY,
        "sources": SOURCE,
        "caveats": [
            "REPRESENTED vs DISTRIBUTED value: headline XRPL figures (e.g. Justoken JMWH $2.23B held entirely by issuer) overstate genuine adoption; distributed RWA value was only $386.1M in Q2 2026.",
            "r-addresses and outstanding figures are REPORTED (Blockworks Q2 2026; XRP Dashboard/xrpl.fi Aug 2026); verify each on XRPScan before publication.",
            "Total-RWA figures conflict (RWA.xyz >$24B vs CoinGecko RWA Report 2026 $19.32B); cite the source explicitly.",
            "No explicit bank mandate for independent third-party verification found; the 'blocker' case rests on IOSCO/OECD/ECB framing + vendor sources (some commercial bias).",
            "This is opportunity-mapping for strategic planning, not execution or investment advice.",
        ],
        "legal": "Unsolicited attestation attached to third-party regulated securities may raise defamation, 'unsolicited rating'/NRSRO-adjacent, market-abuse and data-liability questions per jurisdiction; obtain counsel before publishing risk-negative attestations on named issuers.",
    }
    json.dump(index, open(os.path.join(OUT_DIR, "index.json"), "w"), indent=2)
    with open(os.path.join(OUT_DIR, "xrpl.jsonl"), "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    # cluster summary
    json.dump({"schema": "csoai.rwa-target/0.1", "kind": "evm-clusters",
               "clusters": EVM_CLUSTERS, "register": REGISTER, "neutrality": NEUTRALITY},
              open(os.path.join(OUT_DIR, "evm-clusters.json"), "w"), indent=2)
    print(f"wrote {len(XRPL)} xrpl rows + {len(EVM_CLUSTERS)} evm clusters -> {OUT_DIR}")

if __name__ == "__main__":
    main()
