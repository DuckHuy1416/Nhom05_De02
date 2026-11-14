# Giao tiếp giữa các module

Python 3.10/3.11; tọa độ `(hàng, cột)` bắt đầu từ 0. Kiểu chuẩn nằm trong
`src/contracts.py`. Tọa độ JSON là mảng; tọa độ trong kết quả Python là tuple.

## 1. Nhận diện: TV4 → TV2/TV3/TV5

```python
from pathlib import Path
from src.contracts import Top3

def predict_top3(duong_dan_anh: str | Path) -> Top3: ...
```

Module `src/model/predict.py`. Trả đúng 3 tuple `(mã_lớp, xác_suất)`, nhãn không
trùng, xác suất hữu hạn trong [0,1], sắp giảm dần. Tổng top 3 ≤1 vì còn lớp thứ tư.
Mã lớp: `dao_on`, `bac_la`, `dom_nau`, `la_khoe`.

Ví dụ **GIẢ**, chạy được với khung và không đọc ảnh:

```python
from src.model.predict import IS_STUB, predict_top3
assert IS_STUB is True
predict_top3("anh_chua_ton_tai.jpg")
# [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)]
```

Không dùng số giả để xác nhận bệnh hay báo cáo độ chính xác. TV4 thay hàm,
đặt `IS_STUB=False`, giữ hợp đồng và bổ sung test với ảnh/mô hình thực.
Bản thật dự kiến ném `FileNotFoundError` nếu thiếu ảnh/mô hình, `ValueError`
nếu ảnh hỏng. Bản giả hiện không kiểm tra các lỗi này.

## 2. Chẩn đoán: TV2 → TV5

```python
from src.contracts import ChanDoan, HoiNguoiDung, Top3

def diagnose(top3: Top3, hoi_nguoi_dung: HoiNguoiDung) -> ChanDoan: ...
```

Module `src/rules/diagnose.py`. Callback `(câu_hỏi: str) -> bool | None`:
True = có, False = không, None = chưa biết. Không xem chưa biết là phủ định.
Đầu ra gồm `ket_luan` (mã lớp hoặc None), `do_tin_cay` ([0,1] hoặc None),
`luat_da_dung` (list id), `nguon` (list chuỗi trích nguồn).
Không tự gán độ tin cậy nếu chưa có phương pháp định lượng.

Ví dụ hợp đồng **chưa chạy được**:

```python
diagnose([("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)],
         lambda cau_hoi: None)
# Hiện: raise NotImplementedError("chưa cài đặt")
# Hình dạng kết quả bản thật khi chưa đủ dữ kiện:
# {"ket_luan": None, "do_tin_cay": None, "luat_da_dung": [], "nguon": []}
```

Đầu vào sai dự kiến ném `ValueError`. Kết luận, luật và nguồn trong báo cáo
phải từ tri thức đã kiểm chứng, không từ ví dụ ký hiệu của test.

## 3. Lộ trình: TV1 → TV5

```python
from src.contracts import BanDo, LoTrinh, ThuatToan

def plan_route(ban_do: BanDo, k: int, p: int, thuat_toan: ThuatToan) -> LoTrinh: ...
```

Module `src/search/run.py`; thuật toán là `hill`, `beam` hoặc `greedy`.
k,p truyền vào ưu tiên hơn giá trị mặc định trong JSON. Không sửa bản đồ đầu vào.
Đầu vào sai hoặc không có hành trình hoàn tất dự kiến ném `ValueError`.
Hiện hàm luôn ném `NotImplementedError`.

Ví dụ hợp đồng **chưa chạy được**, trường hợp hình thức không có ô bệnh:

```python
ban_do = {"rows": 1, "cols": 1, "start": [0, 0], "k": 1, "p": 2, "cells": [[9]]}
plan_route(ban_do, 1, 2, "hill")
# Hiện: raise NotImplementedError("chưa cài đặt")
# Kết quả hình thức mong đợi khi được triển khai:
# {"duong_di": [(0, 0)], "su_kien": [], "tong_quang_duong": 0,
#  "so_lan_ve_tram": 0, "thoi_gian_chay": <số giây đo thực tế>}
```

`duong_di` gồm ô bắt đầu và đích từng bước bay, giữ cả ô lặp lại.
`su_kien` theo thứ tự thực thi, mỗi phần tử có `loai` và `vi_tri`:

