from dataclasses import dataclass, field
from typing import Optional, List, Literal

Role = Literal["ADMIN", "MANAGER", "RECEPTIONIST", "PT", "MEMBER"]
MemberStatus = Literal["ACTIVE", "EXPIRED", "PENDING"]
PlanType = Literal["MONTHLY", "SESSION", "PT"]
ProductCategory = Literal["EQUIPMENT", "SUPPLEMENT", "DRINK"]
InvoiceMethod = Literal["CASH", "TRANSFER", "E-WALLET"]
AttendanceType = Literal["GYM", "CLASS", "PT"]


@dataclass
class User:
    id: str
    username: str
    fullName: str
    role: Role
    password: Optional[str] = None
    avatar: Optional[str] = None
    specialty: Optional[str] = None
    activeStudents: int = 0
    phone: Optional[str] = None
    address: Optional[str] = None
    idCard: Optional[str] = None


@dataclass
class Member:
    id: str
    fullName: str
    phone: str
    email: str
    joinDate: str
    status: MemberStatus = "ACTIVE"
    activePlanId: Optional[str] = None
    activePlanName: Optional[str] = None
    expiryDate: Optional[str] = None
    remainingSessions: Optional[int] = None
    assignedPTId: Optional[str] = None
    assignedPTName: Optional[str] = None
    weight: float = 0.0
    previousWeight: float = 0.0
    avatar: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    homeTown: Optional[str] = None


@dataclass
class Plan:
    id: str
    name: str
    type: PlanType
    price: float
    description: str
    durationMonths: Optional[int] = None
    sessions: Optional[int] = None


@dataclass
class ClassSession:
    id: str
    name: str
    trainerId: str
    time: str
    dayOfWeek: str
    capacity: int
    enrolledMemberIds: List[str] = field(default_factory=list)


@dataclass
class Product:
    id: str
    name: str
    category: ProductCategory
    price: float
    stock: int
    minStockAlert: int


@dataclass
class InvoiceItem:
    name: str
    quantity: int
    price: float


@dataclass
class Invoice:
    id: str
    memberId: str
    items: List[InvoiceItem]
    total: float
    date: str
    method: InvoiceMethod


@dataclass
class Event:
    id: str
    name: str
    description: str
    date: str
    time: str
    location: str
    capacity: int
    status: str = "UPCOMING"


@dataclass
class EventParticipant:
    id: str
    eventId: str
    memberId: str
    memberName: str
    registerDate: str
    status: str = "PENDING"


@dataclass
class RenewalRequest:
    id: str
    memberId: str
    planId: str
    requestDate: str
    status: str = "PENDING"
