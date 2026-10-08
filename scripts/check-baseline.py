"""Verify the exact preserved input snapshot; never approve a scientific release."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'baseline/SNAPSHOT.json').read_text())
assert manifest['release_approved'] is False, 'This snapshot manifest is preservation metadata.'
expected = manifest['files']
snapshot = ROOT / 'baseline/v0.1'
assert {p.relative_to(snapshot).as_posix() for p in snapshot.rglob('*') if p.is_file()} == set(expected), 'Snapshot file set changed'
for name, digest in expected.items():
    for base in (ROOT / 'baseline', snapshot):
        path = base / name
        assert path.is_file(), f'Missing baseline file: {path}'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, f'Baseline bytes changed: {path}'
print(f'PASS: {len(expected)} baseline source files match the preserved snapshot.')
