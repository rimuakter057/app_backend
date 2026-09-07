from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    label: str
    count: int


class OwnerDashboardStats(BaseModel):
    properties_by_status: dict[str, int]
    total_views: int
    total_leads: int
    views_over_time: list[TimeSeriesPoint]


class AdminDashboardStats(BaseModel):
    total_users: int
    total_agents: int
    total_properties: int
    active_listings: int
    pending_approvals: int
    sold_count: int
    total_visits: int
    reported_count: int
    new_listings_per_month: list[TimeSeriesPoint]
    signups_by_role: dict[str, int]
