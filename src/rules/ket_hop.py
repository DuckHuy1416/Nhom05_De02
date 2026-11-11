"""C6 - Kết hợp xác suất CNN với hệ luật/mạng Bayes để ra kết luận cuối.

Phụ trách: TV3 | Thời hạn: T6 27/11 (theo Mẫu 01)
Trạng thái: chưa cài đặt.
"""
from __future__ import annotations

import argparse
from typing import Iterable, Mapping

from .bayes import truy_van
from .chung import (
    MA_BENH,
    SU_KIEN_BENH,
    TEN_BENH,
    KetQuaChanDoan,
    canh_bao_tu_bang_chung,
    dinh_dang_ket_qua,
    doc_kho_tri_thuc,
    gom_nguon,
    khuyen_nghi_cho,
    nguon_khuyen_nghi,
)
from .forward import suy_dien_tien

TRONG_SO_MAC_DINH = {"cnn": 0.5, "luat": 0.3, "bayes": 0.2}
NGUON_BAYES = ("S1", "S2", "S3", "S5")

#: Ví dụ mẫu cho báo cáo: ảnh lá nghi đạo ôn, ruộng mưa ẩm và bón nhiều đạm.
VI_DU_CNN = [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)]
VI_DU_BANG_CHUNG = ["tc_vet_thoi", "tt_am_do_cao", "tq_dam_cao", "gd_de_nhanh"]


def _chuan_hoa_cnn(cnn_top3: Iterable[tuple[str, float] | str]) -> dict[str, float]:
    """Chuẩn hóa đầu ra CNN thành phân phối trên 4 lớp dùng chung."""
    tho: dict[str, float] = {}
    for muc in cnn_top3:
        if isinstance(muc, str):
            ma, xac_suat = muc, 1.0
        else:
            if len(muc) != 2:
                raise ValueError(f"Mỗi lớp CNN phải là (mã bệnh, xác suất), nhận {muc!r}.")
            ma, xac_suat = muc
        if ma not in MA_BENH:
            raise ValueError(f"Mã lớp CNN không hợp lệ: {ma}")
        xac_suat = float(xac_suat)
        if not 0.0 <= xac_suat <= 1.0:
            raise ValueError(f"Xác suất CNN của {ma} phải trong [0, 1], nhận {xac_suat}.")
        tho[ma] = tho.get(ma, 0.0) + xac_suat

    if not tho or sum(tho.values()) <= 0:
        raise ValueError("CNN không trả về xác suất dương nào.")

    con_lai = 1.0 - sum(tho.values())
    if con_lai > 1e-9:
        thieu = [ma for ma in MA_BENH if ma not in tho]
        if thieu:
            # CNN chỉ trả top-3: phần xác suất còn lại thuộc lớp không có tên.
            tho[thieu[0]] = con_lai
    tong = sum(tho.values())
    return {ma: tho.get(ma, 0.0) / tong for ma in MA_BENH}


def _do_tin_cay_luat(ket_qua_tien: KetQuaChanDoan, ma_benh: str) -> float:
    return float(ket_qua_tien.bang_chung.get(SU_KIEN_BENH[ma_benh], 0.0))


