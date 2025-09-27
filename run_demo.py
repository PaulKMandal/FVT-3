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
    p.add_argument("--manifest", "-m", required=True, help="Path to YAML manifest")
    p.add_argument("--orch-port", type=int, default=9000, help="Orchestrator port (default: 9000)")
    p.add_argument("--orch-host", type=str, default="0.0.0.0", help="Orchestrator host (default: 0.0.0.0)")
    return p.parse_args()