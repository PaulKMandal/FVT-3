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
    p.add_argument("--config", "-c", required=True, help="Path to YAML config")
    p.add_argument("--orch-port", type=int, default=9000, help="Orchestrator port (default: 9000)")
    p.add_argument("--orch-host", type=str, default="0.0.0.0", help="Orchestrator host (default: 0.0.0.0)")
    return p.parse_args()


def _parse_address(addr: str):
    if ":" not in addr:
        raise ValueError("address must be host:port")
    host, port = addr.rsplit(":", 1)
    return host, int(port)

def main():
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"config not found: {config_path}", file=sys.stderr)

    config = yaml.safe_load(config_path.read_text())
    federates = config.get("federates", [])

    procs = []

    orch_cmd = [
        sys.executable,
        "orchestrator/main.py",
        "--config", str(config_path),
        "--host", args.orch_host,
        "--port", str(args.orch_port),
    ]

    print("Starting orchestrator:", " ".join(orch_cmd))
    orch_proc = subprocess.Popen(orch_cmd)
    procs.append(("orchestrator", orch_proc))

    time.sleep(0.5)

if __name__ == "__main__":
    main()