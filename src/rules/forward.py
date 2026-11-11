"""C3 – Suy diễn tiến: từ triệu chứng, thời tiết, giai đoạn ra kết luận.

Thuật toán tự cài đặt (không dùng thư viện suy diễn có sẵn):

1. Nạp bằng chứng người dùng (triệu chứng, thời tiết, giai đoạn, tập quán canh tác)
   vào bộ nhớ làm việc kèm độ tin cậy.
2. Lặp qua danh sách luật; luật nào có **đủ** tiền đề trong bộ nhớ và chưa kích hoạt
   thì kích hoạt: thêm kết luận với độ tin cậy
   ``do_tin_cay_luat × min(độ tin cậy các tiền đề)``.
3. Lặp đến khi không còn luật mới kích hoạt (điểm bất động) hoặc hết số vòng giới hạn.
   Mỗi luật chỉ kích hoạt một lần, nên giải thuật luôn dừng.

Độ tin cậy của một sự kiện suy ra bằng **giá trị lớn nhất** trong các luật hỗ trợ nó;
cách này đơn giản, giải thích được và tránh việc một kết luận bị "thổi phồng" khi
nhiều luật yếu cùng suy ra.

Chạy thử:
    python -m src.rules.forward
    python -m src.rules.forward --su-kien tc_vet_thoi tc_qua_quang_vang tt_am_do_cao
"""
from __future__ import annotations

import argparse
from typing import Iterable, Mapping

from .chung import (
    KetQuaChanDoan,
    LuatDaDung,
    canh_bao_tu_bang_chung,
    chon_ket_luan,
    chuan_hoa_bang_chung,
    dinh_dang_ket_qua,
    doc_kho_tri_thuc,
    gom_nguon,
    khuyen_nghi_cho,
    nguon_cua_luat,
    nguon_khuyen_nghi,
)

VI_DU = ["tc_vet_thoi", "tc_qua_quang_vang", "tt_am_do_cao", "gd_de_nhanh", "tq_dam_cao"]


def suy_dien_tien(
    bang_chung: Mapping[str, float] | Iterable[str] | None = None,
    kho: dict | None = None,
    toi_da_vong: int = 20,
) -> KetQuaChanDoan:
    """Chạy suy diễn tiến trên bằng chứng đầu vào, trả về kết quả chẩn đoán."""
    kho = kho or doc_kho_tri_thuc()
    bo_nho = chuan_hoa_bang_chung(bang_chung, kho)

    so_su_kien_ban_dau = len(bo_nho)
    da_kich_hoat: set[str] = set()
    luat_da_dung: list[LuatDaDung] = []
    vong = 0
    con_luat_moi = True
    while con_luat_moi and vong < toi_da_vong:
        con_luat_moi = False
        vong += 1
        for luat in kho["luat"]:
            if luat["ma"] in da_kich_hoat:
                continue
            if not all(tien_de in bo_nho for tien_de in luat["neu"]):
                continue

            do_tin_cay = round(
                float(luat["do_tin_cay"]) * min(bo_nho[tien_de] for tien_de in luat["neu"]),
                4,
            )
            da_kich_hoat.add(luat["ma"])
            con_luat_moi = True
            for ket_luan in luat["thi"]:
                bo_nho[ket_luan] = max(bo_nho.get(ket_luan, 0.0), do_tin_cay)
            luat_da_dung.append(
                LuatDaDung(
                    ma=luat["ma"],
                    ten=luat["ten"],
                    do_tin_cay=do_tin_cay,
                    tien_de=list(luat["neu"]),
                    ket_luan=list(luat["thi"]),
                    nguon=list(luat["nguon"]),
                )
            )

    benh, do_tin_cay, xep_hang = chon_ket_luan(bo_nho)
    ma_nguon = nguon_cua_luat(kho, luat_da_dung)
    ma_nguon.extend(ma for ma in nguon_khuyen_nghi(kho, benh) if ma not in ma_nguon)

    giai_thich = [
        f"Đã có {so_su_kien_ban_dau} sự kiện ban đầu, "
        f"kích hoạt {len(luat_da_dung)} luật qua {vong} vòng lặp.",
        "Chuỗi suy luận:",
    ]
    for luat in luat_da_dung:
        giai_thich.append(
            f"  {luat.ma}: "
            + " + ".join(luat.tien_de)
            + "  ⇒  "
            + ", ".join(f"{kl} ({luat.do_tin_cay:.0%})" for kl in luat.ket_luan)
        )
    if benh:
        giai_thich.append(
            f"Kết luận chọn {benh} vì có độ tin cậy cao nhất ({do_tin_cay:.0%}) "
            "trong các bệnh suy ra được."
        )
    else:
        giai_thich.append("Không có luật nào dẫn tới kết luận bệnh: cần thêm triệu chứng.")

    return KetQuaChanDoan(
        phuong_phap="Suy diễn tiến (forward chaining) tự cài đặt",
        benh=benh,
        do_tin_cay=do_tin_cay,
        xep_hang=xep_hang,
        luat_da_dung=luat_da_dung,
        bang_chung=bo_nho,
        nguon=gom_nguon(kho, ma_nguon),
        khuyen_nghi=khuyen_nghi_cho(kho, benh),
        canh_bao=canh_bao_tu_bang_chung(kho, bo_nho),
        giai_thich="\n".join(giai_thich),
    )


def ham_demo() -> None:
    """Chạy ví dụ mẫu cho báo cáo."""
    ket_qua = suy_dien_tien(VI_DU)
    print(dinh_dang_ket_qua(ket_qua))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Suy diễn tiến trên kho tri thức bệnh lá lúa.")
    parser.add_argument(
        "--su-kien",
        nargs="*",
        metavar="MA",
        help="Mã sự kiện đã biết (ví dụ tc_vet_thoi tt_am_do_cao). Bỏ trống để chạy ví dụ mẫu.",
    )
    args = parser.parse_args(argv)
    ket_qua = suy_dien_tien(args.su_kien or VI_DU)
    print(dinh_dang_ket_qua(ket_qua))
    return 0 if ket_qua.benh else 2


if __name__ == "__main__":
    raise SystemExit(main())