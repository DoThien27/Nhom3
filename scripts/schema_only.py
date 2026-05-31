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
    status     ENUM('ACTIVE','INACTIVE','FULL') NOT NULL DEFAULT 'ACTIVE',
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
    status     ENUM('ACTIVE','CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    UNIQUE KEY uq_class_member (classId, memberId),
    FOREIGN KEY (classId)  REFERENCES Classes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (memberId) REFERENCES Members(id) ON DELETE CASCADE ON UPDATE CASCADE
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
