from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()


@router.get("/api-key")
async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # --------------------------------
    # 1. Verify JWT
    # --------------------------------
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

    # --------------------------------
    # 2. Get only the authenticated
    #    user's API key
    # --------------------------------
    try:
        profile_response = (
            supabase_db
            .table("profiles")
            .select("api_key")
            .eq("id", user_id)
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve API key."
        )

    # --------------------------------
    # 3. Verify profile exists
    # --------------------------------
    if not profile_response.data:
        raise HTTPException(
            status_code=404,
            detail="User profile not found."
        )

    api_key = profile_response.data.get("api_key")

    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="API key not found."
        )

    # --------------------------------
    # 4. Return API key
    # --------------------------------
    return {
        "api_key": api_key
    }