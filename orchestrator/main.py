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

class OrchestratorServicer(fvt3_pb2_grpc.OrchestratorServicer):
    def Register(self, request: fvt3_pb2.RegisterRequest, context) -> fvt3_pb2.RegisterResponse:
        ts = datetime.now(timezone.utc).isoformat()
        print(f"\n=== Register received at {ts} ===", flush=True)
        print(f"id: {request.id}")
        print(f"reported_n_samples: {request.reported_n_samples}")
        print(f"device: {request.device}")
        print(f"data_path: {request.data_path}")
        print("==============================\n", flush=True)
        return fvt3_pb2.RegisterResponse(status="ok", note="registered")

    def UploadModel(self, request_iterator, context) -> fvt3_pb2.UploadResponse:
        cnt = 0
        last_artifact = ""
        for chunk in request_iterator:
            cnt += 1
            last_artifact = chunk.artifact_id
        note = f"received {cnt} chunks for {last_artifact}"
        print(f"UploadModel done: {note}", flush=True)
        return fvt3_pb2.UploadResponse(status="ok", artifact_ref=last_artifact, note=note)


def serve_orchestrator(host: str, port: int):
    server = grpc.server(ThreadPoolExecutor(max_workers=8))
    fvt3_pb2_grpc.add_OrchestratorServicer_to_server(OrchestratorServicer(), server)
    addr = f"{host}:{port}"
    server.add_insecure_port(addr)
    server.start()
    print(f"Orchestrator gRPC server listening on {addr}", flush=True)
    return server

def parse_args():
    p = argparse.ArgumentParser(description="Orchestrator (server + client to federates)")
    p.add_argument("--config", "-c", required=True, help="Path to YAML config")
    p.add_argument("--host", default="0.0.0.0", help="Host to bind orchestrator gRPC server")
    p.add_argument("--port", type=int, default=9000, help="Port to bind orchestrator gRPC server")
    return p.parse_args()

def call_init_on_federate(address: str, config_id: str, config_yaml: str):
    # address expected as host:port
    channel = grpc.insecure_channel(address)
    stub = fvt3_pb2_grpc.ServerStub(channel)
    req = fvt3_pb2.InitRequest(config_id=config_id, config_yaml=config_yaml,
                               timestamp_utc=int(time.time()))
    try:
        resp = stub.Init(req, timeout=10.0)
    except Exception as e:
        print(f"Init RPC to {address} failed: {e}", flush=True)
        return None
    print(f"Init ACK from {address}: id={resp.id} status={resp.status} received_ts={resp.received_timestamp}", flush=True)
    return resp

def main():
    args = parse_args()
    cfg_path = Path(args.config)
    cfg = yaml.safe_load(cfg_path.read_text())

    # start orchestrator server
    server = serve_orchestrator(args.host, args.port)

    # prepare config payload (use config name or filename as id)
    config_id = cfg.get("name") or cfg_path.stem
    config_yaml = cfg_path.read_text()

    # call Init on each federate listed
    federates = cfg.get("federates", [])

if __name__ == "__main__":
    main()