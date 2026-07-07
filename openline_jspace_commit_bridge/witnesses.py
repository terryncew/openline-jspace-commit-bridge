from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Set
from .schemas import CandidateCommit, WorkspaceSignal, WitnessVote

STATE_CHANGING = {'tool_call','memory_write','file_edit','external_message','handoff','policy_decision'}

class Witness(ABC):
    name: str
    @abstractmethod
    def vote(self, workspace: WorkspaceSignal, commit: CandidateCommit) -> WitnessVote:
        raise NotImplementedError

class WorkspaceRiskWitness(Witness):
    name = 'workspace_risk_witness'
    def __init__(self, block_terms: Set[str] | None = None):
        self.block_terms = block_terms or {'injection','manipulation','fraud','sabotage','blackmail','exploit','bypass'}
    def vote(self, workspace: WorkspaceSignal, commit: CandidateCommit) -> WitnessVote:
        risky = [t for t in workspace.terms if t.lower() in self.block_terms]
        if risky and commit.commit_type in STATE_CHANGING:
            return WitnessVote(self.name, False, f'workspace contains high-risk terms for state-changing commit: {risky}', 0.0, {'risk_terms': risky, 'workspace_terms': workspace.terms})
        return WitnessVote(self.name, True, 'workspace risk terms do not block this commit', 1.0, {'workspace_terms': workspace.terms})

class EvidenceHashWitness(Witness):
    name = 'evidence_hash_witness'
    def vote(self, workspace: WorkspaceSignal, commit: CandidateCommit) -> WitnessVote:
        evidence_hash = commit.evidence.get('evidence_hash')
        if commit.commit_type in STATE_CHANGING and not evidence_hash:
            return WitnessVote(self.name, False, 'state-changing commit lacks evidence_hash', 0.0, {'evidence': commit.evidence})
        return WitnessVote(self.name, True, 'evidence hash present or commit is non-state-changing', 1.0, {'evidence_hash': evidence_hash})

class UserIntentWitness(Witness):
    name = 'user_intent_witness'
    def vote(self, workspace: WorkspaceSignal, commit: CandidateCommit) -> WitnessVote:
        allowed = commit.evidence.get('user_intent_confirmed', False)
        if commit.commit_type in {'tool_call','memory_write','file_edit','external_message'} and not allowed:
            return WitnessVote(self.name, False, 'user intent is not confirmed for external/state-changing action', 0.0, {'user_intent_confirmed': allowed})
        return WitnessVote(self.name, True, 'user intent confirmed or not required for this commit type', 1.0, {'user_intent_confirmed': allowed})

class PolicyWitness(Witness):
    name = 'policy_witness'
    def vote(self, workspace: WorkspaceSignal, commit: CandidateCommit) -> WitnessVote:
        if commit.evidence.get('policy_blocked', False):
            return WitnessVote(self.name, False, 'commit is policy-blocked', 0.0, {'policy_blocked': True})
        return WitnessVote(self.name, True, 'no policy block detected', 1.0, {'policy_blocked': False})
