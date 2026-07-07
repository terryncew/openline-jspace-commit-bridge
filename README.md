# OpenLine J-space Commit Bridge

A prototype bridge between **workspace interpretability** and **OpenLine commit governance**.

The design rule:

> Let the model think widely. Let actions commit only through verified receipts.

## What this is

Anthropic's Global Workspace research describes an emergent internal workspace in Claude, called **J-space**, where concepts can silently become reportable, controllable, and usable for flexible reasoning.

This repo does not claim Anthropic built or endorsed OpenLine.

This repo asks a separate engineering question:

> If a model has a workspace-like interior, how should workspace contents be allowed to affect the outside world?

The answer tested here:

```text
J-space-like readout
  ↓
candidate action / memory write / file edit / handoff / answer
  ↓
OpenLine verification quorum
  ↓
commit or quarantine
  ↓
portable receipt
```

## Core distinction

```text
workspace = where thoughts become globally usable
commit barrier = where usable thoughts become accountable actions
receipt = durable record of the crossing
```

A workspace helps the model think.

A receipt helps the world hold the crossing accountable.

## What runs today

This prototype runs without access to proprietary model internals.

It includes:

- `MockJSpaceAdapter`: deterministic J-space-like signals for testing.
- `ExternalJSONWorkspaceAdapter`: accepts exported workspace readouts from any future tool.
- `CommitBarrier`: witness quorum around state-changing actions.
- `ReceiptChain`: hash-chained local OpenLine receipts.
- Unit tests for safe commit and quarantine behavior.

## Install / run

```bash
python -m pytest -q
python -m openline_jspace_commit_bridge.demo --scenario safe_answer
python -m openline_jspace_commit_bridge.demo --scenario prompt_injection_tool_call
python -m openline_jspace_commit_bridge.demo --scenario fabricated_score_file_edit
```

Use an external workspace readout:

```bash
python -m openline_jspace_commit_bridge.demo \
  --scenario prompt_injection_tool_call \
  --workspace-json examples/jspace_prompt_injection_readout.json
```

## Demo behavior

Safe answer commits. Prompt-injection tool calls quarantine. Fabricated-score file edits quarantine.

## Claim boundary

This is a prototype. It does not provide real J-space access. It does not prove consciousness or alignment. Workspace evidence is evidence, not truth. A signed lie is still a lie.

## Canon

> Anthropic found a workspace inside the model. OpenLine governs what gets to leave it.

> A workspace helps the model think. A receipt helps the world hold the crossing accountable.

> High-permeability workspace. Low-permeability commit barrier.

> Open edges. Strict commits. Portable receipts.
