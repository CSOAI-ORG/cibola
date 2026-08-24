# AIP-01 Verifier-Matrix — staged corrections (2026-08-24, NOT yet raised)

**Context:** audit `aip-01-verifier-matrix-audit-20260823.md` reviewed public experiment AIP-MATRIX-FIT-001 at frozen commit 8ed65b70 with 17/17 tests green and all pinned source SHA-256s matching. The matrix's conclusions stay within the two pinned drafts — but the audit found four corrections needed before this becomes citable evidence.

## Correction set (staged patch text — raise after owner nod; raising = external comms)
1. **Split artifact identity from live-instance identity.** Matrix marks `identity` row EXACT mapped to Principal Binding C-001. C-001 asks which live agent/runtime/workload/endpoint — the matrix maps a *draft artifact* identity instead. Fix: row semantics = "artifact identity" EXACT; add new row `live-instance identity` = NOT COVERED (C-001 requires runtime evidence, absent in matrix).
2. **Wrong-presenter case** — supported (AIP-01 §5.3 bearer credential): wording fix: "AIP does not authenticate the presenter" → "AIP does not authenticate the *presenter's liveness*; binding to presentation context is out of AIP-01 scope."
3. **Same-control verifier case** — keep as-is but add explicit "no control-domain separation check defined in AIP-01" as a *known scope gap* rather than an implied weakness.
4. **Stale-evidence case** — add note: `verification_status` freshness procedure is undefined in AIP-01; matrix correctly refuses to infer one. Add one line to the report: "frameworks wishing to assert freshness MUST specify a procedure; AIP-01 does not."

## Why these matter (strategic)
The verifier-matrix is our entry artifact into the agent-protocol security conversation (alongside AG-UI audio + MCP #426). A matrix that over-claims EXACT mapping is the same disease as an over-claiming benchmark. Do the honesty at the artifact level: the correction patch turns a reviewer finding into public discipline — credibility deposit, and free.

## Repro facts (for the patch body)
- repo: github.com/Silentpartnercoding/agent-security-verifier-matrix @ 8ed65b70f8933a659dcab00331d86bac40009abe
- matrix/case freeze 815281df · evaluator 7189bebf · results.json sha256 d574a9b2…c69
- all six sources byte-matched (table in audit doc)

*End. Raise via issue/PR only after owner nod (external comms gate).*
