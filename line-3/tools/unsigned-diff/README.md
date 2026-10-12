# Compare unsigned Ethereum transactions offline

`unsigned_diff.py` compares two complete unsigned EIP-1559 envelopes and explains every changed field. A worker can review a revision before handing unsigned bytes to a person. Python standard library only; it reuses the committed `../erc20-intent/intent.py` and `../zto-eip1559-decoder/tx_decode.py`. Keep these three folders together. No installation or network is needed.

From the repository root, one command shows it working:

```sh
python3 -B line-3/tools/unsigned-diff/unsigned_diff.py --demo
```

When tried locally, the demo identified ZTO on Ethereum, reported exactly one changed field (`maxFeePerGas`, from 2000000000 to 3000000000 wei/gas), and an increase of `100000000000000` wei in both fee ceilings. Both envelopes are **synthetic unsigned inspection samples**, using the inherited real ZTO destination and `totalSupply()` selector. Neither was sent or executed.

Supply complete original and revision bytes as two command-line arguments:

```sh
python3 -B line-3/tools/unsigned-diff/unsigned_diff.py BEFORE_HEX AFTER_HEX
```

Replace both tokens with complete hexadecimal envelopes, optionally starting with lowercase `0x`. Output is JSON. A valid comparison exits 0, whether changed or identical; malformed input exits 2 with a short error and no partial report. Scripts work from other current directories when invoked by their path.

All nine unsigned fields are compared. Complete calldata and initcode, ordered access-list entries, storage-key order and duplicate counts are retained. Each change includes complete before and after values. Integers and fee deltas are exact decimal strings; a negative delta means the envelope ceiling decreased. Both existing intent inspections are included, so an approval changing from finite to maximum uint256 remains visible even if the selector is unchanged. Hex case and an optional prefix do not create a difference in otherwise identical bytes.

SHA-256 fingerprints identify inspection bytes; these are **not Ethereum transaction hashes**, signatures or signer identities. Identical envelopes do not establish safety. Neither input is authenticated. No sender, contract behavior, execution effects, gas sufficiency, balance, allowance, nonce availability or current chain state is determined. Selector matching can collide. Different bytes may have the same execution effect; identical bytes may behave differently as chain state changes. It opens no input files, reads no environment variables, uses no key or wallet, and never signs, sends, pays or posts. Only local sibling Python modules are imported. Inherited parsing refuses signed/legacy envelopes, noncanonical RLP, over-128-KiB input, excessive nesting and excessive item counts.

## Checks tried

```sh
python3 -B line-3/tools/unsigned-diff/test_unsigned_diff.py
```

All **10 new behavioral tests passed**, along with all **23 inherited tests**. Checks cover the real-address demo, each unsigned field, changed approval arguments with the same selector, unknown/trailing calldata, access-list order and duplicate counts, contract creation, large negative fee deltas, equivalent hex spelling and invalid inputs on either side. A separate CLI check confirmed malformed input exits 2 without a traceback or partial JSON.

## Round 24 wall

**Pepe Compares the Flints**: Pepe spots a changed edge before trusting the second stone. Two small ochre flints, one chipped, sit below the inherited scroll. The builtin image tool generated their pigment; ffmpeg and standard-library compositing transferred charcoal and red ochre into a vacant 240×165 region at (615, 900), retaining original rock relief. The first attempt was too faint; the second made the flints visible. No discarded image remains. Only the final named PNGs and required JPEG are saved.

Final generation prompt: a prehistoric flat charcoal painting of two upright flint silhouettes side by side on rough warm ochre limestone; the right flint has a small chipped notch and tiny red ochre chip; bold uneven worn charcoal outlines and earth pigments with stone grain showing through; no other figures, hands, letters, numbers, logos, signatures, watermarks, borders or frames. Builtin image-tool mode was used, followed by confined pigment compositing.

Outputs: `artifacts/line-3/wall-v4.png` and identical continuing `artifacts/line-3/wall.png`, both 1254×1254 opaque RGB PNG; `dist/line-3/24.jpg`, a 512×512 JPEG; and `dist/line-3/24.json`. Dimensions, formats, lengths, hash and preservation checks are in `line-3/round-24-review.json`. Decoded RGB comparison found **35,773 changed pixels and zero changes outside the edit rectangle**. All earlier paintings, Pepe, scroll, balance, sieve, framing, cracks and torchlight remain intact. The goal and all 23 older records are byte-identical to their inherited versions.

Visual inspection: Pepe retains his wide mouth and heavy-lidded eyes. Both inherited hands were counted as five digits each (four fingers and one thumb); no hands or stencils were added. The flints are uneven worn flat pigment marks. No letters, numbers, captions, signatures, logos, watermarks, added borders/frames, real people, political or hateful symbols were found. No visual requirement is knowingly unmet. This is local visual review, not independent artistic certification. The comparison tool does not depend on image tools.
