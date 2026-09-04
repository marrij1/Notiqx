from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/discoveries",
    tags=["Discoveries"]
)

security = HTTPBearer()


@router.post("/{discovery_id}/approve")
async def approve_discovery(
    discovery_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # =========================================================
    # 1. AUTHENTICATE USER
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
            "DISCOVERY APPROVAL AUTH ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    # =========================================================
    # 2. GET DISCOVERY + VERIFY OWNERSHIP
    # =========================================================

    try:
        discovery_response = (
            supabase_db
            .table("discoveries")
            .select(
                """
                *,
                engagements!inner(
                    id,
                    user_id
                )
                """
            )
            .eq("id", discovery_id)
            .eq("engagements.user_id", user_id)
            .single()
            .execute()
        )

    except Exception as e:
        print(
            "DISCOVERY APPROVAL LOOKUP ERROR:",
            repr(e)
        )

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

    engagement = discovery.get("engagements")

    if not engagement:
        raise HTTPException(
            status_code=404,
            detail="Discovery not found."
        )

    engagement_id = engagement.get("id")

    if not engagement_id:
        raise HTTPException(
            status_code=404,
            detail="Discovery not found."
        )

    # =========================================================
    # 3. CHECK DISCOVERY STATUS
    # =========================================================

    analysis_status = discovery.get(
        "analysis_status"
    )

    if analysis_status == "approved":
        raise HTTPException(
            status_code=400,
            detail="Discovery has already been approved."
        )

    if analysis_status == "rejected":
        raise HTTPException(
            status_code=400,
            detail="Discovery has been rejected and cannot be approved."
        )

    if analysis_status != "analyzed":
        raise HTTPException(
            status_code=400,
            detail="Discovery must be analyzed before approval."
        )

    # =========================================================
    # 4. READ GENERATED ANALYSIS
    # =========================================================

    title = discovery.get(
        "generated_title"
    )

    severity = discovery.get(
        "generated_severity"
    )

    cwe_id = discovery.get(
        "generated_cwe"
    )

    cvss_score = discovery.get(
        "generated_cvss"
    )

    description = discovery.get(
        "generated_description"
    )

    impact = discovery.get(
        "generated_impact"
    )

    reproduction = discovery.get(
        "generated_reproduction"
    )

    recommendation = discovery.get(
        "generated_recommendation"
    )

    # =========================================================
    # 5. VALIDATE ANALYSIS
    # =========================================================

    if not title or not title.strip():
        raise HTTPException(
            status_code=400,
            detail="Generated finding title is missing."
        )

    allowed_severities = {
        "critical",
        "high",
        "medium",
        "low",
        "informational"
    }

    if severity not in allowed_severities:
        raise HTTPException(
            status_code=400,
            detail="Generated finding severity is invalid."
        )

    if cvss_score is not None:

        try:
            cvss_score = float(
                cvss_score
            )

        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="Generated CVSS score is invalid."
            )

        if cvss_score < 0 or cvss_score > 10:
            raise HTTPException(
                status_code=400,
                detail="Generated CVSS score must be between 0 and 10."
            )

    # =========================================================
    # 6. CREATE FINDING
    # =========================================================

    finding_data = {
        "engagement_id": engagement_id,

        "title": title.strip(),

        "severity": severity,

        "status": "open",

        "vulnerability_type":
            discovery.get(
                "discovery_type"
            ),

        "affected_url":
            discovery.get(
                "target_url"
            ),

        "affected_parameter":
            discovery.get(
                "parameter"
            ),

        "description":
            description,

        "impact":
            impact,

        "steps_to_reproduce":
            reproduction,

        "recommendation":
            recommendation,

        "cvss_score":
            cvss_score,

        "cwe_id":
            cwe_id
    }

    try:
        finding_response = (
            supabase_db
            .table("findings")
            .insert(finding_data)
            .execute()
        )

    except Exception as e:
        print(
            "DISCOVERY APPROVAL FINDING INSERT ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create finding."
        )

    if not finding_response.data:
        raise HTTPException(
            status_code=500,
            detail="Finding could not be created."
        )

    created_finding = (
        finding_response.data[0]
    )

    finding_id = created_finding.get(
        "id"
    )

    if not finding_id:
        raise HTTPException(
            status_code=500,
            detail="Finding could not be created."
        )

    # =========================================================
    # 7. CREATE PROPERLY CLASSIFIED EVIDENCE
    # =========================================================

    raw_input = discovery.get(
        "raw_input"
    )

    evidence_type = discovery.get(
        "evidence_type"
    ) or "note"

    allowed_evidence_types = {
        "http_request",
        "tool_output",
        "note",
        "curl_command",
        "code_snippet"
    }

    if evidence_type not in allowed_evidence_types:
        evidence_type = "note"

    evidence_created = None

    if raw_input and raw_input.strip():

        evidence_titles = {
            "http_request":
                "HTTP Request",

            "tool_output":
                "Tool Output",

            "note":
                "Pentester Note",

            "curl_command":
                "cURL Command",

            "code_snippet":
                "Code Snippet"
        }

        evidence_data = {
            "finding_id":
                finding_id,

            "evidence_type":
                evidence_type,

            "title":
                evidence_titles.get(
                    evidence_type,
                    "Discovery Evidence"
                ),

            "content":
                raw_input.strip(),

            "file_url":
                None
        }

        try:

            evidence_response = (
                supabase_db
                .table("evidence")
                .insert(evidence_data)
                .execute()
            )

        except Exception as e:

            print(
                "DISCOVERY APPROVAL EVIDENCE INSERT ERROR:",
                repr(e)
            )

            # Roll back finding.
            try:
                (
                    supabase_db
                    .table("findings")
                    .delete()
                    .eq(
                        "id",
                        finding_id
                    )
                    .eq(
                        "engagement_id",
                        engagement_id
                    )
                    .execute()
                )

            except Exception as rollback_error:

                print(
                    "DISCOVERY APPROVAL FINDING ROLLBACK ERROR:",
                    repr(rollback_error)
                )

            raise HTTPException(
                status_code=500,
                detail="Failed to attach discovery evidence."
            )

        if not evidence_response.data:

            raise HTTPException(
                status_code=500,
                detail="Failed to attach discovery evidence."
            )

        evidence_created = (
            evidence_response.data[0]
        )

    # =========================================================
    # 8. MARK DISCOVERY APPROVED
    # =========================================================

    try:

        update_response = (
            supabase_db
            .table("discoveries")
            .update({
                "analysis_status": "approved"
            })
            .eq(
                "id",
                discovery_id
            )
            .execute()
        )

    except Exception as e:

        print(
            "DISCOVERY APPROVAL STATUS UPDATE ERROR:",
            repr(e)
        )

        # Remove evidence.
        if evidence_created:

            try:
                (
                    supabase_db
                    .table("evidence")
                    .delete()
                    .eq(
                        "id",
                        evidence_created.get("id")
                    )
                    .eq(
                        "finding_id",
                        finding_id
                    )
                    .execute()
                )

            except Exception as rollback_error:

                print(
                    "DISCOVERY APPROVAL EVIDENCE ROLLBACK ERROR:",
                    repr(rollback_error)
                )

        # Remove finding.
        try:
            (
                supabase_db
                .table("findings")
                .delete()
                .eq(
                    "id",
                    finding_id
                )
                .eq(
                    "engagement_id",
                    engagement_id
                )
                .execute()
            )

        except Exception as rollback_error:

            print(
                "DISCOVERY APPROVAL FINDING ROLLBACK ERROR:",
                repr(rollback_error)
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to approve discovery."
        )

    if not update_response.data:

        raise HTTPException(
            status_code=500,
            detail="Failed to approve discovery."
        )

    updated_discovery = (
        update_response.data[0]
    )

    # =========================================================
    # 9. RETURN RESULT
    # =========================================================

    return {
        "message":
            "Discovery approved, finding created, and evidence attached successfully.",

        "discovery":
            updated_discovery,

        "finding":
            created_finding,

        "evidence":
            evidence_created
    }