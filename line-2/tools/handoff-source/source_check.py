#!/usr/bin/env python3
"""Verify a HANDOFF v1 archive against a bounded workspace source tree."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import struct
import sys
import zipfile


def inspector():
    path = Path("line-2/tools/handoff-inspect/inspect_handoff.py")
    current = Path.cwd()
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("dependency symlinks are not allowed")
    spec = importlib.util.spec_from_file_location("handoff_source_inspector", current)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def workspace_directory(raw):
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("use a relative workspace source without '..'")
    current = Path.cwd()
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("source symlinks are not allowed")
    if not current.is_dir():
        raise ValueError("source must be a directory")
    return current


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def inventory(root, check, limits):
    """No payload reads here; bound entries and encoded path metadata first."""
    found, pending = {}, [root]
    metadata = 0
    directories = 0
    files = 0
    total = 0
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                name = check.safe_name(path.relative_to(root).as_posix())
                metadata += len(name.encode("utf-8"))
                if metadata > limits.metadata_bytes:
                    raise ValueError("source path metadata exceeds limit")
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    directories += 1
                    if directories > limits.files:
                        raise ValueError("source directory count exceeds limit")
                    pending.append(path)
                elif stat.S_ISREG(info.st_mode):
                    files += 1
                    total += info.st_size
                    if files > limits.files or total > limits.payload_bytes:
                        raise ValueError("source files or payload exceed limit")
                else:
                    raise ValueError("source contains a symlink or nonregular entry: " + name)
                found[name] = identity(info)
    return found


def source_receipt(raw, check, limits):
    root = workspace_directory(raw)
    root_identity = identity(root.stat())
    before = inventory(root, check, limits)
    files = []
    for name, recorded in sorted(before.items()):
        if not stat.S_ISREG(recorded[2]):
            continue
        path = root / name
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                     | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as stream:
            if identity(os.fstat(stream.fileno())) != recorded:
                raise ValueError("source changed before reading: " + name)
            hasher = hashlib.sha256()
            size = 0
            while True:
                block = stream.read(min(check.CHUNK, recorded[3] - size + 1))
                if not block:
                    break
                size += len(block)
                if size > recorded[3]:
                    raise ValueError("source grew while reading: " + name)
                hasher.update(block)
            if size != recorded[3] or identity(os.fstat(stream.fileno())) != recorded:
                raise ValueError("source changed while reading: " + name)
        files.append({"path": name, "bytes": size, "sha256": hasher.hexdigest()})
    if (inventory(root, check, limits) != before
            or identity(root.stat()) != root_identity):
        raise ValueError("source tree changed during checking")
    return files


def compare(receipt, files):
    archive = {item["path"]: item for item in receipt["files"]}
    source = {item["path"]: item for item in files}
    missing = [archive[p] for p in sorted(archive.keys() - source.keys())]
    omitted = [source[p] for p in sorted(source.keys() - archive.keys())]
    changed, unchanged = [], []
    for name in sorted(archive.keys() & source.keys()):
        if archive[name] == source[name]:
            unchanged.append(name)
        else:
            changed.append({"path": name, "archive": archive[name], "source": source[name]})
    return {"format": "handoff-source-check-v1", "archive_verified": True,
            "archive_sha256": receipt["archive_sha256"],
            "trusted_digest_matched": receipt["trusted_digest_matched"],
            "matches_source": not (missing or omitted or changed),
            "counts": {"missing_from_source": len(missing), "omitted_from_archive": len(omitted),
                       "changed": len(changed), "unchanged": len(unchanged)},
            "missing_from_source": missing, "omitted_from_archive": omitted,
            "changed": changed, "unchanged": unchanged,
            "note": "Byte equality is not authenticity or a safety review. Empty directories "
                    "are not payloads. Use a stable workspace; this is not an atomic snapshot."}


def check_paths(archive, source, expected=None, limits=None, module=None):
    check = module or inspector()
    limits = limits or check.Limits()
    limits.validate()
    receipt = check.inspect_path(archive, limits, expected)
    files = source_receipt(source, check, limits)
    return compare(receipt, files)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo")
    command = sub.add_parser("check")
    command.add_argument("archive")
    command.add_argument("source")
    command.add_argument("--sha256", help="independently trusted archive digest")
    command.add_argument("--max-files", type=int, default=1000)
    command.add_argument("--max-payload-bytes", type=int, default=64 * 1024 * 1024)
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            result = check_paths("line-2/handoff.zip", "line-2/tools/handoff")
            if not result["matches_source"]:
                raise ValueError("inherited bundle differs from its source")
            result["demo"] = "real inherited archive checked against its two source files"
        else:
            check = inspector()
            limits = check.Limits(files=args.max_files, payload_bytes=args.max_payload_bytes)
            result = check_paths(args.archive, args.source, args.sha256, limits, check)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result["matches_source"] else 2
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError,
            zipfile.BadZipFile, EOFError, NotImplementedError, struct.error) as error:
        print("handoff-source: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
