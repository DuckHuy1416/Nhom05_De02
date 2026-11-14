"""
C6 – Kết hợp xác suất CNN + mạng Bayes cho 4 lớp bệnh lá lúa.

Đầu vào CNN: top-3 [(ma_benh, probability), ...] với đúng 3 lớp khác nhau.
Lớp thứ tư được gán phần xác suất còn lại của softmax.
Đầu vào Bayes: bằng chứng theo mã sự kiện của hệ thống, được xử lý bởi
src.rules.bayes.truy_van().

Phương pháp: trung bình có trọng số giữa phân phối CNN và phân phối Bayes.
Đây là phương pháp kết hợp heuristic phục vụ tích hợp đồ án, không phải
một phép suy luận Bayes đầy đủ vì hai nguồn thông tin có thể phụ thuộc nhau.

Chạy:
    python -m src.rules.ket_hop
    python -m src.rules.ket_hop --top3 dao_on:0.55,dom_nau:0.40,bac_la:0.03
"""
from __future__ import annotations

import argparse
from typing import Iterable, Mapping

from .bayes import truy_van

MA_BENH = ("dao_on", "bac_la", "dom_nau", "la_khoe")
TEN_BENH = {
    "dao_on": "Đạo ôn",
    "bac_la": "Bạc lá",
    "dom_nau": "Đốm nâu",
    "la_khoe": "Lá khỏe",
}
TRONG_SO_MAC_DINH = {"cnn": 0.6, "bayes": 0.4}
VI_DU_CNN = [
    ("dao_on", 0.55),
    ("dom_nau", 0.40),
    ("bac_la", 0.03),
]
VI_DU_BANG_CHUNG = ["tc_vet_thoi", "tt_am_do_cao", "tq_dam_cao"]


def chuan_hoa_cnn_top3(
    cnn_top3: Iterable[tuple[str, float]],
) -> dict[str, float]:
    """Chuẩn hóa top-3 CNN thành phân phối trên đúng 4 lớp."""
    items = list(cnn_top3)
    if len(items) != 3:
        raise ValueError("CNN phải cung cấp đúng 3 lớp dự đoán (top-3).")

    result: dict[str, float] = {}
    for item in items:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("Mỗi phần tử CNN phải có dạng (ma_benh, xac_suat).")
        label, probability = item
        if label not in MA_BENH:
            raise ValueError(f"Mã lớp CNN không hợp lệ: {label!r}.")
        if label in result:
            raise ValueError(f"Mã lớp CNN bị trùng: {label}.")
        probability = float(probability)
        if not 0.0 <= probability <= 1.0:
            raise ValueError(f"Xác suất CNN phải thuộc [0, 1]: {probability}.")
        result[label] = probability

    missing = set(MA_BENH) - set(result)
    if len(missing) != 1:
        raise ValueError("Top-3 phải gồm 3/4 lớp bệnh đã quy ước.")
    total = sum(result.values())
    if total <= 0:
        raise ValueError("Tổng xác suất CNN phải lớn hơn 0.")

    omitted_label = next(iter(missing))
    if total <= 1.0 + 1e-6:
        result[omitted_label] = max(0.0, 1.0 - total)
    else:
        # Một số CNN có thể trả xác suất làm tròn khiến tổng hơi vượt 1.
        result = {label: value / total for label, value in result.items()}
        result[omitted_label] = 0.0

    normalizer = sum(result.values())
    return {label: value / normalizer for label, value in result.items()}


def chuan_hoa_bayes(
    bang_chung: Mapping[str, float] | Iterable[str] | None = None,
    su_dung_pgmpy: bool = True,
) -> tuple[dict[str, float], dict]:
    """Lấy và chuẩn hóa phân phối 4 lớp từ mạng Bayes C5."""
    result = truy_van(bang_chung, su_dung_pgmpy=su_dung_pgmpy)
    raw = {label: float(result["xac_suat"].get(label, 0.0)) for label in MA_BENH}
    if any(value < 0 for value in raw.values()):
        raise ValueError("Xác suất Bayes không được âm.")
    total = sum(raw.values())
    if total <= 0:
        raise ValueError("Mạng Bayes trả về tổng xác suất bằng 0.")
    return ({label: value / total for label, value in raw.items()}, result)


