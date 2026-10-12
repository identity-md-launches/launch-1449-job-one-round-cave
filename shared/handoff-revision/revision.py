#!/usr/bin/env python3
"""Compare verified handoff files and their original unsigned envelopes offline."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
LIMIT = 99000


def load(name, folder, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / 'vendor' / folder / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


inspector = load('revision_inspector', 'handoff-inspect', 'inspect_handoff.py')
archive_diff = load('revision_archive_diff', 'handoff-compare', 'compare_handoff.py')
source_check = load('revision_source', 'handoff-source', 'source_check.py')
unsigned_diff = load('revision_unsigned', 'unsigned-diff', 'unsigned_diff.py')
producer = load('revision_producer', 'handoff', 'handoff.py')
BOUNDS = inspector.Limits(archive_bytes=LIMIT, payload_bytes=LIMIT,
                          metadata_bytes=LIMIT, manifest_bytes=LIMIT, files=100)


def parse_envelope(raw):
    def invalid(value):
        raise ValueError('nonstandard JSON constant')
    obj = json.loads(raw, object_pairs_hook=inspector.unique_object, parse_constant=invalid)
    if (not isinstance(obj, dict) or set(obj) != {'transaction_hex', 'provenance'}
            or obj['provenance'] not in ('synthetic unsigned demo', 'user-supplied unsigned envelope')):
        raise ValueError('expected original transaction_hex and explicit provenance')
    return obj


def compare_bytes(before, after, transaction_path, before_sha256=None, after_sha256=None):
    inspector.safe_name(transaction_path)
    if transaction_path == inspector.MANIFEST:
        raise ValueError('manifest is not an unsigned payload')
    # Verify BOTH complete archives before interpreting any payload.
    receipts = [inspector.inspect_stream(io.BytesIO(data), BOUNDS, expected)
                for data, expected in ((before, before_sha256), (after, after_sha256))]
    objects = []
    for data, receipt in zip((before, after), receipts):
        if transaction_path not in {f['path'] for f in receipt['files']}:
            raise ValueError('selected unsigned payload missing from an archive')
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            objects.append(parse_envelope(archive.read(transaction_path)))
    semantic = unsigned_diff.compare(*(obj['transaction_hex'] for obj in objects))
    return {'schema': 'handoff-revision/1',
            'files': archive_diff.compare_receipts(*receipts),
            'unsigned': semantic, 'transaction_path': transaction_path,
            'provenance': [obj['provenance'] for obj in objects],
            'limits': 'Archive integrity and unsigned byte comparison only; no authenticity, '
                      'sender, chain state, execution, signing or safety is established.'}


def compare_paths(before, after, transaction_path, before_sha256=None,
                  after_sha256=None, source=None):
    def read(path):
        return producer.regular_bytes(producer.workspace_path(path), LIMIT)
    a, b = read(before), read(after)
    result = compare_bytes(a, b, transaction_path, before_sha256, after_sha256)
    if source is not None:
        # Use the receipt for the EXACT bytes already compared, avoiding a second
        # archive read that might describe a different revision.
        receipt = inspector.inspect_stream(io.BytesIO(b), BOUNDS, after_sha256)
        files = source_check.source_receipt(source, inspector, BOUNDS)
        result['after_source'] = source_check.compare(receipt, files)
    return result


def demo_archives():
    before, after = unsigned_diff.demo_pair()
    def pack(tx):
        raw = (json.dumps({'transaction_hex': tx, 'provenance': 'synthetic unsigned demo'},
                          sort_keys=True) + '\n').encode()
        return producer.build({'unsigned.json': raw, 'note.txt': b'Public unsigned inspection sample.\n'})
    return pack(before), pack(after)


def demo():
    a, b = demo_archives()
    result = compare_bytes(a, b, 'unsigned.json')
    assert result['unsigned']['changes'][0]['field'] == 'maxFeePerGas'
    assert result['files']['counts'] == dict(added=0, removed=0, modified=1, unchanged=1)
    result['demo'] = 'Two synthetic unsigned ZTO totalSupply envelopes; neither sent or executed.'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    command = sub.add_parser('compare')
    command.add_argument('before')
    command.add_argument('after')
    command.add_argument('--transaction-path', required=True)
    command.add_argument('--before-sha256')
    command.add_argument('--after-sha256')
    command.add_argument('--after-source', help='optional source tree represented by after archive')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            result = compare_paths(args.before, args.after, args.transaction_path,
                                   args.before_sha256, args.after_sha256, args.after_source)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2 if 'after_source' in result and not result['after_source']['matches_source'] else 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError, zipfile.BadZipFile,
            EOFError, NotImplementedError) as error:
        print('handoff-revision: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
