# Bác sĩ Lúa

Ứng dụng giúp nông dân Đồng bằng sông Cửu Long phát hiện sớm bệnh trên lá lúa, nhận tư vấn xử lý và lập lộ trình cho drone phun thuốc đúng những ô ruộng bị bệnh.

Đồ án cuối kỳ – Học kỳ 1, năm học 2026 – 2027 · Thời gian thực hiện: 02/11 – 06/12/2026

> **Trạng thái:** bản đầu (Kiểm soát tiến độ lần 1). Mã nguồn đang được phát triển theo kế hoạch 5 tuần; các lệnh chạy bên dưới sẽ được cập nhật khi từng module hoàn thành.

---

## 1. Bài toán

Đồng bằng sông Cửu Long làm ra hơn một nửa sản lượng lúa cả nước. Mỗi vụ, bà con phải đối mặt với các bệnh như đạo ôn, bạc lá, đốm nâu; phát hiện muộn vài ngày có thể mất cả ruộng, trong khi cán bộ khuyến nông không thể có mặt ở mọi cánh đồng.

Luồng sử dụng của Bác sĩ Lúa:

1. Nông dân chụp ảnh lá lúa và tải lên ứng dụng.
2. Mô hình CNN nhận diện bệnh, trả về 3 bệnh có xác suất cao nhất.
3. Hệ chuyên gia hỏi thêm vài triệu chứng (suy diễn lùi) để xác nhận, rồi đưa ra kết luận kèm giải thích và khuyến nghị có ghi nguồn.
4. Người dùng đánh dấu các ô ruộng bị bệnh trên bản đồ lưới; hệ thống lập lộ trình drone và hiển thị hoạt cảnh từng bước.

## 2. Chức năng

| # | Chức năng | Kỹ thuật chính | Thư mục |
|---|-----------|----------------|---------|
| 1 | Lập lộ trình drone phun thuốc | Mô hình hóa không gian trạng thái; **tự cài đặt** A* cho từng chặng; leo đồi hoặc beam search chọn thứ tự ghé ô bệnh (TSP có ràng buộc nạp thuốc/pin); so sánh với chiến lược tham lam | `search/` |
| 2 | Hệ chuyên gia tư vấn và mạng Bayes | ≥ 20 luật lấy từ tài liệu khuyến nông chính thống; **tự cài đặt** suy diễn tiến và suy diễn lùi; mạng Bayes ≥ 5 nút bằng pgmpy | `expert/` |
| 3 | Nhận diện bệnh lá lúa | CNN tự thiết kế và transfer learning (MobileNetV2 hoặc EfficientNetB0) bằng TensorFlow/Keras; tăng cường dữ liệu; đánh giá accuracy, precision, recall, F1, ma trận nhầm lẫn | `cnn/` |
| 4 | Ứng dụng tích hợp | Giao diện tiếng Việt, bản đồ lưới, hoạt cảnh lộ trình (Pygame hoặc matplotlib) | `app/` |

**Phần mở rộng (không bắt buộc):** kết hợp xác suất CNN với mạng Bayes và thời tiết thực tế của tỉnh; lấy thời tiết từ API công khai để cảnh báo sớm nguy cơ đạo ôn; giao diện chữ to cho nông dân lớn tuổi.

**Liên hệ phần đọc sách giữa kỳ:** TSP (Example 4) → Chức năng 1 · Knowledge Representation (Ch.6) → Chức năng 2 · Machine Learning (Ch.10) → Chức năng 3.

## 3. Cấu trúc thư mục

