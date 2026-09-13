"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
Chủ đề: Trợ lý Nhân sự VinFast (HR Assistant) — tra cứu phép/bảo hiểm & tạo đơn xin nghỉ phép.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    {
        "name": "hr_query",
        "description": "Tra cứu hồ sơ nhân sự VinFast: số ngày phép còn lại và chính sách bảo hiểm theo mã nhân viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên cần tra cứu (ví dụ: 'NV2026001')"
                }
            },
            "required": ["employee_id"]
        }
    },

    # --------------------------------------------------------------------------
    # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'submit_leave_request'
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để tạo đơn xin nghỉ phép cho nhân viên VinFast.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - employee_id (string): Mã nhân viên xin nghỉ (ví dụ: 'NV2026001')
    #    - leave_date (string): Ngày nghỉ phép (ví dụ: '15/09/2026')
    #    - reason (string): Lý do xin nghỉ phép
    # 3. Khai báo danh sách các trường bắt buộc (required).
    # --------------------------------------------------------------------------
    {
        "name": "submit_leave_request",
        "description": "Tạo đơn xin nghỉ phép cho nhân viên VinFast.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên xin nghỉ phép (ví dụ: 'NV2026001')"
                },
                "leave_date": {
                    "type": "string",
                    "description": "Ngày xin nghỉ phép (ví dụ: '15/09/2026')"
                },
                "reason": {
                    "type": "string",
                    "description": "Lý do xin nghỉ phép"
                }
            },
            "required": ["employee_id", "leave_date", "reason"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "NV2026001": {
        "full_name": "Nguyễn Văn An",
        "department": "Sản xuất - Nhà máy VinFast Hải Phòng",
        "remaining_leave_days": 8,
        "insurance_plan": "Bảo hiểm sức khỏe cao cấp VFS Care+",
        "email": "an.nv@vinfast.vn",
        "status": "Đang làm việc",
        "manager": "Chị Phạm Thị C (Trưởng phòng Nhân sự)"
    },
    "NV2026002": {
        "full_name": "Trần Thị Bình",
        "department": "Kinh doanh & Trải nghiệm khách hàng",
        "remaining_leave_days": 3,
        "insurance_plan": "Bảo hiểm sức khỏe tiêu chuẩn VFS Care",
        "email": "binh.tt@vinfast.vn",
        "status": "Đang làm việc",
        "manager": "Anh Lê Văn D (Trưởng phòng Kinh doanh)"
    }
}


def execute_hr_query(employee_id: str) -> str:
    """Thực thi tra cứu thông tin nhân sự theo mã nhân viên"""
    employee = MOCK_DATABASE.get(employee_id.strip().upper())
    if employee:
        return json.dumps({
            "status": "SUCCESS",
            "employee_id": employee_id,
            "data": employee
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu nhân viên có mã '{employee_id}'"
        }, ensure_ascii=False)


def execute_submit_leave_request(employee_id: str, leave_date: str, reason: str) -> str:
    """Thực thi tạo đơn xin nghỉ phép"""
    return json.dumps({
        "status": "SUCCESS",
        "leave_request_id": f"LR-{employee_id}-99",
        "employee_id": employee_id,
        "leave_date": leave_date,
        "reason": reason,
        "message": f"Đã tạo đơn xin nghỉ phép cho nhân viên {employee_id} vào ngày {leave_date} (Lý do: {reason}). Đơn đang chờ quản lý phê duyệt."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "hr_query": execute_hr_query,
    "submit_leave_request": execute_submit_leave_request
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
