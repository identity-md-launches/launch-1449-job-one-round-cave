#!/usr/bin/env python3
"""Offline behavior tests; disposable fixtures live under /tmp."""
import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import source_check as tool

CHECK = tool.inspector()
spec = importlib.util.spec_from_file_location("source_test_producer", "line-2/tools/handoff/handoff.py")
PRODUCER = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PRODUCER)


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.previous = Path.cwd()
        self.temp = tempfile.TemporaryDirectory(prefix="handoff-source-", dir="/tmp")
        os.chdir(self.temp.name)
        Path("source/sub").mkdir(parents=True)
        self.payload = {"a.txt": b"alpha", "sub/b.txt": b"beta", "empty": b""}
        for name, data in self.payload.items():
            (Path("source") / name).write_bytes(data)
        Path("bundle.zip").write_bytes(PRODUCER.build(self.payload))

    def tearDown(self):
        os.chdir(self.previous)
        self.temp.cleanup()

    def run_check(self, **kwargs):
        return tool.check_paths("bundle.zip", "source", module=CHECK, **kwargs)

    def test_equal(self):
        result = self.run_check()
        self.assertTrue(result["matches_source"])
        self.assertEqual(result["counts"]["unchanged"], 3)

    def test_changed_same_size(self):
        Path("source/a.txt").write_bytes(b"ALPHA")
        result = self.run_check()
        self.assertFalse(result["matches_source"])
        self.assertEqual(result["changed"][0]["path"], "a.txt")

    def test_missing_and_omitted(self):
        Path("source/a.txt").unlink()
        Path("source/new").write_bytes(b"new")
        result = self.run_check()
        self.assertEqual(result["missing_from_source"][0]["path"], "a.txt")
        self.assertEqual(result["omitted_from_archive"][0]["path"], "new")

    def test_empty_source(self):
        for p in Path("source").rglob("*"):
            if p.is_file(): p.unlink()
        self.assertEqual(self.run_check()["counts"]["missing_from_source"], 3)

    def test_empty_directories_not_payload(self):
        Path("source/empty-dir").mkdir()
        self.assertTrue(self.run_check()["matches_source"])

    def test_source_reserved_manifest_is_omitted(self):
        Path("source/HANDOFF.json").write_bytes(b"note")
        self.assertEqual(self.run_check()["omitted_from_archive"][0]["path"], "HANDOFF.json")

    def test_utf8(self):
        Path("source/café.txt").write_bytes(b"public")
        self.assertEqual(self.run_check()["omitted_from_archive"][0]["path"], "café.txt")

    def test_symlink_file(self):
        Path("source/link").symlink_to("a.txt")
        with self.assertRaises(ValueError): self.run_check()

    def test_symlink_directory(self):
        Path("source/link").symlink_to("sub", target_is_directory=True)
        with self.assertRaises(ValueError): self.run_check()

    def test_fifo(self):
        os.mkfifo("source/pipe")
        with self.assertRaises(ValueError): self.run_check()

    def test_unsafe_source_paths(self):
        for name in ("../source", str(Path("source").absolute())):
            with self.subTest(name=name), self.assertRaises(ValueError):
                tool.source_receipt(name, CHECK, CHECK.Limits())

    def test_symlink_root(self):
        Path("link").symlink_to("source", target_is_directory=True)
        with self.assertRaises(ValueError): tool.source_receipt("link", CHECK, CHECK.Limits())

    def test_file_count(self):
        Path("source/extra").write_bytes(b"")
        with self.assertRaises(ValueError): self.run_check(limits=CHECK.Limits(files=3))

    def test_payload_budget(self):
        Path("source/a.txt").write_bytes(b"123456")
        with self.assertRaises(ValueError): self.run_check(limits=CHECK.Limits(payload_bytes=9))

    def test_directory_budget(self):
        for i in range(4): Path("source/d" + str(i)).mkdir()
        with self.assertRaises(ValueError): self.run_check(limits=CHECK.Limits(files=3))

    def test_metadata_budget(self):
        with self.assertRaises(ValueError):
            tool.source_receipt("source", CHECK, CHECK.Limits(metadata_bytes=5))

    def test_trusted_digest(self):
        digest = hashlib.sha256(Path("bundle.zip").read_bytes()).hexdigest()
        self.assertTrue(self.run_check(expected=digest)["trusted_digest_matched"])
        with self.assertRaises(ValueError): self.run_check(expected="f" * 64)

    def test_invalid_archive_before_source_scan(self):
        Path("bundle.zip").write_bytes(b"invalid")
        with patch.object(tool, "source_receipt", side_effect=AssertionError("must not scan")):
            with self.assertRaises(ValueError): self.run_check()

    def test_tree_mutation(self):
        real = tool.inventory
        calls = []
        def changed(*args):
            result = real(*args)
            calls.append(1)
            if len(calls) == 1: Path("source/new").write_bytes(b"change")
            return result
        with patch.object(tool, "inventory", side_effect=changed):
            with self.assertRaises(ValueError): self.run_check()

    def test_repeat_receipt(self):
        self.assertEqual(self.run_check(), self.run_check())

    def test_cli_match_mismatch_invalid(self):
        with patch.object(tool, "inspector", return_value=CHECK):
            for expected in (0, 2, 1):
                if expected == 2: Path("source/a.txt").unlink()
                if expected == 1: Path("bundle.zip").write_bytes(b"invalid")
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = tool.main(["check", "bundle.zip", "source"])
                self.assertEqual(status, expected)
                self.assertEqual(bool(out.getvalue()), expected != 1)


if __name__ == "__main__":
    unittest.main()
