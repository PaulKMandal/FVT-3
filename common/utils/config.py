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

def _ensure(d: Dict[str, Any], key: str, default: Any):
    if key not in d or d[key] is None:
        d[key] = default
    return d[key]


def validate_and_normalize(cfg: Dict[str, Any]) -> Dict[str, Any]:
    # top-level required blocks
    for k in ("task", "model", "federation", "federates", "hyperparams"):
        if k not in cfg:
            raise ValueError(f"config missing required top-level key: '{k}'")

    model = cfg["model"]
    finetune = model.get("finetune_mode")
    if finetune not in ("full", "head", "lora"):
        raise ValueError("model.finetune_mode must be one of: full, head, lora")

    # If lora, require peft.enabled and set communication.send -> lora
    federation = _ensure(cfg, "federation", {})
    comm = federation.get("communication") or {}
    send = comm.get("send") if isinstance(comm, dict) else None

    if finetune == "lora":
        peft = model.get("peft")
        if not (isinstance(peft, dict) and peft.get("enabled")):
            raise ValueError("finetune_mode == 'lora' requires model.peft.enabled == true")
        if not send:
            federation.setdefault("communication", {})["send"] = "lora"
        elif send != "lora":
            raise ValueError("communication.send must be 'lora' when finetune_mode == 'lora'")
    else:
        # infer default send
        inferred = "full" if finetune == "full" else "delta"
        if not send:
            federation.setdefault("communication", {})["send"] = inferred

    # sensible defaults
    federation.setdefault("aggregation", "average")
    federation.setdefault("rounds", 3)
    cfg["federation"] = federation

    # federates list validation & address normalization
    feds = cfg.get("federates")
    if not isinstance(feds, list) or len(feds) == 0:
        raise ValueError("config.federates must be a non-empty list")
    normalized = []
    for i, f in enumerate(feds):
        if not isinstance(f, dict):
            raise ValueError(f"federates[{i}] must be a mapping")
        fid = f.get("id")
        addr = f.get("address")
        if not fid or not isinstance(fid, str):
            raise ValueError(f"federates[{i}] missing string 'id'")
        if not addr or not isinstance(addr, str):
            raise ValueError(f"federates[{i}] missing string 'address' (host:port)")
        addr_norm = _parse_address(addr)
        nf = dict(f)  # shallow copy
        nf["address"] = addr_norm
        normalized.append(nf)
    cfg["federates"] = normalized

    if cfg.get("task") == "classification":
        tp = _ensure(cfg, "task_params", {})
        inferred: dict = {}
        if "num_classes" not in tp:
            inferred["num_classes"] = 1000
            tp.setdefault("num_classes", inferred["num_classes"])
        if "input_size" not in tp:
            inferred["input_size"] = 224
            tp.setdefault("input_size", inferred["input_size"])
        if inferred:
            # minimal, obvious warning for the user + record for reproducibility
            print(
                f"Warning: config missing task_params; inferred defaults: {inferred}. "
                "For reproducibility, set these explicitly in the config.",
                file=sys.stderr,
            )
            cfg["_inferred_defaults"] = inferred
        cfg["task_params"] = tp

def load_config(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p}")
    text = p.read_text()
    doc = yaml.safe_load(text)
    if not isinstance(doc, dict):
        raise ValueError("config must be a YAML mapping (top-level dict)")
    return validate_and_normalize(doc)

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