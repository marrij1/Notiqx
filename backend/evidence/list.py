from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/findings",
    tags=["Evidence"]
)

security = HTTPBearer()


@router.get("/{finding_id}/evidence")
async def list_evidence(
    finding_id: str,
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
    # GET EVIDENCE
    # ==========================================

    try:
        evidence_response = (
            supabase_db
            .table("evidence")
            .select("*")
            .eq("finding_id", finding_id)
            .order("created_at", desc=True)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evidence: {str(e)}"
        )

    return {
        "evidence": evidence_response.data or []
    }