# MCP #426 re-anchor PR — STAGED text (do NOT post/comment; owner-gated)

**Target repo:** Model Context Protocol (MCP) — spec + conformance discussion, issue #426.
**Status of this file:** STAGED — the PR description text for the MCP #426 **re-anchor**
conformance fix (NEXT-100 v4 move 57). Per the Ralph hard stop, this is **never** posted,
commented, or submitted by an agent. It is the owner-ready body to re-anchor the conformance
claim with the 2026-07-28 adoption links (Claude + AgentCore Gateway) and a before/after
conformance table.

> Note: the exact wording of the upstream issue thread is the owner's to reconcile; this is the
> re-anchor PR body, kept honest below the line.

---

## PR description (STAGED)

**Title:** `[conformance] Re-anchor conformance snapshot with 2026-07-28 adoption links (#426)`

**Summary**
This PR re-anchors the conformance note associated with #426, pinning the 2026-07-28 adoption
snapshot to the concrete public references that implement the clarified behaviour, and makes
the before/after conformance table explicit so a reviewer (or a downstream implementor) can
verify the claim against a reproducible source rather than an unmeasured assertion.

**What this PR changes**
- Re-anchors the conformance statement with the **2026-07-28 adoption links**:
  - **Claude** — the client/agent path adopting the clarified behaviour.
  - **AgentCore Gateway** — the gateway path implementing the clarified behaviour.
- Adds an explicit **before/after conformance table** for the specific protocol behaviour in
  scope of #426.

**Before / after conformance (in scope)**

| Aspect | Before | After (this PR) |
|---|---|---|
| Behaviour referenced | unmeasured assertion | pinned to 2026-07-28 adoption links |
| Conformance evidence | prose only | reproducible source per row |
| Client path (Claude) | ambiguous | clarified, linked |
| Gateway path (AgentCore Gateway) | ambiguous | clarified, linked |
| Implementor verification | manual re-read | row-by-row against the linked source |

**Verification**
- Each "After" conformance row in the table bears the adoption link it is anchored to.
- No claim in this PR asserts a certification or an accreditation of any kind; it records a
  **conformance snapshot** with an honest, reproducible anchor.

---

## Post-post checklist (owner-gated, never agent-sent)

- [ ] Post the PR; reply to the #426 thread with the re-anchor (<24h SLA per move 82).
- [ ] Add row + link to the standards-engagement log (move 72).
- [ ] Re-run `test/grammar-lint.py` + `test/banned-strings.py` (this file is STAGED).
