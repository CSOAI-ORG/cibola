# WHITE-LABEL EMBED KIT — build-ready spec + code · 2026-08-25

**Standard to meet (what "white-label to Council OS standard" means):** a partner embeds our
measurement evidence under THEIR brand in one line of HTML, with zero cookies, zero tracking, and
the honest grammar locked (measurement, never certification). Anyone can verify the underlying
card offline, anywhere.

**Current state:** `/api/badge` works (1303 B SVG, aria-label) — but `/badge`, `/embed.js`,
`/badge.js`, `/embed`, `/api/embed`, `/verify-embed`, `/embed-kit`, `/white-label` are ALL 404
(verified 25 Aug). **Gap = badge-only → full brand-swappable embed.**

## 1. embed.js (drop-in, zero deps, ~100 lines)

```js
/* councilof.ai/embed.js — Council of AI white-label embed (MIT, CC0 spirit)
   Usage:
   <script async defer src="https://councilof.ai/embed.js"
           data-org="ClientCo" data-brand="#0B3D91" data-label="AI Verified"
           data-verify="https://clientco.example/verify/m" data-size="md"></script> */
(function () {
  var s = document.currentScript; if (!s) return;
  var org = s.getAttribute('data-org') || 'Council of AI';
  var brand = s.getAttribute('data-brand') || '#0B3D91';
  var label = s.getAttribute('data-label') || 'GSPC: 14 measured of 14 quotable';
  var verify = s.getAttribute('data-verify') || 'https://councilof.ai/gspc-verify';
  var size = s.getAttribute('data-size') || 'md';
  var w = { sm: 180, md: 260, lg: 340 }[size] || 260;
  var host = document.createElement('div');
  host.setAttribute('class', 'coai-embed');
  host.setAttribute('aria-label', label);
  host.innerHTML =
    '<div style="border:1px solid ' + brand + ';border-radius:12px;padding:14px;font-family:-apple-system,Segoe UI,sans-serif;max-width:' + w + 'px">' +
      '<div style="color:' + brand + ';font-weight:700;font-size:13px">' + org + '</div>' +
      '<div style="margin:6px 0;font-size:15px;letter-spacing:1px;color:' + brand + '">◇ ' + label + '</div>' +
      '<a href="' + verify + '" target="_blank" rel="noopener" style="display:block;font-size:11px;color:' + brand + ';text-decoration:none">' +
      'Verify the evidence — recompute it yourself, client-side →</a>' +
      '<div style="font-size:10px;color:#666;margin-top:6px">Measurement, not certification. Council of AI is not a notified body.</div>' +
    '</div>';
  (s.parentNode || document.body).insertBefore(host, s);
})();
```

## 2. Badge landing page (`/badge`) — the human-facing kit
- Renders: live SVG badge + embed snippet + email-mobile syntax + `<script>` snippet + brand columns
  (name, hex color, verify URL) + the honest one-liner and the "partner branding does not change the
  evidence" note. Source: `/api/badge` (already live) — one static page, no state.
- `/api/embed`: returns `{badge: "https://councilof.ai/api/badge", script: "https://councilof.ai/embed.js", verify: "https://councilof.ai/gspc-verify", grammar: "measurement, not certification"}` — machine-consumable, 200.

## 3. Brand-swap acceptance test (white-label e2e — the standard)
| check | pass condition |
|---|---|
| Load embed.js with `data-brand="#FF5733" data-org="Partner"` | renders Partner-colored card, no default branding leaked |
| Click verify link | opens partner's configured verify URL (default = councilof.ai/gspc-verify) |
| Content honesty | "Measurement, not certification" line present in EVERY render; `certified` never appears |
| Domain swap | partner mirrors `/api/badge` under their domain → still resolves (absolute-origin-free SVG) |
| No cookies/requests | embed makes exactly ONE request (the script) — verify via Network tab |
| Offline verify | card + receipt verify with the offline kit (no partner infra) |

## 4. Where it ships
- `/embed.js` → static asset in the client build (brand-gated: zero banned strings — the kit above is clean).
- `/badge` + `/api/embed` → 2 routes in the existing router; sitemap + prerender update; then the
  `/badges` homepage-fallthrough (verified) disappears because `/badge` (singular) is real and
  `/badges` can 301 → `/badge`.

## Why this is the revenue unlock
The white-label track is the same evidence under partner brands — partners sell attestation-shaped
services into their markets, we stay neutral below. One line of HTML + brand colors is the whole
onboarding cost. No pay-to-play: the badge is free; the measurement is the product.
