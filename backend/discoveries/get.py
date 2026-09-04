from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/discoveries",
    tags=["Discoveries"]
)

security = HTTPBearer()


@router.get("/{discovery_id}")
async def get_discovery(
    discovery_id: str,
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
    # Find discovery + verify ownership
    # ----------------------------------------

    try:
        discovery_response = (
            supabase_db
            .table("discoveries")
            .select(
                "*, engagements!inner(id, user_id)"
            )
            .eq("id", discovery_id)
            .eq("engagements.user_id", user_id)
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Discovery not found."
        )

    if not discovery_response.data:
        raise HTTPException(
            status_code=404,
            detail="Discovery not found."
        )

    discovery = discovery_response.data

    # We don't need to expose the internal joined ownership data.
    discovery.pop("engagements", None)

    return {
        "discovery": discovery
    }