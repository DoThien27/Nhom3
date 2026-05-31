import random
import datetime

with open('scripts/schema_only.py', 'r', encoding='utf-8') as f:
    schema_code = f.read()

# Dữ liệu mẫu
first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
mid_names_nam = ["Văn", "Hữu", "Thái", "Minh", "Đức", "Hoàng", "Quang", "Đình", "Tuấn", "Thành", "Gia", "Hải"]
mid_names_nu = ["Thị", "Ngọc", "Thu", "Phương", "Thanh", "Bích", "Hồng", "Mai", "Kiều", "Diễm", "Kim", "Bảo"]
last_names_nam = ["An", "Bảo", "Cường", "Dũng", "Đạt", "Hùng", "Hải", "Khang", "Khoa", "Long", "Nam", "Phong", "Phúc", "Quân", "Sơn", "Tài", "Thắng", "Thiên", "Trung", "Tuấn", "Việt", "Vinh", "Khánh"]
last_names_nu = ["Anh", "Chi", "Châu", "Dung", "Hà", "Hằng", "Hoa", "Huyền", "Linh", "Lan", "Mai", "Ngân", "Nhung", "Oanh", "Quyên", "Tâm", "Thảo", "Trang", "Uyên", "Vy", "Yến", "My"]

def gen_name(gender):
    f = random.choice(first_names)
    if gender == 'Nam':
        m = random.choice(mid_names_nam)
        l = random.choice(last_names_nam)
    else:
        m = random.choice(mid_names_nu)
        l = random.choice(last_names_nu)
    return f"{f} {m} {l}"

pts = [
    {'id': 'PT001', 'name': 'Trần Thế Anh', 'gender': 'Nam', 'spec': 'Gym & Thể hình'},
    {'id': 'PT002', 'name': 'Lê Thu Thủy', 'gender': 'Nữ', 'spec': 'Yoga & Pilates'},
    {'id': 'PT003', 'name': 'Nguyễn Hoàng Khang', 'gender': 'Nam', 'spec': 'Boxing & Võ thuật'},
    {'id': 'PT004', 'name': 'Phạm Ngọc Trâm', 'gender': 'Nữ', 'spec': 'Zumba & Aerobic'},
    {'id': 'PT005', 'name': 'Bùi Quốc Đạt', 'gender': 'Nam', 'spec': 'Bơi lội & Thể lực'}
]

sports = [
    ('SP001', 'Yoga', 'Rèn luyện sự dẻo dai và tĩnh tâm'),
    ('SP002', 'Gym', 'Khu vực tập luyện tạ tự do và máy'),
    ('SP003', 'Boxing', 'Sàn đấu võ thuật và bao cát'),
    ('SP004', 'Zumba', 'Phòng tập nhảy hiện đại'),
    ('SP005', 'Bơi lội', 'Khu vực hồ bơi chuẩn Olympic'),
    ('SP006', 'Cầu lông', 'Sân tập và thi đấu cầu lông')
]

facs = [
    ('FAC001', 'Phòng Yoga ZEN 1', 'Tầng 2 - Khu A', 25, 'SP001'),
    ('FAC002', 'Phòng Yoga ZEN 2', 'Tầng 2 - Khu B', 20, 'SP001'),
    ('FAC003', 'Phòng Tạ Free-Weight', 'Tầng 1 - Khu A', 50, 'SP002'),
    ('FAC004', 'Phòng Máy Cardio', 'Tầng 1 - Khu B', 40, 'SP002'),
    ('FAC005', 'Sàn Boxing Tiêu chuẩn', 'Tầng 3 - Khu A', 15, 'SP003'),
    ('FAC006', 'Phòng Studio Nhảy', 'Tầng 3 - Khu B', 40, 'SP004'),
    ('FAC007', 'Hồ Bơi Vô Cực', 'Tầng thượng', 100, 'SP005'),
    ('FAC008', 'Sân Cầu Lông Số 1', 'Tầng 4', 16, 'SP006'),
    ('FAC009', 'Sân Cầu Lông Số 2', 'Tầng 4', 16, 'SP006')
]

plans = [
    ('PLN001', 'Gói Classic 1 Tháng', 'MEMBERSHIP', 600000, 'Tập luyện tự do tất cả dịch vụ cơ bản trong 30 ngày', 1),
    ('PLN002', 'Gói Premium 3 Tháng', 'MEMBERSHIP', 1500000, 'Tập tự do + Tặng 1 buổi PT + Dùng khăn miễn phí', 3),
    ('PLN003', 'Gói VIP 1 Năm', 'MEMBERSHIP', 5000000, 'Tập tự do + Full dịch vụ (Khăn, nước, xông hơi, locker)', 12),
    ('PLN004', 'Gói PT Định Hình (10 Buổi)', 'PT', 3500000, 'Gói tập 1 kèm 1 chuyên sâu cải thiện vóc dáng', 2)
]

