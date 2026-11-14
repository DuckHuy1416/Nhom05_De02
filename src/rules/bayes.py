"""C5 - Mạng Bayes >= 5 nút bằng pgmpy, bảng CPD, ví dụ truy vấn xác suất hậu nghiệm.
"""

from __future__ import annotations

import argparse
import itertools
from typing import Iterable, Mapping

MA_BENH_BAYES = {"dao_on": "DaoOn", "bac_la": "BacLa", "dom_nau": "DomNau"}

#: Đặc tả mạng: giá trị của từng nút, nút cha và bảng CPD.
#: Khóa của ``cpd`` là tổ hợp giá trị các nút cha (theo đúng thứ tự ``cha``);
#: giá trị là xác suất của các giá trị trong ``gia_tri``.
NUT: dict[str, dict] = {
    "ThoiTiet": {
        "nhan": "Thời tiết",
        "gia_tri": ["mua_am", "kho"],
        "cha": [],
        "cpd": {(): [0.60, 0.40]},
    },
    "BonDam": {
        "nhan": "Bón đạm",
        "gia_tri": ["cao", "thap"],
        "cha": [],
        "cpd": {(): [0.45, 0.55]},
    },
    "Giong": {
        "nhan": "Giống lúa",
        "gia_tri": ["nhiem", "khang"],
        "cha": [],
        "cpd": {(): [0.50, 0.50]},
    },
    "DinhDuong": {
        "nhan": "Dinh dưỡng đất",
        "gia_tri": ["du", "thieu"],
        "cha": [],
        "cpd": {(): [0.55, 0.45]},
    },
    "DaoOn": {
        "nhan": "Bệnh đạo ôn",
        "gia_tri": ["co", "khong"],
        "cha": ["ThoiTiet", "BonDam", "Giong"],
        "cpd": {
            ("mua_am", "cao", "nhiem"): [0.75, 0.25],
            ("mua_am", "cao", "khang"): [0.45, 0.55],
            ("mua_am", "thap", "nhiem"): [0.50, 0.50],
            ("mua_am", "thap", "khang"): [0.20, 0.80],
            ("kho", "cao", "nhiem"): [0.35, 0.65],
            ("kho", "cao", "khang"): [0.15, 0.85],
            ("kho", "thap", "nhiem"): [0.15, 0.85],
            ("kho", "thap", "khang"): [0.05, 0.95],
        },
    },
    "BacLa": {
        "nhan": "Bệnh bạc lá",
        "gia_tri": ["co", "khong"],
        "cha": ["ThoiTiet", "BonDam"],
        "cpd": {
            ("mua_am", "cao"): [0.70, 0.30],
            ("mua_am", "thap"): [0.45, 0.55],
            ("kho", "cao"): [0.30, 0.70],
            ("kho", "thap"): [0.12, 0.88],
        },
    },
    "DomNau": {
        "nhan": "Bệnh đốm nâu",
        "gia_tri": ["co", "khong"],
        "cha": ["DinhDuong", "ThoiTiet"],
        "cpd": {
            ("thieu", "mua_am"): [0.70, 0.30],
            ("thieu", "kho"): [0.60, 0.40],
            ("du", "mua_am"): [0.30, 0.70],
            ("du", "kho"): [0.20, 0.80],
        },
    },
    "TrieuChung": {
        "nhan": "Triệu chứng trên lá",
        "gia_tri": ["vet_thoi", "chop_la_kho", "dom_tron", "khong"],
        "cha": ["DaoOn", "BacLa", "DomNau"],
        "cpd": {
            ("co", "khong", "khong"): [0.85, 0.05, 0.02, 0.08],
            ("khong", "co", "khong"): [0.03, 0.85, 0.02, 0.10],
            ("khong", "khong", "co"): [0.02, 0.03, 0.85, 0.10],
            ("co", "co", "khong"): [0.50, 0.40, 0.03, 0.07],
            ("co", "khong", "co"): [0.50, 0.03, 0.40, 0.07],
            ("khong", "co", "co"): [0.02, 0.45, 0.45, 0.08],
            ("co", "co", "co"): [0.34, 0.33, 0.33, 0.00],
            ("khong", "khong", "khong"): [0.02, 0.02, 0.03, 0.93],
        },
    },
}

