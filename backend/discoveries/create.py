from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Discoveries"]
)

security = HTTPBearer()


class DiscoveryCreate(BaseModel):
    source: str = "manual"

    discovery_type: str = Field(
        min_length=1,
        max_length=100
    )

    target_url: str | None = Field(
        default=None,
        max_length=2048
    )

    parameter: str | None = Field(
        default=None,
        max_length=500
    )

    evidence_type: str = "note"

    raw_input: str = Field(
        min_length=1,
        max_length=1_000_000
    )


@router.post("/{engagement_id}/discoveries")
async def create_discovery(
    engagement_id: str,
    data: DiscoveryCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # =========================================================
    # AUTHENTICATE USER
    # =========================================================

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

    except Exception as e:
        print(
            "DISCOVERY AUTH ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    # =========================================================
    # VALIDATE SOURCE
    # =========================================================

    allowed_sources = {
        "manual",
        "burp",
        "nmap",
        "nuclei",
        "other"
    }

    source = data.source.strip().lower()

    if source not in allowed_sources:
        raise HTTPException(
            status_code=400,
            detail="Invalid discovery source."
        )

    # =========================================================
    # VALIDATE DISCOVERY TYPE
    # =========================================================

    discovery_type = data.discovery_type.strip()

    if not discovery_type:
        raise HTTPException(
            status_code=400,
            detail="Discovery type cannot be empty."
        )

    # =========================================================
    # VALIDATE EVIDENCE TYPE
    # =========================================================

    allowed_evidence_types = {
        "http_request",
        "tool_output",
        "note",
        "curl_command",
        "code_snippet"
    }

    evidence_type = (
        data.evidence_type
        .strip()
        .lower()
    )

    if evidence_type not in allowed_evidence_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid evidence type."
        )

    # =========================================================
    # VALIDATE RAW INPUT
    # =========================================================

    raw_input = data.raw_input.strip()

    if not raw_input:
        raise HTTPException(
            status_code=400,
            detail="Raw input cannot be empty."
        )

    # =========================================================
    # CLEAN OPTIONAL FIELDS
    # =========================================================

    target_url = (
        data.target_url.strip()
        if data.target_url
        else None
    )

    parameter = (
        data.parameter.strip()
        if data.parameter
        else None
    )

    if target_url == "":
        target_url = None

    if parameter == "":
        parameter = None

    # =========================================================
    # VERIFY ENGAGEMENT OWNERSHIP
    # =========================================================

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

    except Exception as e:
        print(
            "DISCOVERY ENGAGEMENT LOOKUP ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=404,
            detail="Engagement not found."
        )

    if not engagement_response.data:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found."
        )

    # =========================================================
    # CREATE DISCOVERY
    # =========================================================

    insert_data = {
        "engagement_id": engagement_id,
        "source": source,
        "discovery_type": discovery_type,
        "target_url": target_url,
        "parameter": parameter,
        "evidence_type": evidence_type,
        "raw_input": raw_input,
        "analysis_status": "pending"
    }

    try:
        response = (
            supabase_db
            .table("discoveries")
            .insert(insert_data)
            .execute()
        )

    except Exception as e:
        print(
            "DISCOVERY INSERT ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create discovery."
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Discovery could not be created."
        )

    return {
        "message": "Discovery created successfully.",
        "discovery": response.data[0]
    }