def ket_hop(
    cnn_top3: Iterable[tuple[str, float] | str],
    bang_chung: Mapping[str, float] | Iterable[str] | None = None,
    trong_so: Mapping[str, float] | None = None,
    kho: dict | None = None,
) -> KetQuaChanDoan:
    """Kết hợp CNN + hệ luật + mạng Bayes, trả về kết luận cuối cùng."""
    kho = kho or doc_kho_tri_thuc()
    trong_so = dict(TRONG_SO_MAC_DINH | dict(trong_so or {}))
    if abs(sum(trong_so.values()) - 1.0) > 1e-6:
        raise ValueError(f"Tổng trọng số phải bằng 1, nhận {sum(trong_so.values()):.3f}.")
    for ten in ("cnn", "luat", "bayes"):
        if trong_so[ten] < 0:
            raise ValueError(f"Trọng số {ten} không được âm.")

    xac_suat_cnn = _chuan_hoa_cnn(cnn_top3)
    ket_qua_tien = suy_dien_tien(bang_chung, kho)
    ket_qua_bayes = truy_van(bang_chung)
    xac_suat_bayes = ket_qua_bayes["xac_suat"]

    diem: dict[str, float] = {}
    for ma in MA_BENH:
        diem[ma] = round(
            trong_so["cnn"] * xac_suat_cnn[ma]
            + trong_so["luat"] * _do_tin_cay_luat(ket_qua_tien, ma)
            + trong_so["bayes"] * float(xac_suat_bayes.get(ma, 0.0)),
            4,
        )
    xep_hang = sorted(diem.items(), key=lambda cap: cap[1], reverse=True)
    benh, do_tin_cay = xep_hang[0]

    canh_bao = list(canh_bao_tu_bang_chung(kho, ket_qua_tien.bang_chung))
    if benh != "la_khoe" and xep_hang[1][1] > 0 and do_tin_cay - xep_hang[1][1] < 0.08:
        canh_bao.append(
            f"Hai kết luận sát nhau ({TEN_BENH[benh]} {do_tin_cay:.0%} và "
            f"{TEN_BENH[xep_hang[1][0]]} {xep_hang[1][1]:.0%}): nên hỏi thêm triệu chứng "
            "hoặc nhờ cán bộ khuyến nông kiểm tra."
        )

    ma_nguon = [n["ma"] for n in ket_qua_tien.nguon]
    for ma in list(NGUON_BAYES) + nguon_khuyen_nghi(kho, benh):
        if ma not in ma_nguon:
            ma_nguon.append(ma)

    giai_thich = [
        f"Điểm = {trong_so['cnn']:.2f}×CNN + {trong_so['luat']:.2f}×hệ luật "
        f"+ {trong_so['bayes']:.2f}×Bayes.",
        "Đóng góp từng nguồn:",
        f"  {'Lớp':<22}{'CNN':>8}{'luật':>8}{'Bayes':>8}{'điểm':>8}",
    ]
    for ma in MA_BENH:
        giai_thich.append(
            f"  {TEN_BENH[ma]:<22}{xac_suat_cnn[ma]:>7.0%}"
            f"{_do_tin_cay_luat(ket_qua_tien, ma):>8.0%}"
            f"{float(xac_suat_bayes.get(ma, 0.0)):>8.0%}{diem[ma]:>8.0%}"
        )
    giai_thich.extend(
        [
            f"Mạng Bayes: {ket_qua_bayes['phuong_phap']}; bằng chứng nút "
            f"{ket_qua_bayes['bang_chung'] or '—'}.",
            "Hệ luật kích hoạt: "
            + (", ".join(f"{luat.ma} ({luat.do_tin_cay:.0%})" for luat in ket_qua_tien.luat_da_dung) or "không"),
            "Hệ luật chỉ dùng để xác nhận triệu chứng/bối cảnh, không tự đặt tên thuốc "
            "hay liều lượng.",
        ]
    )
    for ghi_chu in ket_qua_bayes["ghi_chu"]:
        giai_thich.append(f"Ghi chú Bayes: {ghi_chu}")

    return KetQuaChanDoan(
        phuong_phap="Kết hợp CNN + hệ luật + mạng Bayes (trung bình có trọng số)",
        benh=benh,
        do_tin_cay=do_tin_cay,
        xep_hang=xep_hang,
        luat_da_dung=ket_qua_tien.luat_da_dung,
        bang_chung=ket_qua_tien.bang_chung,
        nguon=gom_nguon(kho, ma_nguon),
        khuyen_nghi=khuyen_nghi_cho(kho, benh),
        canh_bao=canh_bao,
        giai_thich="\n".join(giai_thich),
    )


def ham_demo() -> None:
    """Ví dụ đầu–cuối cho ``demo.py`` và báo cáo."""
    print("Ảnh lá do CNN phân tích (top-3):")
    for ma, p in VI_DU_CNN:
        print(f"  {TEN_BENH[ma]:<22} {p:.0%}")
    print(f"Thông tin thêm từ người dùng: {', '.join(VI_DU_BANG_CHUNG)}")
    print()
    ket_qua = ket_hop(VI_DU_CNN, VI_DU_BANG_CHUNG)
    print(dinh_dang_ket_qua(ket_qua))


#: Bí danh để ``demo.py`` gọi được hàm demo() của Chức năng 2.
demo = ham_demo


def _doc_top3(chuoi: str) -> list[tuple[str, float]]:
    ket_qua: list[tuple[str, float]] = []
    for phan in chuoi.split(","):
        phan = phan.strip()
        if not phan:
            continue
        if ":" not in phan:
            raise ValueError(f"Phần tử --top3 phải có dạng mã:xác_suất, nhận {phan!r}.")
        ma, xac_suat = phan.split(":", 1)
        ket_qua.append((ma.strip(), float(xac_suat)))
    return ket_qua


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kết hợp CNN, hệ luật và mạng Bayes.")
    parser.add_argument(
        "--top3",
        default=",".join(f"{ma}:{p}" for ma, p in VI_DU_CNN),
        help="Đầu ra CNN dạng 'dao_on:0.55,dom_nau:0.40,bac_la:0.03'.",
    )
    parser.add_argument(
        "--bang-chung",
        nargs="*",
        default=None,
        help="Mã sự kiện đã biết (ví dụ tc_vet_thoi tt_am_do_cao tq_dam_cao).",
    )
    args = parser.parse_args(argv)

    cnn_top3 = _doc_top3(args.top3)
    bang_chung = args.bang_chung if args.bang_chung is not None else VI_DU_BANG_CHUNG
    print("CNN top-3:", ", ".join(f"{TEN_BENH.get(ma, ma)} {p:.0%}" for ma, p in cnn_top3))
    ket_qua = ket_hop(cnn_top3, bang_chung)
    print(dinh_dang_ket_qua(ket_qua))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())