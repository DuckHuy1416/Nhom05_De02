"""Suy diễn lùi, hỏi người dùng về sự kiện còn thiếu."""
from src.contracts import HoiNguoiDung, Luat


def backward(goal: str, facts: set[str], rules: list[Luat], hoi_nguoi_dung: HoiNguoiDung) -> bool:
    """Chứng minh đích bằng facts, luật đệ quy hoặc câu trả lời người dùng.

    ``None`` được ghi nhận là chưa biết và không được xem như ``False`` trong
    tập facts. Một mục tiêu chỉ được hỏi tối đa một lần trong cùng lần suy diễn.
    """
    answers: dict[str, bool | None] = {}
    visiting: set[str] = set()

    def prove(target: str) -> bool:
        if target in facts:
            return True
        if target in visiting:
            return False
        visiting.add(target)
        try:
            for rule in rules:
                if rule["thì"] == target and all(prove(item) for item in rule["nếu"]):
                    return True
            if target not in answers:
                answers[target] = hoi_nguoi_dung(target)
            return answers[target] is True
        finally:
            visiting.remove(target)

    return prove(goal)
