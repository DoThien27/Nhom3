"""
Khởi tạo CSDL sports_club_db — Phần mềm Quản lý CLB Thể Thao.
LƯU Ý: Chạy script này sẽ XÓA TOÀN BỘ DỮ LIỆU CŨ và tạo lại CSDL mẫu mới.
"""
import mysql.connector
from datetime import date, timedelta, datetime
import random
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG_SERVER = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "")
}
DB_NAME = os.environ.get("DB_NAME", "sports_club_db")


def init_db():
    conn = mysql.connector.connect(**DB_CONFIG_SERVER)
    cur = conn.cursor()

    print(f"[1/9] Dropping & re-creating database {DB_NAME}...")
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cur.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.execute(f"USE {DB_NAME}")

    # ───────────────────────── CREATE TABLES ─────────────────────────
    print("[2/9] Creating tables...")
    tables = [
        """CREATE TABLE Users (
            id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            fullName VARCHAR(150),
            role VARCHAR(50),
            specialty VARCHAR(100),
            activeStudents INT DEFAULT 0
        )""",
        """CREATE TABLE Plans (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(150),
            type VARCHAR(50),
            price DECIMAL(12,2),
            description TEXT,
            durationMonths INT,
            sessions INT
        )""",
        """CREATE TABLE Members (
            id VARCHAR(50) PRIMARY KEY,
            fullName VARCHAR(150),
            phone VARCHAR(50),
            email VARCHAR(150),
            joinDate DATE,
            status VARCHAR(50),
            weight DECIMAL(5,2),
            activePlanId VARCHAR(50),
            expiryDate DATE,
            assignedPTId VARCHAR(50),
            username VARCHAR(100),
            password VARCHAR(255),
            homeTown VARCHAR(255),
            FOREIGN KEY (activePlanId) REFERENCES Plans(id) ON DELETE SET NULL,
            FOREIGN KEY (assignedPTId) REFERENCES Users(id) ON DELETE SET NULL
        )""",

        """CREATE TABLE Invoices (
            id VARCHAR(50) PRIMARY KEY,
            memberId VARCHAR(50),
            total DECIMAL(12,2) DEFAULT 0,
            discount_amount DECIMAL(12,2) DEFAULT 0,
            final_amount DECIMAL(12,2) DEFAULT 0,
            paid_amount DECIMAL(12,2) DEFAULT 0,
            remaining_amount DECIMAL(12,2) DEFAULT 0,
            date DATETIME,
            method VARCHAR(50) DEFAULT 'CASH',
            payment_status VARCHAR(20) DEFAULT 'UNPAID',
            note TEXT,
            created_by VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (memberId) REFERENCES Members(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE InvoiceItems (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoiceId VARCHAR(50),
            item_type VARCHAR(20) DEFAULT 'OTHER',
            reference_id VARCHAR(50),
            item_name VARCHAR(255),
            quantity INT DEFAULT 1,
            unit_price DECIMAL(12,2) DEFAULT 0,
            discount_amount DECIMAL(12,2) DEFAULT 0,
            line_total DECIMAL(12,2) DEFAULT 0,
            item_note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoiceId) REFERENCES Invoices(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE Events (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(150),
            description TEXT,
            date DATE,
            time VARCHAR(50),
            location VARCHAR(255),
            capacity INT,
            price DECIMAL(12,2) DEFAULT 0,
            status VARCHAR(50)
        )""",
        """CREATE TABLE EventParticipants (
            id VARCHAR(50) PRIMARY KEY,
            eventId VARCHAR(50),
            memberId VARCHAR(50),
            memberName VARCHAR(150),
            registerDate DATETIME,
            status VARCHAR(50),
            FOREIGN KEY (eventId) REFERENCES Events(id) ON DELETE CASCADE,
            FOREIGN KEY (memberId) REFERENCES Members(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE Classes (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(150),
            trainerId VARCHAR(50),
            time VARCHAR(100),
            dayOfWeek VARCHAR(100),
            capacity INT,
            price DECIMAL(12,2) DEFAULT 0,
            FOREIGN KEY (trainerId) REFERENCES Users(id) ON DELETE SET NULL
        )""",
        """CREATE TABLE ClassEnrollments (
            classId VARCHAR(50),
            memberId VARCHAR(50),
            PRIMARY KEY (classId, memberId),
            FOREIGN KEY (classId) REFERENCES Classes(id) ON DELETE CASCADE,
            FOREIGN KEY (memberId) REFERENCES Members(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE Sports (
            sport_id VARCHAR(50) PRIMARY KEY,
            sport_name VARCHAR(150),
            description TEXT,
            status VARCHAR(20) DEFAULT 'ACTIVE',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE Facilities (
            facility_id VARCHAR(50) PRIMARY KEY,
            facility_name VARCHAR(150),
            facility_type VARCHAR(100),
            location VARCHAR(255),
            capacity INT DEFAULT 0,
            rental_price DECIMAL(12,2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'ACTIVE',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
    ]
    for q in tables:
        cur.execute(q)

    # ───────────────────────── USERS ─────────────────────────
    print("[3/9] Inserting users...")
    users = [
        ("U001", "admin",    "admin123",  "Quản trị viên",    "ADMIN",        "Hệ thống",    0),
        ("U002", "hlv_son",  "hlv123",    "Nguyễn Văn Sơn",   "MANAGER",      "Thể hình",    8),
        ("U003", "hlv_lan",  "hlv123",    "Trần Thị Lan",     "PT",           "Yoga & Pilates", 7),
        ("U004", "hlv_duc",  "hlv123",    "Phạm Tiến Đức",    "PT",           "Boxing & Cardio", 5),
        ("U005", "le_thu",   "nv123",     "Lê Thị Thu",       "RECEPTIONIST", "Lễ tân",      0),
    ]
    hashed_users = []
    for u in users:
        pwd = u[2]
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if pwd else pwd
        hashed_users.append((u[0], u[1], hashed, u[3], u[4], u[5], u[6]))

    cur.executemany(
        "INSERT INTO Users VALUES (%s,%s,%s,%s,%s,%s,%s)",
        hashed_users
    )

    # ───────────────────────── PLANS ─────────────────────────
    print("[4/9] Inserting plans...")
    cur.executemany(
        "INSERT INTO Plans VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [
            ("P001", "Gói Cơ Bản (1 tháng)",   "MEMBERSHIP", 500000,  "Truy cập phòng tập cơ bản, giờ hành chính", 1,  0),
            ("P002", "Gói Standard (3 tháng)",  "MEMBERSHIP", 1200000, "Truy cập toàn bộ thiết bị, 7 ngày/tuần",   3,  0),
            ("P003", "Gói VIP (6 tháng)",       "MEMBERSHIP", 2200000, "Toàn bộ thiết bị + 2 buổi PT/tháng",       6,  0),
            ("P004", "Gói Pro (1 năm)",         "MEMBERSHIP", 4000000, "Truy cập VIP + PT không giới hạn",         12, 0),
            ("P005", "Yoga Cơ Bản (12 buổi)",   "CLASS",      800000,  "Lớp yoga 12 buổi với HLV Lan",             1,  12),
            ("P006", "PT cá nhân (10 buổi)",    "PT",         3000000, "10 buổi tập 1-1 với PT chuyên nghiệp",     1,  10),
        ]
    )

    # ───────────────────────── MEMBERS (15 người) ─────────────────────────
    print("[5/9] Inserting members...")
    members = [
        # id, fullName, phone, email, joinDate, status, weight, planId, expiryDate, ptId, username, pwd, hometown
        ("M001","Phạm Văn Nam",       "0912345678","nam@gmail.com",    "2024-01-15","ACTIVE",  75.5,78.0,"P002","2024-04-15","U003","nam01",   "123456",None,"Hà Nội"),
        ("M002","Lê Hoàng Anh",       "0987654321","anh@gmail.com",    "2024-01-20","ACTIVE",  62.0,65.0,"P003","2024-07-20","U002","anh_lh",  "123456",None,"Hải Phòng"),
        ("M003","Nguyễn Thùy Chi",    "0933445566","chi@gmail.com",    "2024-02-05","ACTIVE",  50.5,52.0,"P004","2025-02-05","U003","chi_nt",  "123456",None,"Đà Nẵng"),
        ("M004","Trần Minh Khoa",     "0911223344","khoa@gmail.com",   "2024-02-10","ACTIVE",  80.0,82.5,"P001","2024-03-10","U004","khoa_tm", "123456",None,"TP.HCM"),
        ("M005","Đỗ Thị Hoa",         "0944556677","hoa@gmail.com",    "2024-02-20","ACTIVE",  53.0,55.0,"P005","2024-03-20","U003","hoa_dt",  "123456",None,"Cần Thơ"),
        ("M006","Ngô Quốc Hùng",      "0966778899","hung@gmail.com",   "2024-03-01","ACTIVE",  90.0,92.0,"P002","2024-06-01","U004","hung_nq", "123456",None,"Hà Nội"),
        ("M007","Vũ Thị Hằng",        "0977889900","hang@gmail.com",   "2024-03-15","ACTIVE",  57.0,58.5,"P006","2024-04-15","U002","hang_vt", "123456",None,"Hải Dương"),
        ("M008","Bùi Đức Thắng",      "0988990011","thang@gmail.com",  "2024-03-20","EXPIRED", 85.0,86.0,"P001","2024-04-20","U004","thang_bd","123456",None,"Nghệ An"),
        ("M009","Phạm Lan Anh",        "0922334455","lanh@gmail.com",   "2024-04-01","ACTIVE",  48.0,49.5,"P003","2024-07-01","U003","lanh_pl", "123456",None,"Hà Nội"),
        ("M010","Lý Hoàng Nam",        "0933556677","hnam@gmail.com",   "2024-04-10","ACTIVE",  68.0,70.0,"P002","2024-07-10","U002","hnam_lh", "123456",None,"TP.HCM"),
        ("M011","Đinh Thị Ngọc",       "0944667788","ngoc@gmail.com",   "2024-04-15","ACTIVE",  55.0,56.0,"P004","2025-04-15","U003","ngoc_dt", "123456",None,"Huế"),
        ("M012","Cao Văn Tú",          "0955778899","tu@gmail.com",     "2024-05-01","ACTIVE",  72.0,74.0,"P002","2024-08-01","U004","tu_cv",   "123456",None,"Hà Nội"),
        ("M013","Trịnh Quỳnh Anh",    "0966889900","qanh@gmail.com",   "2024-05-10","EXPIRED", 46.0,47.0,"P005","2024-06-10","U003","qanh_tq", "123456",None,"Nam Định"),
        ("M014","Hoàng Minh Tú",       "0977990011","mtu@gmail.com",    "2024-06-01","ACTIVE",  78.0,80.0,"P003","2024-12-01","U002","mtu_hm",  "123456",None,"Bắc Ninh"),
        ("M015","Phan Thị Thanh",      "0988001122","thanh@gmail.com",  "2024-06-15","PENDING", 51.0,51.0,"P001","2024-07-15","U003","thanh_pt","123456",None,"TP.HCM"),
    ]
    hashed_members = []
    for m in members:
        pwd = m[12]
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if pwd else pwd
        hashed_members.append(m[:7] + m[8:12] + (hashed,) + (m[14],))

    cur.executemany(
        "INSERT INTO Members (id,fullName,phone,email,joinDate,status,weight,"
        "activePlanId,expiryDate,assignedPTId,username,password,homeTown) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        hashed_members
    )


    # ───────────────────────── EVENTS (giải đấu/sự kiện thể thao) ─────────────────────────
    print("[7/9] Inserting events...")
    cur.executemany(
        "INSERT INTO Events VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        [
            ("E001","Giải Bóng Đá Nội Bộ 2024",       "Giải đấu bóng đá giao hữu giữa các hội viên CLB",       "2024-06-15","08:00","Sân bóng đá mini",    150, 50000, "UPCOMING"),
            ("E002","Giải Cầu Lông Thành Viên 2024",    "Thi đấu cầu lông theo thể thức loại trực tiếp",         "2024-05-20","06:30","Sân cầu lông số 1", 40, 0, "UPCOMING"),
            ("E003","Ngày Hội Thể Thao CLB 2024",      "Liên hoan thể thao cuối năm cho toàn bộ hội viên",    "2024-08-10","09:00","Sân ngoài trời", 300, 100000, "UPCOMING"),
            ("E004","Workshop Dinh Dưỡng Thể Thao",    "Chuyên gia chia sẻ về chế độ dinh dưỡng cho VDV",  "2024-05-05","14:00","Phòng hội thảo",  80, 0, "COMPLETED"),
            ("E005","Giải Giao Hữu Võ Thuật",          "Buổi biểu diễn và thi đấu võ thuật giao hữu",       "2024-04-20","15:00","Phòng tập võ",     100, 20000, "COMPLETED"),
            ("E006","Khai Giảng Lớp Bơi Lội 2024",    "Lễ khai giảng lớp bơi lội dành cho mọi lứa tuổi",   "2024-07-01","18:00","Hồ bơi",         60, 0, "UPCOMING"),
        ]
    )

    # ───────────────────────── CLASSES ─────────────────────────
    print("[8/9] Inserting classes & enrollments...")
    cur.executemany(
        "INSERT INTO Classes VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [
            ("C001","Yoga Trưa",        "U003","12:00","Thứ 2, 4, 6",  15, 200000),
            ("C002","Boxing Cơ Bản",    "U004","18:30","Thứ 3, 5, 7",  20, 250000),
            ("C003","Zumba Dance",      "U004","19:00","Thứ 2, 4, 6",  25, 150000),
            ("C004","Thể hình cơ bản",  "U002","07:00","Thứ 2 đến 6",  30, 0),
            ("C005","Pilates",          "U003","08:00","Thứ 3, 5",     12, 300000),
        ]
    )
    enrollments = [
        ("C001","M001"),("C001","M003"),("C001","M005"),("C001","M007"),("C001","M009"),
        ("C001","M011"),("C001","M013"),
        ("C002","M002"),("C002","M004"),("C002","M006"),("C002","M008"),("C002","M010"),
        ("C003","M003"),("C003","M005"),("C003","M007"),("C003","M012"),("C003","M014"),
        ("C004","M001"),("C004","M002"),("C004","M006"),("C004","M010"),("C004","M012"),
        ("C004","M014"),("C004","M015"),
        ("C005","M003"),("C005","M009"),("C005","M011"),("C005","M015"),
    ]
    cur.executemany("INSERT INTO ClassEnrollments VALUES (%s,%s)", enrollments)

    # ───────────────────────── SPORTS ─────────────────────────
    print("[8b/9] Inserting sports...")
    cur.executemany(
        "INSERT INTO Sports (sport_id, sport_name, description, status) VALUES (%s,%s,%s,%s)",
        [
            ("SP001", "Bóng đá",     "Môn bóng đá 11 người và bóng đá mini",     "ACTIVE"),
            ("SP002", "Cầu lông",   "Môn cầu lông đơn và đôi nam nữ",          "ACTIVE"),
            ("SP003", "Bóng chuyền","Môn bóng chuyền trong nhà và ngoài trời", "ACTIVE"),
            ("SP004", "Bơi lội",   "Môn bơi lội các kiểu tự do, ếch",        "ACTIVE"),
            ("SP005", "Yoga",       "Các bài tập yoga, thiền định, pilates",   "ACTIVE"),
            ("SP006", "Gym",        "Tập thể hình, tạ tự do, máy tập",         "ACTIVE"),
            ("SP007", "Võ thuật",   "Boxing, karate, taekwondo, judo",        "ACTIVE"),
        ]
    )

    # ───────────────────────── FACILITIES ─────────────────────────
    print("[8c/9] Inserting facilities...")
    cur.executemany(
        "INSERT INTO Facilities (facility_id, facility_name, facility_type, location, capacity, rental_price, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [
            ("F001", "Sân bóng đá mini",     "Sân ngoài trời",  "Khu A", 22,  300000, "ACTIVE"),
            ("F002", "Sân cầu lông số 1",  "Sân trong nhà",   "Khu B", 6,   100000, "ACTIVE"),
            ("F003", "Sân cầu lông số 2",  "Sân trong nhà",   "Khu B", 6,   100000, "ACTIVE"),
            ("F004", "Phòng yoga",            "Phòng trong nhà", "Khu C", 25,  150000, "ACTIVE"),
            ("F005", "Phòng gym",             "Phòng trong nhà", "Khu C", 50,   50000, "ACTIVE"),
            ("F006", "Hồ bơi",               "Ngoài trời",       "Khu D", 100,  80000, "ACTIVE"),
            ("F007", "Sân bóng chuyền",      "Sân ngoài trời",  "Khu A", 12,  120000, "ACTIVE"),
            ("F008", "Phòng võ thuật",        "Phòng trong nhà", "Khu C", 30,   80000, "ACTIVE"),
        ]
    )

    # ───────────────────────── INVOICES (40+ hóa đơn trải 6 tháng) ─────────────────────────
    print("[9/9] Inserting invoices...")
    # Dữ liệu hóa đơn: (invoice_id, member_id, ngay, phuong_thuc, items)
    # items = list of (ten, so_luong, gia)
    invoice_data = [
        # Tháng 1/2024
        ("INV001","M001","2024-01-15","TRANSFER",  [("Gói Standard 3 tháng",1,1200000)]),
        ("INV002","M002","2024-01-20","CASH",       [("Gói VIP 6 tháng",1,2200000)]),
        ("INV003","M003","2024-01-25","E-WALLET",   [("Whey Protein Gold",1,1500000),("Nước tăng lực Sting",2,15000)]),

        # Tháng 2/2024
        ("INV004","M003","2024-02-05","TRANSFER",   [("Gói Pro 1 năm",1,4000000)]),
        ("INV005","M004","2024-02-10","CASH",        [("Gói Cơ Bản 1 tháng",1,500000),("Găng tay tập gym",1,250000)]),
        ("INV006","M005","2024-02-20","E-WALLET",    [("Yoga Cơ Bản 12 buổi",1,800000)]),
        ("INV007","M001","2024-02-22","CASH",        [("BCAA 3000mg",1,800000),("Nước khoáng Lavie",5,10000)]),
        ("INV008","M002","2024-02-28","TRANSFER",    [("PT cá nhân 10 buổi",1,3000000)]),

        # Tháng 3/2024
        ("INV009","M006","2024-03-01","TRANSFER",    [("Gói Standard 3 tháng",1,1200000)]),
        ("INV010","M007","2024-03-15","CASH",         [("PT cá nhân 10 buổi",1,3000000)]),
        ("INV011","M008","2024-03-20","E-WALLET",     [("Gói Cơ Bản 1 tháng",1,500000)]),
        ("INV012","M004","2024-03-25","CASH",         [("Thảm tập Yoga 6mm",1,350000),("Nước tăng lực Sting",3,15000)]),
        ("INV013","M005","2024-03-28","TRANSFER",     [("Creatine Monohydrate",1,500000),("Bình nước 1.5L",1,120000)]),

        # Tháng 4/2024
        ("INV014","M009","2024-04-01","TRANSFER",    [("Gói VIP 6 tháng",1,2200000)]),
        ("INV015","M010","2024-04-10","CASH",         [("Gói Standard 3 tháng",1,1200000)]),
        ("INV016","M011","2024-04-15","E-WALLET",     [("Gói Pro 1 năm",1,4000000)]),
        ("INV017","M003","2024-04-18","CASH",         [("Whey Protein Gold",1,1500000),("Creatine Monohydrate",1,500000)]),
        ("INV018","M007","2024-04-20","TRANSFER",     [("Thảm tập Yoga 6mm",2,350000),("Nước khoáng Lavie",10,10000)]),
        ("INV019","M006","2024-04-25","E-WALLET",     [("BCAA 3000mg",1,800000),("Nước tăng lực Sting",4,15000)]),
        ("INV020","M001","2024-04-28","CASH",         [("Găng tay tập gym",1,250000),("Bình nước 1.5L",1,120000)]),

        # Tháng 5/2024
        ("INV021","M012","2024-05-01","TRANSFER",    [("Gói Standard 3 tháng",1,1200000)]),
        ("INV022","M009","2024-05-05","CASH",         [("Whey Protein Gold",1,1500000)]),
        ("INV023","M010","2024-05-08","E-WALLET",     [("PT cá nhân 10 buổi",1,3000000)]),
        ("INV024","M011","2024-05-12","TRANSFER",     [("BCAA 3000mg",2,800000),("Nước tăng lực Sting",5,15000)]),
        ("INV025","M013","2024-05-15","CASH",         [("Yoga Cơ Bản 12 buổi",1,800000)]),
        ("INV026","M002","2024-05-18","E-WALLET",     [("Whey Protein Gold",1,1500000),("Bình nước 1.5L",2,120000)]),
        ("INV027","M006","2024-05-22","TRANSFER",     [("Gói VIP 6 tháng",1,2200000)]),
        ("INV028","M012","2024-05-25","CASH",         [("Creatine Monohydrate",1,500000),("Nước khoáng Lavie",6,10000)]),
        ("INV029","M003","2024-05-28","E-WALLET",     [("Găng tay tập gym",1,250000),("Thảm tập Yoga 6mm",1,350000)]),

        # Tháng 6/2024
        ("INV030","M014","2024-06-01","TRANSFER",    [("Gói VIP 6 tháng",1,2200000)]),
        ("INV031","M015","2024-06-15","CASH",         [("Gói Cơ Bản 1 tháng",1,500000)]),
        ("INV032","M001","2024-06-18","E-WALLET",     [("PT cá nhân 10 buổi",1,3000000)]),
        ("INV033","M009","2024-06-20","TRANSFER",     [("Whey Protein Gold",1,1500000),("BCAA 3000mg",1,800000)]),
        ("INV034","M010","2024-06-22","CASH",         [("Creatine Monohydrate",2,500000),("Nước tăng lực Sting",4,15000)]),
        ("INV035","M011","2024-06-25","E-WALLET",     [("Bình nước 1.5L",1,120000),("Nước khoáng Lavie",8,10000)]),
        ("INV036","M014","2024-06-28","TRANSFER",     [("Găng tay tập gym",2,250000),("Thảm tập Yoga 6mm",1,350000)]),
        ("INV037","M012","2024-06-29","CASH",         [("Whey Protein Gold",1,1500000)]),
        ("INV038","M002","2024-06-30","E-WALLET",     [("Gói Standard 3 tháng",1,1200000)]),
    ]

    inv_sql  = (
        "INSERT INTO Invoices (id, memberId, total, discount_amount, final_amount, "
        "paid_amount, remaining_amount, date, method, payment_status, created_by) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    item_sql = (
        "INSERT INTO InvoiceItems (invoiceId, item_type, reference_id, item_name, "
        "quantity, unit_price, discount_amount, line_total) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    for inv_id, mid, ngay, method, items in invoice_data:
        total = sum(qty * gia for _, qty, gia in items)
        cur.execute(inv_sql, (inv_id, mid, total, 0, total, total, 0, ngay, method, 'PAID', 'U001'))
        for ten, qty, gia in items:
            line_total = qty * gia
            cur.execute(item_sql, (inv_id, 'OTHER', None, ten, qty, gia, 0, line_total))

    # ───── EVENT PARTICIPANTS ─────
    participants = [
        ("EP001","E004","M001","Phạm Văn Nam",    "2024-04-25","APPROVED"),
        ("EP002","E004","M002","Lê Hoàng Anh",    "2024-04-26","APPROVED"),
        ("EP003","E004","M003","Nguyễn Thùy Chi", "2024-04-27","APPROVED"),
        ("EP004","E004","M006","Ngô Quốc Hùng",   "2024-04-28","REJECTED"),
        ("EP005","E005","M004","Trần Minh Khoa",  "2024-04-10","APPROVED"),
        ("EP006","E005","M006","Ngô Quốc Hùng",   "2024-04-11","APPROVED"),
        ("EP007","E005","M010","Lý Hoàng Nam",     "2024-04-12","APPROVED"),
        ("EP008","E001","M001","Phạm Văn Nam",    "2024-05-01","PENDING"),
        ("EP009","E001","M002","Lê Hoàng Anh",    "2024-05-02","PENDING"),
        ("EP010","E001","M006","Ngô Quốc Hùng",   "2024-05-03","APPROVED"),
        ("EP011","E002","M003","Nguyễn Thùy Chi", "2024-04-10","PENDING"),
        ("EP012","E002","M005","Đỗ Thị Hoa",      "2024-04-11","APPROVED"),
        ("EP013","E002","M009","Phạm Lan Anh",     "2024-04-12","PENDING"),
    ]
    cur.executemany(
        "INSERT INTO EventParticipants VALUES (%s,%s,%s,%s,%s,%s)",
        participants
    )

    # ───────────────────────── INDEXES ─────────────────────────
    print("[9/9] Creating indexes...")
    indexes = [
        "CREATE INDEX idx_members_name ON Members(fullName)",
        "CREATE INDEX idx_members_phone ON Members(phone)",
        "CREATE INDEX idx_members_status ON Members(status)",
        "CREATE INDEX idx_members_plan ON Members(activePlanId)",
        "CREATE INDEX idx_members_pt ON Members(assignedPTId)",
        "CREATE INDEX idx_users_username ON Users(username)",
        "CREATE INDEX idx_users_role ON Users(role)",
        "CREATE INDEX idx_invoices_member ON Invoices(memberId)",
        "CREATE INDEX idx_invoices_date ON Invoices(date)",
        "CREATE INDEX idx_invoices_status ON Invoices(payment_status)",
        "CREATE INDEX idx_events_date ON Events(date)",
        "CREATE INDEX idx_events_status ON Events(status)",
        "CREATE INDEX idx_classes_trainer ON Classes(trainerId)",
        "CREATE INDEX idx_class_enrollments_member ON ClassEnrollments(memberId)"
    ]
    for idx_sql in indexes:
        try:
            cur.execute(idx_sql)
        except Exception as e:
            print(f"Index creation warning: {e}")

    conn.commit()
    print("\n[OK] Database initialized successfully!")
    print(f"   Users: 5 | Plans: 6 | Members: 15")
    print(f"   Sports: 7 | Facilities: 8 | Events: 6 | Classes: 5")
    print(f"   Invoices: {len(invoice_data)} | Participants: {len(participants)}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    init_db()
