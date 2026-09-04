from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/findings",
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


class FindingUpdate(BaseModel):
    title: str | None = None
    severity: str | None = None
    status: str | None = None
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


@router.put("/{finding_id}")
async def update_finding(
    finding_id: str,
    data: FindingUpdate,
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
    # ONLY USE FIELDS ACTUALLY PROVIDED
    # ==========================================

    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update."
        )

    # ==========================================
    # VALIDATE TITLE
    # ==========================================

    if "title" in update_data:

        if update_data["title"] is None:
            raise HTTPException(
                status_code=400,
                detail="Finding title cannot be null."
            )

        title = update_data["title"].strip()

        if not title:
            raise HTTPException(
                status_code=400,
                detail="Finding title cannot be empty."
            )

        update_data["title"] = title

    # ==========================================
    # VALIDATE SEVERITY
    # ==========================================

    if "severity" in update_data:

        if (
            update_data["severity"] is not None
            and update_data["severity"] not in ALLOWED_SEVERITIES
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid severity."
            )

    # ==========================================
    # VALIDATE STATUS
    # ==========================================

    if "status" in update_data:

        if (
            update_data["status"] is not None
            and update_data["status"] not in ALLOWED_STATUSES
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid finding status."
            )

    # ==========================================
    # CVSS VALIDATION
    # ==========================================

    if "cvss_score" in update_data:

        cvss_score = update_data["cvss_score"]

        if cvss_score is not None:
            if cvss_score < 0 or cvss_score > 10:
                raise HTTPException(
                    status_code=400,
                    detail="CVSS score must be between 0 and 10."
                )

    # ==========================================
    # UPDATE FINDING
    # ==========================================

    try:
        response = (
            supabase_db
            .table("findings")
            .update(update_data)
            .eq("id", finding_id)
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update finding: {str(e)}"
        )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    return {
        "message": "Finding updated successfully.",
        "finding": response.data[0]
    }