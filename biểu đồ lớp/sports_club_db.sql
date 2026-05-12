-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th5 05, 2026 lúc 11:43 AM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `sports_club_db`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `classenrollments`
--

CREATE TABLE `classenrollments` (
  `classId` varchar(50) NOT NULL,
  `memberId` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `classenrollments`
--

INSERT INTO `classenrollments` (`classId`, `memberId`) VALUES
('C001', 'M001'),
('C001', 'M003'),
('C001', 'M005'),
('C001', 'M007'),
('C001', 'M009'),
('C001', 'M011'),
('C001', 'M013'),
('C002', 'M002'),
('C002', 'M004'),
('C002', 'M006'),
('C002', 'M008'),
('C002', 'M010'),
('C003', 'M003'),
('C003', 'M005'),
('C003', 'M007'),
('C003', 'M012'),
('C003', 'M014'),
('C004', 'M001'),
('C004', 'M002'),
('C004', 'M006'),
('C004', 'M010'),
('C004', 'M012'),
('C004', 'M014'),
('C004', 'M015'),
('C005', 'M003'),
('C005', 'M009'),
('C005', 'M011'),
('C005', 'M015');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `classes`
--

CREATE TABLE `classes` (
  `id` varchar(50) NOT NULL,
  `name` varchar(150) DEFAULT NULL,
  `trainerId` varchar(50) DEFAULT NULL,
  `time` varchar(100) DEFAULT NULL,
  `dayOfWeek` varchar(100) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  `price` decimal(12,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `classes`
--

INSERT INTO `classes` (`id`, `name`, `trainerId`, `time`, `dayOfWeek`, `capacity`, `price`) VALUES
('C001', 'Yoga Trưa', 'U003', '12:00', 'Thứ 2, 4, 6', 15, 200000.00),
('C002', 'Boxing Cơ Bản', 'U004', '18:30', 'Thứ 3, 5, 7', 20, 250000.00),
('C003', 'Zumba Dance', 'U004', '19:00', 'Thứ 2, 4, 6', 25, 150000.00),
('C004', 'Thể hình cơ bản', 'U002', '07:00', 'Thứ 2 đến 6', 30, 0.00),
('C005', 'Pilates', 'U003', '08:00', 'Thứ 3, 5', 12, 300000.00);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `eventparticipants`
--

CREATE TABLE `eventparticipants` (
  `id` varchar(50) NOT NULL,
  `eventId` varchar(50) DEFAULT NULL,
  `memberId` varchar(50) DEFAULT NULL,
  `memberName` varchar(150) DEFAULT NULL,
  `registerDate` datetime DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `eventparticipants`
--

INSERT INTO `eventparticipants` (`id`, `eventId`, `memberId`, `memberName`, `registerDate`, `status`) VALUES
('EP001', 'E004', 'M001', 'Phạm Văn Nam', '2024-04-25 00:00:00', 'APPROVED'),
('EP002', 'E004', 'M002', 'Lê Hoàng Anh', '2024-04-26 00:00:00', 'APPROVED'),
('EP003', 'E004', 'M003', 'Nguyễn Thùy Chi', '2024-04-27 00:00:00', 'APPROVED'),
('EP004', 'E004', 'M006', 'Ngô Quốc Hùng', '2024-04-28 00:00:00', 'REJECTED'),
('EP005', 'E005', 'M004', 'Trần Minh Khoa', '2024-04-10 00:00:00', 'APPROVED'),
('EP006', 'E005', 'M006', 'Ngô Quốc Hùng', '2024-04-11 00:00:00', 'APPROVED'),
('EP007', 'E005', 'M010', 'Lý Hoàng Nam', '2024-04-12 00:00:00', 'APPROVED'),
('EP008', 'E001', 'M001', 'Phạm Văn Nam', '2024-05-01 00:00:00', 'PENDING'),
('EP009', 'E001', 'M002', 'Lê Hoàng Anh', '2024-05-02 00:00:00', 'PENDING'),
('EP010', 'E001', 'M006', 'Ngô Quốc Hùng', '2024-05-03 00:00:00', 'APPROVED'),
('EP011', 'E002', 'M003', 'Nguyễn Thùy Chi', '2024-04-10 00:00:00', 'REJECTED'),
('EP012', 'E002', 'M005', 'Đỗ Thị Hoa', '2024-04-11 00:00:00', 'APPROVED'),
('EP013', 'E002', 'M009', 'Phạm Lan Anh', '2024-04-12 00:00:00', 'REJECTED');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `events`
--

CREATE TABLE `events` (
  `id` varchar(50) NOT NULL,
  `name` varchar(150) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `date` date DEFAULT NULL,
  `time` varchar(50) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  `price` decimal(12,2) DEFAULT 0.00,
  `status` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `events`
--

INSERT INTO `events` (`id`, `name`, `description`, `date`, `time`, `location`, `capacity`, `price`, `status`) VALUES
('E001', 'Giải Bóng Đá Nội Bộ 2024', 'Giải đấu bóng đá giao hữu giữa các hội viên CLB', '2024-06-15', '08:00', 'Sân bóng đá mini', 150, 50000.00, 'UPCOMING'),
('E002', 'Giải Cầu Lông Thành Viên 2024', 'Thi đấu cầu lông theo thể thức loại trực tiếp', '2024-05-20', '06:30', 'Sân cầu lông số 1', 40, 0.00, 'UPCOMING'),
('E003', 'Ngày Hội Thể Thao CLB 2024', 'Liên hoan thể thao cuối năm cho toàn bộ hội viên', '2024-08-10', '09:00', 'Sân ngoài trời', 300, 100000.00, 'UPCOMING'),
('E004', 'Workshop Dinh Dưỡng Thể Thao', 'Chuyên gia chia sẻ về chế độ dinh dưỡng cho VDV', '2024-05-05', '14:00', 'Phòng hội thảo', 80, 0.00, 'COMPLETED'),
('E005', 'Giải Giao Hữu Võ Thuật', 'Buổi biểu diễn và thi đấu võ thuật giao hữu', '2024-04-20', '15:00', 'Phòng tập võ', 100, 20000.00, 'COMPLETED'),
('E006', 'Khai Giảng Lớp Bơi Lội 2024', 'Lễ khai giảng lớp bơi lội dành cho mọi lứa tuổi', '2024-07-01', '18:00', 'Hồ bơi', 60, 0.00, 'UPCOMING');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `facilities`
--

CREATE TABLE `facilities` (
  `facility_id` varchar(50) NOT NULL,
  `facility_name` varchar(150) DEFAULT NULL,
  `facility_type` varchar(100) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `capacity` int(11) DEFAULT 0,
  `rental_price` decimal(12,2) DEFAULT 0.00,
  `status` varchar(20) DEFAULT 'ACTIVE',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `facilities`
--

INSERT INTO `facilities` (`facility_id`, `facility_name`, `facility_type`, `location`, `capacity`, `rental_price`, `status`, `created_at`) VALUES
('F001', 'Sân bóng đá mini', 'Sân ngoài trời', 'Khu A', 22, 300000.00, 'ACTIVE', '2026-05-03 13:51:33'),
('F002', 'Sân cầu lông số 1', 'Sân trong nhà', 'Khu B', 6, 100000.00, 'ACTIVE', '2026-05-03 13:51:33'),
('F003', 'Sân cầu lông số 2', 'Sân trong nhà', 'Khu B', 6, 100000.00, 'ACTIVE', '2026-05-03 13:51:33'),
('F004', 'Phòng yoga', 'Phòng trong nhà', 'Khu C', 25, 150000.00, 'ACTIVE', '2026-05-03 13:51:33'),
('F005', 'Phòng gym', 'Phòng trong nhà', 'Khu C', 50, 50000.00, 'ACTIVE', '2026-05-03 13:51:33'),
('F006', 'Hồ bơi', 'Ngoài trời', 'Khu D', 100, 80000.00, 'ACTIVE', '2026-05-03 13:51:33'),
('F007', 'Sân bóng chuyền', 'Sân ngoài trời', 'Khu A', 12, 120000.00, 'ACTIVE', '2026-05-03 13:51:33'),
('F008', 'Phòng võ thuật', 'Phòng trong nhà', 'Khu C', 30, 80000.00, 'ACTIVE', '2026-05-03 13:51:33');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `invoiceitems`
--

CREATE TABLE `invoiceitems` (
  `id` int(11) NOT NULL,
  `invoiceId` varchar(50) DEFAULT NULL,
  `item_type` varchar(20) DEFAULT 'OTHER',
  `reference_id` varchar(50) DEFAULT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `quantity` int(11) DEFAULT 1,
  `unit_price` decimal(12,2) DEFAULT 0.00,
  `discount_amount` decimal(12,2) DEFAULT 0.00,
  `line_total` decimal(12,2) DEFAULT 0.00,
  `item_note` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `invoiceitems`
--

INSERT INTO `invoiceitems` (`id`, `invoiceId`, `item_type`, `reference_id`, `item_name`, `quantity`, `unit_price`, `discount_amount`, `line_total`, `item_note`, `created_at`) VALUES
(1, 'INV001', 'OTHER', NULL, 'Gói Standard 3 tháng', 1, 1200000.00, 0.00, 1200000.00, NULL, '2026-05-03 13:51:33'),
(2, 'INV002', 'OTHER', NULL, 'Gói VIP 6 tháng', 1, 2200000.00, 0.00, 2200000.00, NULL, '2026-05-03 13:51:33'),
(3, 'INV003', 'OTHER', NULL, 'Whey Protein Gold', 1, 1500000.00, 0.00, 1500000.00, NULL, '2026-05-03 13:51:33'),
(4, 'INV003', 'OTHER', NULL, 'Nước tăng lực Sting', 2, 15000.00, 0.00, 30000.00, NULL, '2026-05-03 13:51:33'),
(5, 'INV004', 'OTHER', NULL, 'Gói Pro 1 năm', 1, 4000000.00, 0.00, 4000000.00, NULL, '2026-05-03 13:51:33'),
(6, 'INV005', 'OTHER', NULL, 'Gói Cơ Bản 1 tháng', 1, 500000.00, 0.00, 500000.00, NULL, '2026-05-03 13:51:33'),
(7, 'INV005', 'OTHER', NULL, 'Găng tay tập gym', 1, 250000.00, 0.00, 250000.00, NULL, '2026-05-03 13:51:33'),
(8, 'INV006', 'OTHER', NULL, 'Yoga Cơ Bản 12 buổi', 1, 800000.00, 0.00, 800000.00, NULL, '2026-05-03 13:51:33'),
(9, 'INV007', 'OTHER', NULL, 'BCAA 3000mg', 1, 800000.00, 0.00, 800000.00, NULL, '2026-05-03 13:51:33'),
(10, 'INV007', 'OTHER', NULL, 'Nước khoáng Lavie', 5, 10000.00, 0.00, 50000.00, NULL, '2026-05-03 13:51:33'),
(11, 'INV008', 'OTHER', NULL, 'PT cá nhân 10 buổi', 1, 3000000.00, 0.00, 3000000.00, NULL, '2026-05-03 13:51:33'),
(12, 'INV009', 'OTHER', NULL, 'Gói Standard 3 tháng', 1, 1200000.00, 0.00, 1200000.00, NULL, '2026-05-03 13:51:33'),
(13, 'INV010', 'OTHER', NULL, 'PT cá nhân 10 buổi', 1, 3000000.00, 0.00, 3000000.00, NULL, '2026-05-03 13:51:33'),
(14, 'INV011', 'OTHER', NULL, 'Gói Cơ Bản 1 tháng', 1, 500000.00, 0.00, 500000.00, NULL, '2026-05-03 13:51:33'),
(15, 'INV012', 'OTHER', NULL, 'Thảm tập Yoga 6mm', 1, 350000.00, 0.00, 350000.00, NULL, '2026-05-03 13:51:33'),
(16, 'INV012', 'OTHER', NULL, 'Nước tăng lực Sting', 3, 15000.00, 0.00, 45000.00, NULL, '2026-05-03 13:51:33'),
(17, 'INV013', 'OTHER', NULL, 'Creatine Monohydrate', 1, 500000.00, 0.00, 500000.00, NULL, '2026-05-03 13:51:33'),
(18, 'INV013', 'OTHER', NULL, 'Bình nước 1.5L', 1, 120000.00, 0.00, 120000.00, NULL, '2026-05-03 13:51:33'),
(19, 'INV014', 'OTHER', NULL, 'Gói VIP 6 tháng', 1, 2200000.00, 0.00, 2200000.00, NULL, '2026-05-03 13:51:33'),
(20, 'INV015', 'OTHER', NULL, 'Gói Standard 3 tháng', 1, 1200000.00, 0.00, 1200000.00, NULL, '2026-05-03 13:51:33'),
(21, 'INV016', 'OTHER', NULL, 'Gói Pro 1 năm', 1, 4000000.00, 0.00, 4000000.00, NULL, '2026-05-03 13:51:33'),
(22, 'INV017', 'OTHER', NULL, 'Whey Protein Gold', 1, 1500000.00, 0.00, 1500000.00, NULL, '2026-05-03 13:51:33'),
(23, 'INV017', 'OTHER', NULL, 'Creatine Monohydrate', 1, 500000.00, 0.00, 500000.00, NULL, '2026-05-03 13:51:33'),
(24, 'INV018', 'OTHER', NULL, 'Thảm tập Yoga 6mm', 2, 350000.00, 0.00, 700000.00, NULL, '2026-05-03 13:51:33'),
(25, 'INV018', 'OTHER', NULL, 'Nước khoáng Lavie', 10, 10000.00, 0.00, 100000.00, NULL, '2026-05-03 13:51:33'),
(26, 'INV019', 'OTHER', NULL, 'BCAA 3000mg', 1, 800000.00, 0.00, 800000.00, NULL, '2026-05-03 13:51:33'),
(27, 'INV019', 'OTHER', NULL, 'Nước tăng lực Sting', 4, 15000.00, 0.00, 60000.00, NULL, '2026-05-03 13:51:33'),
(28, 'INV020', 'OTHER', NULL, 'Găng tay tập gym', 1, 250000.00, 0.00, 250000.00, NULL, '2026-05-03 13:51:33'),
(29, 'INV020', 'OTHER', NULL, 'Bình nước 1.5L', 1, 120000.00, 0.00, 120000.00, NULL, '2026-05-03 13:51:33'),
(30, 'INV021', 'OTHER', NULL, 'Gói Standard 3 tháng', 1, 1200000.00, 0.00, 1200000.00, NULL, '2026-05-03 13:51:33'),
(31, 'INV022', 'OTHER', NULL, 'Whey Protein Gold', 1, 1500000.00, 0.00, 1500000.00, NULL, '2026-05-03 13:51:33'),
(32, 'INV023', 'OTHER', NULL, 'PT cá nhân 10 buổi', 1, 3000000.00, 0.00, 3000000.00, NULL, '2026-05-03 13:51:33'),
(33, 'INV024', 'OTHER', NULL, 'BCAA 3000mg', 2, 800000.00, 0.00, 1600000.00, NULL, '2026-05-03 13:51:33'),
(34, 'INV024', 'OTHER', NULL, 'Nước tăng lực Sting', 5, 15000.00, 0.00, 75000.00, NULL, '2026-05-03 13:51:33'),
(35, 'INV025', 'OTHER', NULL, 'Yoga Cơ Bản 12 buổi', 1, 800000.00, 0.00, 800000.00, NULL, '2026-05-03 13:51:33'),
(36, 'INV026', 'OTHER', NULL, 'Whey Protein Gold', 1, 1500000.00, 0.00, 1500000.00, NULL, '2026-05-03 13:51:33'),
(37, 'INV026', 'OTHER', NULL, 'Bình nước 1.5L', 2, 120000.00, 0.00, 240000.00, NULL, '2026-05-03 13:51:33'),
(38, 'INV027', 'OTHER', NULL, 'Gói VIP 6 tháng', 1, 2200000.00, 0.00, 2200000.00, NULL, '2026-05-03 13:51:33'),
(39, 'INV028', 'OTHER', NULL, 'Creatine Monohydrate', 1, 500000.00, 0.00, 500000.00, NULL, '2026-05-03 13:51:33'),
(40, 'INV028', 'OTHER', NULL, 'Nước khoáng Lavie', 6, 10000.00, 0.00, 60000.00, NULL, '2026-05-03 13:51:33'),
(41, 'INV029', 'OTHER', NULL, 'Găng tay tập gym', 1, 250000.00, 0.00, 250000.00, NULL, '2026-05-03 13:51:33'),
(42, 'INV029', 'OTHER', NULL, 'Thảm tập Yoga 6mm', 1, 350000.00, 0.00, 350000.00, NULL, '2026-05-03 13:51:33'),
(43, 'INV030', 'OTHER', NULL, 'Gói VIP 6 tháng', 1, 2200000.00, 0.00, 2200000.00, NULL, '2026-05-03 13:51:33'),
(44, 'INV031', 'OTHER', NULL, 'Gói Cơ Bản 1 tháng', 1, 500000.00, 0.00, 500000.00, NULL, '2026-05-03 13:51:33'),
(45, 'INV032', 'OTHER', NULL, 'PT cá nhân 10 buổi', 1, 3000000.00, 0.00, 3000000.00, NULL, '2026-05-03 13:51:33'),
(46, 'INV033', 'OTHER', NULL, 'Whey Protein Gold', 1, 1500000.00, 0.00, 1500000.00, NULL, '2026-05-03 13:51:33'),
(47, 'INV033', 'OTHER', NULL, 'BCAA 3000mg', 1, 800000.00, 0.00, 800000.00, NULL, '2026-05-03 13:51:33'),
(48, 'INV034', 'OTHER', NULL, 'Creatine Monohydrate', 2, 500000.00, 0.00, 1000000.00, NULL, '2026-05-03 13:51:33'),
(49, 'INV034', 'OTHER', NULL, 'Nước tăng lực Sting', 4, 15000.00, 0.00, 60000.00, NULL, '2026-05-03 13:51:33'),
(50, 'INV035', 'OTHER', NULL, 'Bình nước 1.5L', 1, 120000.00, 0.00, 120000.00, NULL, '2026-05-03 13:51:33'),
(51, 'INV035', 'OTHER', NULL, 'Nước khoáng Lavie', 8, 10000.00, 0.00, 80000.00, NULL, '2026-05-03 13:51:33'),
(52, 'INV036', 'OTHER', NULL, 'Găng tay tập gym', 2, 250000.00, 0.00, 500000.00, NULL, '2026-05-03 13:51:33'),
(53, 'INV036', 'OTHER', NULL, 'Thảm tập Yoga 6mm', 1, 350000.00, 0.00, 350000.00, NULL, '2026-05-03 13:51:33'),
(54, 'INV037', 'OTHER', NULL, 'Whey Protein Gold', 1, 1500000.00, 0.00, 1500000.00, NULL, '2026-05-03 13:51:33'),
(55, 'INV038', 'OTHER', NULL, 'Gói Standard 3 tháng', 1, 1200000.00, 0.00, 1200000.00, NULL, '2026-05-03 13:51:33'),
(56, 'INV1777792704', 'MEMBERSHIP', 'P005', 'Yoga Cơ Bản (12 buổi)', 1, 800000.00, 0.00, 800000.00, '', '2026-05-03 14:18:24');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `invoices`
--

CREATE TABLE `invoices` (
  `id` varchar(50) NOT NULL,
  `memberId` varchar(50) DEFAULT NULL,
  `total` decimal(12,2) DEFAULT 0.00,
  `discount_amount` decimal(12,2) DEFAULT 0.00,
  `final_amount` decimal(12,2) DEFAULT 0.00,
  `paid_amount` decimal(12,2) DEFAULT 0.00,
  `remaining_amount` decimal(12,2) DEFAULT 0.00,
  `date` datetime DEFAULT NULL,
  `method` varchar(50) DEFAULT 'CASH',
  `payment_status` varchar(20) DEFAULT 'UNPAID',
  `note` text DEFAULT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `invoices`
--

INSERT INTO `invoices` (`id`, `memberId`, `total`, `discount_amount`, `final_amount`, `paid_amount`, `remaining_amount`, `date`, `method`, `payment_status`, `note`, `created_by`, `created_at`, `updated_at`) VALUES
('INV001', 'M001', 1200000.00, 0.00, 1200000.00, 1200000.00, 0.00, '2024-01-15 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV002', 'M002', 2200000.00, 0.00, 2200000.00, 2200000.00, 0.00, '2024-01-20 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV003', 'M003', 1530000.00, 0.00, 1530000.00, 1530000.00, 0.00, '2024-01-25 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV004', 'M003', 4000000.00, 0.00, 4000000.00, 4000000.00, 0.00, '2024-02-05 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV005', 'M004', 750000.00, 0.00, 750000.00, 750000.00, 0.00, '2024-02-10 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV006', 'M005', 800000.00, 0.00, 800000.00, 800000.00, 0.00, '2024-02-20 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV007', 'M001', 850000.00, 0.00, 850000.00, 850000.00, 0.00, '2024-02-22 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV008', 'M002', 3000000.00, 0.00, 3000000.00, 3000000.00, 0.00, '2024-02-28 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV009', 'M006', 1200000.00, 0.00, 1200000.00, 1200000.00, 0.00, '2024-03-01 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV010', 'M007', 3000000.00, 0.00, 3000000.00, 3000000.00, 0.00, '2024-03-15 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV011', 'M008', 500000.00, 0.00, 500000.00, 500000.00, 0.00, '2024-03-20 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV012', 'M004', 395000.00, 0.00, 395000.00, 395000.00, 0.00, '2024-03-25 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV013', 'M005', 620000.00, 0.00, 620000.00, 620000.00, 0.00, '2024-03-28 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV014', 'M009', 2200000.00, 0.00, 2200000.00, 2200000.00, 0.00, '2024-04-01 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV015', 'M010', 1200000.00, 0.00, 1200000.00, 1200000.00, 0.00, '2024-04-10 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV016', 'M011', 4000000.00, 0.00, 4000000.00, 4000000.00, 0.00, '2024-04-15 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV017', 'M003', 2000000.00, 0.00, 2000000.00, 2000000.00, 0.00, '2024-04-18 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV018', 'M007', 800000.00, 0.00, 800000.00, 800000.00, 0.00, '2024-04-20 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV019', 'M006', 860000.00, 0.00, 860000.00, 860000.00, 0.00, '2024-04-25 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV020', 'M001', 370000.00, 0.00, 370000.00, 370000.00, 0.00, '2024-04-28 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV021', 'M012', 1200000.00, 0.00, 1200000.00, 1200000.00, 0.00, '2024-05-01 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV022', 'M009', 1500000.00, 0.00, 1500000.00, 1500000.00, 0.00, '2024-05-05 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV023', 'M010', 3000000.00, 0.00, 3000000.00, 3000000.00, 0.00, '2024-05-08 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV024', 'M011', 1675000.00, 0.00, 1675000.00, 1675000.00, 0.00, '2024-05-12 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV025', 'M013', 800000.00, 0.00, 800000.00, 800000.00, 0.00, '2024-05-15 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV026', 'M002', 1740000.00, 0.00, 1740000.00, 1740000.00, 0.00, '2024-05-18 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV027', 'M006', 2200000.00, 0.00, 2200000.00, 2200000.00, 0.00, '2024-05-22 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV028', 'M012', 560000.00, 0.00, 560000.00, 560000.00, 0.00, '2024-05-25 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV029', 'M003', 600000.00, 0.00, 600000.00, 600000.00, 0.00, '2024-05-28 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV030', 'M014', 2200000.00, 0.00, 2200000.00, 2200000.00, 0.00, '2024-06-01 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV031', 'M015', 500000.00, 0.00, 500000.00, 500000.00, 0.00, '2024-06-15 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV032', 'M001', 3000000.00, 0.00, 3000000.00, 3000000.00, 0.00, '2024-06-18 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV033', 'M009', 2300000.00, 0.00, 2300000.00, 2300000.00, 0.00, '2024-06-20 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV034', 'M010', 1060000.00, 0.00, 1060000.00, 1060000.00, 0.00, '2024-06-22 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV035', 'M011', 200000.00, 0.00, 200000.00, 200000.00, 0.00, '2024-06-25 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV036', 'M014', 850000.00, 0.00, 850000.00, 850000.00, 0.00, '2024-06-28 00:00:00', 'TRANSFER', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV037', 'M012', 1500000.00, 0.00, 1500000.00, 1500000.00, 0.00, '2024-06-29 00:00:00', 'CASH', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV038', 'M002', 1200000.00, 0.00, 1200000.00, 1200000.00, 0.00, '2024-06-30 00:00:00', 'E-WALLET', 'PAID', NULL, 'U001', '2026-05-03 13:51:33', '2026-05-03 13:51:33'),
('INV1777792704', 'M001', 800000.00, 0.00, 800000.00, 800000.00, 0.00, '2026-05-03 14:18:24', 'CASH', 'PAID', '', 'U001', '2026-05-03 14:18:24', '2026-05-03 14:21:10');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `members`
--

CREATE TABLE `members` (
  `id` varchar(50) NOT NULL,
  `fullName` varchar(150) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `joinDate` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `previousWeight` decimal(5,2) DEFAULT NULL,
  `activePlanId` varchar(50) DEFAULT NULL,
  `expiryDate` date DEFAULT NULL,
  `assignedPTId` varchar(50) DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `homeTown` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `members`
--

INSERT INTO `members` (`id`, `fullName`, `phone`, `email`, `joinDate`, `status`, `weight`, `previousWeight`, `activePlanId`, `expiryDate`, `assignedPTId`, `username`, `password`, `avatar`, `homeTown`) VALUES
('M001', 'Phạm Văn Nam', '0912345678', 'nam@gmail.com', '2024-01-15', 'ACTIVE', 75.50, 78.00, 'P002', '2024-04-15', 'U003', 'nam01', '$2b$12$A1pKvHaodbhbUqPpHhMGGOMDB1OUtYxNVeFz76dYFyDzIlLzyjgpu', NULL, 'Hà Nội'),
('M002', 'Lê Hoàng Anh', '0987654321', 'anh@gmail.com', '2024-01-20', 'ACTIVE', 62.00, 65.00, 'P003', '2024-07-20', 'U002', 'anh_lh', '$2b$12$UJNzgxs4x7pFuEg..g2KUOfSJ7Yci3bG9diz/mQHRW2i4/Wea45DC', NULL, 'Hải Phòng'),
('M003', 'Nguyễn Thùy Chi', '0933445566', 'chi@gmail.com', '2024-02-05', 'ACTIVE', 50.50, 52.00, 'P004', '2025-02-05', 'U003', 'chi_nt', '$2b$12$fVOUIXMJdknP0BEwf5TBlemmFtEQWcGBRT6wkQFk4LwwwucHRpZpW', NULL, 'Đà Nẵng'),
('M004', 'Trần Minh Khoa', '0911223344', 'khoa@gmail.com', '2024-02-10', 'ACTIVE', 80.00, 82.50, 'P001', '2024-03-10', 'U004', 'khoa_tm', '$2b$12$y8WlSRk6iMgdxixUCfjgkuq4yzmxww1UkP4uWrQ9MBRH/dV8kzPlW', NULL, 'TP.HCM'),
('M005', 'Đỗ Thị Hoa', '0944556677', 'hoa@gmail.com', '2024-02-20', 'ACTIVE', 53.00, 55.00, 'P005', '2024-03-20', 'U003', 'hoa_dt', '$2b$12$e81ErI7yRu28neOD6g/s.OSy5Eed1lFYCAILeuebz14pUtWqtWlbO', NULL, 'Cần Thơ'),
('M006', 'Ngô Quốc Hùng', '0966778899', 'hung@gmail.com', '2024-03-01', 'ACTIVE', 90.00, 92.00, 'P002', '2024-06-01', 'U004', 'hung_nq', '$2b$12$.i1uKX1Pxvj11x2Q.INTCeOB2WTGWpjdq6JSp/GxgJgXq/3gXPgP6', NULL, 'Hà Nội'),
('M007', 'Vũ Thị Hằng', '0977889900', 'hang@gmail.com', '2024-03-15', 'ACTIVE', 57.00, 58.50, 'P006', '2024-04-15', 'U002', 'hang_vt', '$2b$12$vuiQQao46VoHuR5P4mcZK.R7TrzmztzFXx87btlIBWrV.LA1PWGN.', NULL, 'Hải Dương'),
('M008', 'Bùi Đức Thắng', '0988990011', 'thang@gmail.com', '2024-03-20', 'EXPIRED', 85.00, 86.00, 'P001', '2024-04-20', 'U004', 'thang_bd', '$2b$12$liitZon6TQpeSVWSj11pmOczTwcd8O17QbWUM0AFoDY91ySs6C1mK', NULL, 'Nghệ An'),
('M009', 'Phạm Lan Anh', '0922334455', 'lanh@gmail.com', '2024-04-01', 'ACTIVE', 48.00, 49.50, 'P003', '2024-07-01', 'U003', 'lanh_pl', '$2b$12$C94lc.9YIrIWVCHYSwJ8LeXTEcaSmxOBx9qCmDKuPGLNGKvjzQkmS', NULL, 'Hà Nội'),
('M010', 'Lý Hoàng Nam', '0933556677', 'hnam@gmail.com', '2024-04-10', 'ACTIVE', 68.00, 70.00, 'P002', '2024-07-10', 'U002', 'hnam_lh', '$2b$12$sQ8dfd2LcVduq1PvDVbfKOgsHcQPedIP3GitJpOW8nsEY7SXWkJuC', NULL, 'TP.HCM'),
('M011', 'Đinh Thị Ngọc', '0944667788', 'ngoc@gmail.com', '2024-04-15', 'ACTIVE', 55.00, 56.00, 'P004', '2025-04-15', 'U003', 'ngoc_dt', '$2b$12$O6TiRxPHMeA.0f65XdRrfuUSBt1iR6eMBz9JIGOblxu6MRpJH6nWG', NULL, 'Huế'),
('M012', 'Cao Văn Tú', '0955778899', 'tu@gmail.com', '2024-05-01', 'ACTIVE', 72.00, 74.00, 'P002', '2024-08-01', 'U004', 'tu_cv', '$2b$12$W0T3WC6M9g0sFRaL/aSZ/O3aOIR5FbZBaTxRtQ/vVRjVnNPzf9nW.', NULL, 'Hà Nội'),
('M013', 'Trịnh Quỳnh Anh', '0966889900', 'qanh@gmail.com', '2024-05-10', 'EXPIRED', 46.00, 47.00, 'P005', '2024-06-10', 'U003', 'qanh_tq', '$2b$12$i7r8xAgaMp48KSRPYVTb7eAuNmnmkaKbw5b/0/FiMNRy1gjjzEGoC', NULL, 'Nam Định'),
('M014', 'Hoàng Minh Tú', '0977990011', 'mtu@gmail.com', '2024-06-01', 'ACTIVE', 78.00, 80.00, 'P003', '2024-12-01', 'U002', 'mtu_hm', '$2b$12$8es.bYLcQno.7GV8BomReeVW2u4HRxO7ARvy9JpESSMSHJ5UoxHbC', NULL, 'Bắc Ninh'),
('M015', 'Phan Thị Thanh', '0988001122', 'thanh@gmail.com', '2024-06-15', 'PENDING', 51.00, 51.00, 'P001', '2024-07-15', 'U003', 'thanh_pt', '$2b$12$p1aQttcUhYVaKsxsFpJ9Ceg9NIpOYpXSWGBo.tlCMdJAsvi6XFS3K', NULL, 'TP.HCM');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `plans`
--

CREATE TABLE `plans` (
  `id` varchar(50) NOT NULL,
  `name` varchar(150) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `durationMonths` int(11) DEFAULT NULL,
  `sessions` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `plans`
--

INSERT INTO `plans` (`id`, `name`, `type`, `price`, `description`, `durationMonths`, `sessions`) VALUES
('P001', 'Gói Cơ Bản (1 tháng)', 'MEMBERSHIP', 500000.00, 'Truy cập phòng tập cơ bản, giờ hành chính', 1, 0),
('P002', 'Gói Standard (3 tháng)', 'MEMBERSHIP', 1200000.00, 'Truy cập toàn bộ thiết bị, 7 ngày/tuần', 3, 0),
('P003', 'Gói VIP (6 tháng)', 'MEMBERSHIP', 2200000.00, 'Toàn bộ thiết bị + 2 buổi PT/tháng', 6, 0),
('P004', 'Gói Pro (1 năm)', 'MEMBERSHIP', 4000000.00, 'Truy cập VIP + PT không giới hạn', 12, 0),
('P005', 'Yoga Cơ Bản (12 buổi)', 'CLASS', 800000.00, 'Lớp yoga 12 buổi với HLV Lan', 1, 12),
('P006', 'PT cá nhân (10 buổi)', 'PT', 3000000.00, '10 buổi tập 1-1 với PT chuyên nghiệp', 1, 10);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `sports`
--

CREATE TABLE `sports` (
  `sport_id` varchar(50) NOT NULL,
  `sport_name` varchar(150) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `status` varchar(20) DEFAULT 'ACTIVE',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `sports`
--

INSERT INTO `sports` (`sport_id`, `sport_name`, `description`, `status`, `created_at`) VALUES
('SP001', 'Bóng đá', 'Môn bóng đá 11 người và bóng đá mini', 'ACTIVE', '2026-05-03 13:51:33'),
('SP002', 'Cầu lông', 'Môn cầu lông đơn và đôi nam nữ', 'ACTIVE', '2026-05-03 13:51:33'),
('SP003', 'Bóng chuyền', 'Môn bóng chuyền trong nhà và ngoài trời', 'ACTIVE', '2026-05-03 13:51:33'),
('SP004', 'Bơi lội', 'Môn bơi lội các kiểu tự do, ếch', 'ACTIVE', '2026-05-03 13:51:33'),
('SP005', 'Yoga', 'Các bài tập yoga, thiền định, pilates', 'ACTIVE', '2026-05-03 13:51:33'),
('SP006', 'Gym', 'Tập thể hình, tạ tự do, máy tập', 'ACTIVE', '2026-05-03 13:51:33'),
('SP007', 'Võ thuật', 'Boxing, karate, taekwondo, judo', 'ACTIVE', '2026-05-03 13:51:33');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `id` varchar(50) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `fullName` varchar(150) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `specialty` varchar(100) DEFAULT NULL,
  `activeStudents` int(11) DEFAULT 0,
  `avatar` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `fullName`, `role`, `specialty`, `activeStudents`, `avatar`) VALUES
('U001', 'admin', '$2b$12$WBZp59dGKcrHtrmyJ8vRrus1xzd5TsOw2meWtd23xVoqYyJkItsrK', 'Quản trị viên', 'ADMIN', 'Hệ thống', 0, NULL),
('U002', 'hlv_son', '$2b$12$wulsDegkhly8fkproG3Y9uiVMuNoZH89zQtOom1iIoOK8yRG/evEy', 'Nguyễn Văn Sơn', 'MANAGER', 'Thể hình', 8, NULL),
('U003', 'hlv_lan', '$2b$12$c0p5Oy2GsTvnCq/7vTUrNu/Nnkv4Ydzmc7RKqjEoRL6hzx6f6lZny', 'Trần Thị Lan', 'PT', 'Yoga & Pilates', 7, NULL),
('U004', 'hlv_duc', '$2b$12$I4DR3rdd9Qo77uLpFHvBb.mYRwpH/PxSAQQgGBZcDgyjRUbemsz.G', 'Phạm Tiến Đức', 'PT', 'Boxing & Cardio', 5, NULL);

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `classenrollments`
--
ALTER TABLE `classenrollments`
  ADD PRIMARY KEY (`classId`,`memberId`),
  ADD KEY `idx_class_enrollments_member` (`memberId`);

--
-- Chỉ mục cho bảng `classes`
--
ALTER TABLE `classes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_classes_trainer` (`trainerId`);

--
-- Chỉ mục cho bảng `eventparticipants`
--
ALTER TABLE `eventparticipants`
  ADD PRIMARY KEY (`id`),
  ADD KEY `eventId` (`eventId`),
  ADD KEY `memberId` (`memberId`);

--
-- Chỉ mục cho bảng `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_events_date` (`date`),
  ADD KEY `idx_events_status` (`status`);

--
-- Chỉ mục cho bảng `facilities`
--
ALTER TABLE `facilities`
  ADD PRIMARY KEY (`facility_id`);

--
-- Chỉ mục cho bảng `invoiceitems`
--
ALTER TABLE `invoiceitems`
  ADD PRIMARY KEY (`id`),
  ADD KEY `invoiceId` (`invoiceId`);

--
-- Chỉ mục cho bảng `invoices`
--
ALTER TABLE `invoices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_invoices_member` (`memberId`),
  ADD KEY `idx_invoices_date` (`date`),
  ADD KEY `idx_invoices_status` (`payment_status`);

--
-- Chỉ mục cho bảng `members`
--
ALTER TABLE `members`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_members_name` (`fullName`),
  ADD KEY `idx_members_phone` (`phone`),
  ADD KEY `idx_members_status` (`status`),
  ADD KEY `idx_members_plan` (`activePlanId`),
  ADD KEY `idx_members_pt` (`assignedPTId`);

--
-- Chỉ mục cho bảng `plans`
--
ALTER TABLE `plans`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `sports`
--
ALTER TABLE `sports`
  ADD PRIMARY KEY (`sport_id`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `idx_users_username` (`username`),
  ADD KEY `idx_users_role` (`role`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `invoiceitems`
--
ALTER TABLE `invoiceitems`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `classenrollments`
--
ALTER TABLE `classenrollments`
  ADD CONSTRAINT `classenrollments_ibfk_1` FOREIGN KEY (`classId`) REFERENCES `classes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `classenrollments_ibfk_2` FOREIGN KEY (`memberId`) REFERENCES `members` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `classes`
--
ALTER TABLE `classes`
  ADD CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`trainerId`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `eventparticipants`
--
ALTER TABLE `eventparticipants`
  ADD CONSTRAINT `eventparticipants_ibfk_1` FOREIGN KEY (`eventId`) REFERENCES `events` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `eventparticipants_ibfk_2` FOREIGN KEY (`memberId`) REFERENCES `members` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `invoiceitems`
--
ALTER TABLE `invoiceitems`
  ADD CONSTRAINT `invoiceitems_ibfk_1` FOREIGN KEY (`invoiceId`) REFERENCES `invoices` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `invoices`
--
ALTER TABLE `invoices`
  ADD CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`memberId`) REFERENCES `members` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `members`
--
ALTER TABLE `members`
  ADD CONSTRAINT `members_ibfk_1` FOREIGN KEY (`activePlanId`) REFERENCES `plans` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `members_ibfk_2` FOREIGN KEY (`assignedPTId`) REFERENCES `users` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
