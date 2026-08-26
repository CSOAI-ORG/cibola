# THE $1.7B RATERS DON'T SIGN — and why that's now the whole story
*Council of AI · 2026-08-26 · measurement, never certification · staged for publish*

The market just wrote our thesis for us. In the last six weeks, the two most prominent
"independent scorekeepers" in AI evaluation raised extraordinary sums — **Arena Intelligence
(LMArena) took $150M at a $1.7B valuation, and Vals AI closed a $40M Series A led by a16z at
$400M**. The pitch that raised that money is exactly the one we build on: *every market
eventually needs an independent scorekeeper — sellers know more than buyers, and an outside
referee makes the market work.*

So the referee market exists now. The question nobody is answering: **how do you verify the
referee?**

Three things we checked, and what we found, published as a signed card on our board:

1. **Confidence intervals** — some raters do publish them. LMArena's Bradley-Terry CIs are a
   genuine strength; Scale's SEAL/HLE publishes rank upper-bounds. Credit where it's due; we
   measure it as MEASURED.
2. **An append-only corrections ledger** — none of the ten raters we surveyed publish one.
   When a leaderboard changes, the change is edited, not chained. Ours is a signed, append-only
   corrections register — every edit is a new record with its predecessor hashed in.
3. **Signed, verifiable results** — none of the ten sign a single result. No Ed25519 signature,
   no transparency-service receipt, no offline verifier. A benchmark number you cannot
   independently verify is a story about a number, not evidence about a number.

**This isn't a critique of their quality — it's a fact about their evidence layer.** We rated
each rater on these three criteria and published the card: ten raters, thirty cells, every
UNMEASURED cell honestly declared as "no public evidence found as of 26 August 2026" — never as
"they don't do it."

Why we can say this without being a competitor: we certify nothing, we take no money from the
scored, and every claim we make carries an Ed25519 signature, an RFC 9943 (SCITT) receipt, and
an OpenTimestamps Bitcoin anchor — verifiable offline, forever, without asking us.

**The offer stands for every rater on the card:** co-sign your next published result with our
attestation wrapper. Your numbers, your methodology; a fingerprint anyone can check. If the
scorekeeper market is real, it needs an evidence layer. That's the layer we build.

*— Nicholas Templeman, Founder, Council of AI (CSOAI Ltd, UK 16939677). Verified measurement
credential; not a certification, endorsement, or conformity mark.*
