"""Chạy khung CN1–CN3 trên bản đồ mẫu; không cần thư viện học máy."""
import json
import sys
from pathlib import Path

from src.model.predict import IS_STUB, predict_top3
from src.rules.diagnose import diagnose
from src.search.run import plan_route


def main() -> None:
    """Đọc dữ liệu mẫu và chỉ bắt trạng thái chưa cài đặt của từng chức năng."""
    duong_dan = Path(__file__).resolve().parent / "data/sample/maps/map_4x4.json"
    ban_do = json.loads(duong_dan.read_text(encoding="utf-8"))
    print(f"Bản đồ minh họa: {ban_do['rows']} × {ban_do['cols']}")
    print(f"CN3 — dự đoán GIẢ (IS_STUB={IS_STUB}), không phải kết quả CNN:")
    top3 = predict_top3("anh_gia_khong_doc.jpg")
    print(top3)
    try:
        print("CN1:", plan_route(ban_do, ban_do["k"], ban_do["p"], "hill"))
    except NotImplementedError:
        print("CN1: chưa cài đặt")
    try:
        print("CN2:", diagnose(top3, lambda cau_hoi: None))
    except NotImplementedError:
        print("CN2: chưa cài đặt")
    print("Mạng Bayes và ứng dụng tích hợp: chưa cài đặt")


if __name__ == "__main__":
    # Bảo đảm in tiếng Việt khi Windows chuyển đầu ra qua pipe dùng mã hóa cũ.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
