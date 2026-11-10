
---
name: compare_sources
description: >
  Công cụ so sánh nội dung từ hai nguồn thông tin,
  xác định các phát biểu tương đồng và khác biệt.
  Sử dụng khi người dùng yêu cầu đối chiếu hai bài báo,
  tài liệu hoặc nguồn nghiên cứu.
---

# Công cụ so sánh nguồn thông tin (Compare Sources)

## 1. Mục đích

Công cụ `compare_sources` hỗ trợ Research Agent so sánh
nội dung văn bản từ hai nguồn thông tin khác nhau.

Công cụ sử dụng phương pháp so sánh độ tương đồng chuỗi
để xác định:
- Các phát biểu có nội dung câu chữ tương đồng.
- Các phát biểu chỉ xuất hiện trong nguồn thứ nhất.
- Các phát biểu chỉ xuất hiện trong nguồn thứ hai.
- Mức độ tương đồng tổng thể giữa hai văn bản.

## 2. Khi nào sử dụng?

Sử dụng công cụ trong các trường hợp:
- Người dùng muốn so sánh nội dung của hai bài báo.
- Người dùng muốn đối chiếu hai báo cáo nghiên cứu.
- Người dùng muốn tìm các điểm giống và khác nhau
  giữa hai nguồn thông tin.
- Research Agent đã thu thập được nội dung của
  hai nguồn và cần tiến hành so sánh.

Ví dụ:
"So sánh thông tin về AI trong hai bài báo này."

## 3. Khi nào không sử dụng?

Không sử dụng công cụ khi:
- Chỉ có một nguồn thông tin.
- Người dùng chỉ yêu cầu tìm kiếm tin tức.
- Người dùng chỉ yêu cầu tóm tắt một bài viết.
- Người dùng yêu cầu xác minh thông tin đúng hay sai.
- Chưa có nội dung văn bản của hai nguồn cần so sánh.

Nếu chưa có dữ liệu, Research Agent cần sử dụng
`lookup` hoặc `fetch` để thu thập nội dung trước.

## 4. Tham số đầu vào

| Tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
|---|---|---|---|
| source_a | string | Có | Nội dung nguồn thứ nhất |
| source_b | string | Có | Nội dung nguồn thứ hai |
| title_a | string | Không | Tiêu đề nguồn thứ nhất |
| title_b | string | Không | Tiêu đề nguồn thứ hai |

## 5. Dữ liệu đầu ra

Công cụ trả về một đối tượng JSON gồm:

- `tool`: Tên công cụ được sử dụng.
- `title_a`: Tiêu đề nguồn thứ nhất.
- `title_b`: Tiêu đề nguồn thứ hai.
- `similarity_score`: Điểm tương đồng từ 0 đến 1.
- `common_statements`: Các phát biểu tương đồng.
- `unique_to_a`: Các phát biểu chỉ có trong nguồn A.
- `unique_to_b`: Các phát biểu chỉ có trong nguồn B.
- `note`: Ghi chú về giới hạn của kết quả.

Điểm tương đồng càng gần 1 thì hai văn bản
càng giống nhau về mặt câu chữ.

## 6. Ví dụ sử dụng

### Đầu vào

```python
compare_sources(
    source_a="OpenAI vừa công bố mô hình AI mới.",
    source_b="OpenAI vừa công bố mô hình AI mới.",
    title_a="Báo A",
    title_b="Báo B"
)
```

### Kết quả minh họa

```json
{
  "tool": "compare_sources",
  "title_a": "Báo A",
  "title_b": "Báo B",
  "similarity_score": 1.0,
  "common_statements": [
    {
      "source_a": "OpenAI vừa công bố mô hình AI mới.",
      "source_b": "OpenAI vừa công bố mô hình AI mới."
    }
  ],
  "unique_to_a": [],
  "unique_to_b": [],
  "note": "So sánh câu chữ, chưa xác minh tính đúng sai."
}
```

## 7. Quy trình hoạt động

Bước 1: Nhận hai nội dung văn bản đầu vào.

Bước 2: Kiểm tra dữ liệu có hợp lệ và không rỗng.

Bước 3: Tách văn bản thành các câu.

Bước 4: Chuẩn hóa chữ hoa, chữ thường và khoảng trắng.

Bước 5: So sánh các câu bằng SequenceMatcher.

Bước 6: Phân loại các câu tương đồng và khác biệt.

Bước 7: Tính điểm tương đồng tổng thể.

Bước 8: Trả về kết quả dưới dạng JSON.

## 8. Giới hạn của công cụ

- Chỉ so sánh mức độ tương đồng về câu chữ.
- Không sử dụng mô hình ngôn ngữ để hiểu ngữ nghĩa.
- Không tự xác minh độ tin cậy của nguồn.
- Không xác định chính xác các thông tin mâu thuẫn.
- Hai câu có cùng ý nghĩa nhưng diễn đạt khác nhau
  có thể bị đánh giá là không tương đồng.
- Các phát biểu khác nhau không nhất thiết mâu thuẫn.

## 9. Kiểm thử

Chạy kiểm thử chức năng:

```powershell
python -m pytest tests/test_compare_sources.py -v
```

Chạy kiểm thử hợp đồng công cụ:

```powershell
python -m pytest tests/test_tool_contract.py -v
```

Kết quả mong đợi:
- So sánh hai văn bản giống nhau thành công.
- Phân biệt được các câu có nội dung khác nhau.
- Phát hiện dữ liệu đầu vào rỗng.
- Công cụ được đăng ký đúng trong hệ thống.
```
 
## 3. Kiểm tra sau khi cập nhật

Chạy:

```powershell
python -m pytest tests/test_compare_sources.py tests/test_tool_contract.py -v
```

**Lưu ý:** Bạn không cần sửa thuật toán trong `tool.py` chỉ để chuyển mô tả sang tiếng Việt. Tuy nhiên, nếu muốn toàn bộ kết quả JSON trả về cũng bằng tiếng Việt, có thể đổi nội dung của trường `note` và các thông báo `error`, nhưng vẫn giữ nguyên các khóa JSON như `similarity_score`, `common_statements`, `unique_to_a` và `unique_to_b`.