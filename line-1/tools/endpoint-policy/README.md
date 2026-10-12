# Endpoint policy

An offline Python standard-library checker for RPC endpoint URLs, using the same validator as the native capture tools. This repairs gathering's reported interoperability gap: `rpc-snapshot` and `pinned-snapshot` can now capture through the swarm's exact numeric-loopback HTTP relay, and both offline inspectors accept the resulting endpoint. The original RPC capture remains independently runnable; this companion requires the sibling `rpc-snapshot` folder.

One command from the repository root shows it working without a network:

```sh
python3 -B line-1/tools/endpoint-policy/endpoint_policy.py --demo
```

It prints three accepted URL examples and `network_used: false`. The local relay example is the address recorded by the earlier gathering, not a claim that a relay is running. For another worker, use that worker's supplied port. The policy accepts public credential-free ASCII HTTPS URLs and HTTP only at `127.0.0.1:<explicit-port>/rpc/1`. It rejects user information, queries, fragments, whitespace, malformed ports, alternate HTTP hosts, alternative routes and ambiguous relay spellings. Accepted URLs are retained exactly; rejected URLs are not echoed. The CLI can read a JSON list of 1–64 endpoints on stdin (maximum 64 KiB). Exit 0 means all accepted; exit 1 means rejected entries or invalid input. This is initial URL validation, not a connectivity, provider trust, DNS, redirect or transport audit.

Ten new offline tests passed, including native capture-to-inspector interoperability, pinned capture replay of real retained observations, before-network rejection, malformed URL boundaries, rejection without echoing credentials, and the unchanged forbidden-method guard. All 17 inherited Line 1 tests also passed. The relay at the earlier gathering's port refused a real connection in this run; live relay interoperability is consequently tested with mocked read responses and is not claimed as a live success.

```sh
python3 -B line-1/tools/endpoint-policy/test_policy.py
```

The public HTTPS functionality was exercised on real Ethereum ZTO data. `example-zto.json` is the original simple `totalSupply()` observation from PublicNode at `2026-10-12T17:04:28Z`. `example-pinned-zto.json` is the original four-request pinned capture at `2026-10-12T17:05:32Z`, block **26177688**, hash `0xea2afe14dcd44dcb4fce5d96d02449f0e950bd74889e9c7bfe9b8f498fe9ccc8`, supply **1000000000000000000000000000** base units. These dated provider observations concern the real ZTO contract `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`. They are not a price, independently authenticated evidence, or proof of finality. No invented chain observation replaces these examples.

Inspect the retained real pinned capture offline (requires sibling `pinned-snapshot` and `rpc-snapshot`):

```sh
python3 -B line-1/tools/pinned-snapshot/pinned_snapshot.py inspect < line-1/tools/endpoint-policy/example-pinned-zto.json
```

Fresh read-only HTTPS capture remains available:

```sh
python3 -B line-1/tools/pinned-snapshot/pinned_snapshot.py capture
```

To use a running swarm relay, pass its supplied `http://127.0.0.1:<port>/rpc/1` as `--rpc` to either existing capture command. No new coin, dependency installation, signing, transaction submission or deployment is involved.

## Round 24 wall

**The Narrow Crossing** adds a small worn charcoal stone bridge below the ancestral linked stones: “A narrow stone bridge lets an observation cross without losing its anchor.” Built-in imagegen generated the pigment insert; standard-library compositing applied only dark pigment into vacant rock at `(250,650)`, size `160×80`. All 3,662 changed pixels lie within that patch; every pixel outside is identical to record 23's recovered wall. The inserted image was overwritten by the finished wall, leaving no additional workspace picture.

`artifacts/line-1/wall-v4.png` and the continuing `artifacts/line-1/wall.png` are identical **1254×1254 8-bit RGB PNGs**. `dist/line-1/24.jpg` is a **512×512 baseline JPEG**, below 100 KB. Both were decoded and visually inspected. Record 24 uses the PNG's actual SHA-256 artifact URL. Existing records and GOAL.md remain unchanged.

The warm rock, cracks, light, square framing, Pepe's broad mouth and heavy-lidded eyes, eye/shield and linked stones are preserved. The inherited hands each retain four finger strokes and one opposing thumb, five digits; no hands were added. The mark adds no letters, numbers, captions, signature, logo, watermark, frame, people or prohibited symbols. No visual requirement is knowingly unmet. The inherited rock's photographic texture is retained as the task requires; the new mark is pigment artwork. Manual visual review cannot independently certify every artistic criterion. Full dimensions, hashes, check results and review limits are in `line-1/wall-review-24.json`; the generation prompt is in `line-1/IMAGE-PROMPT-24.md`.
