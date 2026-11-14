"""Suy diễn tiến từ sự kiện đã biết qua các luật IF–THEN."""
from src.contracts import Luat


def forward(facts: set[str], rules: list[Luat]) -> set[str]:
    """Tự suy diễn tiến đến điểm cố định; giữ nguyên facts đầu vào."""
    known = set(facts)
    while True:
        inferred = {
            rule["thì"]
            for rule in rules
            if all(condition in known for condition in rule["nếu"])
        }
        new_facts = inferred - known
        if not new_facts:
            return known
        known.update(new_facts)
