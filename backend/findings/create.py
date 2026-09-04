from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Findings"]
)

security = HTTPBearer()


ALLOWED_SEVERITIES = {
    "critical",
    "high",
    "medium",
    "low",
    "informational"
}

ALLOWED_STATUSES = {
    "open",
    "retesting",
    "remediated"
}


class FindingCreate(BaseModel):
    title: str
    severity: str = "informational"
    status: str = "open"
    vulnerability_type: str | None = None
    affected_url: str | None = None
    affected_parameter: str | None = None
    description: str | None = None
    impact: str | None = None
    steps_to_reproduce: str | None = None
    recommendation: str | None = None
    cvss_score: float | None = Field(
        default=None,
        ge=0,
        le=10
    )
    cwe_id: str | None = None


@router.post("/{engagement_id}/findings")
async def create_finding(
    engagement_id: str,
    data: FindingCreate,
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
    # VALIDATE TITLE
    # ==========================================

    title = data.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Finding title cannot be empty."
        )

    # ==========================================
    # VALIDATE SEVERITY
    # ==========================================

    if data.severity not in ALLOWED_SEVERITIES:
        raise HTTPException(
            status_code=400,
            detail="Invalid severity."
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
    # CREATE FINDING
    # ==========================================

    try:
        response = (
            supabase_db
            .table("findings")
            .insert({
                "engagement_id": engagement_id,
                "title": title,
                "severity": data.severity,
                "status": data.status,
                "vulnerability_type": data.vulnerability_type,
                "affected_url": data.affected_url,
                "affected_parameter": data.affected_parameter,
                "description": data.description,
                "impact": data.impact,
                "steps_to_reproduce": data.steps_to_reproduce,
                "recommendation": data.recommendation,
                "cvss_score": data.cvss_score,
                "cwe_id": data.cwe_id
            })
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create finding: {str(e)}"
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Finding could not be created."
        )

    return {
        "message": "Finding created successfully.",
        "finding": response.data[0]
    }