#: Ánh xạ sự kiện của hệ luật sang bằng chứng của mạng Bayes.
ANH_XA_BANG_CHUNG: dict[str, tuple[str, str]] = {
    "tc_vet_thoi": ("TrieuChung", "vet_thoi"),
    "tc_qua_quang_vang": ("TrieuChung", "vet_thoi"),
    "tc_chop_la_kho": ("TrieuChung", "chop_la_kho"),
    "tc_vien_la_nau": ("TrieuChung", "chop_la_kho"),
    "tc_giot_vi_khuan": ("TrieuChung", "chop_la_kho"),
    "tc_dom_tron": ("TrieuChung", "dom_tron"),
    "tc_dom_nhieu": ("TrieuChung", "dom_tron"),
    "tc_khong_co": ("TrieuChung", "khong"),
    "tt_am_do_cao": ("ThoiTiet", "mua_am"),
    "tt_suong_mu": ("ThoiTiet", "mua_am"),
    "tt_mua_nhieu": ("ThoiTiet", "mua_am"),
    "tt_gio_manh": ("ThoiTiet", "mua_am"),
    "tt_nang_mua_xen_ke": ("ThoiTiet", "mua_am"),
    "tt_kho_han": ("ThoiTiet", "kho"),
    "tq_dam_cao": ("BonDam", "cao"),
    "tq_giong_nhiem": ("Giong", "nhiem"),
    "tq_dat_ngheo": ("DinhDuong", "thieu"),
    "tq_thieu_kali": ("DinhDuong", "thieu"),
    "tq_ruong_ngap": ("ThoiTiet", "mua_am"),
}


def bang_chung_bayes(
    bang_chung: Mapping[str, float] | Iterable[str] | None,
) -> tuple[dict[str, str], list[str]]:
    """Chuyển bằng chứng của hệ luật thành bằng chứng nút mạng Bayes.

    Sự kiện không ánh xạ được (giai đoạn, tàn dư bệnh...) sẽ bị bỏ qua và ghi chú,
    vì mạng Bayes ở đây chỉ mô hình hóa thời tiết, đạm, giống, dinh dưỡng, triệu chứng.
    Trả về ``(bằng_chứng, ghi_chú)``.
    """
    if not bang_chung:
        return {}, []
    if isinstance(bang_chung, Mapping):
        ds_su_kien = list(bang_chung)
    else:
        ds_su_kien = list(bang_chung)

    bang_chung_nut: dict[str, str] = {}
    ghi_chu: list[str] = []
    for su_kien in ds_su_kien:
        if su_kien not in ANH_XA_BANG_CHUNG:
            ghi_chu.append(f"Bỏ qua {su_kien}: không có nút tương ứng trong mạng Bayes.")
            continue
        nut, gia_tri = ANH_XA_BANG_CHUNG[su_kien]
        if nut in bang_chung_nut and bang_chung_nut[nut] != gia_tri:
            ghi_chu.append(
                f"Bỏ qua bằng chứng mâu thuẫn cho nút {nut}: "
                f"{bang_chung_nut[nut]} và {gia_tri}."
            )
            bang_chung_nut.pop(nut)
            continue
        bang_chung_nut[nut] = gia_tri
    return bang_chung_nut, ghi_chu


def _xac_suat_dong_nhat(dong: dict[str, str]) -> float:
    xac_suat = 1.0
    for ten_nut, dac_ta in NUT.items():
        khoa = tuple(dong[cha] for cha in dac_ta["cha"])
        chi_so = dac_ta["gia_tri"].index(dong[ten_nut])
        xac_suat *= dac_ta["cpd"][khoa][chi_so]
    return xac_suat


def kiem_tra_cpd() -> None:
    """Kiểm tra mỗi bảng CPD có đủ tổ hợp cha và tổng xác suất bằng 1."""
    for ten_nut, dac_ta in NUT.items():
        so_to_hop = 1
        for cha in dac_ta["cha"]:
            so_to_hop *= len(NUT[cha]["gia_tri"])
        if len(dac_ta["cpd"]) != so_to_hop:
            raise ValueError(f"CPD của {ten_nut} có {len(dac_ta['cpd'])} tổ hợp, cần {so_to_hop}.")
        for khoa, gia_tri in dac_ta["cpd"].items():
            if len(gia_tri) != len(dac_ta["gia_tri"]):
                raise ValueError(f"CPD của {ten_nut} tại {khoa} sai số giá trị.")
            if abs(sum(gia_tri) - 1.0) > 1e-6:
                raise ValueError(f"CPD của {ten_nut} tại {khoa} không cộng lại bằng 1.")
    tong = sum(_xac_suat_dong_nhat(dong) for dong in _tat_ca_dong_nhat())
    if abs(tong - 1.0) > 1e-6:
        raise ValueError(f"Phân phối đồng thời cộng lại bằng {tong}, không phải 1.")


