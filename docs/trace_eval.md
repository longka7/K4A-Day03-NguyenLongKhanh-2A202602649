# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Long Khánh  
> **Mã Sinh Viên / Mã Học viên:** 2A202602649  
> **Chủ đề Lựa chọn:** 2.1 — Trợ lý Nhân sự VinFast (HR Assistant): Tra cứu ngày phép còn lại, chính sách bảo hiểm và tạo đơn xin nghỉ phép.  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Nhiều yêu cầu thực tế cần 2 bước nối tiếp: tra cứu số ngày phép còn lại trước, rồi mới quyết định tạo đơn xin nghỉ (TC04). |
| **2. Tool Interaction** | 5 / 5 | Bắt buộc phải gọi qua MCP Server tới 2 nguồn dữ liệu/hành động thực tế: hồ sơ nhân sự (`hr_query`) và hệ thống tạo đơn nghỉ phép (`submit_leave_request`) — không thể trả lời chính xác chỉ bằng kiến thức tĩnh của LLM. |
| **3. Dynamic Decision** | 4 / 5 | Bước tạo đơn nghỉ phép phụ thuộc vào kết quả tra cứu trước đó (ví dụ chỉ nên tạo đơn nếu còn đủ ngày phép), Agent phải quan sát Observation rồi mới quyết định hành động tiếp theo. |
| **4. Long Horizon Goal** | 3 / 5 | Mỗi phiên hỏi-đáp thường khép kín trong 1-2 lượt (không phải một mục tiêu kéo dài nhiều ngày/nhiều phiên), nhưng vẫn cần giữ đúng ngữ cảnh nhân viên xuyên suốt 1 câu hỏi multi-step. |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | Tổng điểm > 12/20 → Bài toán Trợ lý Nhân sự VinFast rất phù hợp để triển khai ReAct Agent thay vì Chatbot Baseline thông thường. |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Log sau được sinh ra từ `python src/app.py --all` chạy trên **Gemini API thật** (model `gemini-3.6-flash`) — nhận biết qua độ trễ mạng thực tế (`latency_ms` ~1900ms cho mỗi bước gọi LLM, khác hẳn với 0ms của Mock Offline) và `thought` do chính Gemini sinh ra ("Gemini quyết định gọi công cụ...", "Gemini phản hồi trực tiếp bằng văn bản...").

Đoạn trích tiêu biểu — TC03 (Agent tự phát hiện đúng cả 3 tham số `employee_id`, `leave_date`, `reason` từ câu hỏi tự nhiên và gọi tool `submit_leave_request`):

```json
[
  {
    "step": 1,
    "query": "Hãy tạo đơn xin nghỉ phép cho nhân viên NV2026001 vào ngày 20/09/2026 vì lý do khám sức khỏe định kỳ.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "submit_leave_request",
    "arguments": {
      "reason": "khám sức khỏe định kỳ",
      "employee_id": "NV2026001",
      "leave_date": "20/09/2026"
    },
    "observation": {
      "status": "SUCCESS",
      "leave_request_id": "LR-NV2026001-99",
      "employee_id": "NV2026001",
      "leave_date": "20/09/2026",
      "reason": "khám sức khỏe định kỳ",
      "message": "Đã tạo đơn xin nghỉ phép cho nhân viên NV2026001 vào ngày 20/09/2026 (Lý do: khám sức khỏe định kỳ). Đơn đang chờ quản lý phê duyệt."
    },
    "latency_ms": 1933.45
  },
  {
    "step": 2,
    "query": "Hãy tạo đơn xin nghỉ phép cho nhân viên NV2026001 vào ngày 20/09/2026 vì lý do khám sức khỏe định kỳ.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Đã tạo đơn xin nghỉ phép cho nhân viên NV2026001 vào ngày 20/09/2026 (Lý do: khám sức khỏe định kỳ). Đơn đang chờ quản lý phê duyệt.",
    "latency_ms": 10.0
  }
]
```

**Nhận xét thêm về TC04 (multi-step reasoning):** Với câu hỏi 2 bước ("tra cứu ngày phép rồi mới tạo đơn nghỉ"), Agent gọi đúng `hr_query` cho `NV2026002` ở bước đầu, nhưng dừng lại và tổng hợp câu trả lời ngay sau khi có Observation, **chưa tự động gọi tiếp** `submit_leave_request`. Nguyên nhân: hàm `run_react_agent()` (code mẫu có sẵn, không nằm trong TODO) tổng hợp Final Answer bằng logic if/else cứng ngay sau observation đầu tiên và `break`, thay vì đưa Observation quay lại cho LLM suy luận tiếp bước kế — nên vòng lặp ReAct hiện tại chỉ thực thi được tối đa 1 lượt gọi Tool mỗi câu hỏi.

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini `gemini-3.6-flash`).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases (TC01–TC05, chạy qua `python src/app.py --all`).
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 lượt (TC02: `hr_query`, TC03: `submit_leave_request`, TC04: `hr_query`, TC05: `hr_query` với mã không tồn tại → trả `NOT_FOUND` chính xác). TC01 đúng như kỳ vọng không gọi Tool nào (trả lời trực tiếp từ kiến thức chung).
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
