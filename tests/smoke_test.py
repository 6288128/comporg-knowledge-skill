from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> dict:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def main() -> None:
    subprocess.run([sys.executable, "scripts/build_sample_assets.py"], cwd=ROOT, check=True)
    kg = run(["scripts/kg_query.py", "cache", "--limit", "5"])
    assert kg["matched_nodes"], "kg query should return at least one node"
    assert kg["source_pages"], "kg query should include source pages"
    qa = run(["scripts/asset_query.py", "cache", "--kind", "qa"])
    assert qa["results"], "asset query should return sample QA"
    print("smoke test passed")


if __name__ == "__main__":
    main()
