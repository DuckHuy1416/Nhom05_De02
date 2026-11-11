"""C4 – Suy diễn lùi: kiểm chứng giả thuyết (ví dụ “lúa bị đạo ôn?”) bằng câu hỏi thêm.

Thuật toán tự cài đặt theo hướng mục tiêu (goal-driven, AND/OR):

1. Muốn chứng minh mục tiêu (một kết luận bệnh hoặc một sự kiện trung gian),
   tìm các luật có kết luận đó.
2. Với mỗi luật, chứng minh lần lượt **tất cả** tiền đề (AND). Tiền đề nào là sự kiện
   cơ sở (triệu chứng, thời tiết, giai đoạn, tập quán) mà chưa biết thì hỏi người dùng
   câu hỏi có/không; tiền đề trung gian thì đệ quy chứng minh tiếp (OR giữa các luật).
3. Luật ứng viên được thử theo thứ tự ít câu hỏi cần hỏi nhất trước, giúp giảm số câu hỏi.
4. Có bộ nhớ đệm kết quả và kiểm tra chu trình để tránh lặp vô hạn.

Chạy thử (hỏi – đáp trên dòng lệnh):
    python -m src.rules.backward --muc-tieu dao_on
    python -m src.rules.backward --muc-tieu bac_la --tra-loi y
"""
from __future__ import annotations

import argparse
from typing import Callable, Iterable, Mapping

from .chung import (
    LOAI_BENH,
    MA_BENH,
    SU_KIEN_BENH,
    CauHoi,
    KetQuaChanDoan,
    LuatDaDung,
    canh_bao_tu_bang_chung,
    chon_ket_luan,
    dinh_dang_ket_qua,
    doc_kho_tri_thuc,
    gom_nguon,
    khuyen_nghi_cho,
    nhan_su_kien,
    nguon_cua_luat,
    nguon_khuyen_nghi,
)

HamHoi = Callable[[CauHoi], bool]


