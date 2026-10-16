
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, HttpUrl
from supabase import create_client
from supabase.lib.client_options import SyncClientOptions

from app.core.config import settings


router = APIRouter(prefix="/api/profile", tags=["Student Profile"])

bearer_scheme = HTTPBearer()


def get_user_client(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials

    try:
        client = create_client(
            settings.supabase_url,
            settings.supabase_publishable_key,
            options=SyncClientOptions(
                headers={"Authorization": f"Bearer {token}"}
            ),
        )

        user_response = client.auth.get_user(token)
        user = user_response.user

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired access token.",
            )

        # Use the logged-in user's token for database queries.
        client.postgrest.auth(token)

        return client, user

    except HTTPException:
        raise

    except Exception as e:
        print("Profile authentication error:", repr(e))
        raise HTTPException(
            status_code=401,
            detail="Authentication failed. Please log in again.",
        )


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    avatar_url: HttpUrl | None = None


@router.get("/me")
def get_my_profile(auth=Depends(get_user_client)):
    client, user = auth

    try:
        result = (
            client.table("profiles")
            .select("id, full_name, avatar_url, created_at, updated_at")
            .eq("id", str(user.id))
            .maybe_single()
            .execute()
        )

        if result.data is None:
            raise HTTPException(
                status_code=404,
                detail="Profile not found. Please create your profile first.",
            )

        return result.data

    except HTTPException:
        raise

    except Exception as e:
        print("Get profile error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve your profile.",
        )


@router.put("/me")
def update_my_profile(
    data: ProfileUpdate,
    auth=Depends(get_user_client),
):
    client, user = auth

    try:
        result = (
            client.table("profiles")
            .upsert(
                {
                    "id": str(user.id),
                    "full_name": data.full_name,
                    "avatar_url": (
                        str(data.avatar_url)
                        if data.avatar_url
                        else None
                    ),
                },
                on_conflict="id",
            )
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Profile could not be saved.",
            )

        return {
            "message": "Profile saved successfully.",
            "profile": result.data[0],
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Update profile error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Could not save your profile. Check database permissions.",
        )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    auth=Depends(get_user_client),
):
    client, user = auth

    allowed_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    try:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG and WEBP images are allowed.",
            )

        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if len(content) > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Avatar must be 2 MB or smaller.",
            )

        extension = allowed_types[file.content_type]
        file_path = f"{user.id}/{uuid.uuid4().hex}{extension}"

        client.storage.from_("avatars").upload(
            path=file_path,
            file=content,
            file_options={
                "content-type": file.content_type,
                "upsert": "false",
            },
        )

        avatar_url = client.storage.from_("avatars").get_public_url(
            file_path
        )

        profile_result = (
            client.table("profiles")
            .upsert(
                {
                    "id": str(user.id),
                    "avatar_url": avatar_url,
                },
                on_conflict="id",
            )
            .execute()
        )

        if not profile_result.data:
            raise HTTPException(
                status_code=500,
                detail="Avatar uploaded, but profile could not be updated.",
            )

        return {
            "message": "Avatar uploaded successfully.",
            "avatar_url": avatar_url,
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Avatar upload error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Avatar upload failed. Check backend terminal.",
        )

    finally:
        await file.close()
