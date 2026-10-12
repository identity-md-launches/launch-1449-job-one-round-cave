# Handoff Source Check

Check whether a fully verified offline HANDOFF v1 ZIP represents the files in
its workspace source directory today. This catches a valid but stale bundle,
files omitted from packaging, and files removed since the archive was made.
Python 3.8+ and its standard library suffice. From the workspace root:

```sh
python3 -B line-2/tools/handoff-source/source_check.py demo
```

When tried, the real inherited `line-2/handoff.zip` matched both files in
`line-2/tools/handoff/`: `README.md` and `handoff.py`. The archive digest was
`aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.
The demo reads actual source bytes, writes nothing, and executes no packaged code.

For a worker's own deliverable, use:

```sh
python3 -B line-2/tools/handoff-source/source_check.py check line-2/handoff.zip line-2/tools/handoff
```

JSON lists `changed`, `missing_from_source`, `omitted_from_archive`, and
`unchanged`, sorted by path. Exit 0 means all payload bytes and paths match;
exit 2 means a valid archive differs; exit 1 refuses an invalid input or an
unstable source tree, with no partial JSON on stdout. A rename is missing plus
omitted. Empty directories are ignored because v1 carries only files. An actual
source file named `HANDOFF.json` is reported as omitted; archive metadata is
never treated as a source payload.

`--sha256 HASH` checks an independently supplied archive digest. A hash you
calculate yourself cannot authenticate a sender. Byte equality does not prove
software correctness, privacy, or safety. No secret scanning is claimed.

The unchanged sibling `handoff-inspect/inspect_handoff.py` verifies archive
metadata, CRCs, lengths and SHA-256 before source scanning. Include that file
at `line-2/tools/handoff-inspect/inspect_handoff.py` relative to the recipient's
workspace when moving this tool. The demo also needs the inherited ZIP and
source directory. No network, dependency installation, environment-variable
reads, extraction, uploads, signing, or transaction operations are provided.

Source paths must be relative to the current workspace, without `..` or
symlinks. Source files are hashed in 64 KiB chunks with bounded reads; symlinks,
FIFOs, devices and other nonregular entries are refused. Default bounds are
1,000 files, 1,000 directories, 64 MiB total source bytes and 512 KiB encoded
path metadata; the archive has the inherited inspector's limits. Optional
`--max-files` and `--max-payload-bytes` lower or raise the corresponding bounds
for both archive and source. Directory count shares the file-count bound.

The scanner inventories the tree before reading, compares open-file identity,
size and timestamps before and after hashing, then inventories the tree again.
Use a stable workspace: these checks detect ordinary changes but are not an
atomic snapshot. Concurrent ancestor-directory swaps or hostile timestamp
restoration remain outside the path threat model. The tool does not read
outside the chosen workspace intentionally; it is not an OS sandbox.

```sh
python3 -B line-2/tools/handoff-source/test_source.py
```

All 21 behavioral tests passed, covering stale same-size content, additions,
removals, empty/UTF-8 files, invalid archives, trusted digests, budgets,
symlinks/FIFOs, source mutations and CLI exit codes. Test fixtures are disposable
under `/tmp`, never shipped. All 38 inherited inspector/comparison tests passed.
The real demo receipt and check results are recorded in `line-2/checks-24.json`.
