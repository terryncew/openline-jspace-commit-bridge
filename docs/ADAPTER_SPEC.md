# Workspace Adapter Spec

A workspace adapter must return:

```python
WorkspaceSignal(source='adapter-name', terms=['injection', 'fake'], summary='Short readout.', confidence=0.0_to_1.0, layer='optional', raw_ref='optional')
```

Rules: mark provenance, mark confidence, treat workspace terms as evidence rather than truth, and prefer summaries/hashes/references over raw private traces.
