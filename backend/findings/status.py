from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/findings",
    tags=["Findings"]
)

security = HTTPBearer()


ALLOWED_STATUSES = {
    "open",
    "retesting",
    "remediated"
}


class FindingStatusUpdate(BaseModel):
    status: str


@router.patch("/{finding_id}/status")
async def update_finding_status(
    finding_id: str,
    data: FindingStatusUpdate,
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

    if data.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid finding status."
        )

    # ==========================================
    # GET FINDING
    # ==========================================

    try:
        finding_response = (
            supabase_db
            .table("findings")
            .select("id, engagement_id")
            .eq("id", finding_id)
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    if not finding_response.data:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    engagement_id = finding_response.data["engagement_id"]

    # ==========================================
    # VERIFY OWNERSHIP
    # ==========================================

    try:
        engagement_response = (
            supabase_db
            .table("engagements")
            .select("id")
            .eq("id", engagement_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    if not engagement_response.data:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    # ==========================================
    # UPDATE STATUS
    # ==========================================

    try:
        response = (
            supabase_db
            .table("findings")
            .update({
                "status": data.status
            })
            .eq("id", finding_id)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update finding status: {str(e)}"
        )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    return {
        "message": "Finding status updated successfully.",
        "finding": response.data[0]
    }