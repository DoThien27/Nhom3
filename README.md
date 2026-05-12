# Hệ Thống Quản Lý Câu Lạc Bộ Thể Thao (Sports Club Management)

Đây là ứng dụng Web quản lý câu lạc bộ thể thao toàn diện, được xây dựng theo kiến trúc **Single Page Application (SPA)** với Backend Flask và Frontend Vanilla JavaScript hiện đại. Hệ thống hỗ trợ quản lý hội viên, lớp học, sự kiện, chấm công và tính lương chuyên nghiệp.

## 🚀 Công nghệ sử dụng
- **Backend**: Python 3.10+, Flask (RESTful API)
- **Frontend**: HTML5, CSS3 (Modern UI), JavaScript (ES6+), Lucide Icons, Chart.js
- **Cơ sở dữ liệu**: MySQL
- **Bảo mật**: Mã hóa mật khẩu `bcrypt`, xác thực dựa trên Session và phân quyền (RBAC)

## ✨ Chức năng chính
1.  **Quản lý Hội viên**: Đăng ký, gia hạn gói tập, theo dõi trạng thái và gán Huấn luyện viên (PT).
2.  **Quản lý Thẻ hội viên**: Cấp thẻ mới khi đăng ký gói tập, quản lý mã thẻ và ngày hết hạn.
3.  **Chấm công (Check-in/out)**: 
    - Hội viên check-in bằng thẻ (tự động kiểm tra trạng thái thẻ và hóa đơn chưa thanh toán).
    - Huấn luyện viên chấm công theo buổi dạy.
4.  **Quản lý Lớp học & Sự kiện**: Sắp xếp lịch tập, đăng ký học viên, quản lý cơ sở vật chất.
5.  **Tài chính & Lương**: 
    - Tự động tạo hóa đơn khi đăng ký dịch vụ.
    - Tính lương cho HLV dựa trên lương cơ bản, số buổi dạy và số học viên phụ trách.
6.  **Báo cáo & Thống kê**: Dashboard thời gian thực với biểu đồ doanh thu, hiệu suất và tình trạng lớp học.

## 📂 Cấu trúc dự án
- `app/`: Chứa mã nguồn Backend (Logic nghiệp vụ, API Routes, Models).
- `web/`: Chứa mã nguồn Frontend (Giao diện, Static assets, Entry point).
- `.env`: Tệp cấu hình môi trường (Database, Secret Key).

## 🛠️ Cài đặt & Khởi động

### 1. Cài đặt thư viện
```bash
pip install -r web/requirements_web.txt
```

### 2. Cấu hình môi trường
Chỉnh sửa tệp `.env` ở thư mục gốc với thông tin kết nối MySQL của bạn:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=sports_club_db
SECRET_KEY=your_secret_key
```

### 3. Khởi chạy ứng dụng
```bash
python web/app.py
```
Ứng dụng sẽ chạy tại địa chỉ: `http://localhost:5000`

## 🔑 Tài khoản Demo
- **Quản trị viên (Admin):** `admin` / `admin123`
- **Huấn luyện viên (PT):** `hlv_lan` / `hlv123`
