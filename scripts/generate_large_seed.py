import re

with open('scripts/seed_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

users_sql = """    cur.execute(\"\"\"INSERT INTO Users (id, username, password, fullName, role, specialty, phone, address, status) VALUES
        ('ADMIN001', 'admin', %s, 'Quản trị viên', 'ADMIN', NULL, '0901000001', 'CLB Thể thao', 'ACTIVE'),
        ('PT001', 'hlv_tuan', %s, 'Nguyễn Văn Tuấn', 'PT', 'Yoga & Pilates', '0901000002', 'Hà Nội', 'ACTIVE'),
        ('PT002', 'hlv_linh', %s, 'Trần Thị Linh', 'PT', 'Gym & Fitness', '0901000003', 'TP.HCM', 'ACTIVE'),
        ('PT003', 'hlv_hoang', %s, 'Lê Huy Hoàng', 'PT', 'Boxing & Võ thuật', '0901000004', 'Đà Nẵng', 'ACTIVE'),
        ('PT004', 'hlv_mai', %s, 'Phạm Ngọc Mai', 'PT', 'Zumba & Aerobic', '0901000005', 'Hải Phòng', 'ACTIVE'),
        ('PT005', 'hlv_dat', %s, 'Bùi Quốc Đạt', 'PT', 'Bơi lội', '0901000006', 'Cần Thơ', 'ACTIVE')
    \"\"\", (pw_admin, pw_pt, pw_pt, pw_pt, pw_pt, pw_pt))"""

sports_sql = """    cur.execute(\"\"\"INSERT INTO Sports (sport_id, sport_name, description) VALUES
        ('SP001', 'Yoga', 'Các bài tập yoga cải thiện sức khỏe và sự linh hoạt'),
        ('SP002', 'Gym', 'Tập luyện thể hình, nâng tạ tại phòng gym'),
        ('SP003', 'Cầu lông', 'Thi đấu và luyện tập cầu lông'),
        ('SP004', 'Bơi lội', 'Học bơi và luyện tập bơi lội các kiểu'),
        ('SP005', 'Boxing', 'Rèn luyện võ thuật, tăng cường thể lực và phản xạ'),
        ('SP006', 'Zumba', 'Tập luyện thể dục nhịp điệu với nhạc Latin sôi động')
    \"\"\")"""

facs_sql = """    cur.execute(\"\"\"INSERT INTO Facilities (facility_id, facility_name, location, capacity, sport_id) VALUES
        ('FAC001', 'Phòng Yoga Tầng 1', 'Tầng 1 - Khu A', 30, 'SP001'),
        ('FAC002', 'Phòng Yoga VIP', 'Tầng 4 - Khu C', 15, 'SP001'),
        ('FAC003', 'Phòng Gym Tầng 2', 'Tầng 2 - Khu B', 50, 'SP002'),
        ('FAC004', 'Khu tạ tự do', 'Tầng 2 - Khu B', 20, 'SP002'),
        ('FAC005', 'Phòng Cardio', 'Tầng 3 - Khu B', 40, 'SP002'),
        ('FAC006', 'Sân cầu lông số 1', 'Tầng 3 - Khu C', 20, 'SP003'),
        ('FAC007', 'Sân cầu lông số 2', 'Tầng 3 - Khu C', 20, 'SP003'),
        ('FAC008', 'Hồ bơi ngoài trời', 'Khu ngoài trời', 100, 'SP004'),
        ('FAC009', 'Hồ bơi trong nhà', 'Khu trong nhà', 50, 'SP004'),
        ('FAC010', 'Sàn Boxing', 'Tầng 4 - Khu A', 20, 'SP005'),
        ('FAC011', 'Phòng tập Zumba', 'Tầng 1 - Khu C', 40, 'SP006')
    \"\"\")"""

members_sql = "    cur.execute(\"\"\"INSERT INTO Members\n        (id, fullName, phone, email, joinDate, birthDate, gender, homeTown, activePlanId, assignedPTId, status)\n        VALUES\n"
members_list = []
for i in range(1, 21):
    pt_id = f"PT00{(i%5)+1}"
    plan_id = f"PLN00{(i%4)+1}"
    status = "ACTIVE" if i <= 18 else "PENDING"
    pt = f"'{pt_id}'" if status == 'ACTIVE' else "NULL"
    plan = f"'{plan_id}'" if status == 'ACTIVE' else "NULL"
    members_list.append(f"        ('MBR{i:03d}', 'Hội viên {i}', '0912345{i:03d}', 'member{i}@email.com', '2025-01-01', '1995-01-01', 'Nam', 'Hà Nội', {plan}, {pt}, '{status}')")
members_sql += ",\n".join(members_list) + "\n    \"\"\")"

cards_sql = "    cur.execute(\"\"\"INSERT INTO MemberCards (id, memberId, planId, cardNumber, issueDate, expiryDate, status) VALUES\n"
cards_list = []
for i in range(1, 19):
    plan_id = f"PLN00{(i%4)+1}"
    cards_list.append(f"        ('CARD{i:03d}', 'MBR{i:03d}', '{plan_id}', 'CARD{i:03d}VIP', '2025-01-01', '2027-01-01', 'ACTIVE')")
cards_sql += ",\n".join(cards_list) + "\n    \"\"\")"

# Thay thế các đoạn code trong seed_db.py
def replace_block(content, start_marker, end_marker, new_text):
    start = content.find(start_marker)
    if start == -1: return content
    end = content.find(end_marker, start)
    if end == -1: return content
    return content[:start] + start_marker + "\n" + new_text + "\n\n" + content[end:]

content = replace_block(content, "# ─── Seed Users ───────────────────────────────────────────────────────────", "# ─── Seed Sports ──────────────────────────────────────────────────────────", users_sql)
content = replace_block(content, "# ─── Seed Sports ──────────────────────────────────────────────────────────", "# ─── Seed Facilities ──────────────────────────────────────────────────────", sports_sql)
content = replace_block(content, "# ─── Seed Facilities ──────────────────────────────────────────────────────", "# ─── Seed Plans ───────────────────────────────────────────────────────────", facs_sql)
content = replace_block(content, "# ─── Seed Members ─────────────────────────────────────────────────────────", "# ─── Seed MemberCards ─────────────────────────────────────────────────────", members_sql)
content = replace_block(content, "# ─── Seed MemberCards ─────────────────────────────────────────────────────", "# ─── Seed Invoices ────────────────────────────────────────────────────────", cards_sql)

with open('scripts/seed_db.py', 'w', encoding='utf-8') as f:
    f.write(content)
