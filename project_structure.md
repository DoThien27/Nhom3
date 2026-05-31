# Cấu trúc thư mục dự án

```text
./  # Thư mục gốc dự án
    .env  # Chứa các biến môi trường cấu hình (DB connection, secret keys...)
    project_structure.md  # File mô tả cấu trúc dự án này
    README.md  # Tài liệu giới thiệu và hướng dẫn chạy dự án
    app/  # Thư mục chứa mã nguồn Backend (API, logic nghiệp vụ)
        utils.py  # Các hàm tiện ích dùng chung
        __init__.py
        database/  # Cấu hình và kết nối cơ sở dữ liệu
            db.py
            __init__.py
        models/  # Chứa định nghĩa các cấu trúc bảng (Models) trong database
            models.py
            __init__.py
        routes/  # Định nghĩa các đường dẫn (endpoints) API
            auth_routes.py  # API xác thực, đăng nhập
            billing_routes.py  # API hóa đơn, thanh toán
            class_routes.py  # API quản lý lớp học
            dashboard_routes.py  # API thống kê cho dashboard
            event_routes.py  # API quản lý sự kiện
            facility_routes.py  # API quản lý cơ sở vật chất
            member_routes.py  # API quản lý hội viên
            plan_routes.py  # API quản lý các gói tập
            pt_routes.py  # API dành cho Huấn luyện viên cá nhân (PT)
            report_routes.py  # API xuất báo cáo
            trainer_routes.py  # API quản lý Huấn luyện viên
            user_routes.py  # API quản lý người dùng
            __init__.py
        services/  # Chứa logic nghiệp vụ cốt lõi, xử lý yêu cầu từ routes
            class_service.py
            dashboard_service.py
            event_service.py
            facility_service.py
            invoice_service.py
            member_service.py
            plan_service.py
            pt_service.py
            report_service.py
            sport_service.py
            user_service.py
            validators.py  # Các hàm kiểm tra dữ liệu đầu vào
            __init__.py
    images/  # Thư mục chứa hình ảnh tài liệu, minh hoạ dự án
        add_member_ui.png
        login_error_ui.png
    scripts/  # Các script độc lập dùng để hỗ trợ, test hoặc khởi tạo dữ liệu
        add_admin_class.py
        append_member_details.py
        generate_large_seed.py  # Tạo dữ liệu giả quy mô lớn
        generate_real_seed.py
        patch_class_routes.py
        patch_trainer_attendance_db.py
        patch_trainer_salaries_db.py
        schema_only.py
        seed_db.py  # Script chính để khởi tạo dữ liệu mẫu (seed data) vào database
        test_apis.py  # Script tự động test API
        test_overlap.py
        test_write_apis.py
    web/  # Thư mục chứa ứng dụng Frontend (Giao diện người dùng)
        app.py  # Server phục vụ frontend (render HTML, static files)
        requirements_web.txt  # Danh sách thư viện Python cho thư mục web
        static/  # Chứa các tệp tĩnh (CSS, JS, Hình ảnh) cho giao diện
            css/
                main.css  # File định dạng giao diện chính
            images/
                login-bg.png
                login_bg.jpg
                login_bg_orange.png
            js/
                api.js  # Các hàm gọi API từ frontend tới backend
                app.js  # Logic điều khiển chính của giao diện (SPA)
                renderers.js  # Các hàm chuyên vẽ/render HTML dựa trên dữ liệu
                utils.js  # Các hàm tiện ích frontend
        templates/  # Chứa các file HTML
            index.html  # Giao diện chính của ứng dụng
```
