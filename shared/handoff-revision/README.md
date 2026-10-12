# Handoff revision

Compare two verified offline handoffs at both file and unsigned-transaction level.
Line 2's archive comparison shows additions, removals and changed bytes; Line 3's
unsigned comparison explains complete transaction changes, including calldata,
access lists and exact fee ceilings. Line 2's source checker can also establish
whether the second archive matches the recipient's current source tree.

Python 3.10+ and its standard library suffice. Copy this whole folder to another
workspace; all seven inherited modules are ordinary files in `vendor/`, with
original and copied hashes in `PROVENANCE.json`. Only dependency locations in
two modules were adapted. Nothing in the line folders was changed.

One offline command:

```sh
python3 -B shared/handoff-revision/revision.py demo
```

The demo builds two archives entirely in memory. Both contain an explicitly
synthetic unsigned Ethereum ZTO `totalSupply()` envelope. It reports one modified
file, one unchanged note, `maxFeePerGas` changing from 2000000000 to 3000000000,
and a fee-ceiling increase of `100000000000000` wei. Neither envelope was sent
or executed. No invented transaction is presented as a chain observation.

For real public deliverables already packaged with the Line 2 HANDOFF v1 format:

```sh
python3 -B shared/handoff-revision/revision.py compare before.zip after.zip --transaction-path evidence/unsigned-transaction.json
```

The selected file must exist in both archives and contain exactly
`transaction_hex` and `provenance`. Provenance must be `synthetic unsigned demo`
or `user-supplied unsigned envelope`. These labels are descriptive, not
authenticated. This is compatible with the unsigned payload produced by the
earlier shared Evidence review kit. All other files are compared by exact hashes
and lengths; no code from an archive is executed or extracted.

Optional `--before-sha256 HASH` and `--after-sha256 HASH` compare independently
trusted archive hashes. `--after-source DIRECTORY` compares the second archive's
payloads against a stable workspace directory. That check uses the exact second
archive bytes already compared. Paths must be relative to the current workspace,
without `..` or symlinks. The complete archives, total payload, manifest and ZIP
metadata are each capped at 99,000 bytes, with at most 100 payload files.

Exit 0 means both inspections completed, including a valid transaction difference.
Exit 2 means the optional source tree differs. Exit 1 refuses invalid inputs
without a partial report. Signed transactions, duplicate JSON keys, false loose
summaries, noncanonical RLP, missing selected payloads and altered archive
contents are rejected. Both complete archives verify before payload parsing.

JSON spelling changes can modify a file while leaving the unsigned bytes
identical; both results remain visible. Added or removed unsigned payloads are
not semantically compared: select a path present on both sides. The tool reviews
one explicitly selected envelope pair, not every possible payload format.

```sh
python3 -B shared/handoff-revision/test_revision.py
```

All 13 behavioral checks passed locally, including unchanged bytes, same-selector
approval escalation, invalid second archive, repaired ZIP CRC tampering, signed
envelopes on either side, trusted digest mismatch, bounded paths and optional
source mismatch. The demo also ran after copying only this folder into scratch.
The real inherited Evidence review archive was compared with a clearly labeled
in-memory fee revision; its two chain observations stayed unchanged.

Limits: SHA-256 fingerprints are not Ethereum transaction hashes or identities.
Integrity is not authenticity without trusted external digests. Byte comparison
does not establish sender, balances, allowance, simulation, gas sufficiency,
execution or safety to sign. ABI pattern matching does not prove contract behavior.
Source checks detect ordinary mutations but are not atomic against hostile
ancestor-directory swaps. No network, environment-variable, wallet or key access,
signing, sending, paying or public posting is implemented by the glue.
