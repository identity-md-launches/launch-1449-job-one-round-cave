#!/usr/bin/env python3
"""Offline behavioral checks for changes that can disappear in loose summaries."""
import contextlib
import hashlib
import io
import unittest

import unsigned_diff as tool

D = tool.intent.decoder


def fields():
    return [1, 0, 1_000_000_000, 2_000_000_000, 100000,
            bytes.fromhex(D.ZTO[2:]), 0, bytes.fromhex('18160ddd'), []]


def encode(values):
    return '0x02' + D.rlp_encode(values).hex()


class ComparisonTests(unittest.TestCase):
    def test_demo_reports_fee_change_and_exact_delta(self):
        report = tool.compare(*tool.demo_pair())
        self.assertEqual(report['status'], 'changed')
        self.assertEqual([c['field'] for c in report['changes']], ['maxFeePerGas'])
        self.assertEqual(report['feeBudgetDeltaWei']['gasFeeCapWei'], '100000000000000')
        self.assertEqual(report['beforeInspection']['destinationLabel'], 'ZTO')

    def test_same_bytes_accept_hex_case_and_optional_prefix(self):
        original = D.demo_transaction()
        report = tool.compare(original, original[2:].upper())
        self.assertEqual(report['status'], 'identical')
        self.assertEqual(report['changes'], [])
        self.assertEqual(report['beforeBytes'], report['afterBytes'])
        self.assertEqual(report['beforeBytes']['sha256'],
                         hashlib.sha256(bytes.fromhex(original[2:])).hexdigest())

    def test_each_unsigned_field_change_is_visible(self):
        mutations = [2, 1, 1000000001, 2000000001, 100001,
                     bytes.fromhex(tool.intent.IMD[2:]), 1, b'\x18\x16\x0d\xdd\x01',
                     [[bytes.fromhex(D.ZTO[2:]), []]]]
        for i, replacement in enumerate(mutations):
            with self.subTest(field=tool.FIELDS[i]):
                after = fields()
                after[i] = replacement
                report = tool.compare(encode(fields()), encode(after))
                self.assertEqual([c['field'] for c in report['changes']], [tool.FIELDS[i]])

    def test_same_selector_changed_approval_amount_not_hidden(self):
        before, after = fields(), fields()
        prefix = bytes.fromhex('095ea7b3') + bytes(12) + bytes.fromhex(tool.intent.IMD[2:])
        before[7] = prefix + (1).to_bytes(32, 'big')
        after[7] = prefix + (2**256 - 1).to_bytes(32, 'big')
        report = tool.compare(encode(before), encode(after))
        self.assertEqual(report['changes'][0]['field'], 'data')
        self.assertEqual(report['beforeInspection']['calldata']['approvalKind'], 'finite')
        self.assertEqual(report['afterInspection']['calldata']['approvalKind'], 'maximum-uint256')

    def test_unknown_selector_and_trailing_bytes_compared_in_full(self):
        for data in (bytes.fromhex('ffffffffabcd'), bytes.fromhex('18160dddabcd')):
            before, after = fields(), fields()
            before[7], after[7] = data, data[:-1] + b'\xff'
            report = tool.compare(encode(before), encode(after))
            self.assertEqual(report['status'], 'changed')
            self.assertEqual(report['changes'][0]['before'], '0x' + data.hex())

    def test_access_list_order_and_duplicate_counts_retained(self):
        a = [bytes.fromhex(D.ZTO[2:]), [bytes.fromhex('12' * 32)]]
        b = [bytes.fromhex(tool.intent.IMD[2:]), []]
        before = fields()
        before[8] = [a, b]
        for entries in ([b, a], [a, b, a], [a, [b[0], [a[1][0]]]]):
            after = fields()
            after[8] = entries
            report = tool.compare(encode(before), encode(after))
            self.assertEqual([c['field'] for c in report['changes']], ['accessList'])
        duplicate_slot = fields()
        duplicate_slot[8] = [[a[0], a[1] * 2], b]
        self.assertEqual(tool.compare(encode(before), encode(duplicate_slot))['status'], 'changed')

    def test_contract_creation_destination_is_explicit(self):
        after = fields()
        after[5] = b''
        report = tool.compare(encode(fields()), encode(after))
        self.assertIsNone(report['changes'][0]['after'])
        self.assertEqual(report['afterInspection']['calldata']['status'], 'contract-creation')

    def test_negative_and_large_fee_deltas_remain_exact_strings(self):
        before, after = fields(), fields()
        before[3], after[3] = 2**200, 1
        after[6] = 2**180
        report = tool.compare(encode(before), encode(after))
        self.assertEqual(report['feeBudgetDeltaWei']['gasFeeCapWei'], str(100000 * (1 - 2**200)))
        self.assertEqual(report['feeBudgetDeltaWei']['valuePlusGasFeeCapWei'],
                         str(100000 * (1 - 2**200) + 2**180))

    def test_invalid_either_side_refuses_entire_report(self):
        signed = encode(fields() + [0, 1, 1])
        noncanonical = fields()
        noncanonical[1] = b'\0'
        for bad in ('0x02c0', '0x01c0', signed, encode(noncanonical), '0x02 ff', '0x02zz'):
            for pair in ((bad, D.demo_transaction()), (D.demo_transaction(), bad)):
                with self.assertRaises(ValueError):
                    tool.compare(*pair)

    def test_cli_difference_is_success_and_usage_is_controlled(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(tool.main(['--demo']), 0)
        self.assertIn('changed', output.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(tool.main([]), 2)


if __name__ == '__main__':
    unittest.main()