class _MaySuyDienLui:
    """Bộ máy suy diễn lùi với bộ nhớ đệm và bộ đếm câu hỏi."""

    def __init__(
        self,
        kho: dict,
        hoi: HamHoi,
        gia_thiet: Mapping[str, float],
        toi_da_cau_hoi: int,
    ) -> None:
        self.kho = kho
        self.hoi = hoi
        self.gia_thiet = dict(gia_thiet)
        self.toi_da_cau_hoi = toi_da_cau_hoi

        self.chi_so: dict[str, list[dict]] = {}
        for luat in kho["luat"]:
            for ket_luan in luat["thi"]:
                self.chi_so.setdefault(ket_luan, []).append(luat)

        self.da_biet: dict[str, bool] = {}
        self.do_tin_cay: dict[str, float] = {}
        # Giả thiết đã cho (ví dụ câu trả lời từ hồ sơ bệnh án) được coi là đã biết,
        # nhờ vậy bộ máy không hỏi lại và chọn luật ít câu hỏi nhất.
        for ma, do_tin_cay in self.gia_thiet.items():
            self.da_biet[ma] = True
            self.do_tin_cay[ma] = do_tin_cay
        self.cau_tra_loi: dict[str, bool] = {}
        self.dang_xet: set[str] = set()
        self.lich_su: list[LuatDaDung] = []
        self.da_kich_hoat: set[str] = set()
        self.cau_hoi: list[CauHoi] = []
        self.so_cau_hoi = 0

    # -- hỏi người dùng -------------------------------------------------
    def _co_the_hoi(self, ma: str) -> bool:
        return self.kho["su_kien"].get(ma, {}).get("loai") in LOAI_BENH

    def _hoi(self, ma: str) -> tuple[bool, float]:
        if ma in self.gia_thiet:
            return True, self.gia_thiet[ma]
        if ma in self.cau_tra_loi:
            tra_loi = self.cau_tra_loi[ma]
            return tra_loi, 1.0 if tra_loi else 0.0
        if not self._co_the_hoi(ma) or self.so_cau_hoi >= self.toi_da_cau_hoi:
            return False, 0.0

        cau_hoi = CauHoi(ma=ma, noi_dung=self.kho["su_kien"][ma]["cau_hoi"])
        tra_loi = bool(self.hoi(cau_hoi))
        self.so_cau_hoi += 1
        self.cau_hoi.append(cau_hoi)
        self.cau_tra_loi[ma] = tra_loi
        return tra_loi, 1.0 if tra_loi else 0.0

    # -- chứng minh một sự kiện -----------------------------------------
    def _chi_phi(self, luat: dict) -> int:
        """Số câu hỏi ước tính phải hỏi thêm nếu dùng luật này."""
        return sum(
            1
            for tien_de in luat["neu"]
            if tien_de not in self.da_biet and self._co_the_hoi(tien_de)
        )

    def chung_minh(self, muc_tieu: str) -> tuple[bool, float]:
        if muc_tieu in self.da_biet:
            return self.da_biet[muc_tieu], self.do_tin_cay.get(muc_tieu, 0.0)
        if muc_tieu in self.dang_xet:
            return False, 0.0
        if self._co_the_hoi(muc_tieu):
            thanh_cong, do_tin_cay = self._hoi(muc_tieu)
            self.da_biet[muc_tieu] = thanh_cong
            self.do_tin_cay[muc_tieu] = do_tin_cay
            return thanh_cong, do_tin_cay

        ung_vien = sorted(
            self.chi_so.get(muc_tieu, []),
            key=lambda luat: (self._chi_phi(luat), -float(luat["do_tin_cay"])),
        )
        self.dang_xet.add(muc_tieu)
        for luat in ung_vien:
            if luat["ma"] in self.da_kich_hoat:
                continue
            tien_de = [t for t in luat["neu"] if t != muc_tieu]
            do_tin_cay_tien_de = 1.0
            for su_kien in tien_de:
                thanh_cong, do_tin_cay = self.chung_minh(su_kien)
                if not thanh_cong:
                    break
                do_tin_cay_tien_de = min(do_tin_cay_tien_de, do_tin_cay)
            else:
                do_tin_cay = round(float(luat["do_tin_cay"]) * do_tin_cay_tien_de, 4)
                self.da_kich_hoat.add(luat["ma"])
                self.da_biet[muc_tieu] = True
                self.do_tin_cay[muc_tieu] = do_tin_cay
                self.lich_su.append(
                    LuatDaDung(
                        ma=luat["ma"],
                        ten=luat["ten"],
                        do_tin_cay=do_tin_cay,
                        tien_de=list(luat["neu"]),
                        ket_luan=list(luat["thi"]),
                        nguon=list(luat["nguon"]),
                    )
                )
                self.dang_xet.discard(muc_tieu)
                return True, do_tin_cay

        self.dang_xet.discard(muc_tieu)
        self.da_biet[muc_tieu] = False
        self.do_tin_cay[muc_tieu] = 0.0
        return False, 0.0


