#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import yaml
from typing import Any, Dict

def parse_args():
    p = argparse.ArgumentParser(description="Print YAML manifest (minimal)")
    p.add_argument("--config", "-c", required=True, help="Path to YAML manifest")
    return p.parse_args()

def _parse_address(addr: str) -> str:
    # very small canonicalizer: expects host:port (IPv6 may be provided as [::1]:9001)
    if ":" not in addr:
        raise ValueError("address must be host:port")
    host, port = addr.rsplit(":", 1)
    host = host.strip()
    port = port.strip()
    if not port.isdigit():
        raise ValueError("address port must be numeric")
    # wrap bare IPv6 in brackets if needed
    if ":" in host and not host.startswith("[") and not host.endswith("]"):
        host = f"[{host}]"
    return f"{host}:{port}"

def load_config(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p}")
    text = p.read_text()
    doc = yaml.safe_load(text)
    return doc

def main():
    args = parse_args()
    try:
        cfg = load_config(args.config)
    except Exception as e:
        print(f"error loading config: {e}", file=sys.stderr)
        return 2

    print(yaml.safe_dump(cfg, sort_keys=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())