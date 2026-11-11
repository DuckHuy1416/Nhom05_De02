# Danh mục nguồn tri thức – Chức năng 2

Tài liệu này là bảng nguồn cho kho luật `src/rules/rules.json` (C1 – “Thu thập tài liệu
khuyến nông chính thống, lập bảng nguồn”). Mỗi luật trong kho đều có trường `nguon`
trỏ tới mã nguồn dưới đây; chương trình kiểm tra mã nguồn khi nạp kho
(`src/rules/chung.py::doc_kho_tri_thuc`).

## 1. Bảng nguồn

| Mã | Tài liệu | Cơ quan | Đường dẫn | Dùng cho |
|----|----------|---------|-----------|----------|
| S1 | Rice Knowledge Bank – *Blast (leaf and collar)* | IRRI | http://www.knowledgebank.irri.org/training/fact-sheets/pest-management/diseases/item/blast-leaf-collar | Triệu chứng đạo ôn (vết hình thoi/ổ mắt, tâm xám, viền nâu, quầng vàng); thời tiết ẩm, sương mù, nhiệt độ 20–28 °C; bón đạm cao, giống nhiễm; bệnh nặng ở mạ và giai đoạn làm đòng |
| S2 | Rice Knowledge Bank – *Bacterial blight* | IRRI | http://www.knowledgebank.irri.org/training/fact-sheets/pest-management/diseases/item/bacterial-blight | Triệu chứng bạc lá (vết chạy dọc gân từ chóp/mép, mép gợn sóng, giọt vi khuẩn buổi sáng); mưa nhiều, gió mạnh, ruộng ngập, đạm cao |
| S3 | Rice Knowledge Bank – *Brown spot* | IRRI | http://www.knowledgebank.irri.org/training/fact-sheets/pest-management/diseases/item/brown-spot | Triệu chứng đốm nâu (đốm tròn, tâm xám, viền nâu đỏ); đất nghèo dinh dưỡng/không ngập, thiếu kali–silicon, nắng mưa xen kẽ, giai đoạn chín |
| S4 | Rice Doctor – công cụ chẩn đoán bệnh lúa | IRRI | http://knowledgebank.irri.org/decision-tools/rice-doctor | Quy trình hỏi–đáp theo triệu chứng để phân biệt đạo ôn, bạc lá, đốm nâu; dùng cho luật phân biệt và câu hỏi của suy diễn lùi |
| S5 | Tài liệu bệnh hại lúa | Viện Nghiên cứu Lúa Đồng bằng sông Cửu Long (Đại học Cần Thơ) | https://lrc.ctu.edu.vn | Đặc điểm giai đoạn nhiễm bệnh, giống nhiễm, biện pháp canh tác phòng trừ tại ĐBSCL; dùng cho khuyến nghị |
| S6 | Hướng dẫn phòng trừ bệnh hại lúa | Cục Bảo vệ thực vật (Bộ NN&PTNT) | https://ppd.gov.vn | Nguyên tắc phòng trừ, điều tra đồng ruộng và nguyên tắc “4 đúng” khi dùng thuốc BVTV; dùng cho cảnh báo và khuyến nghị |

> S1–S4 là các trang công khai của IRRI, đã đối chiếu nội dung mô tả triệu chứng và
> điều kiện phát bệnh. S5–S6 là trang thông tin của cơ quan chuyên môn trong nước;
> nhóm cần mở đúng chuyên mục “bệnh hại lúa” khi trích dẫn số liệu cụ thể trong báo cáo,
> vì đường dẫn chi tiết có thể thay đổi theo thời điểm.

## 2. Nguyên tắc trích dẫn

- Mỗi luật ghi **ít nhất một mã nguồn**; luật suy ra kết luận bệnh thường dẫn 2 nguồn
  (một nguồn quốc tế + một nguồn trong nước).
- Nội dung luật chỉ mô tả **triệu chứng, điều kiện thời tiết, giai đoạn, tập quán canh tác
  và biện pháp canh tác**. Hệ thống **không tự đặt tên thuốc, hoạt chất hay liều lượng**;
  khuyến nghị luôn chuyển người dùng tới cán bộ bảo vệ thực vật địa phương khi cần dùng thuốc.
- Độ tin cậy `do_tin_cay` là ước lượng định tính từ mức độ đặc trưng của triệu chứng trong
  tài liệu, **không phải** tần suất thống kê. Khi có dữ liệu đồng ruộng, nhóm hiệu chỉnh và
  ghi lại ngày cập nhật trong `rules.json` (`cap_nhat`).

## 3. Quy trình cập nhật kho luật

1. Bổ sung nguồn mới vào mảng `nguon` của `rules.json` (mã tiếp theo S7, S8, …).
2. Thêm luật mới với mã L29, L30, …; khai báo `neu`, `thi`, `do_tin_cay`, `nguon`.
3. Chạy `python -m pytest tests/test_chuyen_gia.py -q` để kiểm tra mã sự kiện, mã nguồn,
   CPD mạng Bayes và các đường suy diễn.
4. Cập nhật bảng nguồn trong tài liệu này và mục “Nguồn tri thức” của báo cáo.

## 4. Khoảng trống cần bổ sung

- Chưa có nguồn tiếng Việt dạng PDF/QR cụ thể cho từng luật; nhóm cần lưu bản in hoặc ảnh
  chụp tài liệu khuyến nông địa phương kèm số hiệu văn bản.
- Chưa có dữ liệu thực nghiệm để hiệu chỉnh `do_tin_cay` và các bảng CPD của mạng Bayes.
- Bệnh khác (vàng lùn, lùn xoắn lá, ngộ độc phèn…) chưa đưa vào kho; cần bổ sung khi mở rộng.