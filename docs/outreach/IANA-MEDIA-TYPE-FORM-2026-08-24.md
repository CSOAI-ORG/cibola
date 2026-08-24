# IANA media-type registration — STAGED form text (do NOT submit; owner-gated)

**Registration request for:** `application/vnd.cibola.measurement-card+json`
**Status of this file:** STAGED — drafted for the IANA application-form process. Per the
Ralph hard stop, this is **never** submitted/sent by an agent. It is the text of the
media-types@ / registration-form application body, kept here so the owner can paste it into
the IANA form when the send window opens.

**Week theme:** the first mover in the verification gap. This type registers a signed,
stranger-verifiable measurement credential — a **verified measurement credential**, never a
certification. The slug decision was logged 2026-08-24 (brand: CIBOLA = public protocol
name; DORADO = internal codename).

---

## IANA application-form body (RFC 6838 vendor tree)

**Type name:** application

**Subtype name:** vnd.cibola.measurement-card+json

**Required parameters:** none

**Optional parameters:** none

**Encoding considerations:** The payload is a JSON object (RFC 8785 canonical form for the
signed portion). It is UTF-8; no 8-bit binary content is carried, so no
`charset`/`Content-Transfer-Encoding` parameter is required. A card is normally JSON-encoded.

**Security considerations:** A measurement card is a *signed* record. Consumers MUST verify
the Ed25519 signature against the publisher's published `did:web` key before relying on any
field, and should treat an unverifiable or non-published-key card as untrusted. The card
carries a register it is a measurement credential, never a certification or conformity mark,
and consumers must not present it as one. The signed payload should be canonicalized (RFC
8785) before verification to avoid signed-data ambiguity. Receipt binding is authenticated by
a separate signature; a bare, unverified card must not be used as evidence. There is no
executable or active content in the payload.

**Interoperability considerations:** The format is designed to be verified offline by any
party with the public key (only `cryptography` + ASN.1 support are needed). Because the type
is vendor-tree (`vnd.`), interoperability is scoped to implementors who implement the
published specification; a standards-tree migration is recorded as intended in the
specification should the format reach working-group adoption.

**Published specification:** `draft-csoai-scitt-measurement-card-00` (the measurement-card
format, on the RFC 9943 / RFC 9942 substrate), available in the developer repository
`https://github.com/CSOAI-ORG/cibola` under `draft/`.

**Applications that use this media type:** The CIBOLA measurement-card exchange, the
stranger-verification surface (`/verify`), the offline verify-kit, and the append-only
measurement register/binding. The type distinguishes a signed measurement credential from a
scoring payload.

**Fragment identifier considerations:** none.

**Additional information:**
- *Magic number(s):* none (JSON).
- *File extension(s):* `.card.json` (informative only).
- *Macintosh file type code(s):* none.

**Person & email address to contact:** CSOAI Ltd (Council of AI), UK Companies House
16939677; `did:web:csoai.org`.

**Intended usage:** COMMON — an interoperable, verifiable exchange format for the result of a
measurement (which the publisher attests via signature + receipt). Not restricted to a single
vendor.

**Restrictions on usage:** none beyond the security considerations above.

**Author / Change controller:** CSOAI Ltd (Council of AI).

---

## Post-send checklist (owner-gated, never agent-sent)

- [ ] Submit the application form to IANA (`media-types@iana.org` + the form).
- [ ] Same-day follow-up post to the `media-types@` list.
- [ ] Update the standards-engagement log (move 72) with the submission + ticket.
- [ ] Re-run `test/grammar-lint.py` + `test/banned-strings.py` (this file is STAGED).