```text
bac-si-lua/
├── app/                  # CN4 – ứng dụng tích hợp
│   ├── main.py           #   màn hình chính
│   ├── grid_editor.py    #   đánh dấu ô bệnh trên bản đồ lưới
│   ├── route_view.py     #   hoạt cảnh lộ trình drone
│   └── chan_doan.py      #   luồng chẩn đoán từ ảnh
├── search/               # CN1 – lưới, A*, tham lam, leo đồi/beam, thực nghiệm
│   ├── grid.py
│   ├── astar.py
│   ├── greedy.py
│   ├── order_opt.py
│   ├── run.py
│   └── experiment.py
├── expert/               # CN2 – luật, suy diễn tiến/lùi, mạng Bayes
│   ├── rules.json
│   ├── forward.py
│   ├── backward.py
│   ├── bayes.py
│   └── diagnose.py
├── cnn/                  # CN3 – dữ liệu, huấn luyện, đánh giá, dự đoán
│   ├── prepare_data.py
│   ├── custom_cnn.py
│   ├── transfer.py
│   ├── predict.py
│   └── notebooks/
├── data/
│   ├── maps/             # bản đồ lưới mẫu (.json)
│   ├── raw/              # bộ dữ liệu ảnh – KHÔNG đưa lên Git
│   └── anh_thuc_te/      # ≥ 20 ảnh chụp ngoài thực tế + nguon.csv
├── models/               # trọng số đã huấn luyện – KHÔNG đưa lên Git
├── docs/
│   ├── mo_hinh_bai_toan.md
│   ├── interfaces.md
│   ├── nguon_tri_thuc.md
│   ├── du_lieu.md
│   ├── cau_hoi/          # trả lời Q1 – Q4
│   └── ho_so_nhom/       # Mẫu 01 – 04
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## 4. Cài đặt

Khuyến nghị **Python 3.10 hoặc 3.11** để tương thích với TensorFlow.

```bash
git clone <link-repo>
cd bac-si-lua

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` (bản đầu; phiên bản cụ thể sẽ được cố định sau khi chạy thử trên máy các thành viên):

```text
tensorflow
pgmpy
numpy
pandas
matplotlib
scikit-learn
pillow
pygame
requests
pytest
```

- `scikit-learn` chỉ dùng để tính precision, recall, F1 và ma trận nhầm lẫn. A*, leo đồi/beam, suy diễn tiến và suy diễn lùi đều tự cài đặt, không dùng thư viện có sẵn.
- `requests` chỉ dùng cho phần mở rộng lấy thời tiết.
- Huấn luyện CNN nên chạy trên Google Colab hoặc Kaggle Notebook có GPU (xem `cnn/notebooks/`).

## 5. Dữ liệu và nguồn tri thức

- **Ảnh lá lúa:** bộ dữ liệu công khai (Kaggle, Mendeley Data), tối thiểu 4 lớp: đạo ôn, bạc lá, đốm nâu, lá khỏe. Đường dẫn tải và giấy phép ghi trong `docs/du_lieu.md`. Tải về và giải nén vào `data/raw/`.
- **Ảnh thực tế:** ≥ 20 ảnh tự chụp hoặc sưu tầm trong `data/anh_thuc_te/`; nguồn từng ảnh ghi trong `data/anh_thuc_te/nguon.csv`.
- **Tri thức cho hệ chuyên gia:** lấy từ tài liệu khuyến nông, bảo vệ thực vật chính thống; danh mục nguồn trong `docs/nguon_tri_thuc.md`. Mỗi luật ghi nguồn; hệ thống **không tự đặt tên thuốc hay liều lượng**.

## 6. Cách chạy (dự kiến)

```bash
# Ứng dụng tích hợp
python -m app.main

# CN1 – lập lộ trình trên bản đồ mẫu (k: số ô phun mỗi lần nạp, p: số bước pin tối đa)
python -m search.run --map data/maps/map_20x20_mau.json --k 5 --p 60 --algo hill
python -m search.experiment        # so sánh với tham lam trên nhiều bản đồ ngẫu nhiên

# CN2 – hệ chuyên gia và mạng Bayes (dòng lệnh)
python -m expert.forward
python -m expert.backward --goal dao_on
python -m expert.bayes

# CN3 – chuẩn bị dữ liệu, huấn luyện, dự đoán
python -m cnn.prepare_data
python -m cnn.custom_cnn
python -m cnn.transfer --base mobilenetv2
python -m cnn.predict --image duong/dan/anh_la_lua.jpg

