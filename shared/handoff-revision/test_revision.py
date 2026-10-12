"""Offline behavior checks; archives stay in memory or authorized scratch."""
import contextlib
import io
import json
from pathlib import Path
import unittest
import zipfile
from unittest.mock import patch
import revision as r


class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b = r.demo_archives()

    def pack(self, tx, **extra):
        obj = {'transaction_hex': tx, 'provenance': 'synthetic unsigned demo'}
        return r.producer.build({'unsigned.json': json.dumps(obj).encode(), **extra})

    def test_demo_changed_fee(self):
        report = r.demo()
        self.assertEqual(report['unsigned']['feeBudgetDeltaWei']['gasFeeCapWei'], '100000000000000')
        self.assertEqual(report['unsigned']['beforeInspection']['destinationLabel'], 'ZTO')

    def test_same_archive_and_original_bytes(self):
        result = r.compare_bytes(self.a, self.a, 'unsigned.json')
        self.assertTrue(result['files']['same_archive'])
        self.assertEqual(result['unsigned']['status'], 'identical')

    def test_semantically_identical_spelling_still_file_change(self):
        tx = r.unsigned_diff.intent.decoder.demo_transaction()
        result = r.compare_bytes(self.pack(tx), self.pack(tx[2:].upper()), 'unsigned.json')
        self.assertFalse(result['files']['same_payload'])
        self.assertEqual(result['unsigned']['status'], 'identical')

    def test_same_selector_approval_change_is_visible(self):
        d = r.unsigned_diff.intent.decoder
        fields, _ = d.rlp_item(bytes.fromhex(d.demo_transaction()[2:]), 1)
        prefix = bytes.fromhex('095ea7b3') + bytes(12) + bytes.fromhex(r.unsigned_diff.intent.IMD[2:])
        fields[7] = prefix + (1).to_bytes(32, 'big')
        a = self.pack('0x02' + d.rlp_encode(fields).hex())
        fields[7] = prefix + (2**256 - 1).to_bytes(32, 'big')
        b = self.pack('0x02' + d.rlp_encode(fields).hex())
        result = r.compare_bytes(a, b, 'unsigned.json')['unsigned']
        self.assertEqual(result['changes'][0]['field'], 'data')
        self.assertEqual(result['afterInspection']['calldata']['approvalKind'], 'maximum-uint256')

    def test_verify_second_before_parse(self):
        with patch.object(r, 'parse_envelope', side_effect=AssertionError('too early')):
            with self.assertRaises(ValueError): r.compare_bytes(self.a, b'invalid', 'unsigned.json')

    def test_repaired_crc_tamper_fails_hash(self):
        out = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.b)) as a, zipfile.ZipFile(out, 'w') as b:
            for entry in a.infolist():
                payload = a.read(entry.filename)
                if entry.filename == 'unsigned.json': payload = payload.replace(b'3000000000', b'4000000000') + b' '
                b.writestr(entry, payload)
        with self.assertRaises(ValueError): r.compare_bytes(self.a, out.getvalue(), 'unsigned.json')

    def test_signed_either_side_refused(self):
        d = r.unsigned_diff.intent.decoder
        fields, _ = d.rlp_item(bytes.fromhex(d.demo_transaction()[2:]), 1)
        bad = self.pack('0x02' + d.rlp_encode(fields + [0, 1, 1]).hex())
        for a,b in ((bad,self.b),(self.a,bad)):
            with self.assertRaises(ValueError): r.compare_bytes(a,b,'unsigned.json')

    def test_duplicate_json_nonstandard_and_false_summary_refused(self):
        for raw in (b'{"transaction_hex":"a","transaction_hex":"b"}', b'{"transaction_hex":NaN}',
                    b'{"transaction_hex":"0x02c0","provenance":"synthetic unsigned demo","summary":{}}'):
            b = r.producer.build({'unsigned.json':raw})
            with self.assertRaises(ValueError): r.compare_bytes(self.a,b,'unsigned.json')

    def test_missing_unsafe_or_manifest_path(self):
        for path in ('absent.json','../unsigned.json','/unsigned.json','HANDOFF.json'):
            with self.assertRaises(ValueError): r.compare_bytes(self.a,self.b,path)

    def test_trusted_digests(self):
        result = r.compare_bytes(self.a,self.b,'unsigned.json',r.producer.digest(self.a),r.producer.digest(self.b))
        self.assertTrue(result['files']['after']['trusted_digest_matched'])
        with self.assertRaises(ValueError): r.compare_bytes(self.a,self.b,'unsigned.json',after_sha256='f'*64)

    def test_bounds_and_workspace_guard(self):
        with self.assertRaises(ValueError): r.compare_bytes(self.a,b'x'*(r.LIMIT+1),'unsigned.json')
        for p in ('../outside','/outside'):
            with self.assertRaises(ValueError): r.compare_paths(p,'anything','unsigned.json')

    def test_optional_source_and_cli_mismatch(self):
        directory = Path('test/scratch/revision')
        source = directory/'source'
        source.mkdir(parents=True,exist_ok=True)
        (directory/'before.zip').write_bytes(self.a)
        (directory/'after.zip').write_bytes(self.b)
        with zipfile.ZipFile(io.BytesIO(self.b)) as archive:
            for name in ('unsigned.json','note.txt'): (source/name).write_bytes(archive.read(name))
        args = ['compare',str(directory/'before.zip'),str(directory/'after.zip'),
                '--transaction-path','unsigned.json','--after-source',str(source)]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(r.main(args),0)
        self.assertTrue(json.loads(out.getvalue())['after_source']['matches_source'])
        (source/'note.txt').write_bytes(b'changed')
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(r.main(args),2)
        self.assertEqual(json.loads(out.getvalue())['after_source']['counts']['changed'],1)

    def test_cli_error_no_partial_report(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(r.main(['compare','../bad','anything','--transaction-path','unsigned.json']),1)
        self.assertEqual(out.getvalue(),'')


if __name__ == '__main__':
    unittest.main(verbosity=2)
