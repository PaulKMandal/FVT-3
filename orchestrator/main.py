#!/usr/bin/env python3
from __future__ import annotations
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import yaml
import grpc
from datetime import datetime, timezone
from common.proto import fvt3_pb2, fvt3_pb2_grpc

def parse_args():
    p = argparse.ArgumentParser(description="Orchestrator (server + client to federates)")
    p.add_argument("--config", "-c", required=True, help="Path to YAML config")
    p.add_argument("--host", default="0.0.0.0", help="Host to bind orchestrator gRPC server")
    p.add_argument("--port", type=int, default=9000, help="Port to bind orchestrator gRPC server")
    return p.parse_args()

def main():
    args = parse_args()
    cfg_path = Path(args.config)
    cfg = yaml.safe_load(cfg_path.read_text())

if __name__ == "__main__":
    main()