code = schema_code
code += """
    pw_admin  = hash_pw('admin123')
    pw_pt     = hash_pw('pt123456')

    # ─── Seed Users ───────────────────────────────────────────────────────────
    cur.execute(\"\"\"INSERT INTO Users (id, username, password, fullName, role, specialty, phone, address, status) VALUES
        ('ADMIN001', 'admin', %s, 'Quản trị viên Hệ thống', 'ADMIN', NULL, '0900000000', 'Văn phòng TT', 'ACTIVE'),
"""
users_sql = []
for pt in pts:
    users_sql.append(f"        ('{pt['id']}', 'hlv_{pt['id'].lower()}', %s, '{pt['name']}', 'PT', '{pt['spec']}', '090{random.randint(1000000, 9999999)}', 'Hà Nội', 'ACTIVE')")
code += ",\n".join(users_sql)
code += "\n    \"\"\", (pw_admin, pw_pt, pw_pt, pw_pt, pw_pt, pw_pt))\n\n"

code += "    # ─── Seed Sports ──────────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO Sports (sport_id, sport_name, description) VALUES\n"
code += ",\n".join([f"        ('{s[0]}', '{s[1]}', '{s[2]}')" for s in sports])
code += "\n    \"\"\")\n\n"

code += "    # ─── Seed Facilities ──────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO Facilities (facility_id, facility_name, location, capacity, sport_id) VALUES\n"
code += ",\n".join([f"        ('{f[0]}', '{f[1]}', '{f[2]}', {f[3]}, '{f[4]}')" for f in facs])
code += "\n    \"\"\")\n\n"

code += "    # ─── Seed Plans ───────────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO Plans (id, name, type, price, description, durationMonths) VALUES\n"
code += ",\n".join([f"        ('{p[0]}', '{p[1]}', '{p[2]}', {p[3]}, '{p[4]}', {p[5]})" for p in plans])
code += "\n    \"\"\")\n\n"

# Generate 30 Members
members = []
cards = []
invoices = []
checkins = []

for i in range(1, 31):
    gender = random.choice(['Nam', 'Nữ'])
    name = gen_name(gender)
    phone = f"09{random.randint(10000000, 99999999)}"
    email = f"{name.split()[-1].lower()}{i}@gmail.com"
    birth_year = random.randint(1985, 2005)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    
    plan = random.choice(plans)
    pt = random.choice(pts) if random.random() > 0.6 else None
    
    status = "ACTIVE" if i <= 25 else "EXPIRED"
    pt_val = f"'{pt['id']}'" if pt else "NULL"
    
    join_date = datetime.date(2024, random.randint(1, 12), random.randint(1, 28))
    exp_date = join_date + datetime.timedelta(days=plan[5]*30)
    
    members.append(f"        ('MBR{i:03d}', '{name}', '{phone}', '{email}', '{join_date}', '{birth_year}-{birth_month:02d}-{birth_day:02d}', '{gender}', 'Hà Nội', '{plan[0]}', {pt_val}, '{status}')")
    
    if status == 'ACTIVE':
        cards.append(f"        ('CRD{i:03d}', 'MBR{i:03d}', '{plan[0]}', 'CARD{random.randint(10000,99999)}{i}', '{join_date}', '{exp_date}', 'ACTIVE')")
        invoices.append(f"        ('INV{i:03d}', 'MBR{i:03d}', 'PLAN', '{plan[0]}', {plan[3]}, 0, {plan[3]}, {plan[3]}, 0, '{join_date}', 'TRANSFER', 'PAID', 'Đăng ký {plan[1]}')")
        
        # Checkins
        for j in range(random.randint(2, 5)):
            c_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30), hours=random.randint(1, 10))
            co_time = c_time + datetime.timedelta(hours=random.randint(1, 2))
            checkins.append(f"        ('CHK{i:03d}_{j}', 'MBR{i:03d}', 'CRD{i:03d}', '{c_time.strftime('%Y-%m-%d %H:%M:%S')}', '{co_time.strftime('%Y-%m-%d %H:%M:%S')}', 'CARD', 'Quét thẻ thành công')")


code += "    # ─── Seed Members ─────────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO Members (id, fullName, phone, email, joinDate, birthDate, gender, homeTown, activePlanId, assignedPTId, status) VALUES\n"
code += ",\n".join(members)
code += "\n    \"\"\")\n\n"

code += "    # ─── Seed MemberCards ─────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO MemberCards (id, memberId, planId, cardNumber, issueDate, expiryDate, status) VALUES\n"
code += ",\n".join(cards)
code += "\n    \"\"\")\n\n"

