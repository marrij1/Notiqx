from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)

security = HTTPBearer()


@router.delete("/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
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
    # GET EVIDENCE
    # ==========================================

    try:
        evidence_response = (
            supabase_db
            .table("evidence")
            .select(
                "id, finding_id, evidence_type, file_url"
            )
            .eq("id", evidence_id)
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    if not evidence_response.data:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    evidence = evidence_response.data

    # ==========================================
    # GET FINDING
    # ==========================================

    try:
        finding_response = (
            supabase_db
            .table("findings")
            .select("id, engagement_id")
            .eq("id", evidence["finding_id"])
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    if not finding_response.data:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
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
            detail="Evidence not found."
        )

    if not engagement_response.data:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    # ==========================================
    # DELETE STORAGE FILE
    # ==========================================

    if (
        evidence["evidence_type"] == "screenshot"
        and evidence["file_url"]
    ):
        try:
            supabase_db.storage.from_(
                "evidence"
            ).remove(
                [evidence["file_url"]]
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to delete screenshot file: {str(e)}"
                )
            )

    # ==========================================
    # DELETE DATABASE RECORD
    # ==========================================

    try:
        response = (
            supabase_db
            .table("evidence")
            .delete()
            .eq("id", evidence_id)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete evidence: {str(e)}"
        )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    return {
        "message": "Evidence deleted successfully."
    }