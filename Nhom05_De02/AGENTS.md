# Hướng dẫn cho thành viên và AI

## Mục tiêu và phạm vi
Chuẩn bị đồ án COMP1314 Bác sĩ Lúa, nhóm 5 người. Đọc README mục 7,
`docs/interfaces.md` và `docs/mo_hinh_bai_toan.md` trước khi sửa giao tiếp.
Khung ban đầu chưa cài thuật toán. Chỉ triển khai khi được giao rõ ràng.
Tài liệu, docstring và comment bằng tiếng Việt; mã hóa UTF-8.

## Lệnh từ thư mục Nhom05_De02
Dùng Python 3.10 hoặc 3.11. Tạo môi trường bằng `python -m venv .venv`;
kích hoạt theo hướng dẫn đa nền tảng trong README.
- Cài chức năng: `python -m pip install -r requirements.txt`
- Cài công cụ: `python -m pip install -r requirements-dev.txt`
- Kiểm thử: `python -m pytest`
- Kiểm tra mã: `ruff check .` hoặc `python -m ruff check .`
- Kiểm tra luật: `python -m scripts.check_rules`
- Chạy khung: `python demo.py`
Các điểm vào `python -m src.*` là khung, chưa có CLI chức năng.

## Phụ trách và định nghĩa xong
| Module | Người | Xong khi |
|---|---|---|
| `src/search/` CN1 | TV1 | A* đúng so với BFS; leo đồi/beam và tham lam tự cài; thỏa thuốc/pin, phun hết và về trạm; so sánh có dữ liệu, mô tả mô hình; Q1 |
| `src/rules/` hệ luật CN2 | TV2 | ≥20 luật có nguồn đã duyệt, tiến/lùi tự cài, giải thích truy được luật/nguồn; kiểm tra luật và test đạt; báo cáo, Q4 |
| `src/rules/bayes.py`, `ket_hop.py`, thời tiết | TV3 | Bayes ≥5 nút, CPT có căn cứ, kết hợp đúng hợp đồng; ≥20 ảnh thực tế ghi nguồn; test và Q2 |
| `src/model/` CN3 | TV4 | CNN tự thiết kế và transfer learning, dữ liệu/giấy phép ghi rõ; accuracy/precision/recall/F1 và ma trận nhầm lẫn từ chạy thật; xuất .keras, predict_top3 thật; Q3 |
| `src/app/` CN4 và đóng gói | TV5 | Luồng tích hợp và hoạt cảnh chạy được; xử lý trạng thái chưa có mô hình; demo/test/lint đạt, README/slide và gói nộp đủ |
TV1 quản lý hồ sơ và nộp bài; TV5 quản lý Git/README theo phân công gốc.

## Quy tắc cứng
- A*, leo đồi/beam, suy diễn tiến/lùi phải tự cài; không gọi thư viện làm thay.
- Không có tên thuốc hoặc liều lượng trong luật, kể cả ghi chú.
- Mỗi luật phải có `nguon`; không bịa luật, nguồn hay kết quả thực nghiệm.
- Không commit dữ liệu ảnh, trọng số, khóa API; không đọc `.env`.
- Mã lớp chung: `dao_on`, `bac_la`, `dom_nau`, `la_khoe`.
- Không sửa/xóa test để cho qua; không thêm bỏ qua để che lỗi.
- Test thuật toán hiện có xfail `chưa cài đặt`; khi làm xong bỏ dấu xfail
  tương ứng trong cùng thay đổi. XPASS là lỗi để nhắc cập nhật trạng thái.
- Commit có tiền tố như `[CN1] …`, `[CN2] …`, `[CN3] …`, `[CN4] …`.
- Không đổi giao tiếp đơn phương; cập nhật docs, bên gọi và test cùng lúc.
- `predict_top3` hiện là giả: kiểm tra `IS_STUB`, không dùng số giả trong báo cáo.
- k là số ô phun, p là số bước bay; mức bệnh không nhân số lần phun.
- Chỉ tuyên bố xong sau khi demo/test/lint đạt, docs khớp mã, có người khác duyệt.
- Chỉ commit/push/tag khi người dùng cho phép; phiên dựng khung để chưa commit.
