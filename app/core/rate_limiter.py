from collections import defaultdict
from time import time
from typing import Dict, List

_log: Dict[str, List[float]] = defaultdict(list)

def check(key: str, max_calls: int, window: int = 60) -> bool:
    """Return True if allowed, False if rate limit exceeded."""
    if max_calls == 0:
        return True
    now = time()
    cutoff = now - window
    _log[key] = [t for t in _log[key] if t > cutoff]
    if len(_log[key]) >= max_calls:
        return False
    _log[key].append(now)
    return True
