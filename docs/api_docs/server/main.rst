# Server

The **Server** executes local training rounds when instructed by the orchestrator. This module implements the gRPC **Server** service.

## RPCs

### `Init(request, context)`
Initializes the server with run configuration and (optional) privacy settings before any rounds start.

**Request – `fvt3.InitRequest`**

| Field | Type | Description |
|---|---|---|
| `config_id` | `string` | Run/experiment identifier (stable across RPCs). |
| `config_yaml` | `string` | Full YAML manifest (stringified). |
| `timestamp_utc` | `int64` | Orchestrator-side Unix seconds (UTC). |
| `method` | `fvt3.Method` | Training method (e.g., `HFL`). |
| `privacy` | `fvt3.Privacy` | Optional DP/secure-agg parameters. |

**Response – `fvt3.Ack`**

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Server id; may be empty on first contact. |
| `received_timestamp` | `int64` | Server-side Unix seconds when `Init` was processed. |
| `status` | `string` | `"ok"` or `"error"`. |
| `note` | `string` | Optional human-readable note. |

**Notes**
- Persist `config_id` for subsequent `StartRound` calls.
- Validate YAML and local environment (model weights availability, device readiness).
- If DP is enabled, initialize your privacy accountant here.

---

### `StartRound(request, context)`  *(if implemented on your Server)*
Starts a local training round using a global reference (e.g., base weights or adapter) and round-specific knobs.

**Request – `fvt3.StartRoundRequest`**

| Field | Type | Description |
|---|---|---|
| `config_id` | `string` | Must match the id from `Init`. |
| `round_id` | `int32` | 0-based round index (`r0`, `r1`, ...). |
| `global_ref` | `string` | Path/URI to base or adapter for this round. |
| `train_spec` | `fvt3.TrainSpec` | Per-round local training settings. |

**Response – `fvt3.Ack`** (same fields as above)

**Typical flow**
1. Load `global_ref` (fail fast if missing).
2. Train per `train_spec` (epochs, LR, batch size).
3. Emit metrics locally; prepare upload artifact.
4. Call `Orchestrator.UploadModel` with streamed chunks.

---

## Data Model (selected)

### `fvt3.Method`
Training method enum.

| Value | Meaning |
|---|---|
| `METHOD_UNSPECIFIED` | Reserved for future methods. |
| `HFL` | Horizontal Federated Learning. |

### `fvt3.UploadChunk`  *(client → orchestrator)*
See orchestrator docs; servers construct these after training.

---

## Examples

### Handling `Init`
    class ServerServicer(fvt3_pb2_grpc.ServerServicer):
        def Init(self, request, context):
            cfg = yaml.safe_load(request.config_yaml)
            self.run_id = request.config_id
            self.dp = request.privacy if request.HasField("privacy") else None
            return fvt3_pb2.Ack(id=self.server_id, received_timestamp=int(time.time()), status="ok")

### Starting a round and uploading
    def run_round(orchestrator_stub, round_id, global_ref, train_spec):
        artifact = train(global_ref, train_spec)  # returns bytes or a file path
        for i, payload in enumerate(split_bytes(artifact, 2<<20)):
            yield fvt3_pb2.UploadChunk(
                id="server-01", artifact_id=f"lora_r{round_id}_server01",
                seq=i, data=payload, final_chunk=(i==last)
            )
        resp = orchestrator_stub.UploadModel(chunks())

---

## Operational Notes
- Validate `round_id` monotonicity and `config_id` consistency.
- Consider backpressure (slow uploads) and resumable uploads for large artifacts.
- If DP is enabled, update privacy accountant per step and stop when ε exceeds target.

