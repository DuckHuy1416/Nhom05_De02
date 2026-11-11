"""C4 - Suy diễn lùi: kiểm chứng giả thuyết (ví dụ lúa bị đạo ôn?) bằng cách hỏi thêm.

Phụ trách: TV2 | Thời hạn: T3 17/11 (theo Mẫu 01)
Trạng thái: chưa cài đặt.
"""
from src.contracts import HoiNguoiDung, Luat


def backward(goal: str, facts: set[str], rules: list[Luat], hoi_nguoi_dung: HoiNguoiDung) -> bool:
    """Tự suy diễn lùi; trả True khi chứng minh được đích."""
    raise NotImplementedError("chưa cài đặt")
