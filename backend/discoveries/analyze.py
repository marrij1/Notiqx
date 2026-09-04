from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/discoveries",
    tags=["Discovery Analysis"]
)

security = HTTPBearer()


def analyze_discovery(discovery: dict) -> dict:
    """
    Temporary deterministic analysis engine.

    This is intentionally NOT presented as AI.
    It will later be replaced/enhanced by the real
    Notiqx AI analysis layer.
    """

    discovery_type = (
        discovery.get("discovery_type") or ""
    ).lower()

    raw_input = (
        discovery.get("raw_input") or ""
    ).lower()

    combined = f"{discovery_type} {raw_input}"

    # ----------------------------------------
    # SQL Injection
    # ----------------------------------------

    if any(keyword in combined for keyword in [
        "sql injection",
        "sqli",
        "union select",
        "' or 1=1",
        "\" or 1=1",
        "mysql error",
        "sql syntax"
    ]):
        return {
            "title": "SQL Injection",
            "severity": "high",
            "cwe": "CWE-89",
            "cvss": 8.8,
            "description": (
                "The application appears to process user-controlled "
                "input in a way that may allow SQL injection."
            ),
            "impact": (
                "An attacker may be able to manipulate database queries, "
                "access unauthorized data, modify database contents, "
                "or potentially affect application functionality."
            ),
            "reproduction": (
                "Review the supplied request and parameter. "
                "Test the affected parameter with controlled SQL "
                "injection payloads and compare the application's response."
            ),
            "recommendation": (
                "Use parameterized queries or prepared statements. "
                "Avoid constructing SQL queries through direct string "
                "concatenation with user-controlled input."
            )
        }

    # ----------------------------------------
    # Cross-Site Scripting
    # ----------------------------------------

    if any(keyword in combined for keyword in [
        "cross site scripting",
        "cross-site scripting",
        "xss",
        "<script>",
        "javascript:"
    ]):
        return {
            "title": "Cross-Site Scripting (XSS)",
            "severity": "medium",
            "cwe": "CWE-79",
            "cvss": 6.1,
            "description": (
                "User-controlled input appears to be reflected or "
                "processed in a context where script execution may be possible."
            ),
            "impact": (
                "Successful exploitation may allow an attacker to execute "
                "malicious JavaScript in another user's browser."
            ),
            "reproduction": (
                "Submit a controlled XSS payload through the affected "
                "input and verify whether it is executed or reflected "
                "without appropriate output encoding."
            ),
            "recommendation": (
                "Apply context-appropriate output encoding and input "
                "validation. Implement a suitable Content Security Policy "
                "where appropriate."
            )
        }

    # ----------------------------------------
    # IDOR / Broken Access Control
    # ----------------------------------------

    if any(keyword in combined for keyword in [
        "idor",
        "insecure direct object reference",
        "broken access control",
        "authorization bypass",
        "unauthorized access"
    ]):
        return {
            "title": "Broken Access Control",
            "severity": "high",
            "cwe": "CWE-639",
            "cvss": 8.1,
            "description": (
                "The application may allow a user to access an object "
                "or resource without sufficient authorization checks."
            ),
            "impact": (
                "An attacker may be able to access or manipulate resources "
                "belonging to another user or unauthorized role."
            ),
            "reproduction": (
                "Modify the relevant object identifier or authorization "
                "context and verify whether access is granted without "
                "the required permissions."
            ),
            "recommendation": (
                "Perform server-side authorization checks for every "
                "protected object and resource."
            )
        }

    # ----------------------------------------
    # SSRF
    # ----------------------------------------

    if any(keyword in combined for keyword in [
        "ssrf",
        "server side request forgery",
        "server-side request forgery",
        "169.254.169.254"
    ]):
        return {
            "title": "Server-Side Request Forgery (SSRF)",
            "severity": "high",
            "cwe": "CWE-918",
            "cvss": 8.2,
            "description": (
                "The application appears to make server-side requests "
                "using attacker-controlled input."
            ),
            "impact": (
                "An attacker may potentially use the server to access "
                "internal services or otherwise restricted resources."
            ),
            "reproduction": (
                "Supply a controlled internal or otherwise restricted "
                "destination through the affected parameter and observe "
                "whether the server performs the request."
            ),
            "recommendation": (
                "Use strict allowlists for permitted destinations and "
                "protocols. Restrict access to internal and cloud metadata "
                "endpoints."
            )
        }

    # ----------------------------------------
    # Information Disclosure
    # ----------------------------------------

    if any(keyword in combined for keyword in [
        "information disclosure",
        "sensitive information",
        "stack trace",
        "debug information",
        "source code disclosure"
    ]):
        return {
            "title": "Information Disclosure",
            "severity": "low",
            "cwe": "CWE-200",
            "cvss": 5.3,
            "description": (
                "The application appears to expose information that "
                "may not be intended for unauthorized users."
            ),
            "impact": (
                "Exposed information may assist attackers in understanding "
                "the application or planning further attacks."
            ),
            "reproduction": (
                "Review the supplied request and response and verify "
                "whether sensitive or internal information is disclosed."
            ),
            "recommendation": (
                "Remove unnecessary sensitive information from responses "
                "and disable detailed debugging information in production."
            )
        }

    # ----------------------------------------
    # Security Headers
    # ----------------------------------------

    if any(keyword in combined for keyword in [
        "security headers",
        "missing security headers",
        "missing header",
        "content-security-policy",
        "x-frame-options"
    ]):
        return {
            "title": "Missing Security Headers",
            "severity": "low",
            "cwe": "CWE-693",
            "cvss": 4.3,
            "description": (
                "One or more recommended HTTP security headers "
                "appear to be missing or improperly configured."
            ),
            "impact": (
                "Missing security headers may reduce browser-side "
                "security protections and increase exposure to certain "
                "web-based attacks."
            ),
            "reproduction": (
                "Inspect the HTTP response headers and verify which "
                "recommended security headers are absent or misconfigured."
            ),
            "recommendation": (
                "Configure appropriate HTTP security headers according "
                "to the application's requirements and security model."
            )
        }

    # ----------------------------------------
    # Unknown / insufficient evidence
    # ----------------------------------------

    return {
        "title": "Potential Security Issue",
        "severity": "informational",
        "cwe": None,
        "cvss": None,
        "description": (
            "The supplied discovery contains information that may "
            "require further investigation."
        ),
        "impact": (
            "The security impact could not be reliably determined "
            "from the supplied discovery alone."
        ),
        "reproduction": (
            "Review the supplied discovery and perform additional "
            "validation before treating it as a confirmed vulnerability."
        ),
        "recommendation": (
            "Collect additional evidence and manually validate the "
            "security impact."
        )
    }


@router.post("/{discovery_id}/analyze")
async def analyze_discovery_endpoint(
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
    # Retrieve discovery with ownership
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

    # ----------------------------------------
    # Analyze
    # ----------------------------------------

    analysis = analyze_discovery(discovery)

    # ----------------------------------------
    # Save analysis
    # ----------------------------------------

    update_data = {
        "analysis_status": "analyzed",
        "generated_title": analysis["title"],
        "generated_severity": analysis["severity"],
        "generated_cwe": analysis["cwe"],
        "generated_cvss": analysis["cvss"],
        "generated_description": analysis["description"],
        "generated_impact": analysis["impact"],
        "generated_reproduction": analysis["reproduction"],
        "generated_recommendation": analysis["recommendation"]
    }

    try:
        update_response = (
            supabase_db
            .table("discoveries")
            .update(update_data)
            .eq("id", discovery_id)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save discovery analysis."
        )

    if not update_response.data:
        raise HTTPException(
            status_code=500,
            detail="Discovery analysis could not be saved."
        )

    updated_discovery = update_response.data[0]

    return {
        "message": "Discovery analyzed successfully.",
        "discovery": updated_discovery,
        "analysis": analysis
    }