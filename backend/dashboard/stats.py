from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

security = HTTPBearer()


@router.get("/stats")
async def get_dashboard_stats(
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
    # GET USER'S ENGAGEMENTS
    # ==========================================

    try:
        engagement_response = (
            supabase_db
            .table("engagements")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve engagements: {str(e)}"
        )

    engagements = engagement_response.data or []

    engagement_count = len(engagements)


    # ==========================================
    # NO ENGAGEMENTS
    # ==========================================

    if not engagements:
        return {
            "engagements": 0,
            "findings": 0,
            "evidence": 0
        }


    engagement_ids = [
        engagement["id"]
        for engagement in engagements
    ]


    # ==========================================
    # GET FINDINGS BELONGING TO USER'S
    # ENGAGEMENTS
    # ==========================================

    try:
        findings_response = (
            supabase_db
            .table("findings")
            .select("id")
            .in_("engagement_id", engagement_ids)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve findings: {str(e)}"
        )

    findings = findings_response.data or []

    finding_count = len(findings)


    # ==========================================
    # NO FINDINGS
    # ==========================================

    if not findings:
        return {
            "engagements": engagement_count,
            "findings": 0,
            "evidence": 0
        }


    finding_ids = [
        finding["id"]
        for finding in findings
    ]


    # ==========================================
    # GET EVIDENCE BELONGING TO USER'S FINDINGS
    # ==========================================

    try:
        evidence_response = (
            supabase_db
            .table("evidence")
            .select("id")
            .in_("finding_id", finding_ids)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evidence: {str(e)}"
        )

    evidence = evidence_response.data or []

    evidence_count = len(evidence)


    # ==========================================
    # RETURN DASHBOARD STATS
    # ==========================================

    return {
        "engagements": engagement_count,
        "findings": finding_count,
        "evidence": evidence_count
    }