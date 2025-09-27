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

    for f in federates:
        fid = f.get("id")
        addr = f.get("address")
        if not fid or not addr:
            print(f"skipping federate with missing id/address: {f}")
            continue
        try:
            host, port = _parse_address(addr)
        except Exception as e:
            print(f"invalid address for federate {fid}: {addr} — skipping ({e})")
            continue

        server_cmd = [
            sys.executable,
            "server/main.py",
            "--id", str(fid),
            "--config", str(config_path),
            "--host", str(host),
            "--port", str(port),
        ]
        print(f"Starting server {fid}:", " ".join(server_cmd))
        p = subprocess.Popen(server_cmd)
        procs.append((f"server:{fid}", p))

    try:
        # keep running until interrupted
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nCaught Ctrl-C — terminating child processes...")

    # terminate children
    for name, p in procs:
        if p.poll() is None:
            print(f"terminating {name} (pid={p.pid})")
            p.terminate()
    # give them a moment, then kill if necessary
    time.sleep(1.0)
    for name, p in procs:
        if p.poll() is None:
            print(f"killing {name} (pid={p.pid})")
            p.kill()

    print("All child processes stopped.")
    return 0

if __name__ == "__main__":
    main()