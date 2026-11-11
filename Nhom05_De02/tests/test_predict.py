"""Hợp đồng dự đoán, áp dụng cả bản giả và bản thật trong tương lai."""
import math

from src.model.predict import predict_top3


def test_predict_top3_contract():
    top3 = predict_top3("duong_dan_thu_nghiem.jpg")
    assert isinstance(top3, list) and len(top3) == 3
    assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in top3)
    labels, scores = zip(*top3, strict=True)
    assert len(set(labels)) == 3
    assert set(labels) <= {"dao_on", "bac_la", "dom_nau", "la_khoe"}
    assert all(isinstance(p, (int, float)) and math.isfinite(p) and 0 <= p <= 1
               for p in scores)
    assert list(scores) == sorted(scores, reverse=True)
    assert 0 < sum(scores) <= 1 + 1e-9
