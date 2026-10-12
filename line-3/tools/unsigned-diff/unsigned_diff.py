#!/usr/bin/env python3
"""Compare complete unsigned type-2 envelopes, offline and without a wallet."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'erc20-intent'))
import intent

FIELDS = ('chainId', 'nonce', 'maxPriorityFeePerGas', 'maxFeePerGas',
          'gasLimit', 'to', 'value', 'data', 'accessList')
MEANINGS = {
    'chainId': 'The chain identifier changed.',
    'nonce': 'The transaction sequence number changed.',
    'maxPriorityFeePerGas': 'The priority fee cap changed (wei per gas).',
    'maxFeePerGas': 'The total fee cap changed (wei per gas).',
    'gasLimit': 'The gas limit changed; this is not a gas estimate.',
    'to': 'The destination changed; null means contract creation.',
    'value': 'The native ETH value changed (wei).',
    'data': 'The complete calldata or initcode changed, including arguments and trailing bytes.',
    'accessList': 'The ordered access list changed; duplicates are retained.',
}


def fingerprint(text):
    """SHA-256 identifies inspection bytes, not an Ethereum transaction hash."""
    raw = bytes.fromhex(text[2:] if text.startswith('0x') else text)
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'byteLength': len(raw)}


def compare(before_hex, after_hex):
    # Validate BOTH originals before returning any report. Never trust summaries.
    before = intent.interpret(before_hex)
    after = intent.interpret(after_hex)
    changes = []
    for field in FIELDS:
        old = before['transaction'][field]
        new = after['transaction'][field]
        if old != new:
            changes.append({'field': field, 'before': old, 'after': new,
                            'meaning': MEANINGS[field]})
    budget_delta = {}
    for field in ('gasFeeCapWei', 'valuePlusGasFeeCapWei'):
        budget_delta[field] = str(int(after['feeBudget'][field]) -
                                 int(before['feeBudget'][field]))
    return {
        'status': 'changed' if changes else 'identical',
        'meaning': 'Exact unsigned envelope comparison; identical does not mean safe to sign.',
        'beforeBytes': fingerprint(before_hex),
        'afterBytes': fingerprint(after_hex),
        'changes': changes,
        'feeBudgetDeltaWei': budget_delta,
        'beforeInspection': before,
        'afterInspection': after,
        'limits': [
            'Synthetic demos are not observed or executed transactions.',
            'SHA-256 fingerprints are not Ethereum transaction hashes or signer identities.',
            'No sender, chain state, simulation, gas sufficiency or safety is established.',
            'ABI patterns do not prove contract behavior; review full calldata and both inspections.',
        ],
    }


def demo_pair():
    original = intent.decoder.demo_transaction()
    fields, _ = intent.decoder.rlp_item(bytes.fromhex(original[2:]), 1)
    fields[3] = 3_000_000_000
    changed = '0x02' + intent.decoder.rlp_encode(fields).hex()
    return original, changed


def main(arguments):
    if arguments == ['--demo']:
        pair = demo_pair()
    elif len(arguments) == 2:
        pair = arguments
    else:
        print('usage: unsigned_diff.py --demo | BEFORE_HEX AFTER_HEX', file=sys.stderr)
        return 2
    result = compare(*pair)
    print(json.dumps(result, indent=2, sort_keys=True))
    # A difference is a successful comparison, not a parser error.
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ValueError as error:
        print(f'error: {error}', file=sys.stderr)
        raise SystemExit(2) from None
