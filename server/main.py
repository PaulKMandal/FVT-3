#!/usr/bin/env python3
from __future__ import annotations
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
import grpc
from common.proto import fvt3_pb2, fvt3_pb2_grpc


def parse_args():
    p = argparse.ArgumentParser(description="Minimal gRPC server")
    p.add_argument("--id", required=True, help="Server id (e.g., server-01)")
    p.add_argument("--host", default="0.0.0.0", help="Host to bind the gRPC server")
    p.add_argument("--port", type=int, default=9001, help="Port to bind the gRPC server")
    return p.parse_args()

def main():
    args = parse_args()

if __name__ == "__main__":
    main()