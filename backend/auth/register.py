import secrets

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)


@router.post("/register")
async def register_user(data: RegisterRequest):

    # --------------------------------
    # 1. Clean and validate input
    # --------------------------------
    email = data.email.strip().lower()
    full_name = data.full_name.strip()

    if not full_name:
        raise HTTPException(
            status_code=400,
            detail="Full name cannot be empty."
        )

    # --------------------------------
    # 2. Create user in Supabase Auth
    # --------------------------------
    try:
        auth_response = supabase_auth.auth.sign_up({
            "email": email,
            "password": data.password
        })

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Registration could not be completed."
        )

    if not auth_response.user:
        raise HTTPException(
            status_code=400,
            detail="Registration could not be completed."
        )

    user_id = auth_response.user.id

    # --------------------------------
    # 3. Generate API key
    # --------------------------------
    api_key = secrets.token_urlsafe(32)

    # --------------------------------
    # 4. Create application profile
    # --------------------------------
    try:
        profile_response = (
            supabase_db
            .table("profiles")
            .insert({
                "id": user_id,
                "full_name": full_name,
                "api_key": api_key
            })
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Account was created, but profile setup failed."
        )

    if not profile_response.data:
        raise HTTPException(
            status_code=500,
            detail="Account was created, but profile setup failed."
        )

    # --------------------------------
    # 5. Do NOT return API key here
    # --------------------------------
    return {
        "message": "Registration successful.",
        "user": {
            "id": user_id,
            "email": auth_response.user.email,
            "full_name": full_name
        }
    }