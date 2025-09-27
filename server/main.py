#!/usr/bin/env python3
from __future__ import annotations
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
import grpc
from common.proto import fvt3_pb2, fvt3_pb2_grpc

AGENT_ID: str = ""