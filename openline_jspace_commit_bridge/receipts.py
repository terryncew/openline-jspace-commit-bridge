from __future__ import annotations
import hashlib, json, time
from pathlib import Path
from typing import Any, Dict, Optional

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def sha256_json(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

class ReceiptChain:
    """Small local hash-chained receipt writer. Integrity/order, not truth."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.parent_hash: Optional[str] = self._last_hash()
    def _last_hash(self) -> Optional[str]:
        if not self.path.exists():
            return None
        last = None
        for line in self.path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                last = json.loads(line)
        return last.get('receipt_hash') if last else None
    def append(self, receipt: Dict[str, Any]) -> Dict[str, Any]:
        body = dict(receipt)
        body.setdefault('schema', 'openline.workspace_commit_receipt.v0')
        body.setdefault('timestamp', time.time())
        body['parent_hash'] = self.parent_hash
        body['receipt_hash'] = sha256_json({k: v for k, v in body.items() if k != 'receipt_hash'})
        with self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(body, sort_keys=True, ensure_ascii=False) + '\n')
        self.parent_hash = body['receipt_hash']
        return body
    def verify(self) -> bool:
        prev = None
        if not self.path.exists():
            return True
        for line in self.path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            receipt = json.loads(line)
            if receipt.get('parent_hash') != prev:
                return False
            expected = sha256_json({k: v for k, v in receipt.items() if k != 'receipt_hash'})
            if receipt.get('receipt_hash') != expected:
                return False
            prev = receipt['receipt_hash']
        return True
