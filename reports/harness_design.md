# Grader and harness contract

`grade_task(task_dir, answer)` reports strict full-answer agreement and the
proportion of correct gold leaf fields. `grade_batch(batch_dir, answers_dir)`
reports the task-level exact-match rate as the primary metric. Its field metric
is a micro average over all gold fields. Per-domain metrics use the same rules.

Answers normally live at `<answers>/<task_id>/answer.json`. Flat
`<answers>/<task_id>.json` files are accepted for convenience. If both exist,
the nested file takes precedence. Missing files and malformed JSON receive zero
credit and remain in the denominator. Duplicate JSON keys and non-finite numbers
are rejected. Additional properties or any schema violation prevent exact match.

## Exactness and normalization

Won integers require JSON integers, with no rounding or tolerance. Boolean and
integral floating-point values do not satisfy integer fields. Strings use Unicode
NFKC normalization followed by whitespace removal and case folding. String enum
and const checks apply the same normalization, so a schema enum does not defeat
the documented grading policy. Other schema constraints still apply normally.

Nested objects are traversed in sorted key order. Arrays are matched by position.
Every scalar is a field. Empty arrays and objects each count as one field, and
missing paths never receive credit. Unrequested fields can therefore leave the
field score high while making exact match zero. Errors identify schema paths and
validators; field results identify the paths that matched.

## Agent-visible staging

Each task gets a newly allocated work directory. The coordinator copies only
files listed in `input_files`, retaining their `inputs/` paths. It writes
`instruction.txt` and `answer_schema.json`. It does not copy `task.yaml`, canary
metadata, `gold.json`, `trace.json`, or `extraction_map.json`. Undeclared input
files are also omitted. Absolute paths and parent traversal are rejected.
Symlink checks include every path component. Reads use `openat` with
`O_NOFOLLOW`, preventing a concurrent symlink replacement from escaping a file
read check.

The trusted fake oracle calls `render.restore_scenario(task_dir)` to parse
rendered inputs using the extraction map. It then recomputes the answer through
`KrRubberStamp.registry.calculate(domain, scenario)`. It does not read gold or
trace to solve the task. The grader reads gold separately after answer submission.
The null solver submits `{}`. Neither fake solver constructs a model adapter or
makes a model API request.

`run_fake(batch_dir, answers_dir, solver='oracle', work_root=None)` returns the
grading metrics plus staging paths. Supplying `work_root` retains the workspaces
for inspection. Omitting it removes temporary workspaces at the end. Submitted
answers persist in either case.

## Python execution and its boundary

File-reading tools accept only relative workspace paths and return at most
65,536 bytes. Binary content is explicitly encoded as base64. Python execution
has a timeout and bounded captured output.

Model-generated Python uses Docker. The command mounts only that task workspace
at `/workspace`. It disables container networking and uses a read-only root
filesystem. It drops Linux capabilities and enables `no-new-privileges`, with
process, CPU, and memory limits. The Docker socket and parent environment
credentials are not mounted or forwarded. The image must already exist locally;
`--pull=never` prevents the harness from fetching one implicitly. Container
cleanup runs after execution, including timeout termination.

A trusted-only local backend is available for tests. It requires both
`execution_backend='local'` and `trusted_local=True`. A current directory plus
path checks cannot isolate arbitrary Python from the host filesystem or
network. That backend must never run model-generated or otherwise untrusted
code. The model runner does not offer a local fallback.

Docker is an operational dependency for untrusted Python. Container isolation
still relies on the installed Docker engine and its security configuration.
These controls do not establish resistance to kernel or container-runtime
exploits. Real container execution must be verified separately in the deployment
environment. On this build host, the Docker CLI is installed but the engine
socket is unavailable, so real container execution could not be exercised.
The default `python:3.12-slim` image supplies the standard library;
users can prepare an image containing PDF and spreadsheet parsers and select it
explicitly.

## Opt-in API interface

`ChatAdapter.complete(messages, tools)` returns an assistant message with optional
function tool calls. `OpenAICompatibleAdapter` implements this interface for an
HTTP(S) chat-completions endpoint. Construction performs no request. API keys are
provided explicitly and remain in the trusted coordinator.

Dataset users can opt in to `run_with_adapter(...)`. It runs a bounded tool loop
and accepts either workspace `answer.json` or a final JSON object. This function
has not been exercised with a real model. Repository validation uses injected
fake adapters and the oracle/null solvers only.

```python
from pathlib import Path
from harness.adapter import OpenAICompatibleAdapter
from harness import run_with_adapter

# User-controlled example only. This benchmark build never executes it.
adapter = OpenAICompatibleAdapter(
    model="YOUR_MODEL",
    base_url="https://YOUR_ENDPOINT/v1",
    api_key="YOUR_KEY",
)
# Prepare a container image with the parsers your model needs before opting in.
# result = run_with_adapter(
#     Path("data/batch_1"), Path("my_answers"), adapter,
#     container_image="your-prepared-krt-image:latest",
# )
```

## Validation coverage

Tests cover integer type traps and normalized enum/const strings. They exercise
missing nested fields, empty arrays, unexpected fields, malformed answer files,
and aggregation. Staging tests inspect every visible filename and prove that
canary/private artifacts are absent. A corrupt-gold test proves the fake oracle
recomputes its answer from inputs rather than copying gold. Tool tests verify
path and symlink rejection. Trusted local execution tests verify timeouts and
output caps. The Docker invocation is tested through a captured command, without
pulling or executing an image. Fake-adapter tests verify that model context has
no private artifacts. Real model APIs are never called.
