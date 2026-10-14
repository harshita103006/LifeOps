from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register")
def register(data: RegisterRequest):
    try:
        response = register_user(
            data.full_name,
            data.email,
            data.password,
        )

        user = response.user
        if user is None:
            raise HTTPException(
                status_code=400,
                detail="Registration could not be completed.",
            )

        return {
            "message": "Registration successful. Check your email if verification is required.",
            "user_id": str(user.id),
            "email": user.email,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Registration failed. Check the email, password and Supabase Auth settings.",
        )


@router.post("/login")
def login(data: LoginRequest):
    try:
        response = login_user(data.email, data.password)

        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Login failed. Verify your credentials and email confirmation status.",
            )

        return {
            "message": "Login successful",
            "user_id": str(response.user.id),
            "email": response.user.email,
            "access_token": response.session.access_token,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Login failed. Check credentials and email verification.",
        )