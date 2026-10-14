from supabase import create_client
from app.core.config import settings


auth_client = create_client(
    settings.supabase_url,
    settings.supabase_publishable_key,
)


def register_user(full_name: str, email: str, password: str):
    response = auth_client.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "full_name": full_name
            }
        }
    })
    return response


def login_user(email: str, password: str):
    response = auth_client.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })
    return response