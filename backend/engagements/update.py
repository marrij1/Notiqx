from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Engagements"]
)

security = HTTPBearer()


class EngagementUpdate(BaseModel):
    name: str | None = None
    client_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    scope: str | None = None
    status: str | None = None


@router.put("/{engagement_id}")
async def update_engagement(
    engagement_id: str,
    data: EngagementUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # --------------------------------
    # 1. Verify JWT
    # --------------------------------
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

    # --------------------------------
    # 2. Get current user's engagement
    # --------------------------------
    try:
        engagement_response = (
            supabase_db
            .table("engagements")
            .select("*")
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

    existing = engagement_response.data

    # --------------------------------
    # 3. Get only fields actually sent
    # --------------------------------
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update."
        )

    # --------------------------------
    # 4. Validate name
    # --------------------------------
    if "name" in update_data:

        if update_data["name"] is None:
            raise HTTPException(
                status_code=400,
                detail="Name cannot be empty."
            )

        update_data["name"] = update_data["name"].strip()

        if not update_data["name"]:
            raise HTTPException(
                status_code=400,
                detail="Name cannot be empty."
            )

    # --------------------------------
    # 5. Validate client name
    # --------------------------------
    if "client_name" in update_data:

        if update_data["client_name"] is None:
            raise HTTPException(
                status_code=400,
                detail="Client name cannot be empty."
            )

        update_data["client_name"] = update_data["client_name"].strip()

        if not update_data["client_name"]:
            raise HTTPException(
                status_code=400,
                detail="Client name cannot be empty."
            )

    # --------------------------------
    # 6. Validate status
    # --------------------------------
    allowed_statuses = [
        "active",
        "completed"
    ]

    if "status" in update_data:

        if update_data["status"] is None:
            raise HTTPException(
                status_code=400,
                detail="Status cannot be empty."
            )

        if update_data["status"] not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Status must be 'active' or 'completed'."
            )

    # --------------------------------
    # 7. Convert dates
    # --------------------------------
    if "start_date" in update_data:
        if update_data["start_date"] is not None:
            update_data["start_date"] = (
                update_data["start_date"].isoformat()
            )

    if "end_date" in update_data:
        if update_data["end_date"] is not None:
            update_data["end_date"] = (
                update_data["end_date"].isoformat()
            )

    # --------------------------------
    # 8. Validate final date range
    # --------------------------------
    current_start_date = existing.get("start_date")
    current_end_date = existing.get("end_date")

    new_start_date = update_data.get(
        "start_date",
        current_start_date
    )

    new_end_date = update_data.get(
        "end_date",
        current_end_date
    )

    # Convert strings from database back to date objects
    if isinstance(new_start_date, str):
        new_start_date = date.fromisoformat(new_start_date)

    if isinstance(new_end_date, str):
        new_end_date = date.fromisoformat(new_end_date)

    if (
        new_start_date is not None
        and new_end_date is not None
        and new_end_date < new_start_date
    ):
        raise HTTPException(
            status_code=400,
            detail="End date cannot be earlier than start date."
        )

    # --------------------------------
    # 9. Clean scope
    # --------------------------------
    if "scope" in update_data:
        if update_data["scope"] is not None:
            update_data["scope"] = update_data["scope"].strip()

    # --------------------------------
    # 10. Perform update
    # --------------------------------
    try:
        response = (
            supabase_db
            .table("engagements")
            .update(update_data)
            .eq("id", engagement_id)
            .eq("user_id", user_id)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to update engagement."
        )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found."
        )

    return {
        "message": "Engagement updated successfully.",
        "engagement": response.data[0]
    }