#!/usr/bin/env python3
from __future__ import annotations
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
import grpc
from common.proto import fvt3_pb2, fvt3_pb2_grpc

class ServerServicer(fvt3_pb2_grpc.ServerServiceServicer):
    def __init__(self, server_id: str):
        self.server_id = server_id

    def Init(self, request: fvt3_pb2.InitRequest, context) -> fvt3_pb2.Ack:
        ts = int(time.time())
        print("\n=== InitRequest received ===", flush=True)
        print(f"config_id: {request.config_id}", flush=True)
        print(f"timestamp_utc: {request.timestamp_utc}", flush=True)
        print("config_yaml:", flush=True)
        # print YAML/body as-is (may be multi-line)
        print(request.config_yaml, flush=True)
        print("===========================\n", flush=True)

        return fvt3_pb2.Ack(
            id=self.server_id,
            received_timestamp=ts,
            status="ok",
            note=""
        )

def parse_args():
    p = argparse.ArgumentParser(description="Minimal gRPC server")
    p.add_argument("--id", required=True, help="Server id (e.g., server-01)")
    p.add_argument("--host", default="0.0.0.0", help="Host to bind the gRPC server")
    p.add_argument("--port", type=int, default=9001, help="Port to bind the gRPC server")
    return p.parse_args()

def serve(host: str, port: int, server_id: str):
    server = grpc.server(ThreadPoolExecutor(max_workers=4))
    servicer = ServerServicer(server_id)
    fvt3_pb2_grpc.add_ServerServiceServicer_to_server(servicer, server)
    listen_addr = f"{host}:{port}"
    server.add_insecure_port(listen_addr)
    print(f"Starting gRPC server (id={server_id}) on {listen_addr} ...", flush=True)
    server.start()

    try:
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        print("Shutting down gRPC server...", flush=True)
        server.stop(0)

def main():
    args = parse_args()
    serve(args.host, args.port, args.id)

if __name__ == "__main__":
    main()