def suy_dien_lui(
    muc_tieu: str,
    hoi_nguoi_dung: HamHoi | None = None,
    kho: dict | None = None,
    gia_thiet: Mapping[str, float] | Iterable[str] | None = None,
    toi_da_cau_hoi: int = 30,
) -> KetQuaChanDoan:
    """Chứng minh ``muc_tieu`` (mã bệnh hoặc mã sự kiện) bằng suy diễn lùi.

    ``hoi_nguoi_dung`` nhận một :class:`CauHoi` và trả về ``True``/``False``.
    Nếu không truyền, mọi câu hỏi được coi là chưa biết (không chứng minh được).
    """
    kho = kho or doc_kho_tri_thuc()
    if muc_tieu in MA_BENH:
        muc_tieu = SU_KIEN_BENH[muc_tieu]
    if muc_tieu not in kho["su_kien"]:
        raise ValueError(f"Mục tiêu không có trong kho tri thức: {muc_tieu}")

    if gia_thiet is None:
        gia_thiet = {}
    elif not isinstance(gia_thiet, Mapping):
        gia_thiet = {ma: 1.0 for ma in gia_thiet}
    gia_thiet = dict(gia_thiet)

    may = _MaySuyDienLui(
        kho=kho,
        hoi=hoi_nguoi_dung or (lambda _cau_hoi: False),
        gia_thiet=gia_thiet,
        toi_da_cau_hoi=toi_da_cau_hoi,
    )
    thanh_cong, do_tin_cay_muc_tieu = may.chung_minh(muc_tieu)

    bang_chung = dict(gia_thiet)
    bang_chung.update({ma: conf for ma, conf in may.do_tin_cay.items() if may.da_biet.get(ma)})
    benh, do_tin_cay, xep_hang = chon_ket_luan(bang_chung)
    if thanh_cong:
        benh = {
            "benh_dao_on": "dao_on",
            "benh_bac_la": "bac_la",
            "benh_dom_nau": "dom_nau",
            "la_khoe": "la_khoe",
        }.get(muc_tieu, benh)
        do_tin_cay = do_tin_cay_muc_tieu
        xep_hang = sorted(
            [cap for cap in xep_hang if cap[0] != benh] + [(benh, do_tin_cay)],
            key=lambda cap: cap[1],
            reverse=True,
        )
    else:
        benh, do_tin_cay = None, 0.0
        xep_hang = []

    ma_nguon = nguon_cua_luat(kho, may.lich_su)
    ma_nguon.extend(ma for ma in nguon_khuyen_nghi(kho, benh) if ma not in ma_nguon)

    giai_thich = [
        f"Mục tiêu: chứng minh “{nhan_su_kien(kho, muc_tieu)}”.",
        f"Đã hỏi {may.so_cau_hoi} câu, kích hoạt {len(may.lich_su)} luật.",
    ]
    for luat in may.lich_su:
        giai_thich.append(
            f"  {luat.ma} ({luat.do_tin_cay:.0%}): "
            + " + ".join(nhan_su_kien(kho, t) for t in luat.tien_de)
            + f"  ⇒  {', '.join(nhan_su_kien(kho, k) for k in luat.ket_luan)}"
        )
    if not thanh_cong:
        giai_thich.append(
            "Không chứng minh được mục tiêu: người dùng trả lời không đủ tiền đề "
            "hoặc đã hết số câu hỏi cho phép."
        )

    return KetQuaChanDoan(
        phuong_phap=f"Suy diễn lùi (backward chaining) tự cài đặt – mục tiêu {muc_tieu}",
        benh=benh,
        do_tin_cay=do_tin_cay,
        xep_hang=xep_hang,
        luat_da_dung=may.lich_su,
        bang_chung=bang_chung,
        cau_hoi=may.cau_hoi,
        nguon=gom_nguon(kho, ma_nguon),
        khuyen_nghi=khuyen_nghi_cho(kho, benh),
        canh_bao=canh_bao_tu_bang_chung(kho, bang_chung),
        giai_thich="\n".join(giai_thich),
        thanh_cong=thanh_cong,
    )


def _hoi_dong_lenh(cau_hoi: CauHoi) -> bool:
    while True:
        tra_loi = input(f"  ? {cau_hoi.noi_dung} [c/k] ").strip().lower()
        if tra_loi in ("c", "co", "có", "y", "yes"):
            return True
        if tra_loi in ("k", "khong", "không", "n", "no"):
            return False
        print("  Vui lòng trả lời c hoặc k.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Suy diễn lùi để kiểm chứng một giả thuyết bệnh.")
    parser.add_argument(
        "--muc-tieu",
        default="dao_on",
        help="Mã bệnh (dao_on, bac_la, dom_nau, la_khoe) hoặc mã sự kiện.",
    )
    parser.add_argument(
        "--tra-loi",
        choices=("y", "n"),
        help="Trả lời sẵn cho mọi câu hỏi (dùng khi chạy thử không tương tác).",
    )
    args = parser.parse_args(argv)

    if args.tra_loi:
        co = args.tra_loi == "y"
        ket_qua = suy_dien_lui(args.muc_tieu, hoi_nguoi_dung=lambda _cau_hoi: co)
    else:
        print(f"Trả lời câu hỏi để kiểm chứng giả thuyết: {args.muc_tieu}")
        ket_qua = suy_dien_lui(args.muc_tieu, hoi_nguoi_dung=_hoi_dong_lenh)

    print(dinh_dang_ket_qua(ket_qua))
    return 0 if ket_qua.thanh_cong else 2


if __name__ == "__main__":
    raise SystemExit(main())
