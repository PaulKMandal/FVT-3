#!/usr/bin/env python3
from __future__ import annotations
import argparse
import subprocess
import sys
import time
from pathlib import Path
import yaml

def parse_args():
    p = argparse.ArgumentParser(description="Start orchestrator + local federates for demo")
    p.add_argument("--manifest", "-m", required=True, help="Path to YAML manifest")
    p.add_argument("--orch-port", type=int, default=9000, help="Orchestrator port (default: 9000)")
    p.add_argument("--orch-host", type=str, default="0.0.0.0", help="Orchestrator host (default: 0.0.0.0)")
    return p.parse_args()


def main():
    args = parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"manifest not found: {manifest_path}", file=sys.stderr)

    manifest = yaml.safe_load(manifest_path.read_text())
    federates = manifest.get("federates", [])

    procs = []

        orch_cmd = [
        sys.executable,
        "orchestrator/main.py",
        "--manifest", str(manifest_path),
        "--host", args.orch_host,
        "--port", str(args.orch_port),
    ]
    
    print("Starting orchestrator:", " ".join(orch_cmd))
    orch_proc = subprocess.Popen(orch_cmd)
    procs.append(("orchestrator", orch_proc))