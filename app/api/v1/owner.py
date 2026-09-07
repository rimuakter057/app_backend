from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.schemas.stats import OwnerDashboardStats
from app.services.stats_service import owner_dashboard_stats

router = APIRouter(prefix="/owner", tags=["owner"])


@router.get("/dashboard", response_model=OwnerDashboardStats)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(require_role("owner", "admin"))):
    return owner_dashboard_stats(db, current_user.id)
