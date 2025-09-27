#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

PROTO_DIR = Path("common/proto")
PROTO_NAME = "fvt3.proto"
PB2_GRPC = PROTO_DIR / "fvt3_pb2_grpc.py"

def main():
    if not PROTO_DIR.exists():
        print(f"proto dir not found: {PROTO_DIR}", file=sys.stderr)
        return 2

    # generate stubs (run protoc from common/proto so we pass only the basename)
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        "-I.",
        "--python_out=.",
        "--grpc_python_out=.",
        PROTO_NAME,
    ]
    res = subprocess.run(cmd, cwd=str(PROTO_DIR))
    if res.returncode != 0:
        print("protoc failed", file=sys.stderr)
        return res.returncode

    # patch the generated file to use relative import
    if not PB2_GRPC.exists():
        print(f"expected generated file not found: {PB2_GRPC}", file=sys.stderr)
        return 3

    s = PB2_GRPC.read_text()
    s_new = s.replace("import fvt3_pb2 as fvt3__pb2", "from . import fvt3_pb2 as fvt3__pb2")
    PB2_GRPC.write_text(s_new)
    print(f"Patched {PB2_GRPC} -> relative import")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
