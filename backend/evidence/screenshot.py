import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/findings",
    tags=["Evidence"]
)

security = HTTPBearer()


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


ALLOWED_EXTENSIONS = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp"
}


ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp"
}


# ==========================================
# IMAGE SIGNATURES / MAGIC BYTES
# ==========================================

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

JPEG_SIGNATURE = b"\xff\xd8\xff"

WEBP_RIFF_SIGNATURE = b"RIFF"
WEBP_FORMAT_SIGNATURE = b"WEBP"


def validate_image_signature(
    file_data: bytes,
    extension: str
) -> bool:

    if extension == ".png":
        return file_data.startswith(PNG_SIGNATURE)

    if extension in {".jpg", ".jpeg"}:
        return file_data.startswith(JPEG_SIGNATURE)

    if extension == ".webp":
        return (
            len(file_data) >= 12
            and file_data[:4] == WEBP_RIFF_SIGNATURE
            and file_data[8:12] == WEBP_FORMAT_SIGNATURE
        )

    return False


@router.post("/{finding_id}/evidence/screenshot")
async def upload_screenshot(
    finding_id: str,
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # ==========================================
    # 1. VERIFY JWT
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
    # 2. VALIDATE FILENAME
    # ==========================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    original_filename = file.filename.lower()

    if "." not in original_filename:
        raise HTTPException(
            status_code=400,
            detail="File extension is required."
        )

    extension = "." + original_filename.rsplit(".", 1)[1]

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "File type not allowed. "
                "Only PNG, JPG, JPEG and WEBP are allowed."
            )
        )

    # ==========================================
    # 3. VALIDATE MIME TYPE
    # ==========================================

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image MIME type."
        )

    expected_content_type = ALLOWED_EXTENSIONS[extension]

    if file.content_type != expected_content_type:
        raise HTTPException(
            status_code=400,
            detail="File extension and MIME type do not match."
        )

    # ==========================================
    # 4. READ WITH SIZE LIMIT
    # ==========================================

    file_data = await file.read(
        MAX_FILE_SIZE + 1
    )

    if not file_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum size is 5 MB."
        )

    # ==========================================
    # 5. VALIDATE ACTUAL FILE SIGNATURE
    # ==========================================

    if not validate_image_signature(
        file_data,
        extension
    ):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image format."
        )

    # ==========================================
    # 6. VERIFY FINDING
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
    # 7. VERIFY OWNERSHIP
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
    # 8. SERVER-GENERATED STORAGE PATH
    # ==========================================

    filename = f"{uuid.uuid4()}{extension}"

    storage_path = (
        f"{user_id}/{finding_id}/{filename}"
    )

    # ==========================================
    # 9. UPLOAD TO SUPABASE STORAGE
    # ==========================================

    try:
        supabase_db.storage.from_("evidence").upload(
            storage_path,
            file_data,
            {
                "content-type": file.content_type,
                "upsert": False
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload screenshot: {str(e)}"
        )

    # ==========================================
    # 10. CREATE DATABASE RECORD
    # ==========================================

    try:
        evidence_response = (
            supabase_db
            .table("evidence")
            .insert({
                "finding_id": finding_id,
                "evidence_type": "screenshot",
                "title": file.filename,
                "content": None,
                "file_url": storage_path
            })
            .execute()
        )

    except Exception as e:

        # Cleanup storage if DB insertion fails
        try:
            supabase_db.storage.from_(
                "evidence"
            ).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to create evidence record: {str(e)}"
            )
        )

    if not evidence_response.data:
        # Cleanup if no database row was returned
        try:
            supabase_db.storage.from_(
                "evidence"
            ).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Evidence record could not be created."
        )

    return {
        "message": "Screenshot uploaded successfully.",
        "evidence": evidence_response.data[0]
    }