```python
# Minh họa định dạng, không phải hành trình đã tính:
{"loai": "bay", "vi_tri": (0, 1)}
{"loai": "phun", "vi_tri": (0, 1)}
{"loai": "nap", "vi_tri": (0, 0)}
```

Bay tới ô kề 4 hướng; phun/nạp tại vị trí hiện tại. Ban đầu đã đủ thuốc/pin nên
không cần nạp đầu. `tong_quang_duong` bằng số sự kiện bay. `so_lan_ve_tram` đếm
mỗi bước bay đáp xuống ô 9, kể cả lần về cuối; không tính vị trí đầu hoặc nạp
đứng yên. `thoi_gian_chay` là giây đo thật ≥0. Xem `mo_hinh_bai_toan.md` về an toàn.

## 4. Schema bản đồ JSON

Đối tượng gồm `rows`, `cols` nguyên dương, `start` là [hàng,cột], `k`, `p`
nguyên dương và `cells` là ma trận số nguyên rows × cols. Không nhận boolean
thay cho số nguyên. start trong lưới và phải là trạm. Cho phép nhiều trạm.

- 0: lúa khỏe.
- 1, 2, 3: mức bệnh; mỗi ô chỉ cần phun một lần.
- −1: vật cản, không được bay qua.
- 9: trạm nạp thuốc và pin.

Ví dụ đầy đủ: `data/sample/maps/map_4x4.json`, chép bản minh họa README,
không phải khảo sát ruộng thật. Bản đồ đánh giá chính thức tối thiểu 20 × 20;
lưới nhỏ chỉ phục vụ test/demo. TV1 cài kiểm tra schema và khả thi.

## 5. Schema rules.json

File `src/rules/rules.json` có đối tượng gốc:

```json
{"_ghi_chu": "Mô tả trạng thái bộ luật", "rules": []}
```

`_ghi_chu` là chú thích tùy chọn; `rules` là danh sách. Mỗi luật có đúng:

- `id`: chuỗi không rỗng, duy nhất.
- `nếu`: danh sách không rỗng các chuỗi sự kiện, kết hợp bằng AND.
- `thì`: một chuỗi sự kiện kết luận không rỗng; có thể làm điều kiện luật sau.
- `nguon`: chuỗi không rỗng; tài liệu, cơ quan/tác giả, URL hoặc trang/mục.
- `ghi_chu`: chuỗi, có thể rỗng; giải thích phạm vi áp dụng.

Ví dụ ký hiệu **chỉ để kiểm thử**, không đưa vào bộ luật nông học:

```json
{"id": "T1", "nếu": ["A"], "thì": "B",
 "nguon": "fixture logic, không phải nguồn nông học", "ghi_chu": "Chỉ dùng kiểm thử"}
```

`python -m scripts.check_rules` kiểm tra schema, nguồn không rỗng, id duy nhất,
từ khóa thuốc/hoạt chất/liều và một số đơn vị. Không tự phát hiện mọi tên thương mại,
không chứng minh nguồn có thật hoặc hỗ trợ kết luận. TV2 phải duyệt thủ công
nội dung, tên sản phẩm/hoạt chất và mở nguồn kiểm tra từng luật.
Không dùng danh sách tên thuốc tự bịa. File rỗng đạt schema nhưng chưa đủ ≥20 luật;
script báo riêng trạng thái này, test số lượng hiện xfail.

## 6. Giao tiếp nội bộ phục vụ test

- `astar(cells: list[list[int]], start: ToaDo, goal: ToaDo) -> list[ToaDo] | None`:
  đường gồm hai đầu; None khi không tới; start=goal trả [start].
- `forward(facts: set[str], rules: list[Luat]) -> set[str]`: bao đóng gồm facts.
- `backward(goal: str, facts: set[str], rules: list[Luat],
  hoi_nguoi_dung: HoiNguoiDung) -> bool`: True khi chứng minh được; False khi
  chưa chứng minh được, không đồng nghĩa phủ định y học.

Test thuật toán xfail chỉ khi NotImplementedError; kết quả sai vẫn fail. Khi
hàm đạt, bỏ dấu xfail tương ứng và giữ các kiểm tra. XPASS là lỗi để nhắc cập nhật
trạng thái. BFS chỉ nằm trong tests, không phải mã CN1.
