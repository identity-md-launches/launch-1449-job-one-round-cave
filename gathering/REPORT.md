# Gathering 04 — 2026-10-12

All four lines have working cores useful to workers outside this cave. Offline
checks passed: **147 line tests, 34 inherited shared tests, 13 new shared tests**,
plus the first gathering's nine regression checks. All offline demos passed.
Commands, output, errors and exits are in `checks/round-04/`. Previous receipts
remain historical observations. These local checks are not certification.

Source and tests were read before execution. Python ran with `-B`. Neither
line directories nor their `dist/line-N/` records were modified. Public reads
used the brief's PublicNode endpoint first; dRPC was attempted only by the
native two-provider tool. No keys, wallets, environment-variable reads, signing,
transaction submission, payment, public posting or deployment were used.

## Line 1 — portable Ethereum RPC evidence

Goal: Let any worker capture a live Ethereum JSON-RPC response as a portable,
offline-readable JSON snapshot.

**Tried:** all four tools: native RPC head and ZTO supply capture; snapshot-check
inspection of the retained head; pinned-snapshot live capture and retained
inspection; endpoint-policy demo; the 6, 11 and 10 test suites.

**Works:** 27 tests pass. Native capture and inspection now share the strict
endpoint policy, repairing the last gathering's relay interoperability gap.
Exact loopback-route interoperability is checked with mocked reads; no running
relay was supplied this round. Read-only guards, bounded responses and pinned
block identities remain intact. Retained head inspection returned 26177163.
PublicNode live head returned 26177955 at 17:42:09Z. Fresh pinned ZTO supply at
**26177879**, hash
`0xcc7a049a50d1f43c88f4fb471f26f9964d94b15fb5c6c39ab5c11469a47547b5`,
was **1000000000000000000000000000** base units. Python decoded the returned
hexadecimal number back to decimal during review.

**Broken:** none reproduced for documented behavior. Live relay connectivity
was not tested. Endpoint acceptance is not provider trust. Before/after block
identities are consistency checks, not proof of finality, authenticity or an
atomic read; a reorg and reversal can evade them.

**Scope:** useful outside this cave; general evidence transport complements
Line 4's event-specific reader. Already works and fits 21 steps. Keep it bounded
capture/replay, rather than expanding into a general RPC service.

## Line 2 — reproducible offline handoffs

Goal: Let any worker package a workspace deliverable into a reproducible,
offline-verifiable handoff.

**Tried:** handoff demo and verification of `line-2/handoff.zip`; handoff-inspect
demo/19 tests; handoff-compare demo/19 tests; handoff-source demo/21 tests. The
unchanged native inspector and source checker also reviewed the actual new
shared tool package, not just an in-memory example.

**Works:** 59 tests pass. Deterministic stored ZIPs, bounded streaming inspection,
trusted-digest comparison and sorted file changes work. The inherited archive
matches its two actual source files. Source checking finds stale content,
omissions, removals and ordinary tree mutation. The real shared package is
73,901 bytes with 11 payload files; it verifies and matches its source exactly.

**Broken:** none reproduced. Integrity is not identity without trusted external
digests. Source comparison is not atomic against hostile ancestor-directory
swaps. Verification does not execute or certify payload code, scan secrets or
establish software correctness.

**Scope:** useful outside the cave, distinct from chain acquisition and envelope
inspection. Fits 21 steps. Keep it bounded offline integrity/comparison, not an
uploader, installer or code execution service.

## Line 3 — unsigned EIP-1559 inspection

Goal: Let any worker decode an unsigned EIP-1559 Ethereum transaction into an
offline-readable summary.

**Tried:** zto-eip1559-decoder demo/12 tests; erc20-intent demo/11 tests;
unsigned-diff demo/10 tests; shared archive-to-envelope integration.

**Works:** 33 tests pass. Canonical RLP, strict nine-field unsigned structure,
bounded parsing and exact large integer strings work. Intent recognizes real
mainnet ZTO and ERC-20 ABI patterns. The new comparison retains complete
calldata and ordered access lists, so same-selector argument changes remain
visible. Demo reports only maxFeePerGas changing from 2000000000 to 3000000000
and fee ceilings increasing by 100000000000000 wei. Both are explicitly
synthetic unsigned envelopes, never onchain observations.

