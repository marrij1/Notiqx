from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Discoveries"]
)

security = HTTPBearer()


@router.get("/{engagement_id}/discoveries")
async def list_discoveries(
    engagement_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # ----------------------------------------
    # Authenticate user
    # ----------------------------------------

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

    # ----------------------------------------
    # Verify engagement ownership
    # ----------------------------------------

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

    # ----------------------------------------
    # Get discoveries
    # ----------------------------------------

    try:
        response = (
            supabase_db
            .table("discoveries")
            .select("*")
            .eq("engagement_id", engagement_id)
            .order("created_at", desc=True)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve discoveries."
        )

    return {
        "discoveries": response.data
    }