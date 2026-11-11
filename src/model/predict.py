"""Dự đoán GIẢ phục vụ tích hợp, không đọc ảnh và không nạp TensorFlow."""
from pathlib import Path

from src.contracts import Top3

IS_STUB = True


def predict_top3(duong_dan_anh: str | Path) -> Top3:
    """Trả số cố định GIẢ, không có giá trị chẩn đoán hay đánh giá mô hình.

    TV4 thay bằng dự đoán thật và đặt IS_STUB = False khi tích hợp mô hình.
    """
    return [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)]
