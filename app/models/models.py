from dataclasses import dataclass
from typing import Optional, List

@dataclass
class HoiVien:
    id: str
    fullName: str
    phone: str
    email: Optional[str] = None
    joinDate: Optional[str] = None
    weight: float = 0.0
    previousWeight: float = 0.0
    activePlanId: Optional[str] = None
    expiryDate: Optional[str] = None
    assignedPTId: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None
    homeTown: Optional[str] = None
    birthDate: Optional[str] = None
    gender: str = 'Nam'
    status: str = 'PENDING'

@dataclass
class NguoiDung:
    id: str
    fullName: str
    username: str
    password: Optional[str] = None
    role: str = 'PT'
    specialty: Optional[str] = None
    activeStudents: int = 0
    avatar: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

@dataclass
class MonTheThao:
    sport_id: str
    sport_name: str
    description: Optional[str] = None

@dataclass
class BuoiHoc:
    id: str
    name: str
    trainerId: str
    sportId: str
    facilityId: str
    time: str
    dayOfWeek: str
    capacity: int = 20
    price: float = 0.0
    status: str = 'ACTIVE'
    startDate: Optional[str] = None
    endDate: Optional[str] = None

@dataclass
class CoSoVatChat:
    facility_id: str
    facility_name: str
    location: Optional[str] = None
    sport_id: Optional[str] = None
    sport_name: Optional[str] = None

@dataclass
class SuKien:
    id: str
    ten: str
    mo_ta: Optional[str] = None
    ngay: Optional[str] = None
    dia_diem: Optional[str] = None
    gio: Optional[str] = None
    gio_ket_thuc: Optional[str] = None
    facility_id: Optional[str] = None
    ten_san: Optional[str] = None
    suc_chua: int = 50
    gia: float = 0.0
    trang_thai: str = 'UPCOMING'

@dataclass
class GoiTap:
    id: str
    name: str
    type: str
    price: float
    description: Optional[str] = None
    durationMonths: int = 1
    sessions: int = 0

@dataclass
class HoaDon:
    id: str
    memberId: str
    sourceType: str # PLAN, CLASS, EVENT, MANUAL
    sourceId: Optional[str] = None
    totalAmount: float = 0.0
    discountAmount: float = 0.0
    finalAmount: float = 0.0
    paidAmount: float = 0.0
    remainingAmount: float = 0.0
    date: Optional[str] = None
    paymentMethod: str = 'CASH'
    paymentStatus: str = 'UNPAID' # PAID, UNPAID, PARTIAL, CANCELLED
    note: Optional[str] = None

@dataclass
class TheHoiVien:
    id: str
    memberId: str
    planId: Optional[str] = None
    cardNumber: str = ""
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    status: str = 'INACTIVE' # ACTIVE, INACTIVE, EXPIRED, REVOKED
    note: Optional[str] = None

@dataclass
class LichSuCheckIn:
    id: str
    memberId: str
    checkInTime: str
    checkOutTime: Optional[str] = None
    status: str = 'VALID'
    note: Optional[str] = None

@dataclass
class DangKyLop:
    id: str
    classId: str
    memberId: str
    enrollDate: str
    status: str = 'ACTIVE'

@dataclass
class DangKySuKien:
    id: str
    eventId: str
    memberId: str
    registerDate: str
    status: str = 'ACTIVE'

@dataclass
class ChamCongHLV:
    id: str
    trainerId: str
    date: str
    status: str = 'PRESENT'
    note: Optional[str] = None

@dataclass
class LuongHLV:
    id: str
    trainerId: str
    month: int
    year: int
    baseSalary: float = 0.0
    bonus: float = 0.0
    totalSalary: float = 0.0
    status: str = 'UNPAID'

@dataclass
class DiemDanhLop:
    id: int
    classId: str
    memberId: str
    date: str
    status: str = 'PRESENT'
    note: Optional[str] = None
