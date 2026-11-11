"""Kiểm thử Chức năng 2 – kho luật, suy diễn tiến, suy diễn lùi, mạng Bayes, kết hợp CNN.

Chạy: python -m pytest tests/ -q
"""
import pytest

from src.rules import backward, bayes, forward, ket_hop
from src.rules.chung import MA_BENH, doc_kho_tri_thuc


@pytest.fixture(scope="module")
def kho():
    return doc_kho_tri_thuc()


def _hoi_tu(dong_y: set[str]):
    """Tạo hàm trả lời: chỉ những câu hỏi trong ``dong_y`` được trả lời “có”."""

    def hoi(cau_hoi):
        return cau_hoi.ma in dong_y

    return hoi


# --------------------------------------------------------------------- kho luật
def test_kho_co_it_nhat_20_luat(kho):
    assert len(kho["luat"]) >= 20
    ma_luat = [luat["ma"] for luat in kho["luat"]]
    assert len(ma_luat) == len(set(ma_luat)), "Mã luật bị trùng"


def test_luat_hop_le_va_co_nguon(kho):
    for luat in kho["luat"]:
        assert luat["nguon"], f"{luat['ma']} thiếu nguồn"
        assert 0 < luat["do_tin_cay"] <= 1
        for su_kien in luat["neu"] + luat["thi"]:
            assert su_kien in kho["su_kien"]


def test_moi_benh_deu_co_luat_ket_luan(kho):
    ket_luan = {su_kien for luat in kho["luat"] for su_kien in luat["thi"]}
    for su_kien in ("benh_dao_on", "benh_bac_la", "benh_dom_nau", "la_khoe"):
        assert su_kien in ket_luan


def test_khong_tu_dat_ten_thuoc_hay_lieu_luong(kho):
    """Nguyên tắc của đồ án: hệ thống không tự đặt tên thuốc, liều lượng."""
    import json

    chuoi = json.dumps(kho, ensure_ascii=False).lower()
    for tu_khoa in ("ml/", "gram/", "g/l", "liều lượng:", "lieu luong:"):
        assert tu_khoa not in chuoi


# --------------------------------------------------------------- suy diễn tiến
def test_suy_dien_tien_ra_dao_on():
    ket_qua = forward.suy_dien_tien(["tc_vet_thoi", "tc_qua_quang_vang", "tt_am_do_cao"])
    assert ket_qua.thanh_cong
    assert ket_qua.benh == "dao_on"
    assert ket_qua.do_tin_cay == pytest.approx(0.85)
    assert any(luat.ma == "L01" for luat in ket_qua.luat_da_dung)
    assert ket_qua.nguon and ket_qua.khuyen_nghi


def test_suy_dien_tien_qua_su_kien_trung_gian():
    bang_chung = ["tt_am_do_cao", "tt_suong_mu", "tt_nhiet_do_thap", "tq_dam_cao", "gd_ma", "tq_giong_nhiem"]
    ket_qua = forward.suy_dien_tien(bang_chung)
    assert ket_qua.benh == "dao_on"
    ma_luat = {luat.ma for luat in ket_qua.luat_da_dung}
    assert {"L03", "L07", "L05"} <= ma_luat
    assert any("Thời tiết thuận lợi" in canh_bao for canh_bao in ket_qua.canh_bao)


@pytest.mark.parametrize(
    ("bang_chung", "benh"),
    [
        (["tc_chop_la_kho", "tc_vien_la_nau"], "bac_la"),
        (["tc_giot_vi_khuan"], "bac_la"),
        (["tc_dom_tron", "tc_dom_nhieu"], "dom_nau"),
        (["tc_khong_co"], "la_khoe"),
    ],
)
def test_suy_dien_tien_cac_benh(bang_chung, benh):
    ket_qua = forward.suy_dien_tien(bang_chung)
    assert ket_qua.benh == benh


def test_suy_dien_tien_tu_choi_su_kien_la(kho):
    with pytest.raises(ValueError):
        forward.suy_dien_tien(["khong_ton_tai"], kho)


