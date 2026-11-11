# Biên bản dựng khung và kiểm chứng

Ngày 2026-11-11 (Asia/Saigon). Gốc repo thực tế là `Nhom05_De02/`.
Cây `src/search`, `src/rules`, `src/model`, `src/app` đã có từ commit ban đầu;
không có cây cũ để chuyển, nên không cần chạy `git mv`. Không tạo repo mới,
không xóa file của nhóm, không commit/push/tag. Thay đổi để chưa commit.

## Kết quả chạy thật

Môi trường kiểm chứng: Windows, Python 3.14.3, pytest 8.3.5, ruff 0.11.13.
Đây chỉ là kiểm chứng khung; môi trường chức năng yêu cầu Python 3.10/3.11.

- `python demo.py`: mã thoát 0, đọc bản đồ 4 × 4, in dự đoán GIẢ,
  CN1/CN2/Bayes/ứng dụng báo chưa cài đặt.
- `python -m pytest`: mã thoát 0; **14 passed, 12 xfailed**, thu thập 26 test.
  12 xfail: A* 4 trường hợp, hành trình/tài nguyên 3 thuật toán, đầu vào sai
  hoặc thiếu pin 2 trường hợp, suy diễn tiến/lùi 2, đủ ≥20 luật 1.
- `ruff check .`: mã thoát 0, `All checks passed!`.
- `python -m scripts.check_rules`: mã thoát 0; schema hợp lệ, **0 luật**,
  báo chưa đủ ít nhất 20 luật thật. Không có tuyên bố bộ tri thức đã hoàn thành.
- `git diff --check`: mã thoát 0.
- `python -m compileall -q src`: đạt, không cần import TensorFlow.

Lần chạy demo đầu thất bại vì pipe Windows dùng cp1252 không in được tiếng Việt.
Test subprocess tái hiện lỗi trước khi sửa; mã điểm vào đã cấu hình stdout/stderr
UTF-8, test và demo sau sửa đạt. Không bắt mọi lỗi để che lỗi chức năng.

Lệnh `ruff check .` ban đầu chưa tìm thấy executable trong PATH. Đã chạy bản
`python -m ruff check .` đạt, sau đó thêm thư mục Scripts của Python vào PATH
**chỉ trong tiến trình PowerShell kiểm chứng** và chạy đúng `ruff check .` đạt.
Không đổi PATH hệ thống. Trong venv đã kích hoạt, executable nằm trên PATH.

## Cài đặt và lệnh kiểm tra môi trường

- `python --version`, `py --list`, `python -m pip --version`:
  máy chỉ có Python 3.14.3; không có Python 3.10/3.11.
- `python -m pytest --version` trước khi cài: chưa có pytest.
- `python -m pip install -r requirements-dev.txt`: cài thành công
  pytest 8.3.5, ruff 0.11.13; dùng Python có sẵn, không đổi trình thông dịch.
- Đã dùng `git status --short`, `git ls-files`, `git log -1 --oneline`,
  `git diff --stat`, `git diff --check` để rà soát repo; không sửa Git index.