code += "    # ─── Seed Invoices ────────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO Invoices (id, memberId, sourceType, sourceId, totalAmount, discountAmount, finalAmount, paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note) VALUES\n"
code += ",\n".join(invoices)
code += "\n    \"\"\")\n\n"

code += "    # ─── Seed CheckIns ────────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO CheckIns (id, memberId, cardId, checkInTime, checkOutTime, checkType, note) VALUES\n"
code += ",\n".join(checkins)
code += "\n    \"\"\")\n\n"

classes = [
    ('CLS001', 'Yoga Thiền Định', 'PT002', 'SP001', 'FAC001', '06:00 - 07:30', 'Thứ 2,Thứ 4,Thứ 6', 25, 0, 'ACTIVE', '2025-06-01', '2025-08-30'),
    ('CLS002', 'Yoga Cân Bằng', 'PT002', 'SP001', 'FAC002', '18:00 - 19:30', 'Thứ 3,Thứ 5', 20, 0, 'ACTIVE', '2025-06-15', '2025-09-15'),
    ('CLS003', 'Boxing Đối Kháng', 'PT003', 'SP003', 'FAC005', '19:00 - 20:30', 'Thứ 2,Thứ 4,Thứ 6', 15, 0, 'ACTIVE', '2025-06-01', '2025-07-31'),
    ('CLS004', 'Zumba Đốt Mỡ', 'PT004', 'SP004', 'FAC006', '17:30 - 18:30', 'Thứ 3,Thứ 5,Thứ 7', 40, 0, 'ACTIVE', '2025-06-01', '2025-12-31'),
    ('CLS005', 'Dạy Bơi Sải', 'PT005', 'SP005', 'FAC007', '08:00 - 09:30', 'Chủ nhật', 10, 500000, 'ACTIVE', '2025-06-01', '2025-06-30')
]

code += "    # ─── Seed Classes ─────────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO Classes (id, name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status, startDate, endDate) VALUES\n"
code += ",\n".join([f"        ('{c[0]}', '{c[1]}', '{c[2]}', '{c[3]}', '{c[4]}', '{c[5]}', '{c[6]}', {c[7]}, {c[8]}, '{c[9]}', '{c[10]}', '{c[11]}')" for c in classes])
code += "\n    \"\"\")\n\n"

enrolls = []
enroll_idx = 1
for c in classes:
    for _ in range(random.randint(5, 12)):
        m_id = f"MBR{random.randint(1, 25):03d}"
        if f"        ('{c[0]}', '{m_id}')" not in enrolls:
            enrolls.append(f"        ('{c[0]}', '{m_id}')")

code += "    # ─── Seed ClassEnrollments ────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO ClassEnrollments (classId, memberId) VALUES\n"
code += ",\n".join(enrolls)
code += "\n    \"\"\")\n\n"

events = [
    ('EVT001', 'Đại hội Thể hình Cơ bắp', 'Cuộc thi khoe nét đẹp hình thể cơ bắp nam nữ', '2025-07-15', '09:00', 'Sân khấu lớn', 'FAC004', 100, 200000, 'UPCOMING'),
    ('EVT002', 'Giao lưu Yoga Cộng đồng', 'Buổi tập yoga chung kết nối cộng đồng 500 người', '2025-08-20', '06:00', 'Công viên Trung tâm', 'FAC001', 500, 0, 'UPCOMING'),
    ('EVT003', 'Giải Vô địch Cầu Lông CLB', 'Giải đấu nội bộ chọn ra tay vợt xuất sắc nhất', '2025-09-02', '08:00', 'Sân Cầu Lông 1 & 2', 'FAC008', 32, 100000, 'UPCOMING')
]
code += "    # ─── Seed Events ──────────────────────────────────────────────────────────\n"
code += "    cur.execute(\"\"\"INSERT INTO Events (id, name, description, date, time, location, facilityId, capacity, price, status) VALUES\n"
code += ",\n".join([f"        ('{e[0]}', '{e[1]}', '{e[2]}', '{e[3]}', '{e[4]}', '{e[5]}', '{e[6]}', {e[7]}, {e[8]}, '{e[9]}')" for e in events])
code += "\n    \"\"\")\n\n"

code += """
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cur.close()
    conn.close()

    print("=" * 55)
    print("[OK] Database khoi tao thanh cong voi du lieu THUC TE!")
    print("=" * 55)
    print(f"  Database : {DB_NAME}")
    print("  Tai khoan mac dinh:")
    print("    admin     / admin123     (Quan tri vien)")
    print("    hlv_pt001 / pt123456     (Huan luyen vien Tran The Anh)")
    print("=" * 55)

if __name__ == '__main__':
    run()
"""

with open('scripts/seed_db.py', 'w', encoding='utf-8') as f:
    f.write(code)
