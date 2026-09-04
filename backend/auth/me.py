from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()


@router.get("/me")
async def get_current_user(
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

        user = user_response.user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    # --------------------------------
    # 2. Get authenticated user's
    #    profile only
    # --------------------------------
    try:
        profile_response = (
            supabase_db
            .table("profiles")
            .select("id, full_name")
            .eq("id", user.id)
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user profile."
        )

    # --------------------------------
    # 3. Verify profile exists
    # --------------------------------
    if not profile_response.data:
        raise HTTPException(
            status_code=404,
            detail="User profile not found."
        )

    profile = profile_response.data

    # --------------------------------
    # 4. Return user information
    # --------------------------------
    return {
        "id": user.id,
        "email": user.email,
        "full_name": profile.get("full_name")
    }