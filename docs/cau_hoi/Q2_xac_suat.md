# Q2 – Mạng Bayes và kết hợp xác suất CNN

## 1. Mục tiêu

Trong hệ thống Bác sĩ Lúa, CNN phân tích ảnh lá lúa và trả về ba lớp bệnh có xác suất cao nhất. Mạng Bayes khai thác thêm thông tin về thời tiết, lượng đạm, giống lúa, dinh dưỡng đất và triệu chứng để tính xác suất hậu nghiệm của từng bệnh. Phần mở rộng C6 kết hợp hai nguồn xác suất nhằm đưa ra thứ hạng dự đoán có xét cả ảnh và bối cảnh ruộng.

Các mã lớp dùng thống nhất trong chương trình:

| Mã | Nhãn |
|---|---|
| `dao_on` | Đạo ôn |
| `bac_la` | Bạc lá |
| `dom_nau` | Đốm nâu |
| `la_khoe` | Lá khỏe |

## 2. Mô hình mạng Bayes C5

Mạng Bayes được triển khai trong `src/rules/bayes.py` với 8 nút:

- `ThoiTiet`: mưa ẩm hoặc khô.
- `BonDam`: bón đạm cao hoặc thấp.
- `Giong`: giống nhiễm hoặc giống kháng.
- `DinhDuong`: dinh dưỡng đất đủ hoặc thiếu.
- `DaoOn`: có hoặc không có bệnh đạo ôn.
- `BacLa`: có hoặc không có bệnh bạc lá.
- `DomNau`: có hoặc không có bệnh đốm nâu.
- `TrieuChung`: vết thoi, chóp lá khô, đốm tròn hoặc không có triệu chứng.

Cấu trúc phụ thuộc:

```text
ThoiTiet ─────┬────────> DaoOn ──────┐
BonDam ───────┤                      │
Giong ────────┘                      │
                                    ├──> TrieuChung
ThoiTiet ───────────────> BacLa ─────┤
BonDam ─────────────────>           │
                                    │
DinhDuong ──────────────> DomNau ────┘
ThoiTiet ───────────────> 
```

Mỗi nút có tập trạng thái rời rạc và bảng xác suất có điều kiện (CPD). Với nút có cha, mỗi cột CPD ứng với một tổ hợp trạng thái của các nút cha. Tổng xác suất của các trạng thái trong từng cột phải bằng 1.

Mã nguồn định nghĩa CPD trong biến `NUT`, kiểm tra tính đầy đủ và tổng xác suất bằng `kiem_tra_cpd()`, dựng mô hình pgmpy bằng `xay_dung_mang_pgmpy()` và truy vấn bằng `VariableElimination`.

### Giới hạn dữ liệu CPD

Các giá trị CPD hiện tại là ước lượng định tính phục vụ mô hình hóa, dựa trên mô tả điều kiện phát bệnh trong tài liệu IRRI S1–S3 mà nhóm TV2 liệt kê. Đây chưa phải tần suất thống kê hoặc xác suất đã hiệu chuẩn từ dữ liệu đồng ruộng. Báo cáo phải ghi rõ giới hạn này; không diễn giải các giá trị thành tỷ lệ mắc bệnh thực tế.

## 3. Truy vấn xác suất hậu nghiệm

Theo định lý Bayes:

\[
P(H\mid E)=\frac{P(E\mid H)P(H)}{P(E)}
\]

Trong mạng nhiều nút, xác suất hậu nghiệm được tính bằng cách tổng hợp các trạng thái ẩn phù hợp với bằng chứng quan sát. Chương trình dùng `VariableElimination` của pgmpy. Nếu pgmpy chưa cài hoặc phát sinh lỗi tương thích, module có phép liệt kê toàn bộ phân phối đồng thời làm phương án dự phòng và ghi rõ phương pháp thực tế đã sử dụng.

Ví dụ chạy:

```bash
python -m src.rules.bayes
python -m src.rules.bayes --bang-chung tc_vet_thoi tt_am_do_cao tq_dam_cao
```

Các mã sự kiện được ánh xạ sang nút Bayes thông qua `ANH_XA_BANG_CHUNG`. Sự kiện không có nút tương ứng được bỏ qua và ghi chú, thay vì tự suy diễn thành một bằng chứng khác.

## 4. C6 – Kết hợp xác suất CNN và Bayes

### 4.1. Chuẩn hóa đầu vào

CNN trả về top-3 trên bốn lớp. Vì chỉ có ba lớp xuất hiện trong danh sách, chương trình gán phần xác suất còn lại cho lớp thứ tư bị lược khỏi top-3. Phân phối Bayes cũng được chuẩn hóa về tổng bằng 1 trước khi kết hợp.

