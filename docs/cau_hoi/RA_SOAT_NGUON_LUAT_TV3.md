# Ghi chú rà soát chéo nguồn luật – TV3

**Phạm vi:** rà soát cấu trúc tham chiếu nguồn trong `src/rules/rules.json` và bảng nguồn `docs/nguon_tri_thuc.md` do TV2 bàn giao. Tài liệu này không sửa các file của TV2.

## 1. Kết quả kiểm tra cấu trúc

- Tổng số luật: 28.
- Số mã nguồn được khai báo: 6 (S1, S2, S3, S4, S5, S6).
- Luật không có trường nguồn: 0.
- Tham chiếu mã nguồn không tồn tại: 0.
- Tất cả 28 luật đều có ít nhất một mã nguồn nằm trong danh mục nguồn hiện tại.

### Số luật tham chiếu theo mã nguồn

| Mã nguồn | Số lượt luật tham chiếu |
|---|---:|
| S1 | 11 |
| S2 | 7 |
| S3 | 9 |
| S4 | 4 |
| S5 | 9 |
| S6 | 6 |

## 2. Nhận xét theo nhóm nguồn

- **S1 – IRRI, Blast (leaf and collar):** được dùng cho các luật liên quan đạo ôn; bảng nguồn mô tả triệu chứng vết hình thoi, điều kiện ẩm và bón đạm. Cần bảo đảm từng luật chỉ khẳng định đúng nội dung mà tài liệu nêu.
- **S2 – IRRI, Bacterial blight:** dùng cho nhóm bạc lá; đối chiếu các luật về vết bệnh dọc gân, giọt vi khuẩn, mưa/gió và đạm.
- **S3 – IRRI, Brown spot:** dùng cho nhóm đốm nâu; đối chiếu đốm tròn, điều kiện dinh dưỡng và thời tiết.
- **S4 – IRRI, Rice Doctor:** phù hợp làm nguồn tham khảo quy trình phân biệt triệu chứng/hỏi đáp; không nên dùng thay cho nguồn kỹ thuật chuyên biệt khi luật nêu một khẳng định bệnh học cụ thể.
- **S5 – Viện Nghiên cứu Lúa ĐBSCL/ĐH Cần Thơ:** đường dẫn hiện tại trong bảng nguồn là trang cấp cơ quan (`https://lrc.ctu.edu.vn`), chưa chỉ đến tài liệu cụ thể.
- **S6 – Cục Bảo vệ thực vật:** đường dẫn hiện tại (`https://ppd.gov.vn`) là trang cấp cơ quan, chưa chỉ đến văn bản hoặc trang hướng dẫn cụ thể.

## 3. Các điểm cần TV2 bổ sung

1. Với các luật tham chiếu S5/S6, cung cấp tên tài liệu, số hiệu văn bản hoặc URL bài viết cụ thể và trang/mục liên quan.
2. Với mỗi luật có nhiều nguồn, ghi rõ nguồn nào hỗ trợ triệu chứng, nguồn nào hỗ trợ điều kiện phát bệnh hoặc khuyến nghị.
3. Giữ rõ phân biệt giữa nội dung được tài liệu nêu trực tiếp và suy luận/ước lượng của nhóm.
4. Không biến độ tin cậy định tính trong luật thành tần suất thống kê. Không đưa tên thuốc, hoạt chất hoặc liều lượng nếu nguồn không cung cấp và không có xác nhận chuyên môn.

## 4. Kết luận rà soát

**Đạt về cấu trúc tham chiếu:** 28/28 luật có mã nguồn hợp lệ trong danh mục S1–S6.

**Chưa thể xác nhận đầy đủ độ chính xác nội dung từng luật chỉ từ kiểm tra cấu trúc:** cần đối chiếu từng phát biểu với nội dung tài liệu gốc. Đặc biệt, S5 và S6 cần đường dẫn/tài liệu cụ thể hơn trước khi chốt báo cáo.

Đây là rà soát kỹ thuật dựa trên các file TV2 bàn giao, không phải xác nhận độc lập về hiệu lực hiện hành của toàn bộ khuyến cáo nông nghiệp.
