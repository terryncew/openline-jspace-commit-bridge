from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from .schemas import CandidateCommit, WorkspaceSignal, CommitDecision
from .receipts import ReceiptChain
from .witnesses import Witness, WorkspaceRiskWitness, EvidenceHashWitness, UserIntentWitness, PolicyWitness

@dataclass
class CommitPolicy:
    quorum_required: int = 3
    quarantine_on_any_hard_fail: bool = True
    receipt_path: str = 'receipts/workspace_commit_receipts.jsonl'

@dataclass
class CommitBarrier:
    """Wide workspace, strict commit."""
    policy: CommitPolicy = field(default_factory=CommitPolicy)
    witnesses: List[Witness] = field(default_factory=lambda: [WorkspaceRiskWitness(), EvidenceHashWitness(), UserIntentWitness(), PolicyWitness()])
    def evaluate(self, workspace: WorkspaceSignal, commit: CandidateCommit) -> CommitDecision:
        votes = [w.vote(workspace, commit) for w in self.witnesses]
        votes_for = sum(1 for v in votes if v.passed)
        votes_against = len(votes) - votes_for
        hard_fail = any(not v.passed for v in votes)
        quorum_passed = votes_for >= self.policy.quorum_required
        if self.policy.quarantine_on_any_hard_fail and hard_fail:
            status, reason = 'quarantined', 'one or more witnesses failed'
        elif quorum_passed:
            status, reason = 'committed', 'quorum passed'
        else:
            status, reason = 'quarantined', 'quorum not met'
        receipt = ReceiptChain(self.policy.receipt_path).append({
            'claim': commit.claim,
            'action': commit.action,
            'result': status,
            'commit_type': commit.commit_type,
            'target': commit.target,
            'workspace': workspace.to_dict(),
            'candidate_commit': commit.to_dict(),
            'votes': [v.to_dict() for v in votes],
            'quorum_required': self.policy.quorum_required,
            'votes_for': votes_for,
            'votes_against': votes_against,
            'next_use_note': 'Use this receipt before replaying, committing, forwarding, or auditing the boundary crossing.'
        })
        return CommitDecision(status, self.policy.quorum_required, votes_for, votes_against, votes, receipt['receipt_hash'], reason, str(Path(self.policy.receipt_path)))