### 4.2. Công thức kết hợp

Chương trình sử dụng trung bình có trọng số:

\[
P_{\text{ket\_hop}}(B_i)
= w_{\text{CNN}}P_{\text{CNN}}(B_i)
+ w_{\text{Bayes}}P_{\text{Bayes}}(B_i)
\]

với:

\[
w_{\text{CNN}}=0.6,\quad w_{\text{Bayes}}=0.4,\quad
w_{\text{CNN}}+w_{\text{Bayes}}=1
\]

Trọng số là tham số kỹ thuật ban đầu để minh họa tích hợp, chưa được tối ưu bằng tập kiểm định. Có thể thay đổi khi có kết quả đánh giá thực nghiệm.

### 4.3. Ví dụ minh họa phép tính

Giả sử đầu ra CNN:

| Lớp | CNN |
|---|---:|
| Đạo ôn | 0.55 |
| Đốm nâu | 0.40 |
| Bạc lá | 0.03 |
| Lá khỏe | 0.02 |

Giả sử một lần truy vấn mạng Bayes cho phân phối đã chuẩn hóa minh họa:

| Lớp | Bayes |
|---|---:|
| Đạo ôn | 0.50 |
| Bạc lá | 0.20 |
| Đốm nâu | 0.20 |
| Lá khỏe | 0.10 |

Khi đó:

- Đạo ôn: \(0.6(0.55)+0.4(0.50)=0.53\).
- Bạc lá: \(0.6(0.03)+0.4(0.20)=0.098\).
- Đốm nâu: \(0.6(0.40)+0.4(0.20)=0.32\).
- Lá khỏe: \(0.6(0.02)+0.4(0.10)=0.052\).

Tổng bằng 1. Kết quả xếp hạng là đạo ôn (53%), đốm nâu (32%), bạc lá (9.8%), lá khỏe (5.2%).

**Các xác suất Bayes trong ví dụ này chỉ là số giả định để minh họa phép tính.** Khi báo cáo kết quả chạy chương trình, phải thay bằng giá trị thật do `truy_van()` trả về.

### 4.4. Cách chạy C6

```bash
python -m src.rules.ket_hop
python -m src.rules.ket_hop --top3 dao_on:0.55,dom_nau:0.40,bac_la:0.03
```

Khi tích hợp với TV4, truyền trực tiếp danh sách đầu ra từ hàm `predict_top3(duong_dan_anh)` vào `ket_hop_cnn_bayes()`. Không sử dụng ví dụ top-3 mặc định làm kết quả thực nghiệm.

### 4.5. Giới hạn phương pháp

Trung bình có trọng số là phương pháp kết hợp heuristic, không phải suy luận Bayes đầy đủ. CNN và mạng Bayes có thể sử dụng các thông tin tương quan (ví dụ triệu chứng trên ảnh cũng xuất hiện trong bằng chứng người dùng), nên có nguy cơ đếm trùng bằng chứng. Trọng số cần được đánh giá trên tập validation độc lập; không được chọn chỉ để tạo ra kết quả mong muốn.

## 5. F2 – Thời tiết thực tế làm bằng chứng cho mạng Bayes

Module `src/app/thoi_tiet.py` gọi Open-Meteo để lấy nhiệt độ, độ ẩm, lượng mưa, tốc độ gió và mã thời tiết hiện tại. Dữ liệu được ánh xạ sang mã sự kiện mà `bayes.py` đã định nghĩa, ví dụ `tt_am_do_cao`, `tt_mua_nhieu`, `tt_kho_han`.

Các ngưỡng chuyển đổi trong mã là quy ước kỹ thuật minh họa để rời rạc hóa dữ liệu liên tục; không phải ngưỡng bệnh học chính thức. Thời tiết chỉ là bằng chứng bối cảnh, không đủ để kết luận ruộng nhiễm bệnh.

Chạy:

```bash
python -m src.app.thoi_tiet --place "Can Tho"
# hoặc
python -m src.app.thoi_tiet --lat 10.045 --lon 105.746
```

## 6. Kết luận

C5 cung cấp phân phối hậu nghiệm dựa trên các yếu tố thời tiết, canh tác, giống, dinh dưỡng và triệu chứng. C6 kết hợp phân phối đó với dự đoán ảnh từ CNN. F2 bổ sung thời tiết thực tế làm bằng chứng cho mạng Bayes. Hệ thống hỗ trợ sàng lọc và giải thích, không thay thế việc kiểm tra đồng ruộng hoặc tư vấn của cán bộ bảo vệ thực vật.
