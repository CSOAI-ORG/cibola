# DORADO — Runbook (all work OFF the Mac)

DORADO is the measurement body + engine. **The Mac is terminal-only.** All
measurement, mining, minting, chaining and backup run on the pod fleet (RunPod
3090 = `sov-brain-2`, A100 = `sovos-light-a100`) and Oracle volumes.

## Layout

| Path | What |
|---|---|
| `~/cibola` → `CSOAI-ORG/dorado` | the monorepo source of truth (git remote) |
| `/workspace/dorado` (3090 pod) | the live engine worktree the EAT loop runs from |
| `/workspace/dorado/board/` | the measurement board (content-addressed chain) |
| `/workspace/dorado-backup/` | durable pod-side snapshots (rotated to last 10) |
| Oracle `/evac-bulk/dorado-backup` | secondary off-pod backup destination |

## One EAT iteration (`scripts/dorado-eat.sh`)

```
MINE   measure a model on a domain registry via the pod's own Ollama
MINT   sign the card (Ed25519 COSE_Sign1; identity-gated — a non-published key is
       stamped kid=test, only --allow-test-identity, never mislabelled)
CHAIN  build the SCITT receipt + RFC 3161 anchor + publish to the board
PUSH   keep board on the pod volume (durable) + rsync/git to the remote
```

Run it on the pod (the 3090, `sov-brain-2`):

```bash
ssh sov-brain-2                                   # the reliable producer
cd /workspace/dorado
MODEL=qwen3:4b-8k DOMAIN=bond CYCLES=24 bash scripts/dorado-eat.sh
# production signing (real #card-attestation-1 key, pod-held):
DORADO_SIGNING_KEY_FILE=/path/to/pod-key bash scripts/dorado-eat.sh
```

`CYCLES` is the number of EAT rotations. The loop is fail-open (one cycle's error
is logged and the next runs).

### Parallel EAT batch (`scripts/eat-batch.sh`)

Fan out a full MINE→MINT→CHAIN→PUBLISH cycle per domain, in parallel (default
concurrency 3), entirely on the pod:

```bash
ssh sov-brain-2 && cd /workspace/dorado
MODEL=sov33-unified:latest CONC=3 bash scripts/eat-batch.sh   # all 6 domains
```

Verified e2e on the pod: board grew to 14 measurements (all 6 domains), `chainOk=True`,
`linked=14`, every entry has a real RFC 3161 anchor time. All batch cards stranger-verify
VALID. **If a measure returns `measured=0/6`, that is the harness honestly reporting the
pod's Ollama inference is degraded/contended OR not serving — NOT a wiring bug.** Check
`ss -tlnp | grep 11434` + `ollama list` on the pod; if `ollama list` says "could not
connect", the model server is down and must be started/restarted before scores appear.
The harness never fakes a score.

## Backup (`scripts/dorado-backup.sh`)

Snapshot the worktree + board to a durable off-Mac location, rotated to the last
10, preserving the git remote as source of truth:

```bash
ssh sov-brain-2 'cd /workspace/dorado && DEST=/workspace/dorado-backup bash scripts/dorado-backup.sh'
# secondary -> Oracle:
DEST=/evac-bulk/dorado-backup bash scripts/dorado-backup.sh
```

## Deploying the monorepo to the pod (from the Mac, `rsync` — no Mac git pressure)

```bash
rsync -az --delete -e "ssh -o StrictHostKeyChecking=no" \
  --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' --exclude 'data-out' \
  ./ sov-brain-2:/workspace/dorado/
```

(The remote `git` lives on `CSOAI-ORG/dorado`; pushing the rename of the GitHub repo
itself is an owner action — `CSOAI-ORG/cibola` can be renamed to `CSOAI-ORG/dorado`.)

## Doctrine (unchanged, still binding on the pod)

- Measurement, never certification — register verbatim on every card.
- One-signer identity gate: a non-published key is never stamped as the production
  identity; it is stamped kid=test (only with `--allow-test-identity`).
- The RFC 3161 TSA anchor is the authoritative external time-binding. Rekor v1 is
  attempted with the corrected schema; a full sigstore-signature needs the signing
  pipeline (infra dependency, not a code bug).
- Board is content-addressed, append-only, refuses unsigned cards.
