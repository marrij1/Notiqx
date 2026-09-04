from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/findings",
    tags=["Evidence"]
)

security = HTTPBearer()


ALLOWED_EVIDENCE_TYPES = {
    "http_request",
    "screenshot",
    "note",
    "curl_command",
    "code_snippet",
    "tool_output"
}

MAX_TEXT_CONTENT_LENGTH = 1_000_000
MAX_TITLE_LENGTH = 255


class EvidenceCreate(BaseModel):
    evidence_type: str
    title: str | None = Field(default=None, max_length=MAX_TITLE_LENGTH)
    content: str | None = None


@router.post("/{finding_id}/evidence")
async def create_evidence(
    finding_id: str,
    data: EvidenceCreate,
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
    # VALIDATE EVIDENCE TYPE
    # ==========================================

    if data.evidence_type not in ALLOWED_EVIDENCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid evidence type."
        )

    # ==========================================
    # VALIDATE TITLE
    # ==========================================

    title = None

    if data.title is not None:
        title = data.title.strip()

        if not title:
            raise HTTPException(
                status_code=400,
                detail="Evidence title cannot be empty."
            )

    # ==========================================
    # VALIDATE CONTENT
    # ==========================================

    if data.evidence_type == "screenshot":
        if data.content is not None:
            raise HTTPException(
                status_code=400,
                detail="Screenshot evidence must use the screenshot upload endpoint."
            )

    else:
        if data.content is None:
            raise HTTPException(
                status_code=400,
                detail="Content is required for text-based evidence."
            )

        content = data.content.strip()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Evidence content cannot be empty."
            )

        if len(content) > MAX_TEXT_CONTENT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail="Evidence content is too large."
            )

        data.content = content

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
    # CREATE EVIDENCE
    # ==========================================

    try:
        response = (
            supabase_db
            .table("evidence")
            .insert({
                "finding_id": finding_id,
                "evidence_type": data.evidence_type,
                "title": title,
                "content": (
                    data.content
                    if data.evidence_type != "screenshot"
                    else None
                ),
                "file_url": None
            })
            .execute()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create evidence: {str(e)}"
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Evidence could not be created."
        )

    return {
        "message": "Evidence added successfully.",
        "evidence": response.data[0]
    }