from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Engagements"]
)

security = HTTPBearer()


@router.get("")
async def list_engagements(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # Verify JWT
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

    # Get only this user's engagements
    try:
        response = (
            supabase_db
            .table("engagements")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve engagements: {str(e)}"
        )

    return {
        "engagements": response.data
    }