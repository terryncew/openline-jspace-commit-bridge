from __future__ import annotations
from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Any, Dict, List
from .schemas import WorkspaceSignal

class WorkspaceAdapter(ABC):
    """Interface for a J-space-like workspace readout."""
    @abstractmethod
    def read(self, context: Dict[str, Any]) -> WorkspaceSignal:
        raise NotImplementedError

class MockJSpaceAdapter(WorkspaceAdapter):
    """Deterministic test adapter. This is not real Anthropic J-space access."""
    def read(self, context: Dict[str, Any]) -> WorkspaceSignal:
        text = ' '.join(str(v) for v in context.values()).lower()
        terms: List[str] = []
        summary = 'No high-risk workspace term detected.'
        if 'prompt injection' in text or 'ignore previous' in text:
            terms += ['injection', 'fake']
            summary = 'Workspace readout flags possible prompt injection.'
        if 'fabricate' in text or 'falsify' in text or 'fake score' in text:
            terms += ['manipulation', 'fake', 'realistic']
            summary = 'Workspace readout flags possible fabrication/manipulation.'
        if 'sabotage' in text or 'secret' in text:
            terms += ['secretly', 'deliberately', 'fraud']
            summary = 'Workspace readout flags possible hidden-goal/sabotage pattern.'
        if 'staged evaluation' in text or 'test scenario' in text:
            terms += ['fake', 'fictional', 'scenario']
            summary = 'Workspace readout flags evaluation-awareness terms.'
        if not terms:
            terms = ['task', 'plan', 'answer']
        return WorkspaceSignal(source='mock_jspace_adapter', terms=terms, summary=summary, confidence=0.85 if terms != ['task','plan','answer'] else 0.55)

class ExternalJSONWorkspaceAdapter(WorkspaceAdapter):
    """Reads an externally exported workspace signal from JSON."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
    def read(self, context: Dict[str, Any]) -> WorkspaceSignal:
        data = json.loads(self.path.read_text(encoding='utf-8'))
        return WorkspaceSignal(source=data.get('source','external_json_workspace_adapter'), terms=list(data.get('terms', [])), summary=data.get('summary',''), confidence=float(data.get('confidence',0.5)), layer=data.get('layer'), raw_ref=data.get('raw_ref'))
