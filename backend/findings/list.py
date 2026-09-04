from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Findings"]
)

security = HTTPBearer()


@router.get("/{engagement_id}/findings")
async def list_findings(
    engagement_id: str,
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
    # VERIFY ENGAGEMENT OWNERSHIP
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
            detail="Engagement not found."
        )

    if not engagement_response.data:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found."
        )

    # ==========================================
    # GET FINDINGS
    # ==========================================

    try:
        response = (
            supabase_db
            .table("findings")
            .select("*")
            .eq("engagement_id", engagement_id)
            .order("created_at", desc=True)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve findings: {str(e)}"
        )

    return {
        "findings": response.data or []
    }