# ---------------------------------------------------------------- suy diễn lùi
def test_suy_dien_lui_chung_minh_dao_on():
    ket_qua = backward.suy_dien_lui(
        "dao_on", hoi_nguoi_dung=_hoi_tu({"tc_vet_thoi", "tc_qua_quang_vang"})
    )
    assert ket_qua.thanh_cong
    assert ket_qua.benh == "dao_on"
    assert ket_qua.cau_hoi, "Suy diễn lùi phải đặt câu hỏi"
    assert any(luat.ma == "L01" for luat in ket_qua.luat_da_dung)


def test_suy_dien_lui_that_bai_khi_tra_loi_khong():
    ket_qua = backward.suy_dien_lui("dao_on", hoi_nguoi_dung=lambda _cau_hoi: False)
    assert not ket_qua.thanh_cong
    assert ket_qua.benh is None


def test_suy_dien_lui_dung_gia_thiet_thay_cho_hoi():
    ket_qua = backward.suy_dien_lui(
        "bac_la", gia_thiet=["tc_chop_la_kho", "tc_vien_la_nau"]
    )
    assert ket_qua.thanh_cong
    assert ket_qua.benh == "bac_la"
    assert ket_qua.cau_hoi == []


# ------------------------------------------------------------------ mạng Bayes
def test_bang_cpd_hop_le():
    bayes.kiem_tra_cpd()


def test_mang_bayes_co_it_nhat_5_nut():
    assert len(bayes.NUT) >= 5


def test_bang_chung_lam_tang_xac_suat_dao_on():
    truoc = bayes.truy_van(None, su_dung_pgmpy=False)["xac_suat"]["dao_on"]
    bang_chung = {"tc_vet_thoi": 1.0, "tt_am_do_cao": 1.0, "tq_dam_cao": 1.0}
    sau = bayes.truy_van(bang_chung, su_dung_pgmpy=False)["xac_suat"]["dao_on"]
    assert 0.0 <= truoc <= 1.0
    assert sau > truoc


def test_pgmpy_khop_voi_phep_liet_ke():
    pytest.importorskip("pgmpy")
    bang_chung = {"tc_dom_tron": 1.0, "tq_dat_ngheo": 1.0, "tt_kho_han": 1.0}
    liet_ke = bayes.truy_van(bang_chung, su_dung_pgmpy=False)
    pgmpy = bayes.truy_van(bang_chung, su_dung_pgmpy=True)
    assert pgmpy["phuong_phap"].startswith("pgmpy")
    for ma in ("dao_on", "bac_la", "dom_nau"):
        assert pgmpy["xac_suat"][ma] == pytest.approx(liet_ke["xac_suat"][ma], abs=1e-6)


def test_bang_chung_mau_thuan_bi_bo_qua():
    bang_chung, ghi_chu = bayes.bang_chung_bayes(["tt_am_do_cao", "tt_kho_han"])
    assert "ThoiTiet" not in bang_chung
    assert ghi_chu


# ------------------------------------------------------------------- kết hợp
def test_ket_hop_chon_dao_on():
    ket_qua = ket_hop.ket_hop(
        [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)],
        ["tc_vet_thoi", "tt_am_do_cao", "tq_dam_cao", "gd_de_nhanh"],
    )
    assert ket_qua.benh == "dao_on"
    assert len(ket_qua.xep_hang) == 4
    assert ket_qua.xep_hang[0][1] >= ket_qua.xep_hang[1][1]
    assert ket_qua.khuyen_nghi and ket_qua.nguon
    assert "CNN" in ket_qua.giai_thich


def test_ket_hop_cnn_manh_co_the_doi_ket_luan():
    ket_qua = ket_hop.ket_hop([("dom_nau", 0.95), ("dao_on", 0.03), ("bac_la", 0.02)])
    assert ket_qua.benh == "dom_nau"


def test_ket_hop_tu_choi_trong_so_sai():
    with pytest.raises(ValueError):
        ket_hop.ket_hop([("dao_on", 0.9)], trong_so={"cnn": 0.5, "luat": 0.5, "bayes": 0.5})


def test_ket_hop_tu_choi_ma_benh_la():
    with pytest.raises(ValueError):
        ket_hop.ket_hop([("benh_la", 0.9)])


def test_demo_chay_duoc(capsys):
    ket_hop.demo()
    noi_dung = capsys.readouterr().out
    assert "Kết luận" in noi_dung
    assert "đạo ôn" in noi_dung
    assert len(MA_BENH) == 4