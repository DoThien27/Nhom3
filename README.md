# 🏋️ Sports Club - Hệ thống Quản lý CLB Thể thao

Hệ thống quản lý câu lạc bộ thể thao full-stack: **Flask** (backend) + **MySQL** (database) + **HTML/CSS/JS** (frontend). Giao diện dark-mode hiện đại, không cần cài Node.js.

---

## 📋 Yêu cầu hệ thống

| Phần mềm | Phiên bản |
|----------|-----------|
| Python | 3.9+ |
| MySQL | 8.0+ |
| Pip | Mới nhất |

---

## 🚀 Hướng dẫn cài đặt và chạy

### Bước 1: Clone / tải project về

```
d:\app_python_web\
```

### Bước 2: Cài thư viện Python

```bash
pip install -r web/requirements_web.txt
```

Các thư viện chính:
- `flask` >= 3.0 - Web framework
- `flask-cors` - CORS support
- `mysql-connector-python` - Kết nối MySQL
- `bcrypt` - Hash mật khẩu
- `python-dotenv` - Đọc file .env

### Bước 3: Cấu hình kết nối MySQL

Chỉnh file `.env` ở thư mục gốc:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=sports_club_db
SECRET_KEY=clb-the-thao-secret-key-2024
```

### Bước 4: Tạo database và import dữ liệu mẫu

**Cách 1 (Khuyến nghị):** Chạy script Python tự động:

```bash
python scripts/seed_db.py
```

Script này sẽ:
- Tự tạo database `sports_club_db`
- Tạo đầy đủ 14 bảng
- Import dữ liệu mẫu với mật khẩu được mã hóa bcrypt đúng

**Cách 2:** Import file SQL thủ công:

```bash
mysql -u root -p < sports_club_db.sql
```

> ⚠️ Nếu dùng cách 2, mật khẩu trong seed data là plain text chưa hash. Dùng cách 1 để có mật khẩu bcrypt đúng.

### Bước 5: Chạy Flask app

```bash
python web/app.py
```

Truy cập: **http://localhost:5000**

---

## 🔑 Tài khoản đăng nhập mẫu

| Tài khoản | Mật khẩu | Vai trò |
|-----------|----------|---------|
| `admin` | `admin123` | Quản trị viên (ADMIN) |
| `hlv_tuan` | `pt123456` | Huấn luyện viên (PT) |
| `hlv_linh` | `pt123456` | Huấn luyện viên (PT) |

---

## 📁 Cấu trúc project

```
app_python_web/
├── .env                    # Cấu hình kết nối DB
├── sports_club_db.sql      # Schema SQL (tham khảo)
├── scripts/
│   └── seed_db.py         # Script khởi tạo DB + seed data
├── web/
│   ├── app.py             # Điểm khởi động Flask
│   ├── requirements_web.txt
│   ├── templates/
│   │   └── index.html     # SPA entry point
│   └── static/
│       ├── css/main.css
│       └── js/
│           ├── api.js     # HTTP client helper
│           ├── app.js     # Routing, menu, auth
│           ├── renderers.js # Các trang (UI)
│           └── utils.js   # Tiện ích chung
└── app/
    ├── database/db.py     # Connection pool MySQL
    ├── models/models.py   # Data classes
    ├── services/          # Business logic
    │   ├── member_service.py
    │   ├── invoice_service.py
    │   ├── event_service.py
    │   ├── class_service.py
    │   └── ...
    ├── routes/            # Flask Blueprints (API)
    │   ├── member_routes.py   # /api/members + /api/member-cards
    │   ├── trainer_routes.py  # /api/trainers + attendance + salary
    │   ├── dashboard_routes.py # /api/checkins + /api/dashboard
    │   ├── event_routes.py    # /api/events
    │   ├── billing_routes.py  # /api/billing
    │   └── ...
    └── utils.py           # Decorators, helpers
