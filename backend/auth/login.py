from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from supabase_client import supabase_auth


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@router.post("/login")
async def login_user(data: LoginRequest):

    # --------------------------------
    # 1. Clean email
    # --------------------------------
    email = data.email.strip().lower()

    # --------------------------------
    # 2. Authenticate with Supabase
    # --------------------------------
    try:
        response = supabase_auth.auth.sign_in_with_password({
            "email": email,
            "password": data.password
        })

        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

    except HTTPException:
        raise

    except Exception:
        # Keep authentication errors generic.
        # Do not expose Supabase's internal error details.
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # --------------------------------
    # 3. Return authentication result
    # --------------------------------
    return {
        "message": "Login successful.",
        "access_token": response.session.access_token,
        "token_type": "bearer",
        "user": {
            "id": response.user.id,
            "email": response.user.email
        }
    }