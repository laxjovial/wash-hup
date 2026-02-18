from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from app.models.admin.profile import Category


class AdminBaseResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AdminDataResponse(AdminBaseResponse):
    data: Any

class DashboardOverviewData(BaseModel):
    total_users: int
    total_owners: int
    total_washers: int
    total_washes: int
    total_revenue: float
    active_washes: int

class WalletOverviewData(BaseModel):
    total_payments_count: int
    total_payments_amount: float
    total_remittance_amount: float
    platform_earnings: float

class DashboardOverviewResponse(AdminBaseResponse):
    data: DashboardOverviewData

class WalletOverviewResponse(AdminBaseResponse):
    data: WalletOverviewData

class AdminUserResponse(BaseModel):
    id: str
    user_id: str
    is_flagged: bool
    is_restricted: bool
    is_deactivated: bool
    created: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminUsersListResponse(AdminBaseResponse):
    data: List[AdminUserResponse]
