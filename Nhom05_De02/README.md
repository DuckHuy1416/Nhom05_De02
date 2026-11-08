# Bác sĩ Lúa - Nhóm 5

Đồ án cuối kỳ học phần Trí tuệ nhân tạo (COMP1314), Khoa Công nghệ thông tin, Trường ĐH Sư phạm TP.HCM. Giảng viên: Võ Hoàng Quân.

Ứng dụng "Bác sĩ Lúa": nông dân chụp ảnh lá lúa, hệ thống nhận diện bệnh (CNN), hỏi thêm triệu chứng (hệ chuyên gia), đưa ra khuyến nghị và lập lộ trình cho drone phun thuốc đúng các ô ruộng bị bệnh.

## Thành viên

| Mã | Họ và tên | MSSV | Phụ trách chính |
|---|---|---|---|
| TV1 (nhóm trưởng) | Danh Đức Khánh Huy | 50.01.104.057 | Chức năng 1 - lộ trình drone |
| TV2 | Phạm Nguyễn Thái An | 50.01.104.002 | Chức năng 2 - hệ chuyên gia |
| TV3 | Nguyễn Phạm Phú An | 50.01.104.001 | Chức năng 2 - mạng Bayes, kết hợp CNN |
| TV4 | Lê Thế Bảo | 50.01.104.012 | Chức năng 3 - CNN |
| TV5 | Phan Phước Đông Triều | 50.01.104.168 | Chức năng 4 - ứng dụng tích hợp, Git |

## Cấu trúc thư mục

```
Nhom05_De02/
├── .git/               thư mục ẩn của Git (không xóa)
├── .gitignore          bỏ qua venv/, __pycache__/, dữ liệu lớn
├── README.md           thành viên, cài đặt, cách chạy, nguồn dữ liệu
├── requirements.txt    thư viện kèm phiên bản
├── demo.py             chạy Chức năng 1 - 3 trên dữ liệu mẫu
├── src/                mã nguồn
│   ├── search/         Chức năng 1: tìm kiếm
│   ├── rules/          Chức năng 2: tập luật, suy diễn
│   ├── model/          Chức năng 3: TensorFlow/Keras
│   └── app/            Chức năng 4: ứng dụng tích hợp
├── data/sample/        dữ liệu mẫu đủ để chạy demo.py
└── models/             mô hình đã huấn luyện (.keras)
```

## Cài đặt

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Python 3.10 - 3.11. Các phiên bản trong `requirements.txt` là dự kiến, cần cài thử và chỉnh lại khi có kết quả.

## Cách chạy

```bash
python demo.py                  # chạy Chức năng 1 - 3 trên dữ liệu mẫu
python -m src.app.main          # ứng dụng tích hợp (Chức năng 4) - chưa cài đặt
```

## Nguồn dữ liệu

Xem `data/sample/README.md`. Hiện tại: bộ ảnh lá lúa chưa chốt (khảo sát Kaggle, Mendeley Data); tri thức hệ luật lấy từ tài liệu khuyến nông chính thống và ghi nguồn trong từng luật.

## Quy ước làm việc

- Mỗi chức năng một nhánh Git, ghép qua pull request có người khác duyệt.
- Không tự đặt tên thuốc, liều lượng trong hệ chuyên gia.

## Tiến độ (Tuần 1)

Đã lập kế hoạch, phân công, mô hình hóa bài toán và dựng cấu trúc thư mục. Mã nguồn các chức năng bắt đầu từ Tuần 2.
