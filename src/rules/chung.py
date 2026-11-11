"""Tiện ích dùng chung cho Chức năng 2 – kho tri thức, kết quả chẩn đoán, định dạng.

Kho tri thức nằm trong ``src/rules/rules.json``: mỗi luật ghi mã luật, tiền đề,
kết luận, độ tin cậy và mã nguồn tài liệu khuyến nông. Hàm :func:`doc_kho_tri_thuc`
kiểm tra tính nhất quán của kho (mã sự kiện, mã nguồn) trước khi dùng.

Nhóm 05 – Đồ án Bác sĩ Lúa (Chức năng 2).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

DUONG_DAN_LUAT = Path(__file__).with_name("rules.json")

#: Mã lớp bệnh dùng chung cho CNN, hệ luật và mạng Bayes (xem docs/interfaces.md).
MA_BENH = ("dao_on", "bac_la", "dom_nau", "la_khoe")
TEN_BENH = {
    "dao_on": "Bệnh đạo ôn",
    "bac_la": "Bệnh bạc lá",
    "dom_nau": "Bệnh đốm nâu",
    "la_khoe": "Lá khỏe",
}
#: Sự kiện kết luận tương ứng với từng mã bệnh.
SU_KIEN_BENH = {
    "dao_on": "benh_dao_on",
    "bac_la": "benh_bac_la",
    "dom_nau": "benh_dom_nau",
    "la_khoe": "la_khoe",
}
#: Sự kiện cảnh báo cần hiển thị cho người dùng.
SU_KIEN_CANH_BAO = (
    "canh_bao_thoi_tiet_dao_on",
    "nguy_co_dao_on_cao",
    "nguy_co_bac_la_cao",
    "nguy_co_dom_nau_cao",
    "canh_bao_dao_on_co_bong",
    "can_kiem_tra_dinh_duong",
)
LOAI_BENH = ("trieu_chung", "thoi_tiet", "giai_doan", "tap_quan")
TRUONG_LUAT = ("ma", "ten", "neu", "thi", "do_tin_cay", "nguon")


@dataclass(frozen=True)
class CauHoi:
    """Câu hỏi có/không mà suy diễn lùi đặt cho người dùng."""

    ma: str
    noi_dung: str


@dataclass
class LuatDaDung:
    """Một luật đã kích hoạt, kèm độ tin cậy tính được."""

    ma: str
    ten: str
    do_tin_cay: float
    tien_de: list[str] = field(default_factory=list)
    ket_luan: list[str] = field(default_factory=list)
    nguon: list[str] = field(default_factory=list)


@dataclass
class KetQuaChanDoan:
    """Kết quả thống nhất của suy diễn tiến, suy diễn lùi và bước kết hợp."""

    phuong_phap: str
    benh: str | None = None
    do_tin_cay: float = 0.0
    thanh_cong: bool = True
    xep_hang: list[tuple[str, float]] = field(default_factory=list)
    luat_da_dung: list[LuatDaDung] = field(default_factory=list)
    bang_chung: dict[str, float] = field(default_factory=dict)
    cau_hoi: list[CauHoi] = field(default_factory=list)
    nguon: list[dict] = field(default_factory=list)
    khuyen_nghi: list[str] = field(default_factory=list)
    canh_bao: list[str] = field(default_factory=list)
    giai_thich: str = ""

    @property
    def nhan_benh(self) -> str:
        return TEN_BENH.get(self.benh or "", "Chưa đủ dữ kiện để kết luận")

    def tom_tat(self) -> str:
        dong = [
            f"Phương pháp: {self.phuong_phap}",
            f"Kết luận: {self.nhan_benh} (độ tin cậy {self.do_tin_cay:.0%})",
        ]
        if not self.thanh_cong:
            dong.append("Chưa chứng minh được mục tiêu.")
        if self.xep_hang:
            dong.append(
                "Xếp hạng: "
                + ", ".join(f"{TEN_BENH.get(ma, ma)} {diem:.0%}" for ma, diem in self.xep_hang)
            )
        if self.canh_bao:
            dong.append("Cảnh báo: " + "; ".join(self.canh_bao))
        for noi_dung in self.khuyen_nghi:
            dong.append(f"- {noi_dung}")
        if self.nguon:
            dong.append("Nguồn: " + "; ".join(f"{n['ma']} {n['ten']}" for n in self.nguon))
        return "\n".join(dong)


def doc_kho_tri_thuc(duong_dan: str | Path = DUONG_DAN_LUAT) -> dict:
    """Đọc và kiểm tra kho tri thức (luật + nguồn + khuyến nghị)."""
    duong_dan = Path(duong_dan)
    with duong_dan.open(encoding="utf-8") as tep:
        kho = json.load(tep)

    su_kien = kho["su_kien"]
    nguon = {n["ma"] for n in kho["nguon"]}
    for n in kho["nguon"]:
        if not n.get("url") or not n.get("ten"):
            raise ValueError(f"Nguồn {n.get('ma')} thiếu tên hoặc đường dẫn.")
    for ma_benh in MA_BENH:
        if SU_KIEN_BENH[ma_benh] not in su_kien:
            raise ValueError(f"Thiếu sự kiện kết luận {SU_KIEN_BENH[ma_benh]}.")

    for luat in kho["luat"]:
        thieu = [t for t in TRUONG_LUAT if t not in luat]
        if thieu:
            raise ValueError(f"Luật {luat.get('ma')} thiếu trường {thieu}.")
        if not 0.0 < float(luat["do_tin_cay"]) <= 1.0:
            raise ValueError(f"Luật {luat['ma']} có độ tin cậy ngoài (0, 1].")
        for su_kien_ma in luat["neu"] + luat["thi"]:
            if su_kien_ma not in su_kien:
                raise ValueError(f"Luật {luat['ma']} dùng sự kiện lạ: {su_kien_ma}.")
        if not luat["nguon"]:
            raise ValueError(f"Luật {luat['ma']} chưa ghi nguồn.")
        la = [ma for ma in luat["nguon"] if ma not in nguon]
        if la:
            raise ValueError(f"Luật {luat['ma']} dẫn nguồn không tồn tại: {la}.")

    for ma_benh, ds in kho.get("khuyen_nghi", {}).items():
        if ma_benh not in MA_BENH:
            raise ValueError(f"Khuyến nghị cho mã bệnh lạ: {ma_benh}")
        for muc in ds:
            if not muc.get("noi_dung"):
                raise ValueError(f"Khuyến nghị {ma_benh} thiếu nội dung.")
            la = [ma for ma in muc.get("nguon", []) if ma not in nguon]
            if la:
                raise ValueError(f"Khuyến nghị {ma_benh} dẫn nguồn không tồn tại: {la}.")
    return kho


def chuan_hoa_bang_chung(
    bang_chung: Mapping[str, float] | Iterable[str] | None,
    kho: dict,
) -> dict[str, float]:
    """Chuẩn hóa bằng chứng đầu vào thành ``{mã sự kiện: độ tin cậy}``."""
    if not bang_chung:
        return {}
    if isinstance(bang_chung, Mapping):
        tho = dict(bang_chung)
    else:
        tho = {ma: 1.0 for ma in bang_chung}
    ket_qua: dict[str, float] = {}
    for ma, gia_tri in tho.items():
        if ma not in kho["su_kien"]:
            raise ValueError(f"Sự kiện không có trong kho tri thức: {ma}")
        do_tin_cay = float(gia_tri)
        if not 0.0 <= do_tin_cay <= 1.0:
            raise ValueError(f"Độ tin cậy của {ma} phải trong [0, 1], nhận {do_tin_cay}.")
        ket_qua[ma] = do_tin_cay
    return ket_qua


def nhan_su_kien(kho: dict, ma: str) -> str:
    return kho["su_kien"].get(ma, {}).get("nhan", ma)


def gom_nguon(kho: dict, ma_nguon: Iterable[str]) -> list[dict]:
    """Trả về thông tin nguồn theo thứ tự khai báo trong kho tri thức."""
    can = set(ma_nguon)
    return [n for n in kho["nguon"] if n["ma"] in can]


def nguon_cua_luat(kho: dict, luat_da_dung: Iterable[LuatDaDung]) -> list[str]:
    ma: list[str] = []
    for luat in luat_da_dung:
        ma.extend(m for m in luat.nguon if m not in ma)
    return ma


def khuyen_nghi_cho(kho: dict, benh: str | None) -> list[str]:
    if not benh:
        return []
    return [muc["noi_dung"] for muc in kho.get("khuyen_nghi", {}).get(benh, [])]


def nguon_khuyen_nghi(kho: dict, benh: str | None) -> list[str]:
    if not benh:
        return []
    ma: list[str] = []
    for muc in kho.get("khuyen_nghi", {}).get(benh, []):
        ma.extend(m for m in muc.get("nguon", []) if m not in ma)
    return ma


def chon_ket_luan(bang_chung: Mapping[str, float]) -> tuple[str | None, float, list[tuple[str, float]]]:
    """Chọn bệnh có độ tin cậy cao nhất trong các kết luận suy ra được."""
    xep_hang = sorted(
        (
            (ma_benh, float(bang_chung[su_kien]))
            for ma_benh, su_kien in SU_KIEN_BENH.items()
            if su_kien in bang_chung
        ),
        key=lambda cap: cap[1],
        reverse=True,
    )
    if not xep_hang:
        return None, 0.0, []
    benh, do_tin_cay = xep_hang[0]
    return benh, do_tin_cay, xep_hang


def canh_bao_tu_bang_chung(kho: dict, bang_chung: Mapping[str, float]) -> list[str]:
    return [
        f"{nhan_su_kien(kho, ma)} (độ tin cậy {bang_chung[ma]:.0%})"
        for ma in SU_KIEN_CANH_BAO
        if ma in bang_chung
    ]


def dinh_dang_ket_qua(ket_qua: KetQuaChanDoan) -> str:
    """In kết quả chẩn đoán ra màn hình dạng dễ đọc."""
    dong = ["=" * 66, f"  {ket_qua.phuong_phap}", "=" * 66]
    dong.append(f"Kết luận : {ket_qua.nhan_benh}  ({ket_qua.do_tin_cay:.0%})")
    if ket_qua.xep_hang:
        dong.append("Xếp hạng : " + " | ".join(
            f"{TEN_BENH.get(ma, ma)} {diem:.0%}" for ma, diem in ket_qua.xep_hang
        ))
    if ket_qua.cau_hoi:
        dong.append("Câu hỏi  : " + " | ".join(f"{c.ma}={c.noi_dung}" for c in ket_qua.cau_hoi))
    if ket_qua.luat_da_dung:
        dong.append("Luật dùng:")
        for luat in ket_qua.luat_da_dung:
            dong.append(f"  {luat.ma} ({luat.do_tin_cay:.0%}) {luat.ten}")
    if ket_qua.canh_bao:
        dong.append("Cảnh báo :")
        dong.extend(f"  - {muc}" for muc in ket_qua.canh_bao)
    if ket_qua.khuyen_nghi:
        dong.append("Khuyến nghị:")
        dong.extend(f"  - {muc}" for muc in ket_qua.khuyen_nghi)
    if ket_qua.nguon:
        dong.append("Nguồn tài liệu:")
        dong.extend(f"  [{n['ma']}] {n['ten']} – {n['url']}" for n in ket_qua.nguon)
    if ket_qua.giai_thich:
        dong.append("Giải thích:")
        dong.extend(f"  {t}" for t in ket_qua.giai_thich.splitlines())
    dong.append("Lưu ý: kết quả chỉ mang tính tham khảo, không thay thế cán bộ khuyến nông.")
    return "\n".join(dong)