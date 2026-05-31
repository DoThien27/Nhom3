"""
scripts/seed_db.py
──────────────────
Script tạo database và seed data với mật khẩu được hash bcrypt đúng.
Chạy: python scripts/seed_db.py

Tài khoản mặc định:
  admin / Admin@123
  hlv_tuan / Hlv@123456
  hlv_linh / Hlv@123456
"""
import sys
import os

# Thêm thư mục gốc vào path để import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import mysql.connector
import bcrypt
from datetime import datetime, timedelta

# ─── Config ──────────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'user':     os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
}
DB_NAME = os.environ.get('DB_NAME', 'sports_club_db')


def hash_pw(pw):
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def run():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Tạo database
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.execute(f"USE `{DB_NAME}`")
    conn.commit()

    cur.execute("SET FOREIGN_KEY_CHECKS = 0")

    # ─── Drop & Create Tables ──────────────────────────────────────────────────
    tables_sql = """
DROP TABLE IF EXISTS TrainerSalaries;
DROP TABLE IF EXISTS TrainerAttendance;
DROP TABLE IF EXISTS EventParticipants;
DROP TABLE IF EXISTS Events;
DROP TABLE IF EXISTS Invoices;
DROP TABLE IF EXISTS ClassAttendance;
DROP TABLE IF EXISTS ClassEnrollments;
DROP TABLE IF EXISTS CheckIns;
DROP TABLE IF EXISTS MemberCards;
DROP TABLE IF EXISTS Members;
DROP TABLE IF EXISTS Classes;
DROP TABLE IF EXISTS Plans;
DROP TABLE IF EXISTS Facilities;
DROP TABLE IF EXISTS Sports;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    id           VARCHAR(36)  NOT NULL PRIMARY KEY,
    username     VARCHAR(100) NOT NULL UNIQUE,
    password     VARCHAR(255) NOT NULL,
    fullName     VARCHAR(200) NOT NULL,
    role         ENUM('ADMIN','PT') NOT NULL DEFAULT 'PT',
    specialty    VARCHAR(200) NULL,
    phone        VARCHAR(20)  NULL,
    address      VARCHAR(300) NULL,
    email        VARCHAR(200) NULL,
    status       ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    activeStudents INT NOT NULL DEFAULT 0,
    createdAt    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Sports (
    sport_id    VARCHAR(36)  NOT NULL PRIMARY KEY,
    sport_name  VARCHAR(200) NOT NULL,
    description TEXT NULL,
    createdAt   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Facilities (
    facility_id   VARCHAR(36)  NOT NULL PRIMARY KEY,
    facility_name VARCHAR(200) NOT NULL,
    location      VARCHAR(300) NULL,
    capacity      INT NULL DEFAULT 0,
    status        ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    sport_id      VARCHAR(36) NULL,
    createdAt     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sport_id) REFERENCES Sports(sport_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Plans (
    id             VARCHAR(36)   NOT NULL PRIMARY KEY,
    name           VARCHAR(200)  NOT NULL,
    type           ENUM('MEMBERSHIP','CLASS','PT') NOT NULL DEFAULT 'MEMBERSHIP',
    price          DECIMAL(12,0) NOT NULL DEFAULT 0,
    description    TEXT NULL,
    durationMonths INT  NOT NULL DEFAULT 1,
    sessions       INT  NOT NULL DEFAULT 0,
    status         ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    createdAt      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Members (
    id             VARCHAR(36)  NOT NULL PRIMARY KEY,
    fullName       VARCHAR(200) NOT NULL,
    phone          VARCHAR(20)  NOT NULL,
    email          VARCHAR(200) NULL DEFAULT '',
    joinDate       DATE NULL,
    birthDate      DATE NULL,
    gender         ENUM('Nam','Nữ','Khác') NOT NULL DEFAULT 'Nam',
    homeTown       VARCHAR(300) NULL,
    weight         DECIMAL(5,1) NULL DEFAULT 0,
    previousWeight DECIMAL(5,1) NULL DEFAULT 0,
    username       VARCHAR(100) NULL UNIQUE,
    password       VARCHAR(255) NULL,
    avatar         VARCHAR(500) NULL,
    assignedPTId   VARCHAR(36)  NULL,
    activePlanId   VARCHAR(36)  NULL,
    expiryDate     DATE NULL,
    status         ENUM('ACTIVE','INACTIVE','PENDING','EXPIRED') NOT NULL DEFAULT 'PENDING',
    createdAt      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignedPTId) REFERENCES Users(id)  ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (activePlanId) REFERENCES Plans(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE MemberCards (
    id         VARCHAR(36) NOT NULL PRIMARY KEY,
    memberId   VARCHAR(36) NOT NULL,
    planId     VARCHAR(36) NULL,
    cardNumber VARCHAR(50) NOT NULL UNIQUE,
    issueDate  DATE NULL,
    expiryDate DATE NULL,
    status     ENUM('ACTIVE','INACTIVE','EXPIRED','REVOKED') NOT NULL DEFAULT 'INACTIVE',
    note       TEXT NULL,
    createdAt  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memberId) REFERENCES Members(id)  ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (planId)   REFERENCES Plans(id)    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE CheckIns (
    id           VARCHAR(36) NOT NULL PRIMARY KEY,
    memberId     VARCHAR(36) NOT NULL,
    cardId       VARCHAR(36) NULL,
    checkInTime  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checkOutTime DATETIME NULL,
    checkType    ENUM('MANUAL','CARD') NOT NULL DEFAULT 'MANUAL',
    note         TEXT NULL,
    FOREIGN KEY (memberId) REFERENCES Members(id)     ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (cardId)   REFERENCES MemberCards(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Classes (
    id         VARCHAR(36)   NOT NULL PRIMARY KEY,
    name       VARCHAR(200)  NOT NULL,
    trainerId  VARCHAR(36)   NULL,
    sportId    VARCHAR(36)   NULL,
    facilityId VARCHAR(36)   NULL,
    time       VARCHAR(100)  NULL,
    dayOfWeek  VARCHAR(100)  NULL,
    capacity   INT           NOT NULL DEFAULT 20,
    price      DECIMAL(12,0) NOT NULL DEFAULT 0,
    status     ENUM('ACTIVE','INACTIVE','FULL','CANCELLED','COMPLETED') NOT NULL DEFAULT 'ACTIVE',
    startDate  DATE NULL,
    endDate    DATE NULL,
    createdAt  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainerId)  REFERENCES Users(id)           ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (sportId)    REFERENCES Sports(sport_id)    ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (facilityId) REFERENCES Facilities(facility_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ClassEnrollments (
    id         INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    classId    VARCHAR(36) NOT NULL,
    memberId   VARCHAR(36) NOT NULL,
    enrolledAt DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status     ENUM('PENDING','ACTIVE','CANCELLED') NOT NULL DEFAULT 'PENDING',
    UNIQUE KEY uq_class_member (classId, memberId),
    FOREIGN KEY (classId)  REFERENCES Classes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (memberId) REFERENCES Members(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ClassAttendance (
    id         INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    classId    VARCHAR(36) NOT NULL,
    memberId   VARCHAR(36) NOT NULL,
    date       DATE        NOT NULL,
    status     ENUM('PRESENT','ABSENT') NOT NULL DEFAULT 'PRESENT',
    note       TEXT        NULL,
    createdAt  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_attendance (classId, memberId, date),
    FOREIGN KEY (classId)  REFERENCES Classes(id)  ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (memberId) REFERENCES Members(id)  ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE TrainerAttendance (
    id             VARCHAR(36)  NOT NULL PRIMARY KEY,
    trainerId      VARCHAR(36)  NOT NULL,
    classId        VARCHAR(36)  NULL,
    attendanceDate DATE         NOT NULL,
    checkIn        VARCHAR(10)  NULL,
    checkOut       VARCHAR(10)  NULL,
    status         ENUM('PRESENT','LATE','HALF','ABSENT') NOT NULL DEFAULT 'PRESENT',
    sessionsCount  INT          NOT NULL DEFAULT 0,
    note           TEXT         NULL,
    createdAt      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainerId) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (classId) REFERENCES Classes(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE TrainerSalaries (
    id            VARCHAR(36)   NOT NULL PRIMARY KEY,
    trainerId     VARCHAR(36)   NOT NULL,
    month         INT           NOT NULL,
    year          INT           NOT NULL,
    baseSalary    DECIMAL(12,0) NOT NULL DEFAULT 0,
    totalSessions INT           NOT NULL DEFAULT 0,
    sessionBonus  DECIMAL(12,0) NOT NULL DEFAULT 0,
    bonus         DECIMAL(12,0) NOT NULL DEFAULT 0,
    deductions    DECIMAL(12,0) NOT NULL DEFAULT 0,
    totalAmount   DECIMAL(12,0) NOT NULL DEFAULT 0,
    paymentStatus ENUM('PENDING','PAID') NOT NULL DEFAULT 'PENDING',
    paidDate      DATETIME      NULL,
    note          TEXT          NULL,
    UNIQUE KEY uq_trainer_month_year (trainerId, month, year),
    FOREIGN KEY (trainerId) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Events (
    id          VARCHAR(36)   NOT NULL PRIMARY KEY,
    name        VARCHAR(200)  NOT NULL,
    description TEXT NULL,
    date        DATE NULL,
    time        VARCHAR(10)   NULL,
    endTime     VARCHAR(10)   NULL,
    location    VARCHAR(300)  NULL,
    facilityId  VARCHAR(36)   NULL,
    capacity    INT           NOT NULL DEFAULT 50,
    price       DECIMAL(12,0) NOT NULL DEFAULT 0,
    status      ENUM('UPCOMING','ONGOING','COMPLETED','CANCELLED') NOT NULL DEFAULT 'UPCOMING',
    createdAt   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facilityId) REFERENCES Facilities(facility_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE EventParticipants (
    id           VARCHAR(36)  NOT NULL PRIMARY KEY,
    eventId      VARCHAR(36)  NOT NULL,
    memberId     VARCHAR(36)  NOT NULL,
    memberName   VARCHAR(200) NULL,
    registerDate DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       ENUM('PENDING','CONFIRMED','CANCELLED') NOT NULL DEFAULT 'PENDING',
    UNIQUE KEY uq_event_member (eventId, memberId),
    FOREIGN KEY (eventId)  REFERENCES Events(id)  ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (memberId) REFERENCES Members(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Invoices (
    id              VARCHAR(36)   NOT NULL PRIMARY KEY,
    memberId        VARCHAR(36)   NOT NULL,
    sourceType      ENUM('PLAN','CLASS','EVENT','OTHER','MANUAL') NOT NULL DEFAULT 'OTHER',
    sourceId        VARCHAR(36)   NULL,
    relatedCardId   VARCHAR(36)   NULL,
    totalAmount     DECIMAL(12,0) NOT NULL DEFAULT 0,
    discountAmount  DECIMAL(12,0) NOT NULL DEFAULT 0,
    finalAmount     DECIMAL(12,0) NOT NULL DEFAULT 0,
    paidAmount      DECIMAL(12,0) NOT NULL DEFAULT 0,
    remainingAmount DECIMAL(12,0) NOT NULL DEFAULT 0,
    date            DATE NULL,
    paymentMethod   ENUM('CASH','TRANSFER','CARD') NOT NULL DEFAULT 'CASH',
    paymentStatus   ENUM('UNPAID','PARTIAL','PAID','CANCELLED') NOT NULL DEFAULT 'UNPAID',
    note            TEXT NULL,
    createdAt       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memberId) REFERENCES Members(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

    # Tách từng câu lệnh và chạy
    for stmt in tables_sql.strip().split(';'):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()

    # ─── Hash passwords ────────────────────────────────────────────────────────

    pw_admin  = hash_pw('admin123')
    pw_pt     = hash_pw('pt123456')

    # ─── Seed Users ───────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Users (id, username, password, fullName, role, specialty, phone, address, status) VALUES
        ('ADMIN001', 'admin', %s, 'Quản trị viên Hệ thống', 'ADMIN', NULL, '0900000000', 'Văn phòng TT', 'ACTIVE'),
        ('PT001', 'hlv_pt001', %s, 'Trần Thế Anh', 'PT', 'Gym & Thể hình', '0909658846', 'Hà Nội', 'ACTIVE'),
        ('PT002', 'hlv_pt002', %s, 'Lê Thu Thủy', 'PT', 'Yoga & Pilates', '0905223798', 'Hà Nội', 'ACTIVE'),
        ('PT003', 'hlv_pt003', %s, 'Nguyễn Hoàng Khang', 'PT', 'Boxing & Võ thuật', '0908604824', 'Hà Nội', 'ACTIVE'),
        ('PT004', 'hlv_pt004', %s, 'Phạm Ngọc Trâm', 'PT', 'Zumba & Aerobic', '0908790120', 'Hà Nội', 'ACTIVE'),
        ('PT005', 'hlv_pt005', %s, 'Bùi Quốc Đạt', 'PT', 'Bơi lội & Thể lực', '0906029557', 'Hà Nội', 'ACTIVE')
    """, (pw_admin, pw_pt, pw_pt, pw_pt, pw_pt, pw_pt))

    # ─── Seed Sports ──────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Sports (sport_id, sport_name, description) VALUES
        ('SP001', 'Yoga', 'Rèn luyện sự dẻo dai và tĩnh tâm'),
        ('SP002', 'Gym', 'Khu vực tập luyện tạ tự do và máy'),
        ('SP003', 'Boxing', 'Sàn đấu võ thuật và bao cát'),
        ('SP004', 'Zumba', 'Phòng tập nhảy hiện đại'),
        ('SP005', 'Bơi lội', 'Khu vực hồ bơi chuẩn Olympic'),
        ('SP006', 'Cầu lông', 'Sân tập và thi đấu cầu lông')
    """)

    # ─── Seed Facilities ──────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Facilities (facility_id, facility_name, location, capacity, sport_id) VALUES
        ('FAC001', 'Phòng Yoga ZEN 1', 'Tầng 2 - Khu A', 25, 'SP001'),
        ('FAC002', 'Phòng Yoga ZEN 2', 'Tầng 2 - Khu B', 20, 'SP001'),
        ('FAC003', 'Phòng Tạ Free-Weight', 'Tầng 1 - Khu A', 50, 'SP002'),
        ('FAC004', 'Phòng Máy Cardio', 'Tầng 1 - Khu B', 40, 'SP002'),
        ('FAC005', 'Sàn Boxing Tiêu chuẩn', 'Tầng 3 - Khu A', 15, 'SP003'),
        ('FAC006', 'Phòng Studio Nhảy', 'Tầng 3 - Khu B', 40, 'SP004'),
        ('FAC007', 'Hồ Bơi Vô Cực', 'Tầng thượng', 100, 'SP005'),
        ('FAC008', 'Sân Cầu Lông Số 1', 'Tầng 4', 16, 'SP006'),
        ('FAC009', 'Sân Cầu Lông Số 2', 'Tầng 4', 16, 'SP006')
    """)

    # ─── Seed Plans ───────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Plans (id, name, type, price, description, durationMonths) VALUES
        ('PLN001', 'Gói Classic 1 Tháng', 'MEMBERSHIP', 600000, 'Tập luyện tự do tất cả dịch vụ cơ bản trong 30 ngày', 1),
        ('PLN002', 'Gói Premium 3 Tháng', 'MEMBERSHIP', 1500000, 'Tập tự do + Tặng 1 buổi PT + Dùng khăn miễn phí', 3),
        ('PLN003', 'Gói VIP 1 Năm', 'MEMBERSHIP', 5000000, 'Tập tự do + Full dịch vụ (Khăn, nước, xông hơi, locker)', 12),
        ('PLN004', 'Gói PT Định Hình (10 Buổi)', 'PT', 3500000, 'Gói tập 1 kèm 1 chuyên sâu cải thiện vóc dáng', 2)
    """)

    # ─── Seed Members ─────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Members (id, fullName, phone, email, joinDate, birthDate, gender, homeTown, activePlanId, assignedPTId, status) VALUES
        ('MBR001', 'Lê Thu Nhung', '0958629450', 'nhung1@gmail.com', '2026-05-17', '1989-11-18', 'Nữ', 'Hà Nội', 'PLN003', NULL, 'ACTIVE'),
        ('MBR002', 'Phạm Thị Châu', '0940922989', 'châu2@gmail.com', '2026-09-25', '1988-09-19', 'Nữ', 'Hà Nội', 'PLN004', NULL, 'ACTIVE'),
        ('MBR003', 'Vũ Tuấn Hải', '0994811877', 'hải3@gmail.com', '2026-08-20', '1988-10-22', 'Nam', 'Hà Nội', 'PLN003', NULL, 'ACTIVE'),
        ('MBR004', 'Lê Hồng Huyền', '0912789545', 'huyền4@gmail.com', '2026-03-16', '1990-09-14', 'Nữ', 'Hà Nội', 'PLN001', NULL, 'ACTIVE'),
        ('MBR005', 'Ngô Thu Oanh', '0980400515', 'oanh5@gmail.com', '2026-02-28', '1995-11-19', 'Nữ', 'Hà Nội', 'PLN001', NULL, 'ACTIVE'),
        ('MBR006', 'Võ Đình Quân', '0972815617', 'quân6@gmail.com', '2026-02-19', '1999-11-22', 'Nam', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR007', 'Hoàng Kiều Hà', '0954117028', 'hà7@gmail.com', '2026-03-04', '2001-11-19', 'Nữ', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR008', 'Huỳnh Mai Tâm', '0939438336', 'tâm8@gmail.com', '2026-09-03', '1993-12-22', 'Nữ', 'Hà Nội', 'PLN003', NULL, 'ACTIVE'),
        ('MBR009', 'Võ Kiều Chi', '0940611670', 'chi9@gmail.com', '2026-02-06', '1997-06-16', 'Nữ', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR010', 'Hồ Thái Thiên', '0982744278', 'thiên10@gmail.com', '2026-01-19', '1997-11-02', 'Nam', 'Hà Nội', 'PLN004', NULL, 'ACTIVE'),
        ('MBR011', 'Đặng Hồng Linh', '0959264191', 'linh11@gmail.com', '2026-03-01', '1989-05-08', 'Nữ', 'Hà Nội', 'PLN004', 'PT005', 'ACTIVE'),
        ('MBR012', 'Ngô Đình Vinh', '0910411968', 'vinh12@gmail.com', '2026-11-28', '1992-01-05', 'Nam', 'Hà Nội', 'PLN001', 'PT005', 'ACTIVE'),
        ('MBR013', 'Phan Ngọc Ngân', '0913310186', 'ngân13@gmail.com', '2026-05-20', '1989-05-10', 'Nữ', 'Hà Nội', 'PLN003', NULL, 'ACTIVE'),
        ('MBR014', 'Huỳnh Hoàng Trung', '0980852864', 'trung14@gmail.com', '2026-03-01', '1999-10-28', 'Nam', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR015', 'Đỗ Bích Hằng', '0963714698', 'hằng15@gmail.com', '2026-10-22', '1994-01-27', 'Nữ', 'Hà Nội', 'PLN001', NULL, 'ACTIVE'),
        ('MBR016', 'Lê Kim Anh', '0919946152', 'anh16@gmail.com', '2026-11-22', '1999-09-21', 'Nữ', 'Hà Nội', 'PLN001', NULL, 'ACTIVE'),
        ('MBR017', 'Ngô Văn Thắng', '0948848658', 'thắng17@gmail.com', '2026-10-17', '2003-04-14', 'Nam', 'Hà Nội', 'PLN001', NULL, 'ACTIVE'),
        ('MBR018', 'Bùi Đức Khang', '0994827472', 'khang18@gmail.com', '2026-04-22', '1996-09-16', 'Nam', 'Hà Nội', 'PLN001', 'PT005', 'ACTIVE'),
        ('MBR019', 'Ngô Thanh Châu', '0944377360', 'châu19@gmail.com', '2026-02-17', '1994-09-26', 'Nữ', 'Hà Nội', 'PLN004', NULL, 'ACTIVE'),
        ('MBR020', 'Trần Phương Anh', '0987721534', 'anh20@gmail.com', '2026-12-18', '1994-06-12', 'Nữ', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR021', 'Lý Quang Thiên', '0997831906', 'thiên21@gmail.com', '2026-03-03', '2004-04-21', 'Nam', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR022', 'Dương Thị Hoa', '0926381311', 'hoa22@gmail.com', '2026-05-25', '1991-05-06', 'Nữ', 'Hà Nội', 'PLN001', NULL, 'ACTIVE'),
        ('MBR023', 'Võ Ngọc Hoa', '0912378184', 'hoa23@gmail.com', '2026-10-13', '1996-11-01', 'Nữ', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR024', 'Huỳnh Quang Dũng', '0946495516', 'dũng24@gmail.com', '2026-02-04', '2000-01-25', 'Nam', 'Hà Nội', 'PLN001', NULL, 'ACTIVE'),
        ('MBR025', 'Hồ Kiều Oanh', '0995994586', 'oanh25@gmail.com', '2026-04-26', '1988-03-10', 'Nữ', 'Hà Nội', 'PLN002', NULL, 'ACTIVE'),
        ('MBR026', 'Lý Thành Dũng', '0931057210', 'dũng26@gmail.com', '2026-10-05', '1992-11-23', 'Nam', 'Hà Nội', 'PLN001', NULL, 'EXPIRED'),
        ('MBR027', 'Hoàng Diễm Yến', '0935427224', 'yến27@gmail.com', '2026-06-23', '2004-06-12', 'Nữ', 'Hà Nội', 'PLN004', NULL, 'EXPIRED'),
        ('MBR028', 'Võ Mai Mai', '0980683484', 'mai28@gmail.com', '2026-05-13', '1993-06-13', 'Nữ', 'Hà Nội', 'PLN004', NULL, 'EXPIRED'),
        ('MBR029', 'Phạm Minh Sơn', '0979596801', 'sơn29@gmail.com', '2026-03-09', '1985-09-14', 'Nam', 'Hà Nội', 'PLN004', NULL, 'EXPIRED'),
        ('MBR030', 'Phan Hải Tài', '0961749952', 'tài30@gmail.com', '2026-09-05', '1986-01-20', 'Nam', 'Hà Nội', 'PLN001', NULL, 'EXPIRED')
    """)

    # ─── Seed MemberCards ─────────────────────────────────────────────────────
    cur.execute("""INSERT INTO MemberCards (id, memberId, planId, cardNumber, issueDate, expiryDate, status) VALUES
        ('CRD001', 'MBR001', 'PLN003', 'CARD425441', '2026-05-17', '2027-05-12', 'ACTIVE'),
        ('CRD002', 'MBR002', 'PLN004', 'CARD481522', '2026-09-25', '2026-11-24', 'ACTIVE'),
        ('CRD003', 'MBR003', 'PLN003', 'CARD487303', '2026-08-20', '2027-08-15', 'ACTIVE'),
        ('CRD004', 'MBR004', 'PLN001', 'CARD257574', '2026-03-16', '2026-04-15', 'ACTIVE'),
        ('CRD005', 'MBR005', 'PLN001', 'CARD710315', '2026-02-28', '2026-03-29', 'ACTIVE'),
        ('CRD006', 'MBR006', 'PLN002', 'CARD310566', '2026-02-19', '2026-05-19', 'ACTIVE'),
        ('CRD007', 'MBR007', 'PLN002', 'CARD798847', '2026-03-04', '2026-06-02', 'ACTIVE'),
        ('CRD008', 'MBR008', 'PLN003', 'CARD310198', '2026-09-03', '2027-08-29', 'ACTIVE'),
        ('CRD009', 'MBR009', 'PLN002', 'CARD935709', '2026-02-06', '2026-05-06', 'ACTIVE'),
        ('CRD010', 'MBR010', 'PLN004', 'CARD4229110', '2026-01-19', '2026-03-19', 'ACTIVE'),
        ('CRD011', 'MBR011', 'PLN004', 'CARD8374911', '2026-03-01', '2026-04-30', 'ACTIVE'),
        ('CRD012', 'MBR012', 'PLN001', 'CARD2213412', '2026-11-28', '2026-12-28', 'ACTIVE'),
        ('CRD013', 'MBR013', 'PLN003', 'CARD3534713', '2026-05-20', '2027-05-15', 'ACTIVE'),
        ('CRD014', 'MBR014', 'PLN002', 'CARD7120014', '2026-03-01', '2026-05-30', 'ACTIVE'),
        ('CRD015', 'MBR015', 'PLN001', 'CARD8184215', '2026-10-22', '2026-11-21', 'ACTIVE'),
        ('CRD016', 'MBR016', 'PLN001', 'CARD9422716', '2026-11-22', '2026-12-22', 'ACTIVE'),
        ('CRD017', 'MBR017', 'PLN001', 'CARD4392417', '2026-10-17', '2026-11-16', 'ACTIVE'),
        ('CRD018', 'MBR018', 'PLN001', 'CARD3037918', '2026-04-22', '2026-05-22', 'ACTIVE'),
        ('CRD019', 'MBR019', 'PLN004', 'CARD5904119', '2026-02-17', '2026-04-17', 'ACTIVE'),
        ('CRD020', 'MBR020', 'PLN002', 'CARD5823720', '2026-12-18', '2027-03-18', 'ACTIVE'),
        ('CRD021', 'MBR021', 'PLN002', 'CARD1650421', '2026-03-03', '2026-06-01', 'ACTIVE'),
        ('CRD022', 'MBR022', 'PLN001', 'CARD2638222', '2026-05-25', '2026-06-24', 'ACTIVE'),
        ('CRD023', 'MBR023', 'PLN002', 'CARD9486823', '2026-10-13', '2027-01-11', 'ACTIVE'),
        ('CRD024', 'MBR024', 'PLN001', 'CARD8353024', '2026-02-04', '2026-03-05', 'ACTIVE'),
        ('CRD025', 'MBR025', 'PLN002', 'CARD9286025', '2026-04-26', '2026-07-25', 'ACTIVE')
    """)

    # ─── Seed Invoices ────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Invoices (id, memberId, sourceType, sourceId, relatedCardId, totalAmount, discountAmount, finalAmount, paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note) VALUES
        ('INV001', 'MBR001', 'PLAN', 'PLN003', 'CRD001', 5000000, 0, 5000000, 5000000, 0, '2026-05-17', 'TRANSFER', 'PAID', 'Đăng ký Gói VIP 1 Năm'),
        ('INV002', 'MBR002', 'PLAN', 'PLN004', 'CRD002', 3500000, 0, 3500000, 3500000, 0, '2026-09-25', 'TRANSFER', 'PAID', 'Đăng ký Gói PT Định Hình (10 Buổi)'),
        ('INV003', 'MBR003', 'PLAN', 'PLN003', 'CRD003', 5000000, 0, 5000000, 5000000, 0, '2026-08-20', 'TRANSFER', 'PAID', 'Đăng ký Gói VIP 1 Năm'),
        ('INV004', 'MBR004', 'PLAN', 'PLN001', 'CRD004', 600000, 0, 600000, 600000, 0, '2026-03-16', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV005', 'MBR005', 'PLAN', 'PLN001', 'CRD005', 600000, 0, 600000, 600000, 0, '2026-02-28', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV006', 'MBR006', 'PLAN', 'PLN002', 'CRD006', 1500000, 0, 1500000, 1500000, 0, '2026-02-19', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng'),
        ('INV007', 'MBR007', 'PLAN', 'PLN002', 'CRD007', 1500000, 0, 1500000, 1500000, 0, '2026-03-04', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng'),
        ('INV008', 'MBR008', 'PLAN', 'PLN003', 'CRD008', 5000000, 0, 5000000, 5000000, 0, '2026-09-03', 'TRANSFER', 'PAID', 'Đăng ký Gói VIP 1 Năm'),
        ('INV009', 'MBR009', 'PLAN', 'PLN002', 'CRD009', 1500000, 0, 1500000, 1500000, 0, '2026-02-06', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng'),
        ('INV010', 'MBR010', 'PLAN', 'PLN004', 'CRD010', 3500000, 0, 3500000, 3500000, 0, '2026-01-19', 'TRANSFER', 'PAID', 'Đăng ký Gói PT Định Hình (10 Buổi)'),
        ('INV011', 'MBR011', 'PLAN', 'PLN004', 'CRD011', 3500000, 0, 3500000, 3500000, 0, '2026-03-01', 'TRANSFER', 'PAID', 'Đăng ký Gói PT Định Hình (10 Buổi)'),
        ('INV012', 'MBR012', 'PLAN', 'PLN001', 'CRD012', 600000, 0, 600000, 600000, 0, '2026-11-28', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV013', 'MBR013', 'PLAN', 'PLN003', 'CRD013', 5000000, 0, 5000000, 5000000, 0, '2026-05-20', 'TRANSFER', 'PAID', 'Đăng ký Gói VIP 1 Năm'),
        ('INV014', 'MBR014', 'PLAN', 'PLN002', 'CRD014', 1500000, 0, 1500000, 1500000, 0, '2026-03-01', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng'),
        ('INV015', 'MBR015', 'PLAN', 'PLN001', 'CRD015', 600000, 0, 600000, 600000, 0, '2026-10-22', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV016', 'MBR016', 'PLAN', 'PLN001', 'CRD016', 600000, 0, 600000, 600000, 0, '2026-11-22', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV017', 'MBR017', 'PLAN', 'PLN001', 'CRD017', 600000, 0, 600000, 600000, 0, '2026-10-17', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV018', 'MBR018', 'PLAN', 'PLN001', 'CRD018', 600000, 0, 600000, 600000, 0, '2026-04-22', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV019', 'MBR019', 'PLAN', 'PLN004', 'CRD019', 3500000, 0, 3500000, 3500000, 0, '2026-02-17', 'TRANSFER', 'PAID', 'Đăng ký Gói PT Định Hình (10 Buổi)'),
        ('INV020', 'MBR020', 'PLAN', 'PLN002', 'CRD020', 1500000, 0, 1500000, 1500000, 0, '2026-12-18', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng'),
        ('INV021', 'MBR021', 'PLAN', 'PLN002', 'CRD021', 1500000, 0, 1500000, 1500000, 0, '2026-03-03', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng'),
        ('INV022', 'MBR022', 'PLAN', 'PLN001', 'CRD022', 600000, 0, 600000, 600000, 0, '2026-05-25', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV023', 'MBR023', 'PLAN', 'PLN002', 'CRD023', 1500000, 0, 1500000, 1500000, 0, '2026-10-13', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng'),
        ('INV024', 'MBR024', 'PLAN', 'PLN001', 'CRD024', 600000, 0, 600000, 600000, 0, '2026-02-04', 'TRANSFER', 'PAID', 'Đăng ký Gói Classic 1 Tháng'),
        ('INV025', 'MBR025', 'PLAN', 'PLN002', 'CRD025', 1500000, 0, 1500000, 1500000, 0, '2026-04-26', 'TRANSFER', 'PAID', 'Đăng ký Gói Premium 3 Tháng')
    """)

    # ─── Seed CheckIns ────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO CheckIns (id, memberId, cardId, checkInTime, checkOutTime, checkType, note) VALUES
        ('CHK001_0', 'MBR001', 'CRD001', '2026-04-29 10:56:39', '2026-04-29 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK001_1', 'MBR001', 'CRD001', '2026-05-16 05:56:39', '2026-05-16 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK001_2', 'MBR001', 'CRD001', '2026-05-09 10:56:39', '2026-05-09 12:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK001_3', 'MBR001', 'CRD001', '2026-05-17 08:56:39', '2026-05-17 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK002_0', 'MBR002', 'CRD002', '2026-05-13 04:56:39', '2026-05-13 05:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK002_1', 'MBR002', 'CRD002', '2026-05-14 10:56:39', '2026-05-14 12:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK002_2', 'MBR002', 'CRD002', '2026-05-19 05:56:39', '2026-05-19 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK002_3', 'MBR002', 'CRD002', '2026-05-05 07:56:39', '2026-05-05 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK002_4', 'MBR002', 'CRD002', '2026-05-15 09:56:39', '2026-05-15 10:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK003_0', 'MBR003', 'CRD003', '2026-04-24 06:56:39', '2026-04-24 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK003_1', 'MBR003', 'CRD003', '2026-05-16 09:56:39', '2026-05-16 10:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK004_0', 'MBR004', 'CRD004', '2026-04-27 01:56:39', '2026-04-27 02:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK004_1', 'MBR004', 'CRD004', '2026-05-22 04:56:39', '2026-05-22 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK004_2', 'MBR004', 'CRD004', '2026-04-28 01:56:39', '2026-04-28 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK004_3', 'MBR004', 'CRD004', '2026-05-04 08:56:39', '2026-05-04 10:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK005_0', 'MBR005', 'CRD005', '2026-05-07 02:56:39', '2026-05-07 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK005_1', 'MBR005', 'CRD005', '2026-05-06 04:56:39', '2026-05-06 05:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK006_0', 'MBR006', 'CRD006', '2026-05-13 01:56:39', '2026-05-13 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK006_1', 'MBR006', 'CRD006', '2026-05-13 02:56:39', '2026-05-13 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK006_2', 'MBR006', 'CRD006', '2026-05-21 10:56:39', '2026-05-21 12:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK006_3', 'MBR006', 'CRD006', '2026-05-19 01:56:39', '2026-05-19 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK007_0', 'MBR007', 'CRD007', '2026-04-29 08:56:39', '2026-04-29 10:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK007_1', 'MBR007', 'CRD007', '2026-04-29 03:56:39', '2026-04-29 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK008_0', 'MBR008', 'CRD008', '2026-05-05 05:56:39', '2026-05-05 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK008_1', 'MBR008', 'CRD008', '2026-05-10 01:56:39', '2026-05-10 02:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK009_0', 'MBR009', 'CRD009', '2026-05-15 05:56:39', '2026-05-15 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK009_1', 'MBR009', 'CRD009', '2026-05-04 02:56:39', '2026-05-04 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK009_2', 'MBR009', 'CRD009', '2026-05-17 08:56:39', '2026-05-17 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK009_3', 'MBR009', 'CRD009', '2026-05-07 05:56:39', '2026-05-07 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK010_0', 'MBR010', 'CRD010', '2026-04-24 09:56:39', '2026-04-24 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK010_1', 'MBR010', 'CRD010', '2026-04-24 10:56:39', '2026-04-24 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK010_2', 'MBR010', 'CRD010', '2026-05-03 04:56:39', '2026-05-03 05:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK011_0', 'MBR011', 'CRD011', '2026-05-11 04:56:39', '2026-05-11 05:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK011_1', 'MBR011', 'CRD011', '2026-05-02 01:56:39', '2026-05-02 02:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK011_2', 'MBR011', 'CRD011', '2026-05-14 08:56:39', '2026-05-14 10:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK011_3', 'MBR011', 'CRD011', '2026-04-27 04:56:39', '2026-04-27 05:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK012_0', 'MBR012', 'CRD012', '2026-05-12 02:56:39', '2026-05-12 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK012_1', 'MBR012', 'CRD012', '2026-05-15 02:56:39', '2026-05-15 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK012_2', 'MBR012', 'CRD012', '2026-05-02 02:56:39', '2026-05-02 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK012_3', 'MBR012', 'CRD012', '2026-05-01 09:56:39', '2026-05-01 10:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK013_0', 'MBR013', 'CRD013', '2026-04-25 03:56:39', '2026-04-25 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK013_1', 'MBR013', 'CRD013', '2026-05-07 04:56:39', '2026-05-07 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK014_0', 'MBR014', 'CRD014', '2026-05-01 10:56:39', '2026-05-01 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK014_1', 'MBR014', 'CRD014', '2026-04-27 07:56:39', '2026-04-27 08:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK015_0', 'MBR015', 'CRD015', '2026-05-22 08:56:39', '2026-05-22 10:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK015_1', 'MBR015', 'CRD015', '2026-05-22 02:56:39', '2026-05-22 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK015_2', 'MBR015', 'CRD015', '2026-05-12 03:56:39', '2026-05-12 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK015_3', 'MBR015', 'CRD015', '2026-05-18 05:56:39', '2026-05-18 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK016_0', 'MBR016', 'CRD016', '2026-05-03 10:56:39', '2026-05-03 12:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK016_1', 'MBR016', 'CRD016', '2026-05-20 03:56:39', '2026-05-20 05:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK017_0', 'MBR017', 'CRD017', '2026-04-28 05:56:39', '2026-04-28 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK017_1', 'MBR017', 'CRD017', '2026-05-04 09:56:39', '2026-05-04 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK017_2', 'MBR017', 'CRD017', '2026-05-17 08:56:39', '2026-05-17 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK017_3', 'MBR017', 'CRD017', '2026-04-28 02:56:39', '2026-04-28 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK017_4', 'MBR017', 'CRD017', '2026-05-19 03:56:39', '2026-05-19 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK018_0', 'MBR018', 'CRD018', '2026-05-12 02:56:39', '2026-05-12 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK018_1', 'MBR018', 'CRD018', '2026-05-03 05:56:39', '2026-05-03 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK019_0', 'MBR019', 'CRD019', '2026-05-09 06:56:39', '2026-05-09 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK019_1', 'MBR019', 'CRD019', '2026-04-23 06:56:39', '2026-04-23 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK019_2', 'MBR019', 'CRD019', '2026-05-01 04:56:39', '2026-05-01 05:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK019_3', 'MBR019', 'CRD019', '2026-05-18 05:56:39', '2026-05-18 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK019_4', 'MBR019', 'CRD019', '2026-04-28 09:56:39', '2026-04-28 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK020_0', 'MBR020', 'CRD020', '2026-05-22 09:56:39', '2026-05-22 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK020_1', 'MBR020', 'CRD020', '2026-05-13 01:56:39', '2026-05-13 02:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK021_0', 'MBR021', 'CRD021', '2026-05-13 07:56:39', '2026-05-13 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK021_1', 'MBR021', 'CRD021', '2026-05-19 06:56:39', '2026-05-19 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK021_2', 'MBR021', 'CRD021', '2026-04-27 01:56:39', '2026-04-27 02:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK021_3', 'MBR021', 'CRD021', '2026-05-16 05:56:39', '2026-05-16 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK021_4', 'MBR021', 'CRD021', '2026-05-11 02:56:39', '2026-05-11 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK022_0', 'MBR022', 'CRD022', '2026-05-21 09:56:39', '2026-05-21 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK022_1', 'MBR022', 'CRD022', '2026-05-16 03:56:39', '2026-05-16 04:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK022_2', 'MBR022', 'CRD022', '2026-04-25 10:56:39', '2026-04-25 12:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK022_3', 'MBR022', 'CRD022', '2026-05-12 07:56:39', '2026-05-12 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK023_0', 'MBR023', 'CRD023', '2026-05-12 10:56:39', '2026-05-12 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK023_1', 'MBR023', 'CRD023', '2026-05-08 05:56:39', '2026-05-08 07:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK024_0', 'MBR024', 'CRD024', '2026-04-29 06:56:39', '2026-04-29 08:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK024_1', 'MBR024', 'CRD024', '2026-04-23 02:56:39', '2026-04-23 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK024_2', 'MBR024', 'CRD024', '2026-05-18 02:56:39', '2026-05-18 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK024_3', 'MBR024', 'CRD024', '2026-04-24 07:56:39', '2026-04-24 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK024_4', 'MBR024', 'CRD024', '2026-04-28 09:56:39', '2026-04-28 11:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK025_0', 'MBR025', 'CRD025', '2026-04-23 07:56:39', '2026-04-23 09:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK025_1', 'MBR025', 'CRD025', '2026-05-07 02:56:39', '2026-05-07 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK025_2', 'MBR025', 'CRD025', '2026-05-02 04:56:39', '2026-05-02 06:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK025_3', 'MBR025', 'CRD025', '2026-04-26 01:56:39', '2026-04-26 03:56:39', 'CARD', 'Quét thẻ thành công'),
        ('CHK025_4', 'MBR025', 'CRD025', '2026-05-10 05:56:39', '2026-05-10 07:56:39', 'CARD', 'Quét thẻ thành công')
    """)

    # ─── Seed Classes ─────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Classes (id, name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status, startDate, endDate) VALUES
        ('CLS001', 'Yoga Thiền Định', 'PT002', 'SP001', 'FAC001', '06:00 - 07:30', 'Thứ 2,Thứ 4,Thứ 6,Chủ nhật', 25, 0, 'ACTIVE', '2026-01-01', '2026-12-30'),
        ('CLS002', 'Yoga Cân Bằng', 'PT002', 'SP001', 'FAC002', '18:00 - 19:30', 'Thứ 3,Thứ 5,Chủ nhật', 20, 0, 'ACTIVE', '2026-01-15', '2026-12-15'),
        ('CLS003', 'Boxing Đối Kháng', 'PT003', 'SP003', 'FAC005', '19:00 - 20:30', 'Thứ 2,Thứ 4,Thứ 6,Chủ nhật', 15, 0, 'ACTIVE', '2026-01-01', '2026-12-31'),
        ('CLS004', 'Zumba Đốt Mỡ', 'PT004', 'SP004', 'FAC006', '17:30 - 18:30', 'Thứ 3,Thứ 5,Thứ 7,Chủ nhật', 40, 0, 'ACTIVE', '2026-01-01', '2026-12-31'),
        ('CLS005', 'Dạy Bơi Sải', 'PT005', 'SP005', 'FAC007', '08:00 - 09:30', 'Chủ nhật', 10, 500000, 'ACTIVE', '2026-01-01', '2026-12-30')
    """)

    # ─── Seed ClassEnrollments ────────────────────────────────────────────────
    cur.execute("""INSERT INTO ClassEnrollments (classId, memberId, status) VALUES
        ('CLS001', 'MBR022', 'ACTIVE'),
        ('CLS001', 'MBR011', 'ACTIVE'),
        ('CLS001', 'MBR010', 'ACTIVE'),
        ('CLS001', 'MBR013', 'ACTIVE'),
        ('CLS001', 'MBR016', 'ACTIVE'),
        ('CLS001', 'MBR002', 'ACTIVE'),
        ('CLS001', 'MBR012', 'ACTIVE'),
        ('CLS002', 'MBR022', 'ACTIVE'),
        ('CLS002', 'MBR006', 'ACTIVE'),
        ('CLS002', 'MBR012', 'ACTIVE'),
        ('CLS002', 'MBR016', 'ACTIVE'),
        ('CLS002', 'MBR020', 'ACTIVE'),
        ('CLS002', 'MBR001', 'ACTIVE'),
        ('CLS002', 'MBR004', 'ACTIVE'),
        ('CLS003', 'MBR006', 'ACTIVE'),
        ('CLS003', 'MBR009', 'ACTIVE'),
        ('CLS003', 'MBR019', 'ACTIVE'),
        ('CLS003', 'MBR008', 'ACTIVE'),
        ('CLS003', 'MBR002', 'ACTIVE'),
        ('CLS003', 'MBR018', 'ACTIVE'),
        ('CLS003', 'MBR003', 'ACTIVE'),
        ('CLS004', 'MBR023', 'ACTIVE'),
        ('CLS004', 'MBR017', 'ACTIVE'),
        ('CLS004', 'MBR012', 'ACTIVE'),
        ('CLS004', 'MBR005', 'ACTIVE'),
        ('CLS004', 'MBR009', 'ACTIVE'),
        ('CLS004', 'MBR018', 'ACTIVE'),
        ('CLS004', 'MBR015', 'ACTIVE'),
        ('CLS004', 'MBR014', 'ACTIVE'),
        ('CLS004', 'MBR007', 'ACTIVE'),
        ('CLS004', 'MBR001', 'ACTIVE'),
        ('CLS004', 'MBR016', 'ACTIVE'),
        ('CLS005', 'MBR023', 'ACTIVE'),
        ('CLS005', 'MBR017', 'ACTIVE'),
        ('CLS005', 'MBR004', 'ACTIVE'),
        ('CLS005', 'MBR021', 'ACTIVE'),
        ('CLS005', 'MBR001', 'ACTIVE'),
        ('CLS005', 'MBR002', 'ACTIVE')
    """)

    # ─── Seed Events ──────────────────────────────────────────────────────────
    cur.execute("""INSERT INTO Events (id, name, description, date, time, endTime, location, facilityId, capacity, price, status) VALUES
        ('EVT001', 'Đại hội Thể hình Cơ bắp', 'Cuộc thi khoe nét đẹp hình thể cơ bắp nam nữ', '2026-07-15', '09:00', '12:00', 'Sân khấu lớn', 'FAC004', 100, 200000, 'UPCOMING'),
        ('EVT002', 'Giao lưu Yoga Cộng đồng', 'Buổi tập yoga chung kết nối cộng đồng 500 người', '2026-08-20', '06:00', '08:00', 'Công viên Trung tâm', 'FAC001', 500, 0, 'UPCOMING'),
        ('EVT003', 'Giải Vô địch Cầu Lông CLB', 'Giải đấu nội bộ chọn ra tay vợt xuất sắc nhất', '2026-09-02', '08:00', '16:00', 'Sân Cầu Lông 1 & 2', 'FAC008', 32, 100000, 'UPCOMING')
    """)
    
    # ─── Seed TrainerAttendance ───────────────────────────────────────────────
    cur.execute("""INSERT INTO TrainerAttendance (id, trainerId, classId, attendanceDate, checkIn, checkOut, status, sessionsCount, note) VALUES
        ('TATT_001', 'PT002', 'CLS001', '2026-05-15', '05:45', '07:45', 'PRESENT', 1, 'Dạy đúng giờ'),
        ('TATT_002', 'PT002', 'CLS002', '2026-05-15', '17:45', '19:40', 'PRESENT', 1, ''),
        ('TATT_003', 'PT003', 'CLS003', '2026-05-15', '18:50', '20:35', 'PRESENT', 1, ''),
        ('TATT_004', 'PT004', 'CLS004', '2026-05-16', '17:20', '18:40', 'PRESENT', 1, ''),
        ('TATT_005', 'PT005', 'CLS005', '2026-05-17', '07:50', '09:40', 'PRESENT', 1, ''),
        ('TATT_006', 'PT002', 'CLS001', '2026-05-18', '05:50', '07:35', 'PRESENT', 1, ''),
        ('TATT_007', 'PT003', 'CLS003', '2026-05-18', '19:05', '20:30', 'LATE', 1, 'Đến muộn 5p do kẹt xe'),
        ('TATT_008', 'PT002', 'CLS002', '2026-05-19', '17:50', '19:35', 'PRESENT', 1, ''),
        ('TATT_009', 'PT004', 'CLS004', '2026-05-19', '17:25', '18:35', 'PRESENT', 1, ''),
        ('TATT_010', 'PT002', 'CLS001', '2026-05-20', '05:40', '07:40', 'PRESENT', 1, ''),
        ('TATT_011', 'PT003', 'CLS003', '2026-05-20', '18:45', '20:45', 'PRESENT', 1, ''),
        ('TATT_012', 'PT002', 'CLS002', '2026-05-21', '17:55', '19:40', 'PRESENT', 1, ''),
        ('TATT_013', 'PT004', 'CLS004', '2026-05-21', '17:20', '18:45', 'PRESENT', 1, ''),
        ('TATT_014', 'PT002', 'CLS001', '2026-05-22', '05:55', '07:35', 'PRESENT', 1, ''),
        ('TATT_015', 'PT003', 'CLS003', '2026-05-22', '18:55', '20:40', 'PRESENT', 1, ''),
        ('TATT_016', 'PT002', 'CLS001', '2026-05-24', '05:50', '07:30', 'PRESENT', 1, ''),
        ('TATT_017', 'PT003', 'CLS003', '2026-05-24', '18:45', NULL, 'PRESENT', 1, '')
    """)

    # ─── Seed TrainerSalaries ─────────────────────────────────────────────────
    cur.execute("""INSERT INTO TrainerSalaries (id, trainerId, month, year, baseSalary, totalSessions, sessionBonus, bonus, deductions, totalAmount, paymentStatus, paidDate, note) VALUES
        ('SAL_04_002', 'PT002', 4, 2026, 5000000, 24, 3600000, 500000, 0, 9100000, 'PAID', '2026-05-05 10:00:00', 'Lương tháng 4 (đã thanh toán)'),
        ('SAL_04_003', 'PT003', 4, 2026, 5000000, 12, 1800000, 0, 200000, 6600000, 'PAID', '2026-05-05 10:00:00', 'Lương tháng 4 (đã thanh toán)'),
        ('SAL_04_004', 'PT004', 4, 2026, 5000000, 14, 2100000, 200000, 0, 7300000, 'PAID', '2026-05-05 10:00:00', 'Lương tháng 4 (đã thanh toán)'),
        ('SAL_04_005', 'PT005', 4, 2026, 5000000, 4, 600000, 0, 0, 5600000, 'PAID', '2026-05-05 10:00:00', 'Lương tháng 4 (đã thanh toán)'),
        ('SAL_05_002', 'PT002', 5, 2026, 5000000, 6, 900000, 300000, 0, 6200000, 'PENDING', NULL, 'Tạm tính lương tháng 5'),
        ('SAL_05_003', 'PT003', 5, 2026, 5000000, 4, 600000, 0, 100000, 5500000, 'PENDING', NULL, 'Tạm tính lương tháng 5'),
        ('SAL_05_004', 'PT004', 5, 2026, 5000000, 3, 450000, 0, 0, 5450000, 'PENDING', NULL, 'Tạm tính lương tháng 5'),
        ('SAL_05_005', 'PT005', 5, 2026, 5000000, 1, 150000, 0, 0, 5150000, 'PENDING', NULL, 'Tạm tính lương tháng 5')
    """)


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

