"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.
"""

from datetime import datetime, timedelta

# Mock Cơ sở dữ liệu đơn hàng thương mại điện tử
MOCK_ORDER_DB = {
    "ORD-88219": {
        "order_id": "ORD-88219",
        "customer": "Nguyen Thi Thu Trang",
        "order_date": "2026-07-25",
        "status": "Đã giao hàng thành công",
        "delivery_date": "2026-07-26",
        "items": [
            {"item_id": "ITEM-101", "name": "Áo sơ mi nam Size L", "price": 450000, "quantity": 1, "returnable": True},
            {"item_id": "ITEM-102", "name": "Quần Jeans Slimfit", "price": 650000, "quantity": 1, "returnable": True}
        ],
        "shipping_fee": 30000,
        "total_paid": 1130000
    },
    "ORD-12345": {
        "order_id": "ORD-12345",
        "customer": "Tran Van A",
        "order_date": "2026-05-10",
        "status": "Đã giao hàng thành công",
        "delivery_date": "2026-05-12",
        "items": [
            {"item_id": "ITEM-999", "name": "Smartphone X 128GB", "price": 15000000, "quantity": 1, "returnable": False}
        ],
        "shipping_fee": 50000,
        "total_paid": 15050000
    }
}


def get_order_details(order_id: str) -> str:
    """
    Tra cứu chi tiết thông tin đơn hàng, danh sách sản phẩm, ngày mua và trạng thái giao hàng.
    
    Args:
        order_id (str): Mã đơn hàng (Ví dụ: 'ORD-88219', 'ORD-12345')
        
    Returns:
        str: Chi tiết thông tin đơn hàng từ CSDL
    """
    clean_id = order_id.strip().upper()
    if not clean_id.startswith("ORD-"):
        clean_id = f"ORD-{clean_id}"

    if clean_id not in MOCK_ORDER_DB:
        return f"LỖI: Không tìm thấy đơn hàng với mã '{order_id}'. Vui lòng kiểm tra lại mã đơn hàng."
    
    order = MOCK_ORDER_DB[clean_id]
    item_list_str = "\n".join([
        f"  - [{item['item_id']}] {item['name']} | Giá: {item['price']:,} VNĐ | Số lượng: {item['quantity']}"
        for item in order["items"]
    ])
    
    return (
        f"📦 BÁO CÁO ĐƠN HÀNG [{order['order_id']}]:\n"
        f"- Khách hàng: {order['customer']}\n"
        f"- Ngày đặt: {order['order_date']}\n"
        f"- Trạng thái: {order['status']} (Ngày nhận: {order['delivery_date']})\n"
        f"- Danh sách sản phẩm:\n{item_list_str}\n"
        f"- Phí vận chuyển: {order['shipping_fee']:,} VNĐ\n"
        f"- Tổng tiền đã thanh toán: {order['total_paid']:,} VNĐ"
    )


def check_return_eligibility(order_id: str, reason: str) -> str:
    """
    Kiểm tra điều kiện đổi trả của đơn hàng dựa trên chính sách (Thời hạn 7 ngày kể từ khi nhận, lý do hợp lệ).
    
    Args:
        order_id (str): Mã đơn hàng (Ví dụ: 'ORD-88219')
        reason (str): Lý do muốn đổi trả (Ví dụ: 'Rách khuy', 'Giao sai size', 'Không thích nữa')
        
    Returns:
        str: Kết quả kiểm tra điều kiện đổi trả
    """
    clean_id = order_id.strip().upper()
    if not clean_id.startswith("ORD-"):
        clean_id = f"ORD-{clean_id}"

    if clean_id not in MOCK_ORDER_DB:
        return f"LỖI: Đơn hàng '{order_id}' không tồn tại trên hệ thống."
    
    order = MOCK_ORDER_DB[clean_id]
    delivery_dt = datetime.strptime(order["delivery_date"], "%Y-%m-%d")
    current_dt = datetime.now()
    days_passed = (current_dt - delivery_dt).days

    # Quy định chính sách: Đổi trả trong vòng 7 ngày kể từ delivery_date
    if days_passed > 7:
        return (
            f"TỪ CHỐI ĐỔI TRẢ: Đơn hàng {clean_id} đã nhận từ ngày {order['delivery_date']} "
            f"(đã qua {days_passed} ngày). Chính sách cửa hàng chỉ hỗ trợ đổi trả trong vòng 7 ngày."
        )

    invalid_reasons = ["không thích nữa", "đổi ý", "hết tiền"]
    if any(ir in reason.lower() for ir in invalid_reasons) and any(not item["returnable"] for item in order["items"]):
        return f"❌ TỪ CHỐI ĐỔI TRẢ: Lý do '{reason}' không áp dụng cho loại sản phẩm này theo chính sách."

    return (
        f"ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng {clean_id} trong thời hạn hỗ trợ (nhận cách đây {days_passed} ngày). "
        f"Lý do '{reason}' nằm trong danh mục được chấp nhận đổi trả miễn phí."
    )


def calculate_refund_amount(order_id: str, item_id: str) -> str:
    """
    Tính toán số tiền hoàn trả cho sản phẩm cụ thể trong đơn hàng.
    
    Args:
        order_id (str): Mã đơn hàng (Ví dụ: 'ORD-88219')
        item_id (str): Mã sản phẩm (Ví dụ: 'ITEM-101')
        
    Returns:
        str: Số tiền hoàn chi tiết
    """
    clean_id = order_id.strip().upper()
    if clean_id not in MOCK_ORDER_DB:
        return f"LỖI: Đơn hàng '{order_id}' không tồn tại."
    
    order = MOCK_ORDER_DB[clean_id]
    target_item = None
    for item in order["items"]:
        if item["item_id"].strip().upper() == item_id.strip().upper() or item_id in item["name"]:
            target_item = item
            break
            
    if not target_item:
        return f"LỖI: Không tìm thấy sản phẩm '{item_id}' trong đơn hàng {clean_id}."
    
    refund_val = target_item["price"] * target_item["quantity"]
    return (
        f"BẢNG TÍNH HOÀN TIỀN [{clean_id} - {target_item['name']}]:\n"
        f"- Giá niêm yết sản phẩm: {refund_val:,} VNĐ\n"
        f"- Phí hoàn bù (Miễn phí): 0 VNĐ\n"
        f"Tổng số tiền hoàn dự kiến trả lại khách hàng: {refund_val:,} VNĐ"
    )


def create_return_ticket(order_id: str, item_id: str, reason: str) -> str:
    """
    Tạo vé yêu cầu đổi trả chính thức và cấp mã vận đơn thu hồi cho khách hàng.
    
    Args:
        order_id (str): Mã đơn hàng
        item_id (str): Mã sản phẩm
        reason (str): Lý do đổi trả
        
    Returns:
        str: Xác nhận tạo vé thành công và mã vận đơn thu hồi
    """
    clean_id = order_id.strip().upper()
    ticket_code = f"RET-TICKET-{clean_id}-2026"
    return_shipping_code = f"SPX-RET-99201"
    
    return (
        f"🎉 TẠO VÉ ĐỔI TRẢ THÀNH CÔNG!\n"
        f"- Mã yêu cầu đổi trả: {ticket_code}\n"
        f"- Mã đơn hàng gốc: {clean_id}\n"
        f"- Lý do: {reason}\n"
        f"- Mã vận đơn gửi trả lại hàng (Miễn phí): {return_shipping_code}\n"
        f"- Hướng dẫn: Đóng gói sản phẩm cẩn thận, ghi mã {return_shipping_code} lên bưu kiện và giao cho bưu tá Shopee Xpress/GHTK."
    )


# Danh sách các tool đăng ký sẵn cho ReAct Agent trong Đề tài 5
AVAILABLE_TOOLS = {
    "get_order_details": get_order_details,
    "check_return_eligibility": check_return_eligibility,
    "calculate_refund_amount": calculate_refund_amount,
    "create_return_ticket": create_return_ticket,
}
