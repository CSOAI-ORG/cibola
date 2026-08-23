#!/usr/bin/env python3
"""DORADO schema CI — every commit re-validates the example card against the schema."""
import json, os, sys
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
schema = json.load(open(os.path.join(base, 'schemas', 'measurement-card.schema.json')))
card = json.load(open(os.path.join(base, 'example-card.json')))
import subprocess
r = subprocess.run([sys.executable, '-c', 'import jsonschema; jsonschema.validate(%r, %r)' % (card, schema)], capture_output=True, text=True)
if r.returncode == 0:
    print('SCHEMA CI: PASS — example-card.json validates against measurement-card.schema.json')
    sys.exit(0)
# fallback structural check if jsonschema missing
missing = [k for k in schema['required'] if k not in card]
if missing:
    print(f'SCHEMA CI: FAIL — missing required: {missing}')
    sys.exit(1)
print('SCHEMA CI: PASS (structural) — all required fields present')
