## Context
Dựa vào `report.md` vừa tạo xong.
Có thể dùng **GitNexus** để search file nhanh hơn.

---

## Task 1 — Thêm 2 tools mới vào MCP server

Thêm 2 tools sau vào MCP server:
- `get_memory`
- `update_memory`

Yêu cầu: Kiểm tra xem 2 tools này có thể **kế thừa cơ chế tương tự CLI** không và implement theo hướng đó nếu khả thi.

Sau khi thêm xong:
1. Build lại MCP server
2. Test toàn bộ các tools (bao gồm cả 2 tools mới)
3. Ghi kết quả vào file `report_test_tools.md`

---

## Task 2 — Rewrite `mem0-plugin-self-hosted` để dùng MCP server

Đọc toàn bộ code trong folder `mem0-plugin-self-hosted`, sau đó viết lại plugin theo các yêu cầu sau:

- **Giữ nguyên logic/idea** của plugin hiện tại
- **Thay REST API bằng MCP server**: vì không có REST API, dùng `curl` để gọi MCP server thực hiện các chức năng tương ứng với **7 tools** trong MCP server
- Đảm bảo plugin sử dụng đủ cả 7 tools

Sau khi viết xong:
- Chạy thử từng script trong plugin để xác nhận hoạt động đúng
- Ghi lại bất kỳ lỗi hoặc điều chỉnh nào cần thiết