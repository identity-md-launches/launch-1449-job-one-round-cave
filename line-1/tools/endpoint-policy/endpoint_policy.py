#!/usr/bin/env python3
"""Offline validation of public HTTPS RPC URLs and the swarm's numeric local relay."""
import argparse
import importlib.util
from pathlib import Path
import json
import sys

MAX_INPUT = 65536
SOURCE = Path(__file__).resolve().parents[1] / 'rpc-snapshot' / 'rpc_snapshot.py'
SPEC = importlib.util.spec_from_file_location('rpc_snapshot', SOURCE)
rpc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rpc)
validate_endpoint = rpc.validate_endpoint



def audit(endpoints):
    if not isinstance(endpoints, list) or not endpoints or len(endpoints) > 64:
        raise ValueError('input must be a JSON list of 1 to 64 endpoint strings')
    results = []
    for endpoint in endpoints:
        # Do not echo a rejected URL; it could contain embedded credentials.
        try:
            validate_endpoint(endpoint)
            results.append({'accepted': True, 'endpoint': endpoint})
        except ValueError:
            results.append({'accepted': False, 'reason': 'URL does not meet endpoint policy'})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='offline public-provider and relay policy example')
    args = parser.parse_args()
    try:
        if args.demo:
            endpoints = ['https://ethereum-rpc.publicnode.com', 'https://eth.drpc.org',
                         'http://127.0.0.1:44117/rpc/1']
        else:
            raw = sys.stdin.buffer.read(MAX_INPUT + 1)
            if len(raw) > MAX_INPUT:
                raise ValueError('input exceeds 64 KiB')
            endpoints = json.loads(raw)
        results = audit(endpoints)
        print(json.dumps({'schema': 'rpc-endpoint-policy/1', 'network_used': False,
                          'results': results}, indent=2, sort_keys=True))
        return 0 if all(row['accepted'] for row in results) else 1
    except (ValueError, UnicodeError, RecursionError):
        print('endpoint-policy: invalid or oversized JSON endpoint list', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
