# SỔ TAY PHÂN CÔNG & CHECKLIST THỰC HÀNH - ĐỀ TÀI 5: TRỢ LÝ ĐƠN HÀNG & ĐỔI TRẢ

---

## 👥 1. BẢNG PHÂN VAI & FILE ĐẢM NHẬN (NHÓM 3 NGƯỜI)

| Vai trò (Role) | File đảm nhận | Nhiệm vụ chính | Phân công nhóm 3 người |
| :--- | :--- | :--- | :--- |
| **Role 1: Product Architect** | `config/test_cases.json` | Định hướng bài toán đơn hàng & soạn 5 test cases chi tiết | Trần Lương Hoàng Anh |
| **Role 2: Tool Engineer** | `src/tools.py` | Định nghĩa các Tools: `get_order_details`, `check_return_eligibility`, `calculate_refund_amount`, `create_return_ticket` | Trần Lương Hoàng Anh |
| **Role 3: Prompt Engineer** | `src/prompts.py` | Viết ReAct System Prompt & Guardrails phanh an toàn | Nguyễn Thị Thu Trang |
| **Role 4: Core Developer / Integrator** | `src/app.py` | Ghép nối tất cả các phần vào ReAct Agent Loop hoàn chỉnh | Nguyễn Trung Đức |
| **Role 5: Observability** | `docs/trace_eval.md` | Lập bảng Scoring Matrix & Soi nhật ký Trace Log | Nguyễn Thị Thu Trang |

---

## ⏱2. CHECKLIST THỰC HÀNH CHECKPOINT 1 (MỐC 1)

- [x] **Chọn đề tài**: Đề tài 5 - Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả.
- [x] **Scoring Matrix Agentic Fit**: Hoàn thành bảng chấm điểm (19/20 điểm) trong `docs/trace_eval.md`.
- [x] **Định nghĩa Candidate Tools**: Thiết kế 4 tools tra cứu và xử lý đổi trả trong `src/tools.py`.
- [x] **Phân tích Bẫy lỗi (Failure Modes)**: Liệt kê các kịch bản quá thời hạn, mã đơn giả trong `docs/trace_eval.md` & `src/prompts.py`.
- [x] **Môi trường & Cấu hình**: Khởi tạo `.env`, `requirements.txt` và bộ thư viện chuẩn.