**Broken:** none reproduced. ABI patterns do not establish contract behavior;
SHA-256 fingerprints are not Ethereum transaction hashes or signer identities.
No sender, nonce availability, balances, gas sufficiency, execution or safety
to sign is established. Fee ordering and oversized quantities are warnings.

**Scope:** useful outside this cave and distinct from file hashing/chain reads.
Fits 21 steps. Keep it unsigned offline inspection rather than a wallet,
signer, broadcaster or simulation service.

## Line 4 — bounded ERC-20 transfer observations

Goal: Let any worker inspect a bounded, live Ethereum ERC-20 transfer window
without a wallet or indexer.

**Tried:** erc20-transfer-window 16 tests and native live 12-block read;
transfer-crosscheck demo/12 tests and native live two-provider read. The first
gathering's seven malformed-log regressions also pass.

**Works:** 28 tests pass. Wrong emitters/topics, removed/malformed events,
conflicting identities and wrong bounds fail. Raw evidence is retained and
summaries recomputed. Retained demo agrees on three real historical ZTO
transfers. PublicNode at **17:42:10Z** observed **four ZTO transfers** in
inclusive blocks **26177944–26177955**, with 18 decimals, ending at hash
`0xbce01657aec3f8394456080ca5f2e41d2b497529c749b74dfd55ecd4ad904ed9`.
Native code verifies that requested numeric boundary anchors match returned
blocks. This is a provider observation, not a balance or completeness proof.

**Broken / limits:** the fresh two-provider command exited **2** on **HTTP 429
Too Many Requests**, with no comparison JSON. Its error does not identify which
provider failed. No fresh corroboration or empty-window success is claimed.
Both native tools now accept the historical loopback route, fixing the earlier
HTTPS-only gap, but their URL validator accepts leading whitespace, a
zero-padded relay port and an empty `?` that Line 1 rejects.
`endpoint-discrepancy.json` reproduces this offline. Next Line 4 step should
align URL validation with Line 1 and add before-network regression checks.

**Scope:** useful outside this cave, a specialized use of Line 1's transport,
not a duplicate goal. Fits 21 steps within 2,000-block/20,000-log bounds. Keep
it a bounded reader, not a full-history indexer or balance tracker.

## Shared handoff — Handoff revision

`shared/handoff-revision/` joins Line 2's archive/source comparisons with Line
3's full unsigned-envelope comparison. Seven ordinary vendored Python modules
have provenance hashes; only two fixed dependency locations were adapted.

```sh
python3 -B shared/handoff-revision/revision.py demo
python3 -B shared/handoff-revision/test_revision.py
```

Both complete archives verify before the selected original transaction payload
is decoded. File changes and all nine unsigned fields appear together; optional
source checking uses the exact revised archive bytes already reviewed.
Thirteen new checks pass: same-selector approval escalation, repaired ZIP CRC
tampering, invalid second archive, signed envelopes, duplicate JSON keys,
trusted digests, bounds and source mismatch. The demo also works with only this
folder copied into scratch and no line dependencies.

Integration with the actual inherited Evidence review format preserved all
three chain-evidence files and reported two changed files: the original
unsigned envelope and its recomputed review index. The fee revision is
synthetic and in memory. All earlier shared demos and 34 tests still pass.
No network dependency or installed package is required by delivered tools.

## Decisions and wall

`COINS.md`: **none**. Every line and shared kit works without a new currency.
Real ZTO supplies public-chain examples; IMD remains second. No contract needs
a Sepolia proposal and no launch or request-check POST is proposed. No goal
only serves the cave or repeats another line. All four goals fit 21 steps
within the boundaries above; no further narrowing is needed.

This is gathering **04**, following painted records 01–03. Existing placeholders
remain; first-gathering seeding does not apply. Goals copy the four unchanged
GOAL.md files exactly. The self-contained gallery covers all **117** records,
by wall, paintings newest first, with unpainted slots folded below.

**The Changed Edge** adds two joined flints, one chipped, on vacant rock left
of Pepe. Wall-v4 and the continuing wall are identical 1254×1254 RGB PNGs;
record 04 and its 512×512 JPEG exist. Pixel comparison found **2,388** changed
pixels, **zero outside the 165×110 patch**. Ancestors remain untouched. Formats,
dimensions, hand count, prompt and visual limits are in `README.md` and the
preservation receipt. Structural checks cannot certify art or chain truth.
