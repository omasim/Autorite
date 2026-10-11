# RP005A — Reviewed source and input freeze

2026-10-11. Pre-execution provenance record. RP-005A remains PLANNED; Test TST-RP005A001 is registered and Q-2 ACTIVE. No recorded attempt or Result exists. Cycle 01 remains ACTIVE at 3/13 (23.1%).

## Reviewed implementation

The pinned source commit is [fe796a089df3e53101c20a20358391e84f59fc13](https://github.com/omasim/Autorite/commit/fe796a089df3e53101c20a20358391e84f59fc13). It contains the reviewed protocol, fixtures, implementation, registration and software controls before a recorded research attempt. The following SHA-256 values bind all sixteen exact inputs.

| Input | SHA-256 |
| --- | --- |
| [research/RP005A/RP005A_OPERATIONAL_PROTOCOL.md](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/RP005A_OPERATIONAL_PROTOCOL.md) | `95701fa189b39d0610b26df359dd2bc5abffa2bf7f69630b76f155f1d725ffe7` |
| [research/RP005A/RP005A_FIXTURES.json](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/RP005A_FIXTURES.json) | `b3fd3b78bd6d52be132e34127247599156c5a4db12d28167e0fcaa4fad0f6f1c` |
| [research/RP005A/planning.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/planning.py) | `40e2e80bd0a1065aa6ed882a27062cbec0596ba89fc24d4b40c413e197316998` |
| [research/RP005A/RP005A_COLLISION_REVIEW.md](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/RP005A_COLLISION_REVIEW.md) | `f648b1502958460f8c5e4ed0c3a771472c1da2984d3a083206413345e63e0d24` |
| [research/RP005A/RP005A_PREPARATION_REVIEW.md](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/RP005A_PREPARATION_REVIEW.md) | `546b18789fbe36a599495df461625dc9c1ea75f9511b0163f49984f900a4b0e8` |
| [research/RP005A/RP005A_AUDIT_CONFIG.json](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/RP005A_AUDIT_CONFIG.json) | `b2d21f1f2cc8dbdfcf33c066f0cb67ea2c6e6498c446989d95b57b1f3b661394` |
| [research/RP005A/audit.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/audit.py) | `781b41f7fc67509357f919160d502dc660ff3153ff23e22e0cc1180af7baf0fc` |
| [research/RP005A/replay.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/replay.py) | `66ad0ea70d30ab98a08ab597d366d81c2a161834639aa433b7f8fbdbd95ad883` |
| [research/RP005A/contract.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/contract.py) | `d95cb3b8e947cdc98d1df360887916ce297bd8f34ccedbbbe6241f7844c87de4` |
| [research/RP005A/RP005A_EXECUTION_REVIEW.md](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/RP005A_EXECUTION_REVIEW.md) | `55bb2a873d4604d0b1b6314e48cc6d5461f7cd37e75045216bc495de2b911cf5` |
| [research/RP005A/audit-001/RECORD.md](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/research/RP005A/audit-001/RECORD.md) | `feb15f20d71ae77c6579ef838e5eac4a1f235098bcdb0e218b8e73eb9f404578` |
| [scripts/run-rp005a-audit.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/scripts/run-rp005a-audit.py) | `0e710412055101b4b685bd5a2ec05058d30764f86c021c823c2ac08bb81239c7` |
| [scripts/check-rp005a-audit.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/scripts/check-rp005a-audit.py) | `82046245c5f07daaddb9c59103ad74c33e2590ee4b47b3572f5ec5ec67813ee7` |
| [scripts/check-rp005a-preparation.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/scripts/check-rp005a-preparation.py) | `00c9afb12b8675bea5756be3ce72939c4af24b3202a17836797e8c2b77a1ad05` |
| [tests/test_rp005a_planning.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/tests/test_rp005a_planning.py) | `b3cab32d6b58f109e83a316bd9291813a35c2471431acea5f36d611283e02517` |
| [tests/test_rp005a_audit.py](https://github.com/omasim/Autorite/blob/fe796a089df3e53101c20a20358391e84f59fc13/tests/test_rp005a_audit.py) | `ea997871618a1aaad9e32197e9392348b0461f88a3783a465dec1f643c22631d` |

## Configuration and artifact contract

The [machine-readable freeze](https://github.com/omasim/Autorite/blob/main/research/RP005A/RP005A_SOURCE_FREEZE.json) repeats this commit/hash inventory and the exact numerical configuration. The freeze sidecar/note are outside the sixteen scientific/implementation inputs, avoiding a self-referential source hash. A subsequent publication-ledger commit does not change the selected implementation source.

Configuration v0.1 reserves audit-20261011-001: V0/V1/V2/C0; H=1/2/4; both arms; fixed t1–t5; B=3; 24 planner rows; 12 paired comparisons; 35 source certificates and 313 ordered pairs for each raw/budget inclusion family. One deterministic 60-second/128-MiB attempt, Python >=3.11, no audit network or random seeds. These are declared limits, not observed runtime.

Before any execution the sidecar must be committed, every input must match this source, the tracked checkout must be clean, and the reserved run directory must not exist. The runner records the actual user execution instruction supplied as its authorization note. Preparation checks do not supply that instruction or create a research outcome.

Eight complete-run files are declared: manifest, frozen-inputs, planner, pairs, structural, summary, replay and timing. Seven output hashes, full inventory, source-freeze hash and independent full-value replay are required before a VALID Result. Failures preserve partial bytes plus failure.txt, without overwrite or automatic retry.

Verify the committed freeze with `python3 scripts/check-rp005a-audit.py`. Until execution, the expected report is sixteen inputs verified and zero recorded attempts.

[Implementation review](https://autorite.net/sources/rp005a-audit-execution-review/) · [Preserved operational protocol](https://autorite.net/sources/rp005a-operational-protocol/)