def _tat_ca_dong_nhat():
    ten_nut = list(NUT)
    for to_hop in itertools.product(*[NUT[n]["gia_tri"] for n in ten_nut]):
        yield dict(zip(ten_nut, to_hop))


def _truy_van_liet_ke(bang_chung: dict[str, str]) -> dict[str, dict[str, float]]:
    """Tính phân phối biên chính xác bằng liệt kê (dùng khi không có pgmpy)."""
    tong = 0.0
    tich: dict[str, dict[str, float]] = {
        ten: {gia_tri: 0.0 for gia_tri in dac_ta["gia_tri"]} for ten, dac_ta in NUT.items()
    }
    for dong in _tat_ca_dong_nhat():
        if any(dong[nut] != gia_tri for nut, gia_tri in bang_chung.items()):
            continue
        p = _xac_suat_dong_nhat(dong)
        tong += p
        for ten_nut, gia_tri in dong.items():
            tich[ten_nut][gia_tri] += p
    if tong <= 0:
        raise ValueError(f"Bằng chứng không thể xảy ra: {bang_chung}")
    return {
        ten: {gia_tri: gia_tri_xac_suat / tong for gia_tri, gia_tri_xac_suat in ds.items()}
        for ten, ds in tich.items()
    }


def xay_dung_mang_pgmpy():
    """Dựng ``DiscreteBayesianNetwork`` của pgmpy từ đặc tả CPD ở trên."""
    import numpy as np
    from pgmpy.factors.discrete import TabularCPD

    try:  # pgmpy >= 1.0
        from pgmpy.models import DiscreteBayesianNetwork as LopMang
    except ImportError:  # pgmpy 0.1.x
        from pgmpy.models import BayesianNetwork as LopMang

    mang = LopMang()
    for ten_nut, dac_ta in NUT.items():
        mang.add_node(ten_nut)
        for cha in dac_ta["cha"]:
            mang.add_edge(cha, ten_nut)

    ds_cpd = []
    for ten_nut, dac_ta in NUT.items():
        cot = [
            dac_ta["cpd"][tuple(to_hop)]
            for to_hop in itertools.product(*[NUT[cha]["gia_tri"] for cha in dac_ta["cha"]])
        ]
        gia_tri = np.array(cot, dtype=float).T
        tham_so = {
            "variable": ten_nut,
            "variable_card": len(dac_ta["gia_tri"]),
            "values": gia_tri,
            # Phải khai báo tên trạng thái, nếu không pgmpy gán mặc định "0", "1"
            # và truy vấn theo tên (mua_am, cao, nhiem...) sẽ lỗi KeyError.
            "state_names": {ten_nut: list(dac_ta["gia_tri"])},
        }
        for cha in dac_ta["cha"]:
            tham_so["state_names"][cha] = list(NUT[cha]["gia_tri"])
        if dac_ta["cha"]:
            tham_so["evidence"] = list(dac_ta["cha"])
            tham_so["evidence_card"] = [len(NUT[cha]["gia_tri"]) for cha in dac_ta["cha"]]
        ds_cpd.append(TabularCPD(**tham_so))

    mang.add_cpds(*ds_cpd)
    if not mang.check_model():
        raise ValueError("Mô hình Bayes không hợp lệ (kiểm tra CPD).")
    return mang


