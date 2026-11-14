# Tri thức hệ luật TV2

## Phạm vi và cách dùng

Bộ luật trong `src/rules/rules.json` có 24 luật dựa trên triệu chứng và yếu tố môi trường trong các nguồn dưới đây. Đây là dấu hiệu gợi ý phục vụ bài tập, không phải chẩn đoán xác định hay chỉ dẫn can thiệp. Nhiều bệnh và phi bệnh có biểu hiện gần nhau; khi dữ kiện chưa đủ, để kết quả chưa xác định và nhờ cán bộ chuyên môn kiểm tra. Không dùng việc thiếu một dấu hiệu để kết luận cây khỏe.

Trong schema, các điều kiện trong `nếu` kết hợp bằng AND. Mã sự kiện là quy ước máy đọc được, không khẳng định một triệu chứng tự nó xác nhận bệnh. Các kết quả `goi_y_*`, `can_xem_xet_*` và `dieu_kien_*` phải được diễn giải riêng biệt.

## Bảng nguồn

| Mã | Tài liệu và đơn vị | Phần dùng | Phạm vi |
|---|---|---|---|
| S1 | Trung tâm Khuyến nông Quốc gia, “Phòng trừ bệnh đạo ôn hại lúa”, cập nhật 20/08/2021. [Trang tài liệu](https://khuyennongvn.gov.vn/khoa-hoc-cong-nghe/khcn-trong-nuoc/phong-tru-benh-dao-on-hai-lua-21414.html) | Mục 1: lá, cổ lá, đốt thân, cổ bông; mục 2: thời tiết, thiếu nước, sạ dày, thừa đạm. | Nguồn Việt Nam cho đạo ôn. |
| S2 | Đại học Nông nghiệp Tamil Nadu (TNAU), Trung tâm Nghiên cứu Bảo vệ cây trồng, “Bệnh bạc lá vi khuẩn trên lúa” (*Bacterial leaf blight*). [Trang HTML](https://www.agritech.tnau.ac.in/expert_system/paddy/cpdisblb.html) | Mục Triệu chứng: héo cây mạ; vết úng nước đến vàng chạy từ chóp lá, có mép lượn sóng; vùng bệnh chuyển vàng/trắng; dịch vi khuẩn trên vết non. | Nguồn hướng dẫn kỹ thuật của đại học; chỉ dùng mô tả triệu chứng, không dùng phần xử lý. |
| S3 | Viện Nghiên cứu và Phát triển Lúa, Bộ Nông nghiệp Sri Lanka, “Bệnh đốm nâu” (*Brown Spot*). [Trang tài liệu](https://doa.gov.lk/rrdi_ricediseases_brownspot/) | Triệu chứng; bộ phận cây và giai đoạn sinh trưởng bị ảnh hưởng. | Đốm nâu trên mạ, lá, bẹ, bông/vỏ trấu và giai đoạn cây trưởng thành. |
| S4 | Chương trình Quản lý dịch hại tổng hợp toàn bang California, Đại học California, “Bệnh đạo ôn lúa” (*Rice Blast*). [Trang tài liệu](https://ipm.ucanr.edu/agriculture/rice/rice-blast/) | Triệu chứng; thông tin về bệnh. | Đối chiếu hình dạng vết đạo ôn, cổ lá, đốt và cổ bông. |

Ngày đối chiếu trực tuyến: 12/11/2026. Mỗi luật ghi mã nguồn và mục cụ thể; bảng này ánh xạ tới cơ quan, tài liệu, URL để kiểm tra. Nguồn chưa được chuyên gia địa phương duyệt; cần nhờ cán bộ bảo vệ thực vật rà soát trước khi dùng thực tế.

## Ma trận bệnh × thông tin

| Bệnh / nhóm thông tin | Dấu hiệu hoặc yếu tố mô hình hóa | Luật | Nguồn |
|---|---|---|---|
| Đạo ôn – lá | vết hình thoi; tâm xám khô; viền nâu | DO01–DO03 | S1, S2, S4 |
| Đạo ôn – cổ lá, thân, bông | cổ lá nâu đỏ; đốt teo nâu; cổ bông thối nâu; bông lép trắng sớm (chỉ xem xét) | DO04–DO07 | S1, S4 |
| Đạo ôn – điều kiện thuận lợi | âm u/sương; thiếu nước; sạ dày; thừa đạm | DO08–DO11 | S1, S4 |
| Bạc lá – mép và diễn tiến vết | vết úng nước; vệt kéo dài từ chóp; màu vàng/trắng khi bệnh tiến triển; mép lượn sóng | BL01–BL04 | S2 |
| Bạc lá – héo | héo lá/cây non, chỉ là dấu hiệu cần xem xét | BL05 | S2 |
| Đốm nâu – hình dạng/màu | đốm tròn/bầu dục; viền sẫm; tâm nhạt/xám | DN01–DN03 | S3 |
| Đốm nâu – vị trí/giai đoạn | bao tử; lá già; vỏ trấu; mạ mọc kém cùng đốm bao tử | DN04–DN08 | S3 |

## Ánh xạ và giới hạn diễn giải

- `DO01`–`DO07`, `BL01`–`BL05`, `DN01`–`DN08`: mã điều kiện mô tả một đặc điểm theo nguồn. Luật đơn triệu chứng chỉ sinh gợi ý.
- `DO08`–`DO11`: yếu tố thuận lợi là ngữ cảnh nguy cơ, không phải bằng chứng cây đang mắc bệnh.
- `can_xem_xet_*` dùng cho dấu hiệu kém đặc hiệu; không gộp với gợi ý triệu chứng khi giải thích.
- Bộ luật chưa bao phủ mọi bệnh, thiếu dữ liệu địa phương và chưa đo độ chính xác; không báo cáo hiệu năng hay độ tin cậy định lượng.

## Câu hỏi Q4 và nội dung báo cáo

### Q4 – Vì sao phải truy vết luật và nguồn?

Hệ chuyên gia dùng điều kiện triệu chứng để suy ra gợi ý. Người dùng cần biết gợi ý dựa trên dấu hiệu nào, luật nào đã khớp và tài liệu nào hỗ trợ dấu hiệu đó. Truy vết id luật và nguồn giúp kiểm tra lại, phát hiện luật áp dụng sai phạm vi, cập nhật tri thức khi nguồn thay đổi và tránh trình bày suy luận như kết luận chắc chắn. Nguồn trong JSON trỏ tới bảng nguồn này; khả năng truy vết không đồng nghĩa chuyên gia đã chứng thực nội dung.

### Đoạn đưa vào chương “Tri thức, luật”

Cơ sở tri thức được biểu diễn thành các luật IF–THEN. Mỗi luật có mã duy nhất, danh sách điều kiện kết hợp bằng AND, sự kiện kết luận, nguồn và ghi chú phạm vi. TV2 xây dựng 24 luật gợi ý nhận diện đạo ôn, bạc lá và đốm nâu từ tài liệu của Trung tâm Khuyến nông Quốc gia, IRRI và cơ quan nông nghiệp Sri Lanka. Luật mô tả triệu chứng và một số điều kiện thuận lợi; không chứa tên thuốc hay liều lượng. Bộ suy diễn tiến lặp đến khi không phát sinh sự kiện mới; bộ suy diễn lùi lần theo các luật có thể chứng minh mục tiêu, hỏi người dùng khi thiếu dữ kiện và không xem câu trả lời chưa biết là phủ định. Kết quả lưu id luật và nguồn để giải thích. Vì triệu chứng có thể chồng lấp và bộ luật chưa được thẩm định thực địa, kết quả chỉ là gợi ý, không thay thế cán bộ chuyên môn.

## Kiểm tra và cập nhật

Chạy `python -m scripts.check_rules` để kiểm tra schema, id, nguồn và dấu hiệu nội dung bị cấm. Tự động hóa không chứng minh URL còn tồn tại hoặc nguồn thực sự hỗ trợ luật; việc đó cần đối chiếu thủ công. Khi sửa luật, cập nhật bảng nguồn, ma trận, ghi chú phạm vi và kiểm thử. Không thêm tri thức từ suy đoán, không đưa tên thuốc/hoạt chất/liều vào các trường luật.
