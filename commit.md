# Danh sách các tệp tin trong dự án

Dưới đây là danh sách các tệp tin và mô tả chức năng của chúng:

### Cấu hình & Tài liệu
- `.env`: Chứa các biến môi trường (kết nối Database, Secret Key).
- `README.md`: Tài liệu hướng dẫn cài đặt và sử dụng ứng dụng.
- `web/requirements_web.txt`: Danh sách các thư viện Python cần cài đặt.

### Backend - Core (app/)
- `app/utils.py`: Các hàm tiện ích dùng chung cho Backend (xử lý lỗi, phân quyền).
- `app/__init__.py`: Khởi tạo package chính của ứng dụng.
- `app/database/db.py`: Quản lý kết nối (Connection Pool) và context manager cho MySQL.
- `app/models/models.py`: Định nghĩa các cấu trúc dữ liệu (Dataclasses) như Hội viên, Lớp học, Sự kiện...
- `app/services/`: Chứa logic nghiệp vụ (Business Logic) cho từng module:
    - `member_service.py`: Quản lý hội viên.
    - `class_service.py`: Quản lý lớp học/buổi tập.
    - `event_service.py`: Quản lý sự kiện thể thao.
    - `invoice_service.py`: Xử lý hóa đơn và thanh toán.
    - `dashboard_service.py`: Tổng hợp dữ liệu cho trang thống kê.
    - `trainer_service.py`: Quản lý huấn luyện viên.
    - `validators.py`: Kiểm tra tính hợp lệ của dữ liệu đầu vào.
- `app/routes/`: Định nghĩa các API Endpoints (Flask Blueprints):
    - `auth_routes.py`: Đăng nhập, đăng xuất và xác thực người dùng.
    - `member_routes.py`, `class_routes.py`, `event_routes.py`...: Các API tương ứng với từng module.

### Web Interface (web/)
- `web/app.py`: File khởi chạy ứng dụng Flask (Entry point).
- `web/templates/index.html`: File giao diện chính (Single Page Application).
- `web/static/css/main.css`: Chứa toàn bộ định dạng giao diện và hiệu ứng.
- `web/static/js/`: Logic xử lý phía trình duyệt:
    - `app.js`: Điều hướng trang và quản lý trạng thái ứng dụng.
    - `api.js`: Gửi yêu cầu (Request) đến Backend API.
    - `renderers.js`: Hiển thị dữ liệu lên giao diện HTML.
    - `utils.js`: Các hàm bổ trợ (định dạng tiền tệ, ngày tháng).
- `web/static/images/`: Chứa các tài nguyên hình ảnh của ứng dụng.
