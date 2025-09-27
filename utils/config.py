#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import yaml

def parse_args():
    p = argparse.ArgumentParser(description="Print YAML manifest (minimal)")
    p.add_argument("--config", "-c", required=True, help="Path to YAML manifest")
    return p.parse_args()

def main():
    args = parse_args()
    path = Path(args.config)
    data = yaml.safe_load(path.read_text())
    if not path.exists():
        print("Error: Path not found")

    try:
        text = path.read_text()
    except Exception as e:
        print(f"error reading file: {e}", file=sys.stderr)

    print(yaml.safe_dump(data, sort_keys=False))

if __name__ == "__main__":
    main()