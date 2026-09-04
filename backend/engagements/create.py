from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Engagements"]
)

security = HTTPBearer()


class EngagementCreate(BaseModel):
    name: str
    client_name: str
    start_date: date | None = None
    end_date: date | None = None
    scope: str | None = None
    status: str = "active"


@router.post("")
async def create_engagement(
    data: EngagementCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # ==========================================
    # VERIFY JWT
    # ==========================================

    try:
        user_response = supabase_auth.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token."
            )

        user_id = user_response.user.id

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    # ==========================================
    # VALIDATE STATUS
    # ==========================================

    if data.status not in ["active", "completed"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be 'active' or 'completed'."
        )

    # ==========================================
    # VALIDATE DATES
    # ==========================================

    if (
        data.start_date is not None
        and data.end_date is not None
        and data.end_date < data.start_date
    ):
        raise HTTPException(
            status_code=400,
            detail="End date cannot be earlier than start date."
        )

    # ==========================================
    # CREATE ENGAGEMENT
    # ==========================================

    try:
        response = (
            supabase_db
            .table("engagements")
            .insert({
                "user_id": user_id,
                "name": data.name,
                "client_name": data.client_name,
                "start_date": (
                    data.start_date.isoformat()
                    if data.start_date
                    else None
                ),
                "end_date": (
                    data.end_date.isoformat()
                    if data.end_date
                    else None
                ),
                "scope": data.scope,
                "status": data.status
            })
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create engagement: {str(e)}"
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Engagement could not be created."
        )

    return {
        "message": "Engagement created successfully.",
        "engagement": response.data[0]
    }