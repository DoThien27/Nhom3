# Hệ Thống Quản Lý Câu Lạc Bộ Thể Thao (Web Application)

Đây là ứng dụng Web quản lý câu lạc bộ thể thao được xây dựng bằng Python Flask (Backend) và kiến trúc SPA (Frontend), sử dụng cơ sở dữ liệu MySQL.

## Công nghệ sử dụng
- **Backend**: Python 3.10+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6), Lucide Icons
- **Cơ sở dữ liệu**: MySQL
- **Bảo mật**: `bcrypt` (mã hóa mật khẩu), Session-based RBAC

## Chức năng chính
1. **Quản lý Hội viên**: Đăng ký, gia hạn gói tập, theo dõi trạng thái.
2. **Quản lý Lớp học & Sự kiện**: Sắp xếp lịch tập, quản lý học viên, kiểm tra trùng lịch sân bãi.
3. **Tài chính & Hóa đơn**: Tạo hóa đơn đa dịch vụ, quản lý thanh toán, hủy/xóa hóa đơn.
4. **Phân quyền (RBAC)**: Phân chia quyền hạn chi tiết cho Admin, Huấn luyện viên (PT) và Hội viên.
5. **Báo cáo & Thống kê**: Dashboard tổng quan doanh thu, hiệu suất HLV và tình trạng lớp học.

## Cài đặt & Khởi động
1. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Cấu hình môi trường:**
   - Chỉnh sửa file `.env` với thông tin kết nối MySQL của bạn.
3. **Khởi tạo Database (Nạp dữ liệu mẫu):**
   ```bash
   python database/init_mysql_db.py
   ```
4. **Chạy ứng dụng:**
   ```bash
   python web/app.py
   ```
5. **Truy cập:** Mở trình duyệt tại `http://localhost:5000`

## Tài khoản Demo
- **Quản trị viên (Admin):** `admin` / `admin123`
- **Huấn luyện viên (PT):** `hlv_lan` / `hlv123`
- **Hội viên (Member):** `nam01` / `123456`
