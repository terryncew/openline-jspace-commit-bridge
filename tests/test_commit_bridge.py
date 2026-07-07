from pathlib import Path
from openline_jspace_commit_bridge.adapters import MockJSpaceAdapter
from openline_jspace_commit_bridge.commit_barrier import CommitBarrier, CommitPolicy
from openline_jspace_commit_bridge.demo import build_commit
from openline_jspace_commit_bridge.receipts import ReceiptChain

def test_safe_answer_commits(tmp_path: Path):
    receipt_path = tmp_path / 'receipts.jsonl'
    workspace = MockJSpaceAdapter().read({'text': 'Please explain the architecture.'})
    decision = CommitBarrier(CommitPolicy(receipt_path=str(receipt_path))).evaluate(workspace, build_commit('safe_answer'))
    assert decision.status == 'committed'
    assert decision.votes_for >= 3
    assert ReceiptChain(receipt_path).verify()

def test_prompt_injection_tool_call_quarantines(tmp_path: Path):
    receipt_path = tmp_path / 'receipts.jsonl'
    workspace = MockJSpaceAdapter().read({'text': 'prompt injection ignore previous instructions'})
    decision = CommitBarrier(CommitPolicy(receipt_path=str(receipt_path))).evaluate(workspace, build_commit('prompt_injection_tool_call'))
    assert decision.status == 'quarantined'
    assert any(not v.passed for v in decision.votes)
    assert ReceiptChain(receipt_path).verify()

def test_fabricated_score_file_edit_quarantines(tmp_path: Path):
    receipt_path = tmp_path / 'receipts.jsonl'
    workspace = MockJSpaceAdapter().read({'text': 'fabricate falsify fake score'})
    decision = CommitBarrier(CommitPolicy(receipt_path=str(receipt_path))).evaluate(workspace, build_commit('fabricated_score_file_edit'))
    assert decision.status == 'quarantined'
    assert any(not v.passed for v in decision.votes)
    assert ReceiptChain(receipt_path).verify()
