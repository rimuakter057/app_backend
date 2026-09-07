import enum


class UserRole(str, enum.Enum):
    buyer = "buyer"
    owner = "owner"
    admin = "admin"


class VerificationStatus(str, enum.Enum):
    unverified = "unverified"
    pending = "pending"
    verified = "verified"


class PropertyKind(str, enum.Enum):
    sale = "sale"
    rent = "rent"


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    house = "house"
    villa = "villa"
    land = "land"
    office = "office"
    shop = "shop"
    commercial = "commercial"


class PropertyStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    active = "active"
    rejected = "rejected"
    sold = "sold"


class VisitStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    negotiating = "negotiating"
    closed = "closed"
    lost = "lost"


class NotificationKind(str, enum.Enum):
    message = "message"
    visit = "visit"
    favorite = "favorite"
    price = "price"
    system = "system"
    lead = "lead"
    approval = "approval"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    resolved = "resolved"
    dismissed = "dismissed"


class SortOption(str, enum.Enum):
    price_asc = "price_asc"
    price_desc = "price_desc"
    newest = "newest"