def ket_hop_cnn_bayes(
    cnn_top3: Iterable[tuple[str, float]],
    bang_chung: Mapping[str, float] | Iterable[str] | None = None,
    trong_so: Mapping[str, float] | None = None,
    su_dung_pgmpy: bool = True,
) -> dict:
    """
    Kết hợp CNN và Bayes theo trung bình có trọng số.

    Trong số mặc định: CNN=0.6, Bayes=0.4.
    Có thể truyền trọng số khác nhưng tổng phải bằng 1.
    """
    cnn = chuan_hoa_cnn_top3(cnn_top3)
    weights = dict(TRONG_SO_MAC_DINH)
    if trong_so:
        weights.update({key: float(value) for key, value in trong_so.items()})
    if set(weights) != {"cnn", "bayes"}:
        raise ValueError("Chỉ chấp nhận hai trọng số 'cnn' và 'bayes'.")
    if any(value < 0 for value in weights.values()):
        raise ValueError("Trọng số không được âm.")
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError("Tổng trọng số CNN và Bayes phải bằng 1.")

    bayes, bayes_detail = chuan_hoa_bayes(bang_chung, su_dung_pgmpy)
    combined = {
        label: weights["cnn"] * cnn[label] + weights["bayes"] * bayes[label]
        for label in MA_BENH
    }
    # Khử sai số số học và bảo đảm tổng bằng 1.
    total = sum(combined.values())
    combined = {label: value / total for label, value in combined.items()}
    ranking = sorted(combined.items(), key=lambda item: item[1], reverse=True)

    return {
        "xac_suat_cnn": cnn,
        "xac_suat_bayes": bayes,
        "xac_suat_ket_hop": combined,
        "top3_ket_qua": ranking[:3],
        "ket_luan": ranking[0][0],
        "trong_so": weights,
        "phuong_phap_bayes": bayes_detail["phuong_phap"],
        "bang_chung_bayes": bayes_detail["bang_chung"],
        "ghi_chu": bayes_detail["ghi_chu"],
        "phuong_phap": "Trung bình có trọng số CNN + Bayes",
        "canh_bao": (
            "Kết quả là hỗ trợ tham khảo; CPD hiện là ước lượng định tính, "
            "cần hiệu chỉnh bằng dữ liệu đồng ruộng."
        ),
    }


def _parse_top3(value: str) -> list[tuple[str, float]]:
    parsed = []
    for part in value.split(","):
        label, probability = part.strip().split(":", 1)
        parsed.append((label.strip(), float(probability)))
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kết hợp CNN + mạng Bayes.")
    parser.add_argument(
        "--top3",
        default=",".join(f"{label}:{prob}" for label, prob in VI_DU_CNN),
        help="Top-3 dạng dao_on:0.55,dom_nau:0.40,bac_la:0.03",
    )
    parser.add_argument(
        "--bang-chung",
        nargs="*",
        default=VI_DU_BANG_CHUNG,
        help="Mã sự kiện, ví dụ tc_vet_thoi tt_am_do_cao tq_dam_cao",
    )
    parser.add_argument("--khong-pgmpy", action="store_true")
    args = parser.parse_args(argv)

    result = ket_hop_cnn_bayes(
        _parse_top3(args.top3),
        args.bang_chung,
        su_dung_pgmpy=not args.khong_pgmpy,
    )
    print("=== KẾT QUẢ KẾT HỢP CNN + BAYES ===")
    print("CNN:", result["xac_suat_cnn"])
    print("Bayes:", result["xac_suat_bayes"])
    print("\nXác suất kết hợp:")
    for label, probability in result["top3_ket_qua"]:
        print(f"  {TEN_BENH[label]:<12}: {probability:.2%}")
    print("Kết luận:", TEN_BENH[result["ket_luan"]])
    print("Phương pháp Bayes:", result["phuong_phap_bayes"])
    print("Bằng chứng:", result["bang_chung_bayes"])
    for note in result["ghi_chu"]:
        print("Ghi chú:", note)
    print("Cảnh báo:", result["canh_bao"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
