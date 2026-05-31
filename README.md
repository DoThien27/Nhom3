# 🏋️ Sports Club - Hệ thống Quản lý CLB Thể thao

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

## 📞 Thông tin nhóm

Đề tài: **Hệ thống quản lý câu lạc bộ thể thao**  
Nhóm: Nhóm 3
