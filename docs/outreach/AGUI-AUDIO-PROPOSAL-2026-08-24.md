# AG-UI audio proposal — STAGED issue text (do NOT post; owner-gated)

**Target repo:** AG-UI (agent-user interaction protocol) — spec + dojo.
**Status of this file:** STAGED — the proposal issue text, drafted for the AG-UI issue
tracker. Per the Ralph hard stop, this is **never** posted/commented by an agent. It is the
owner-ready issue body for the AG-UI **audio** proposal (NEXT-100 v4 move 58). The 14-day
fallback trigger is armed but not yet fired.

---

## Issue body (STAGED)

**Title:** Add an `audio` content/part type + `audio` channel for streaming user↔agent voice

**Summary**
The AG-UI protocol currently models agent→user output as text / reasoning / tool-call parts
and the user→agent direction as text / tool calls, over a small set of UI channels (text,
video, mcpServer). Real-time voice is the missing first-class interaction mode: a user should
be able to speak to an agent and hear an answer **without** bouncing an opaque blob through a
custom extension. This issue proposes a first-class, schema'd **audio** part + channel so
both directions are spec'd, cancellable, and testable in the dojo.

**Motivation**
- Voice is a primary modality for hands-free / high-throughput agent interaction, and the
  common case (a live agent loop) needs more than a final transcript appended to the end.
- Streaming audio needs explicit begin/fragment/end semantics + cancellation so a UI and an
  agent agree on what has and has not been spoken.
- A schema'd, versioned `audio` part keeps the protocol extensible while remaining
  deterministic and interoperable.

**Proposal**
1. Add a text-part `type: "audio"` (analogous to `"text"` / `"reasoning"` / `"tool-call"`),
   carrying a sequence of audio fragments with a transport hint:
   `{ audio: { mediaType, format, sequence, base64, durationMs, digest } }`.
2. Add a channel value `audio` (alongside `text`/`video`/`mcpServer`) for both
   server→user (`agent→ui`, streaming) and user→agent (`user→ui`, streaming).
3. Define cancellation: an `audio` part may be superseded by an explicit `stop` event, and the
   receiver must not treat a superseded fragment as final.
4. Keep the payload **measurement-neutral**: audio carries *content*, not a score or a
   judgment — it must never be mistaken for a certification or an assessment of the agent.

**Before / after (scope of the change)**

| Aspect | Before | After (proposed) |
|---|---|---|
| Voice content | opaque blob in a custom extension | schema'd `audio` part (fragments) |
| Channel | `text`/`video`/`mcpServer` | + `audio` (both directions) |
| Streaming | not specified | begin → fragment* → stop |
| Cancellation | unspecified | explicit `stop` supersedes fragments |
| Dojo coverage | none (not testable) | e2e audio round-trip + cancellation test |

**Reference / adoption links**
- AG-UI text/tool-call part schema + channel enum (current spec).
- AgentCore Gateway audio-transport example (integration reference).

**Tests (dojo)**
- `audio` part round-trip server→user and user→server.
- Fragment-sequencing + `base64` integrity (digest check on reassembly).
- `stop` supersedes in-flight fragments (cancellation not treated as final).
- Versioning: an older client ignores `audio` parts it does not understand.

---

## Post-post checklist (owner-gated, never agent-sent)

- [ ] Post the issue; link the follow-up PR (move 58's PR + dojo E2E tests).
- [ ] Add row + link to the standards-engagement log (move 72).
- [ ] Re-run `test/grammar-lint.py` + `test/banned-strings.py` (this file is STAGED).