def truy_van(
    bang_chung: Mapping[str, float] | Iterable[str] | None = None,
    su_dung_pgmpy: bool = True,
) -> dict:
    """Truy vấn xác suất hậu nghiệm của 3 bệnh khi biết bằng chứng.

    Trả về ``xac_suat`` (theo mã bệnh dùng chung), ``chi_tiet`` (phân phối từng nút),
    ``phuong_phap`` và ``ghi_chu``.
    """
    kiem_tra_cpd()
    bang_chung_nut, ghi_chu = bang_chung_bayes(bang_chung)
    phuong_phap = "Liệt kê toàn bộ phân phối đồng thời (fallback, không cần pgmpy)"

    if su_dung_pgmpy:
        try:
            from pgmpy.inference import VariableElimination

            mang = xay_dung_mang_pgmpy()
            bo_suy_dien = VariableElimination(mang)
            chi_tiet: dict[str, dict[str, float]] = {}
            for ten_nut, dac_ta in NUT.items():
                if ten_nut in bang_chung_nut:
                    # Nút đã là bằng chứng: pgmpy không cho vừa truy vấn vừa làm bằng chứng.
                    gia_tri_da_biet = bang_chung_nut[ten_nut]
                    chi_tiet[ten_nut] = {
                        gia_tri: 1.0 if gia_tri == gia_tri_da_biet else 0.0
                        for gia_tri in dac_ta["gia_tri"]
                    }
                    continue
                phan_phoi = bo_suy_dien.query(
                    variables=[ten_nut],
                    evidence=bang_chung_nut or None,
                    show_progress=False,
                )
                chi_tiet[ten_nut] = {
                    gia_tri: float(phan_phoi.values[dac_ta["gia_tri"].index(gia_tri)])
                    for gia_tri in dac_ta["gia_tri"]
                }
            phuong_phap = "pgmpy – VariableElimination"
        except ImportError:
            ghi_chu.append("Chưa cài pgmpy: dùng phép liệt kê tự cài đặt, kết quả tương đương.")
            chi_tiet = _truy_van_liet_ke(bang_chung_nut)
        except Exception as loi:  # noqa: BLE001 - pgmpy có thể lỗi phiên bản
            ghi_chu.append(f"pgmpy lỗi ({loi}): dùng phép liệt kê tự cài đặt.")
            chi_tiet = _truy_van_liet_ke(bang_chung_nut)
    else:
        chi_tiet = _truy_van_liet_ke(bang_chung_nut)

    xac_suat = {ma: chi_tiet[ten]["co"] for ma, ten in MA_BENH_BAYES.items()}
    # Ước lượng xác suất lá khỏe: xác suất đồng thời không mắc cả 3 bệnh,
    # giả định ba bệnh độc lập có điều kiện khi đã biết bằng chứng.
    xac_suat["la_khoe"] = round(
        (1 - xac_suat["dao_on"]) * (1 - xac_suat["bac_la"]) * (1 - xac_suat["dom_nau"]), 4
    )
    return {
        "xac_suat": {ma: round(p, 4) for ma, p in xac_suat.items()},
        "chi_tiet": chi_tiet,
        "bang_chung": bang_chung_nut,
        "phuong_phap": phuong_phap,
        "ghi_chu": ghi_chu,
        "ghi_chu_la_khoe": (
            "P(lá khỏe) là ước lượng P(¬đạo ôn)·P(¬bạc lá)·P(¬đốm nâu) "
            "theo giả định độc lập có điều kiện."
        ),
    }


def in_cau_truc() -> None:
    print("Mạng Bayes 8 nút (bảng CPD khai báo trong NUT):")
    for ten_nut, dac_ta in NUT.items():
        cha = ", ".join(dac_ta["cha"]) or "—"
        print(f"  {ten_nut:<11} | cha: {cha:<28} | giá trị: {', '.join(dac_ta['gia_tri'])}")
    print(
        "\nGhi chú: các CPD được ước lượng định tính từ mô tả điều kiện phát bệnh của IRRI "
        "(S1–S3), cần hiệu chỉnh khi có dữ liệu đồng ruộng.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Truy vấn mạng Bayes bệnh lá lúa.")
    parser.add_argument(
        "--bang-chung",
        nargs="*",
        default=None,
        help="Mã sự kiện đã biết (ví dụ tc_vet_thoi tt_am_do_cao tq_dam_cao).",
    )
    parser.add_argument(
        "--khong-pgmpy",
        action="store_true",
        help="Bắt buộc dùng phép liệt kê thay vì pgmpy (để đối chiếu kết quả).",
    )
    args = parser.parse_args(argv)

    in_cau_truc()
    ds = args.bang_chung
    for nhan, bang_chung in (
        ("Truy vấn 1: chưa có bằng chứng (tiên nghiệm)", None),
        ("Truy vấn 2: vết hình thoi + mưa ẩm + bón nhiều đạm", ds or ["tc_vet_thoi", "tt_am_do_cao", "tq_dam_cao"]),
    ):
        ket_qua = truy_van(bang_chung, su_dung_pgmpy=not args.khong_pgmpy)
        print(f"{nhan}")
        print(f"  Bằng chứng nút: {ket_qua['bang_chung'] or '—'} ({ket_qua['phuong_phap']})")
        for ma, p in ket_qua["xac_suat"].items():
            print(f"    P({ma:<8}) = {p:.1%}")
        for ghi_chu in ket_qua["ghi_chu"]:
            print(f"  * {ghi_chu}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())