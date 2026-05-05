# Phần mềm quản lý Câu lạc bộ Thể thao

Đây là ứng dụng desktop quản lý câu lạc bộ thể thao được xây dựng bằng Python, giao diện CustomTkinter và cơ sở dữ liệu MySQL.

## Công nghệ sử dụng
- Python 3.10+
- Giao diện: CustomTkinter
- Đồ thị/Báo cáo: Matplotlib
- Lịch/Date picker: tkcalendar
- Cơ sở dữ liệu: MySQL (thư viện `mysql-connector-python`)
- Mã hóa mật khẩu: `bcrypt`

## Chức năng chính sau nâng cấp
1. **Quản lý Đa Dịch Vụ**: Tích hợp các loại dịch vụ: Gói hội viên, Lớp học, Sự kiện, Đặt sân, Sản phẩm.
2. **Hóa đơn & Thanh toán Nâng cao**: 
   - Thanh toán đa dịch vụ trong cùng một hóa đơn.
   - Hỗ trợ thanh toán một phần, tính công nợ.
   - Tự động trừ/hoàn tồn kho khi mua/hủy sản phẩm.
3. **Lịch Hoạt Động & Đặt Sân**:
   - Quản lý đặt sân/phòng tập với cơ chế chống trùng lịch.
   - Bảng tổng hợp lịch hoạt động (Lớp, Sự kiện, Đặt sân) trên một giao diện thống nhất.
4. **Báo cáo & Dashboard**: Doanh thu, số lượng hội viên, biểu đồ hoạt động.
5. **Đồng bộ Tiếng Việt 100%** cho toàn bộ giao diện và định dạng dữ liệu (tiền tệ đ, ngày tháng DD/MM/YYYY).

## Cài đặt & Khởi động
1. **Clone repository và cài thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Cấu hình môi trường:**
   - Copy file `.env.example` thành `.env`
   - Điền thông tin kết nối MySQL của bạn (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME).
3. **Khởi tạo Database (Tạo bảng & Data mẫu):**
   ```bash
   python database/init_mysql_db.py
   ```
4. **Chạy ứng dụng:**
   ```bash
   python main.py
   ```

## Tài khoản Demo
- **Quản trị viên (Admin):**
  - Username: `admin`
  - Password: `1`

## Lưu ý khi dùng MySQL
- Đảm bảo MySQL Server đang chạy trước khi bật app.
- Nếu bạn cần tạo lại database từ đầu, có thể xóa bảng cũ trong MySQL hoặc chỉ cần chạy lại `python database/init_mysql_db.py` (script sử dụng `CREATE TABLE IF NOT EXISTS` nên an toàn).
