"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.

Chủ đề #5: Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả

Dữ liệu đơn hàng bên dưới là dữ liệu giả lập (deterministic) để bài Lab chạy
được ngay không cần API/CSDL thật. "Hôm nay" được cố định là 2026-07-28 để
kết quả tra cứu luôn nhất quán giữa các lần chạy.
"""

from datetime import date, datetime

TODAY = date(2026, 7, 28)
RETURN_WINDOW_DAYS = 7

MOCK_ORDERS = {
    "ORD-12345": {
        "status": "Đã giao",
        "delivered_date": "2026-07-22",
        "items": [{"name": "Áo thun nam Size M", "price": 250000}],
    },
    "ORD-88219": {
        "status": "Đã giao",
        "delivered_date": "2026-07-26",
        "items": [{"name": "Áo sơ mi nam Size L", "price": 450000}],
    },
    "ORD-99999": {
        "status": "Đang giao",
        "delivered_date": None,
        "items": [{"name": "Quần jean Slim Fit", "price": 550000}],
    },
}


def lookup_order(order_id: str) -> str:
    """
    Tra cứu trạng thái và thông tin của một đơn hàng.

    Purpose: Dùng khi cần biết đơn hàng đang ở trạng thái nào (đang giao / đã
    giao / v.v.), ngày giao và sản phẩm bên trong. Không dùng để kiểm tra
    điều kiện đổi trả (dùng check_return_eligibility cho việc đó).

    Args:
        order_id (str): Mã đơn hàng (ví dụ: 'ORD-12345').

    Returns:
        str: Thông tin đơn hàng nếu tìm thấy, hoặc chuỗi bắt đầu bằng "LỖI:"
        nếu mã đơn không tồn tại. Không bao giờ raise exception.

    Example:
        >>> lookup_order("ORD-12345")
        "Đơn hàng ORD-12345: Đã giao ngày 2026-07-22. Sản phẩm: Áo thun nam Size M (250,000 VNĐ)."
    """
    order = MOCK_ORDERS.get(order_id.strip().upper())
    if not order:
        return f"LỖI: Không tìm thấy đơn hàng '{order_id}'. Vui lòng kiểm tra lại mã đơn."

    items_str = ", ".join(f"{item['name']} ({item['price']:,} VNĐ)" for item in order["items"])
    if order["status"] == "Đã giao":
        return f"Đơn hàng {order_id.upper()}: Đã giao ngày {order['delivered_date']}. Sản phẩm: {items_str}."
    return f"Đơn hàng {order_id.upper()}: {order['status']}. Sản phẩm: {items_str}."


def check_return_eligibility(order_id: str, reason: str = "") -> str:
    """
    Kiểm tra một đơn hàng có đủ điều kiện đổi/trả hay không.

    Purpose: Chỉ gọi SAU KHI đã có thông tin đơn hàng (thường sau khi gọi
    lookup_order). Điều kiện: đơn phải đã giao và còn trong hạn
    RETURN_WINDOW_DAYS (7 ngày) kể từ ngày giao.

    Args:
        order_id (str): Mã đơn hàng cần kiểm tra.
        reason (str): Lý do khách hàng muốn đổi/trả (không bắt buộc).

    Returns:
        str: "ĐỦ ĐIỀU KIỆN..." hoặc "KHÔNG ĐỦ ĐIỀU KIỆN..." kèm lý do, hoặc
        chuỗi bắt đầu bằng "LỖI:" nếu không tìm thấy đơn hàng. Không crash.

    Example:
        >>> check_return_eligibility("ORD-88219", "Rách khuy")
        "ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng ORD-88219 giao 2 ngày trước, còn trong thời hạn 7 ngày. Lý do: 'Rách khuy'."
    """
    order = MOCK_ORDERS.get(order_id.strip().upper())
    if not order:
        return f"LỖI: Không tìm thấy đơn hàng '{order_id}' để kiểm tra điều kiện đổi trả."

    if order["status"] != "Đã giao":
        return (
            f"KHÔNG ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng {order_id.upper()} chưa được giao "
            f"(trạng thái hiện tại: {order['status']})."
        )

    delivered = datetime.strptime(order["delivered_date"], "%Y-%m-%d").date()
    days_passed = (TODAY - delivered).days

    if days_passed > RETURN_WINDOW_DAYS:
        return (
            f"KHÔNG ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng {order_id.upper()} đã giao được {days_passed} ngày, "
            f"vượt quá thời hạn đổi trả {RETURN_WINDOW_DAYS} ngày."
        )

    reason_str = reason.strip() if reason and reason.strip() else "không nêu rõ"
    return (
        f"ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng {order_id.upper()} giao {days_passed} ngày trước, "
        f"còn trong thời hạn {RETURN_WINDOW_DAYS} ngày. Lý do: '{reason_str}'."
    )


def initiate_return(order_id: str, reason: str) -> str:
    """
    Tạo yêu cầu đổi/trả cho một đơn hàng.

    Purpose: Chỉ gọi SAU KHI check_return_eligibility xác nhận "ĐỦ ĐIỀU
    KIỆN". Đây là tool có side effect thật (tạo yêu cầu), không phải tool
    chỉ tra cứu.

    Args:
        order_id (str): Mã đơn hàng cần tạo yêu cầu đổi/trả.
        reason (str): Lý do đổi/trả.

    Returns:
        str: Xác nhận đã tạo yêu cầu kèm mã vé và số tiền hoàn dự kiến, hoặc
        chuỗi bắt đầu bằng "LỖI:" nếu đơn hàng không tồn tại. Không crash.

    Example:
        >>> initiate_return("ORD-88219", "Rách khuy")
        "ĐÃ TẠO YÊU CẦU ĐỔI TRẢ: Mã vé RET-88219 cho đơn ORD-88219. Lý do: 'Rách khuy'. Số tiền hoàn dự kiến: 450,000 VNĐ."
    """
    order = MOCK_ORDERS.get(order_id.strip().upper())
    if not order:
        return f"LỖI: Không thể tạo yêu cầu đổi trả — đơn hàng '{order_id}' không tồn tại."

    refund_amount = sum(item["price"] for item in order["items"])
    ticket_id = f"RET-{order_id.upper().replace('ORD-', '')}"
    return (
        f"ĐÃ TẠO YÊU CẦU ĐỔI TRẢ: Mã vé {ticket_id} cho đơn {order_id.upper()}. "
        f"Lý do: '{reason}'. Số tiền hoàn dự kiến: {refund_amount:,} VNĐ."
    )


# Danh sách các tool đăng ký sẵn cho ReAct Agent trong Đề tài 5
AVAILABLE_TOOLS = {
    "lookup_order": lookup_order,
    "check_return_eligibility": check_return_eligibility,
    "initiate_return": initiate_return,
}
