"""Measure in-memory shape for maximum placeholder witness inventory only.

No lineage queries, candidate cases, answers, projections, or sufficiency
outcomes are generated. This checks whether a list-of-dicts handoff can fit the
existing RP006 128 MiB worker-tree ceiling at the proposed row-count maximum.
"""
from __future__ import annotations

import json
import resource
import sys
from time import perf_counter


COUNT = 1_077_936
RSS_LIMIT_BYTES = 128 * 1024 * 1024


def peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(value)
    if sys.platform.startswith("linux"):
        return int(value * 1024)
    raise RuntimeError("Unsupported ru_maxrss unit contract")


def main() -> None:
    started = perf_counter()
    # Distinct dicts and case/query arrays model producer list retention. Values
    # are fixed placeholders, not computed query answers.
    rows = [
        {"ordinal": index, "mask": "111", "family": "FULL",
         "cases": ["PLACEHOLDER-L", "PLACEHOLDER-R"],
         "query": {"kind": "PLACEHOLDER", "args": ["X", "Y"]},
         "left_truth": None, "right_truth": None}
        for index in range(COUNT)
    ]
    peak = peak_rss_bytes()
    result = {"purpose": "ANSWER_FREE_IN_MEMORY_PLACEHOLDER_SHAPE",
              "candidate_inputs_read": False, "candidate_answers_generated": False,
              "placeholder_rows": len(rows), "peak_rss_bytes": peak,
              "existing_worker_rss_limit_bytes": RSS_LIMIT_BYTES,
              "fits_existing_rss_limit": peak <= RSS_LIMIT_BYTES,
              "elapsed_seconds": round(perf_counter() - started, 3)}
    print(json.dumps(result, sort_keys=True))
    del rows


if __name__ == "__main__":
    main()