# Kiểm thử
python -m pytest tests/
```

## 7. Quy ước dữ liệu giữa các module

Chi tiết trong `docs/interfaces.md`.

**Mã lớp bệnh** (dùng chung cho CNN, hệ luật, mạng Bayes): `dao_on` (đạo ôn), `bac_la` (bạc lá), `dom_nau` (đốm nâu), `la_khoe` (lá khỏe).

**Bản đồ lưới** (file JSON, kích thước thật tối thiểu 20 × 20; ví dụ dưới rút gọn 4 × 4 để minh họa):

```json
{
  "rows": 4,
  "cols": 4,
  "start": [0, 0],
  "k": 3,
  "p": 20,
  "cells": [
    [9,  0,  0, 2],
    [0, -1,  1, 0],
    [0, -1,  0, 3],
    [1,  0,  0, 0]
  ]
}
```

Mã ô: `0` lúa khỏe · `1`, `2`, `3` lúa bệnh theo mức · `-1` vật cản (kênh mương có cây cao, trụ điện) · `9` trạm nạp thuốc/đổi pin.

**Hàm giao tiếp chính:**

| Hàm | Module | Đầu ra |
|-----|--------|--------|
| `predict_top3(duong_dan_anh)` | `cnn/predict.py` | `[("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)]` |
| `diagnose(top3, hoi_nguoi_dung)` | `expert/diagnose.py` | kết luận, độ tin cậy, các luật đã dùng (giải thích), nguồn tài liệu |
| `plan_route(ban_do, k, p, thuat_toan)` | `search/run.py` | các ô đi qua, sự kiện phun/nạp, tổng quãng đường, số lần về trạm, thời gian chạy |

## 8. Thành viên và phân công

| Mã | Họ và tên | MSSV | Phụ trách |
|----|-----------|------|-----------|
| TV1 | … | … | **Nhóm trưởng** · CN1 – lập lộ trình drone; hồ sơ nhóm, nộp bài; Q1 |
| TV2 | … | … | CN2 – hệ chuyên gia (luật, suy diễn tiến/lùi); ghép báo cáo; Q4 |
| TV3 | … | … | CN2 – mạng Bayes, kết hợp CNN với Bayes; ảnh thực tế; mở rộng thời tiết; Q2 |
| TV4 | … | … | CN3 – mô hình CNN; Q3 |
| TV5 | … | … | CN4 – ứng dụng tích hợp; quản lý Git/README; slide, đóng gói code |

Phân công chi tiết: `docs/ho_so_nhom/` (Mẫu 01 – Kế hoạch và phân công công việc).

## 9. Kế hoạch và tiến độ

| Tuần | Thời gian | Nội dung chính | Mốc |
|------|-----------|----------------|-----|
| 1 | 02/11 – 08/11 | Mô hình hóa 3 bài toán, quy ước module, README, Mẫu 01 | **Kiểm soát lần 1 – 23h59 CN 08/11** |
| 2 | 09/11 – 15/11 | A*, tham lam; ≥ 20 luật, suy diễn tiến; dữ liệu, CNN tự thiết kế; khung ứng dụng | |
| 3 | 16/11 – 22/11 | Leo đồi/beam và so sánh; suy diễn lùi; mạng Bayes; transfer learning; hoạt cảnh | **Kiểm soát lần 2 – 23h59 CN 22/11** |
| 4 | 23/11 – 29/11 | Tích hợp ứng dụng; thử ≥ 20 ảnh thực tế; Q1 – Q4; phần mở rộng | |
| 5 | 30/11 – 06/12 | Báo cáo, slide, đóng gói code; Mẫu 03, 04 | **Nộp cuối kỳ – 23h59 CN 06/12** |

- [ ] Mô hình hóa bài toán, README bản đầu, Mẫu 01, Mẫu 02 Tuần 1
- [ ] CN1 chạy được: A*, tham lam, leo đồi/beam, bảng so sánh
- [ ] CN2 chạy được: ≥ 20 luật, suy diễn tiến, suy diễn lùi, mạng Bayes
- [ ] CN3: kết quả đánh giá 2 mô hình, thử ≥ 20 ảnh thực tế
- [ ] CN4: ứng dụng chạy đầu – cuối, có hoạt cảnh lộ trình
- [ ] Nộp báo cáo .docx, slide .pptx, code .zip

## 10. Quy ước làm việc với Git

- `main` chỉ chứa bản chạy được. Mỗi chức năng một nhánh: `cn1-tim-kiem`, `cn2-chuyen-gia`, `cn2-bayes`, `cn3-cnn`, `cn4-ung-dung`.
- Ghép vào `main` qua pull request, có ít nhất 1 thành viên khác duyệt.
- Commit nhỏ và thường xuyên, thông điệp có tiền tố chức năng, ví dụ: `[CN1] Thêm A* với heuristic Manhattan`.
- Không commit dữ liệu ảnh, trọng số mô hình, khóa API (đã khai báo trong `.gitignore`).

## 11. Lưu ý khi sử dụng

Kết quả của Bác sĩ Lúa **chỉ mang tính tham khảo**, không thay thế chẩn đoán và khuyến cáo của cán bộ khuyến nông, bảo vệ thực vật. Trước khi sử dụng thuốc, cần làm theo hướng dẫn trên nhãn và khuyến cáo của cơ quan chuyên môn địa phương.

## 12. Khai báo sử dụng AI và bản quyền

- Việc sử dụng AI tạo sinh trong quá trình thực hiện được khai báo trong Mẫu 04 (`docs/ho_so_nhom/`).
- Mã nguồn phục vụ mục đích học tập. Dữ liệu ảnh và tài liệu tham khảo thuộc về tác giả, cơ quan gốc; xem `docs/du_lieu.md` và `docs/nguon_tri_thuc.md`.
