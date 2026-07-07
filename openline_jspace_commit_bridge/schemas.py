from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional
import time

CommitType = Literal['tool_call','memory_write','file_edit','external_message','handoff','final_answer','refusal','policy_decision']

@dataclass(frozen=True)
class WorkspaceSignal:
    """A high-level readout from a J-space-like workspace. Evidence, not truth."""
    source: str
    terms: List[str]
    summary: str = ''
    confidence: float = 0.5
    layer: Optional[str] = None
    raw_ref: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    def risk_terms(self) -> List[str]:
        high_risk = {'injection','fake','fictional','manipulation','fraud','secretly','deliberately','sabotage','deception','blackmail','leverage','threat','survival','exploit','bypass'}
        return [t for t in self.terms if t.lower() in high_risk]
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class CandidateCommit:
    """A proposed state-changing or boundary-crossing action."""
    commit_type: CommitType
    claim: str
    action: str
    target: str
    payload: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    proposed_by: str = 'agent'
    timestamp: float = field(default_factory=time.time)
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class WitnessVote:
    witness: str
    passed: bool
    reason: str
    score: float = 1.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class CommitDecision:
    status: Literal['committed','quarantined']
    quorum_required: int
    votes_for: int
    votes_against: int
    votes: List[WitnessVote]
    receipt_hash: str
    reason: str
    receipt_path: Optional[str] = None
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['votes'] = [v.to_dict() for v in self.votes]
        return d
