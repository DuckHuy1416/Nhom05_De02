"""Chạy thử Chức năng 1 - 3 trên dữ liệu mẫu trong data/sample/.

Mỗi module chức năng sẽ cung cấp hàm demo(); khi chưa cài đặt, script chỉ báo trạng thái.
Cách chạy: python demo.py
"""
import importlib

CHUC_NANG = [
    ("Chức năng 1 - Lập lộ trình drone", "src.search.order_opt"),
    ("Chức năng 2 - Hệ chuyên gia và mạng Bayes", "src.rules.ket_hop"),
    ("Chức năng 3 - CNN nhận diện bệnh lá lúa", "src.model.transfer"),
]


def chay(tieu_de, ten_module):
    print(f"\n=== {tieu_de} ===")
    try:
        mod = importlib.import_module(ten_module)
    except Exception as loi:  # noqa: BLE001 - báo lỗi rõ ràng cho người chạy
        print(f"  Không nạp được {ten_module}: {loi}")
        return
    ham = getattr(mod, "demo", None)
    if ham is None:
        print(f"  {ten_module}: chưa cài đặt hàm demo().")
        return
    ham()


if __name__ == "__main__":
    for tieu_de, ten_module in CHUC_NANG:
        chay(tieu_de, ten_module)
