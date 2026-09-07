from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.lead import lead as lead_crud
from app.crud.property import property_ as property_crud
from app.crud.report import report as report_crud
from app.crud.visit import visit as visit_crud
from app.models.enums import PropertyStatus, UserRole
from app.models.property import Property
from app.models.user import User
from app.models.visit import Visit
from app.schemas.stats import AdminDashboardStats, OwnerDashboardStats, TimeSeriesPoint


def owner_dashboard_stats(db: Session, owner_id: int) -> OwnerDashboardStats:
    properties_by_status = property_crud.properties_by_status_count(db, owner_id)
    total_views = property_crud.total_views_for_owner(db, owner_id)
    total_leads = lead_crud.distinct_leads_count_for_owner(db, owner_id)
    views_over_time = [
        TimeSeriesPoint(label=label, count=count)
        for label, count in visit_crud.visits_per_month(db, owner_id)
    ]
    return OwnerDashboardStats(
        properties_by_status=properties_by_status,
        total_views=total_views,
        total_leads=total_leads,
        views_over_time=views_over_time,
    )


def admin_dashboard_stats(db: Session) -> AdminDashboardStats:
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    total_agents = db.scalar(select(func.count()).select_from(User).where(User.role == UserRole.owner)) or 0
    total_properties = db.scalar(select(func.count()).select_from(Property)) or 0
    status_counts = property_crud.counts_by_status_global(db)
    active_listings = status_counts.get(PropertyStatus.active.value, 0)
    pending_approvals = status_counts.get(PropertyStatus.pending.value, 0)
    sold_count = status_counts.get(PropertyStatus.sold.value, 0)
    total_visits = db.scalar(select(func.count()).select_from(Visit)) or 0
    reported_count = report_crud.count_pending(db)

    new_listings_per_month = [
        TimeSeriesPoint(label=label, count=count) for label, count in property_crud.new_listings_per_month(db)
    ]

    signup_rows = db.execute(select(User.role, func.count()).group_by(User.role)).all()
    signups_by_role = {role.value: count for role, count in signup_rows}

    return AdminDashboardStats(
        total_users=total_users,
        total_agents=total_agents,
        total_properties=total_properties,
        active_listings=active_listings,
        pending_approvals=pending_approvals,
        sold_count=sold_count,
        total_visits=total_visits,
        reported_count=reported_count,
        new_listings_per_month=new_listings_per_month,
        signups_by_role=signups_by_role,
    )
