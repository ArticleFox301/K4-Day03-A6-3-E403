# BÁO CÁO GIÁM SÁT VÀ ĐÁNH GIÁ - CHECKPOINT 1
**Đề tài 5: Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả**  
*Dành cho Role 5: Observability & Reviewer*

---

##  1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX) - CHECKPOINT 1

| Tiêu chí | Điểm (1-5) | Lý do đánh giá chi tiết cho Đề tài 5 |
| :--- | :---: | :--- |
|  **Multi-step Reasoning** | `5/5` | Cần suy luận qua nhiều bước liên tiếp: Nhận dạng mã đơn ➔ Tra cứu CSDL ➔ Đối chiếu chính sách đổi trả (thời hạn 7 ngày, lý do) ➔ Tính tiền hoàn ➔ Xuất vé thu hồi. |
| **Tool Interaction** | `5/5` | Bắt buộc tương tác với hệ thống CSDL thực tế via APIs: `get_order_details`, `check_return_eligibility`, `calculate_refund_amount`, `create_return_ticket`. |
| **Dynamic Decision** | `5/5` | Quyết định bước tiếp theo hoàn toàn phụ thuộc kết quả bước trước (VD: Nếu đơn quá 7 ngày ➔ Ngắt quy trình & từ chối; Nếu đủ điều kiện ➔ Tiếp tục tính số tiền hoàn trả). |
|**Long Horizon** | `4/5` | Quy trình gồm 3-4 bước thực thi liên chuỗi với dữ liệu động từ người dùng và hệ thống quản trị kho. |
| **TỔNG ĐIỂM AGENTIC FIT** | **19/20** | **KẾT LUẬN: ĐỀ TÀI 5 CÓ ĐỘ PHÙ HỢP CỰC KỲ CAO VỚI REACT AGENT!** |

---

## 📍 MỐC 3 — TRACE LOG THẬT (Thought → Action → Observation)

*Chạy thật bằng `python src/app.py`, LLM Provider: Ollama local (`qwen3:4b`, không cần API key). Bộ tool đã đồng bộ về 3-tool: `lookup_order`, `check_return_eligibility`, `initiate_return`.*

### Test Case #3: "Đơn hàng #ORD-12345 của tôi hiện đang ở đâu rồi?"

```
[REACT AGENT] Câu hỏi: Đơn hàng #ORD-12345 của tôi hiện đang ở đâu rồi?

--- Vòng lặp ReAct (Step 1/4) ---
Thought: Tôi cần tra cứu trạng thái đơn hàng #ORD-12345 để biết được thông tin hiện tại.
Action: lookup_order[order_id="ORD-12345"]
Observation: Đơn hàng ORD-12345: Đã giao ngày 2026-07-22. Sản phẩm: Áo thun nam Size M (250,000 VNĐ).

--- Vòng lặp ReAct (Step 2/4) ---
Thought: Tôi đã có đủ thông tin để trả lời khách hàng.
Final Answer: Chào bạn, đơn hàng #ORD-12345 của bạn đã được giao ngày 2026-07-22. Sản phẩm
trong đơn hàng là Áo thun nam Size M với giá 250,000 VNĐ. Nếu bạn cần thêm thông tin hoặc có
thắc mắc khác, vui lòng liên hệ với chúng tôi!

[REACT AGENT] Hoàn thành xuất sắc nhiệm vụ. (Dừng ở Step 2/4, không chạm Guardrail)
```

**Nhận xét**: Agent suy luận đúng cần gọi `lookup_order` trước khi trả lời, Observation lấy từ dữ liệu thật (`MOCK_ORDERS` trong `tools.py`) chứ không bịa, và dừng đúng lúc khi đã đủ bằng chứng.

**Failed trace phát hiện & đã fix (root cause analysis)**: Ở lần chạy đầu tiên, model sinh Action dạng `lookup_order[order_id=#ORD-12345]` (có tiền tố `order_id=` và dấu `#`). Vì `lookup_order()` khi đó tra thẳng khớp chuỗi, nó trả về `LỖI: Không tìm thấy đơn hàng` **sai** (đơn thực ra tồn tại) → Agent kết luận nhầm là khách nhập sai mã. **Root cause**: tool không chuẩn hóa input trước khi tra cứu. **Fix**: thêm hàm `_normalize_order_id()` trong `tools.py` để bỏ tiền tố `key=`, bỏ dấu `#`, trước khi so khớp — áp dụng cho cả 3 tool. Sau khi vá, chạy lại cho kết quả đúng như log ở trên.

---

## 2. PHÂN TÍCH CHI TIẾT CHECKPOINT 1 (MỐC 1)