```

---

## ✅ Chức năng đã hoàn thiện

### Quản lý Hội viên (ADMIN)
- [x] Xem danh sách hội viên
- [x] Thêm hội viên mới (INSERT, không REPLACE INTO)
- [x] Sửa thông tin hội viên (UPDATE, không mất FK)
- [x] Xóa hội viên (kiểm tra hóa đơn chưa TT, thẻ đang ACTIVE)
- [x] Gán gói tập → tự tạo thẻ INACTIVE + hóa đơn UNPAID
- [x] Đổi gói tập (Ràng buộc hủy gói cũ nếu đang ACTIVE)

### Thẻ Hội viên (ADMIN)
- [x] Xem danh sách thẻ
- [x] Cấp thẻ mới thủ công (ACTIVE ngay)
- [x] Thu hồi/Xóa thẻ (Tự động cập nhật lại trạng thái hội viên)

### Check-in / Check-out (ADMIN, PT)
- [x] Check-in với kiểm tra: thẻ ACTIVE, hóa đơn chưa TT, đang trong CLB
- [x] Check-out
- [x] Thống kê: lượt hôm nay, đang trong CLB, 7 ngày gần nhất
- [x] Xóa bản ghi check-in

### Huấn luyện viên (ADMIN)
- [x] Thêm / Sửa / Xóa HLV
- [x] Chấm công: thêm / xóa
- [x] Tính lương tự động theo buổi dạy
- [x] Đánh dấu đã thanh toán lương

### Lớp học (ADMIN, PT)
- [x] Thêm / Sửa / Xóa lớp (Không cho xóa cứng nếu có học viên, chuyển trạng thái CANCELLED)
- [x] Đăng ký / Hủy đăng ký hội viên vào lớp
- [x] Kiểm tra thẻ ACTIVE khi đăng ký
- [x] Các trạng thái: ACTIVE, INACTIVE, FULL, CANCELLED, COMPLETED

### Sự kiện (ADMIN, PT)
- [x] Thêm / Sửa / Xóa sự kiện (Có giờ bắt đầu, giờ kết thúc)
- [x] Đăng ký / Hủy đăng ký hội viên
- [x] Kiểm tra sức chứa, không trùng

### Tài chính (ADMIN)
- [x] Xem danh sách hóa đơn
- [x] Tạo hóa đơn thủ công
- [x] Thanh toán (toàn phần hoặc một phần, không vượt số tiền còn lại)
- [x] Trạng thái: UNPAID → PARTIAL → PAID
- [x] Khi PAID: Tự kích hoạt liên kết Dịch vụ tương ứng (Thẻ/Gói tập/Lớp học/Sự kiện)

### Báo cáo (ADMIN, PT)
- [x] Doanh thu tháng / tổng
- [x] Hội viên mới, lớp hoạt động
- [x] Biểu đồ doanh thu theo tháng
- [x] Hội viên theo gói tập (doughnut)
- [x] Hóa đơn theo trạng thái
- [x] Top hội viên đóng góp

### Dashboard (ADMIN, PT)
- [x] Số liệu tổng quan
- [x] Biểu đồ doanh thu
- [x] Cảnh báo lớp học sắp đầy

---

## 🗄️ Các bảng database

| Bảng | Mô tả |
|------|-------|
| `Users` | Admin, HLV (PT) |
| `Members` | Hội viên |
| `Plans` | Gói tập |
| `MemberCards` | Thẻ hội viên |
| `CheckIns` | Lịch sử check-in/out |
| `Sports` | Môn thể thao |
| `Facilities` | Sân bãi, cơ sở |
| `Classes` | Lớp học |
| `ClassEnrollments` | Đăng ký lớp |
| `TrainerAttendance` | Chấm công HLV |
| `TrainerSalaries` | Bảng lương HLV |
| `Events` | Sự kiện |
| `EventParticipants` | Đăng ký sự kiện |
| `Invoices` | Hóa đơn |

---

## 🐛 Troubleshooting

**Lỗi kết nối MySQL:**
- Kiểm tra MySQL đang chạy
- Kiểm tra thông tin trong `.env`
- Đảm bảo user MySQL có quyền tạo database

**Lỗi import bcrypt:**
```bash
pip install bcrypt
```

**Lỗi encoding UTF-8 trên Windows:**
- Đặt terminal về UTF-8: `chcp 65001`

**Reset database:**
```bash
python scripts/seed_db.py
```

---

## 📞 Thông tin nhóm

Đề tài: **Hệ thống quản lý câu lạc bộ thể thao**  
Nhóm: Nhóm 3