- Đã đối chiếu metadata chính thức trên PyPI cho
  [TensorFlow 2.16.1](https://pypi.org/project/tensorflow/2.16.1/) và
  [pgmpy 0.1.25](https://pypi.org/project/pgmpy/0.1.25/).
  TensorFlow yêu cầu NumPy >=1.23.5,<2 trên Python <=3.11; ghim 1.26.4 nằm
  trong khoảng này. pgmpy bản đã chọn không yêu cầu NumPy >=2.

## Chưa kiểm chứng

- Toàn bộ `requirements.txt` trên Python 3.10/3.11: **chưa cài thử**.
  Không cố cài TensorFlow 2.16.1 vào Python 3.14. Cần một thành viên tạo venv
  Python 3.10/3.11, cài cả hai file requirements, chạy kiểm tra và `pip check`.
- Chưa chạy macOS/Linux, chưa kiểm tra GPU, nạp/xuất .keras, mô hình hay dữ liệu thật.
- Chỉ ghim phụ thuộc trực tiếp, chưa khóa toàn bộ phụ thuộc bắc cầu.
- A*, tham lam, leo đồi/beam, suy diễn, Bayes, CNN và giao diện chưa cài đặt.
- Nguồn luật/dữ liệu, giấy phép, CPT và số liệu đánh giá chưa được nhóm cung cấp.
- Bộ kiểm tra luật là sàng lọc cấu trúc/từ khóa/đơn vị, không thể nhận biết mọi
  tên thương mại hoặc xác thực nội dung nguồn; TV2 phải duyệt thủ công từng luật.
- `.claude/settings.json` đã tạo cấu hình, chưa chạy thử trong Claude Code.

## Điểm nhóm cần xác nhận

1. Xác nhận với thầy cách hiểu k: hiện theo README, số ô phun mỗi lần nạp,
   mỗi ô bệnh chỉ tốn một đơn vị dù mức 1–3. Cảnh báo đặt trong mô hình bài toán.
2. Tên gốc giữ `Nhom05_De02` theo repo thực tế; TV5 kiểm tra quy định tên gói nộp.
3. Chính sách đã áp dụng: trọng số không lên Git; gói cuối kỳ kèm `.keras`
   hoặc link tải truy cập được. TV4/TV5 chốt tên file, nơi tải và thử đóng gói.
4. TV2 chốt nguồn tri thức; TV4 chốt bộ ảnh/giấy phép; nhóm điền tên/MSSV và
   tự ghi lịch sử dùng AI thật vào `docs/ho_so_nhom/ai_log.md`.

Đã thêm test hồi quy cho dấu phần trăm: test thất bại trước khi sửa biên regex,
sau sửa toàn bộ kiểm thử đạt như kết quả trên. `AGENTS.md` có 44 dòng (≤120);
JSON cấu hình Claude đã được parse hợp lệ.

## File tạo mới

- `.claude/settings.json`
- `.gitignore`
- `AGENTS.md`
- `data/anh_thuc_te/.gitkeep`
- `data/anh_thuc_te/nguon.csv`
- `data/sample/maps/map_4x4.json`
- `docs/cau_hoi/.gitkeep`
- `docs/du_lieu.md`
- `docs/ho_so_nhom/ai_log.md`
- `docs/interfaces.md`
- `docs/kiem_chung.md`
- `docs/mo_hinh_bai_toan.md`
- `docs/nguon_tri_thuc.md`
- `models/.gitkeep`
- `models/README.md`
- `pyproject.toml`
- `requirements-dev.txt`
- `scripts/__init__.py`
- `scripts/check_rules.py`
- `src/app/chan_doan.py`
- `src/contracts.py`
- `src/model/notebooks/.gitkeep`
- `src/model/predict.py`
- `src/model/prepare_data.py`
- `src/rules/diagnose.py`
- `src/search/experiment.py`
- `src/search/run.py`
- `tests/test_demo.py`
- `tests/test_predict.py`
- `tests/test_rules.py`
- `tests/test_search.py`

Thư mục `data/raw/` và `.gitkeep` trong đó chỉ tồn tại cục bộ, bị ignore đúng yêu cầu.

## File đã cập nhật

- `README.md`
- `data/sample/README.md`
- `demo.py`
- `requirements.txt`
- `src/__init__.py`
- `src/app/__init__.py`
- `src/app/grid_editor.py`
- `src/app/main.py`
- `src/app/route_view.py`
- `src/app/thoi_tiet.py`
- `src/model/__init__.py`
- `src/model/custom_cnn.py`
- `src/model/data_pipeline.py`
- `src/model/transfer.py`
- `src/rules/__init__.py`
- `src/rules/backward.py`
- `src/rules/bayes.py`
- `src/rules/forward.py`
- `src/rules/ket_hop.py`
- `src/search/__init__.py`
- `src/search/astar.py`
- `src/search/greedy.py`
- `src/search/grid.py`
- `src/search/order_opt.py`

## File di chuyển

Không có. Cấu trúc vật lý đã đúng; chỉ README mô tả cây cũ.
