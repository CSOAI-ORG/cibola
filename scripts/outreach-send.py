#!/usr/bin/env python3
"""outreach-send.py — send the audited, non-cost external batch from nicholas@csoai.org.

Every send REQUIRES a pre-existing contact row (audit-first) and is archived +
logged into connections.db. Run:  python3 scripts/outreach-send.py
"""
import os, sys, ssl, smtplib, datetime, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "connections"))
import conn as connmod

SMTP_HOST, SMTP_PORT = "smtp.privateemail.com", 465
FROM = "nicholas@csoai.org"
ARCH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "connections", "mail-archive",
                    datetime.date.today().isoformat())
os.makedirs(ARCH, exist_ok=True)
# The mail password is sourced ONLY from the environment — never hardcoded/committed.
PW = os.environ.get("CSOAI_MAIL_PW")
if not PW:
    raise SystemExit("CSOAI_MAIL_PW not set — refusing to send (no hardcoded password). "
                     "Export it in your shell or a gitignored env file, then re-run.")

SIG = "\n\nBest regards,\nNicholas Templeman\nFounder, Council of AI (CSOAI Ltd, UK 16939677)\ncouncilof.ai · csoai.org\nWe measure, sign and preserve the evidence; regulators and accredited bodies decide."

MAILS = [
 {
  "to": "media-types@iana.org",
  "subject": "Proposed media type: application/vnd.cibola.measurement-card+json",
  "body": (
"Hello,\n\nI'd like to request community review of a proposed vendor-tree media type for signed AI "
"measurement cards, per RFC 6838 section 5.6:\n\n"
"Type name: application\nSubtype name: vnd.cibola.measurement-card\nRequired parameters: none\n"
"Optional parameters: profile (URL of the card profile)\n"
"Encoding considerations: JSON (UTF-8), 8bit\n\n"
"Security considerations: the payload is a self-contained measurement credential — signed "
"(COSE_Sign1, Ed25519), content-addressed, with an optional transparency-service receipt "
"(RFC 9943). Verifiers must treat it as data, never as certification; the card embeds an explicit "
"measurement-not-approval disclaimer. No executable content.\n\n"
"Interoperability: the format is the score layer above the standardized SCITT receipts — "
"profiles exist as individual IETF drafts (draft-csoai-scitt-measurement-card-00).\n"
"Published specification: please see the draft + conformance suite in the repo (link on request).\n\n"
"Use: independent AI measurement bodies, benchmark operators and regulators exchanging "
"verifiable measurement evidence across jurisdictions.\n\n"
"Happy to answer expert-review questions promptly."
 )
 },
 {
  "to": "hello@metr.org",
  "subject": "Signed provenance for your next published result — an offer from an outside measurement body",
  "body": (
"Hello METR team,\n\nYour GPT-5.6 Sol finding landed with force, and the question it raised is the one we "
"build for: a result is only as good as its provenance, and narrating evidence is not the same as "
"binding it.\n\nI'm Nicholas Templeman, founder of Council of AI (CSOAI Ltd, UK) — an independent "
"measurement body. We do exactly one thing: we take a measurement, sign it (Ed25519), anchor it in "
"transparency services (RFC 9943 receipts), and publish a stranger-verify page so anyone can check "
"the card offline in 60 seconds, forever. We certify nothing and we never take money from the "
"scored — our zero-lab-token policy is a written policy, not a slogan.\n\nWhat I'm offering, in three "
"bullet points:\n1. A 45-minute walkthrough (async works too) — measure -> card -> dual receipts -> "
"stranger-verify.\n2. Co-sign one of your published results with our attestation wrapper, so your "
"number carries an independent, verifiable fingerprint.\n3. A no-strings re-measurement swap: we "
"re-run one of your headline benchmarks in our deterministic harness and publish with a method note "
"— you keep the raw data either way.\n\nThe referee market is consolidating fast (Vals, LMArena, "
"Braintrust are now under one roof), and the only inventory left unsold is independence. If that "
"interests you, a 15-minute reply or call is enough to start."
 )
 },
 {
  "to": "giulio.tanganelli@equidam-88d5f8b18090.intercom-mail.com",
  "subject": "Re: Is your valuation ready to be used outside Equidam?",
  "body": (
"Hi Giulio,\n\nYes — and now is exactly the right moment. The valuation is moving from an internal "
"exercise into a real conversation: I'm preparing investor and partner conversations, and the "
"underlying asset story has been independently profiled (an Inngot Goldseam IP profile this month "
"and Tracxn now tracking the company), so I need the valuation to be defendable and quoteable "
"outside the tool.\n\nA bit of context that helps the full report land: the company (CSOAI Ltd, UK "
"16939677) runs an IP-backed platform — a signed-measurement engine published on PyPI (55-package "
"monorepo), three DOI-registered papers, trade-mark applications in flight, held-out item banks "
"kept as trade secrets, and two domain assets in active use.\n\nAlso — our 30-minute call on 19 "
"August was canceled at short notice; could we reschedule for this Thursday or Friday (10:30–11:00 "
"works)? Better yet, I'll book a slot from Equidam's calendar and we can combine the reschedule with "
"the full-report handoff.\n\nThanks — looking forward to the next step."
 )
 },
 {
  "to": "drcf@fca.org.uk",
  "subject": "DRCF Phase 2 submission — signable, verifiable incident and post-market-monitoring feeds for AI regulation",
  "body": (
"Dear DRCF team,\n\nI'm writing in response to your Phase 2 work programme, on behalf of Council of AI "
"(CSOAI Ltd, UK 16939677) — an independent AI measurement body. We measure, sign and preserve "
"evidence; regulators decide. We are not a notified body, we certify nothing, and we claim no "
"accreditation.\n\nOur submission is short and concrete: a working prototype of signed feeds for "
"two obligations that Phase 2 already touches — Article 73 serious-incident reporting (15-day/24h "
"clock fields, near-miss scope) and Article 72 post-market monitoring (daily continuous stream), "
"each emitted as Ed25519-signed cards with RFC 9943 (SCITT) receipts, a public verification path, "
"and regulator-facing pre-commitment terms modeled on the FAA ASRS structure — the immunity "
"pre-commitment is exactly why aviation's feed flows, and we offer the same shape in writing.\n\nWhy "
"this matters now: the October 2026 Digital Omnibus (Reg 2026/174) keeps both obligations live for "
"high-risk systems, and the market has zero signed feeds today — regulators receive channel-"
"authenticated but unsigned data. Signed, DNS-anchored, offline-verifiable evidence is the "
"difference between reading someone's email and auditing their record.\n\nWe're happy to demo the "
"prototype, share the schema, and align the fields with any implementing act or guidance you are "
"drafting. The full submission pack (schema, sample cards, verification kit, pre-commitment terms) "
"is available on request.\n\nThank you for your time."
 )
 },
]

def send(m):
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
        s.login(FROM, PW)
        msg = f"From: Nicholas Templeman <{FROM}>\nTo: {m['to']}\nSubject: {m['subject']}\n\n{m['body']}{SIG}"
        s.sendmail(FROM, [m['to']], msg.encode('utf-8') if isinstance(msg, str) else msg)
    with open(os.path.join(ARCH, m['to'].replace('@','_at_') + ".txt"), 'w') as f:
        f.write(f"To: {m['to']}\nSubject: {m['subject']}\n\n{m['body']}{SIG}\n")
    connmod.connmod = None
    c = connmod.conn()
    connmod.log_msg(c, m['to'], m['subject'], 'out', 'sent', m['body'][:400], os.path.join(ARCH, m['to']))
    c.commit(); c.close()
    print(f"SENT: {m['to']} | {m['subject'][:60]}")

if __name__ == '__main__':
    for m in MAILS:
        try:
            send(m)
        except Exception as e:
            print(f"FAIL {m['to']}: {type(e).__name__}: {str(e)[:120]}")