### 2.1 Tại sao bài toán này KHÔNG THỂ giải quyết chỉ bằng Chatbot Baseline (Cấp 2)?
1. **Rào cản dữ liệu tĩnh**: Chatbot Cấp 2 chỉ dựa vào tri thức được huấn luyện sẵn (LLM weights). Nó không thể biết mã đơn hàng `#ORD-88219` thuộc về ai, đã giao ngày nào, hay chứa sản phẩm gì.
2. **Ảo giác dữ liệu (Hallucination)**: Khi khách hàng đưa mã đơn hàng, Chatbot Cấp 2 dễ tự bịa ra thông tin đơn hàng giả hoặc trả lời chung chung: *"Tôi không có kết nối CSDL nên không thể kiểm tra đơn hàng cho bạn"*.
3. **Không thể thực thi tác vụ (No Execution)**: Chatbot thông thường không thể tự động bấm nút chấp nhận đổi trả hay tự tạo mã vận đơn thu hồi hàng trên hệ thống Shopee Xpress/GHTK.

###  2.2 Ưu thế vượt trội của ReAct Agent (Cấp 3) trong Đề tài 5:
- **Chuỗi suy luận Thought ➔ Action ➔ Observation**: Agent chủ động phân tích câu hỏi người dùng, quyết định cần gọi tool nào (`get_order_details`), nhận kết quả thực tế từ CSDL (`Observation`), sau đó suy luận bước tiếp theo (`check_return_eligibility`) một cách hoàn toàn tự động.
- **Tuân thủ Guardrails (Phanh an toàn)**: Đảm bảo kiểm tra nghiêm ngặt điều kiện 7 ngày, tránh việc hoàn tiền sai cho các đơn hàng quá hạn hoặc lý do không phù hợp.

---

##  3. NỘI DUNG SO SÁNH THỬ NGHIỆM BAN ĐẦU (TEST CASE #3 & #4)

###  Câu hỏi Test Case #4:
*"Tôi muốn trả sản phẩm 'Áo sơ mi nam Size L' trong đơn hàng #ORD-88219 vì bị rách khuy. Hãy kiểm tra xem đơn này có đủ điều kiện đổi trả không và tính số tiền hoàn lại."*

###  Chatbot Baseline (Dự kiến):
* **Phản hồi**: *"Chào bạn, để đổi trả sản phẩm bị rách khuy, bạn cần gửi sản phẩm về shop trong vòng 7 ngày. Tuy nhiên tôi không kiểm tra được mã đơn #ORD-88219 của bạn trên hệ thống."*
* **Nhận xét**: Không giải quyết được nhu cầu thực tế của khách hàng.

###  ReAct Agent Trace Log (Dự kiến thực thi):
* **Step 1 - Thought**: Cần tra cứu thông tin đơn hàng `#ORD-88219` từ CSDL.
  * **Action**: `get_order_details["ORD-88219"]`
  * **Observation**: `Đơn hàng ORD-88219: Giao thành công ngày 2026-07-26. Sản phẩm: Áo sơ mi nam Size L (450,000 VNĐ).`
* **Step 2 - Thought**: Đơn hàng giao ngày 26/07/2026 (trong vòng 7 ngày). Cần kiểm tra điều kiện đổi trả với lý do "Rách khuy".
  * **Action**: `check_return_eligibility["ORD-88219", "Rách khuy"]`
  * **Observation**: `ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng trong thời hạn 7 ngày. Lý do rách khuy được hỗ trợ đổi trả miễn phí.`
* **Step 3 - Thought**: Cần tính toán chính xác số tiền hoàn lại cho sản phẩm 'Áo sơ mi nam Size L'.
  * **Action**: `calculate_refund_amount["ORD-88219", "ITEM-101"]`
  * **Observation**: ` Tổng số tiền hoàn dự kiến: 450,000 VNĐ.`
* **Final Answer**: *"Đơn hàng #ORD-88219 của quý khách đủ điều kiện đổi trả miễn phí do lỗi rách khuy từ nhà sản xuất. Số tiền hoàn lại là 450,000 VNĐ. Quý khách có muốn tôi tạo vé đổi trả và phát mã vận đơn thu hồi ngay không?"*

---

##  4. XÁC ĐỊNH BẪY LỖI & PHANH AN TOÀN (FAILURE MODES & GUARDRAILS)

| Kịch bản lỗi / Bẫy (Edge Case) | Phản ứng của Tool / Agent | Phanh Guardrail bảo vệ |
| :--- | :--- | :--- |
| Khách yêu cầu đổi trả đơn mua từ 60 ngày trước (`ORD-12345`) | Tool `check_return_eligibility` phát hiện quá 7 ngày và trả về lời từ chối | Agent dừng quy trình hoàn tiền, chuyển sang Final Answer từ chối lịch sự dựa trên điều khoản |
| Khách nhập mã đơn không tồn tại (`ORD-99999`) | Tool `get_order_details` báo lỗi "Không tìm thấy đơn hàng" | Agent không bị đơ/crash code, mà báo cho khách hàng kiểm tra lại mã |
| Vòng lặp lặp lại quá nhiều lần | Đạt `MAX_ITERATIONS = 4` | Guardrail ngắt vòng lặp lập tức, trả về thông báo hỗ trợ nhân sự |
