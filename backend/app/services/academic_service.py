
from app.core.supabase import supabase
from app.schemas.academic import AssignmentCreate, AssignmentUpdate


def create_assignment(user_id: str, data: AssignmentCreate):
    payload = data.model_dump(mode="json")
    payload["user_id"] = user_id

    return (
        supabase.table("assignments")
        .insert(payload)
        .execute()
        .data
    )


def get_assignments(user_id: str):
    return (
        supabase.table("assignments")
        .select("*")
        .eq("user_id", user_id)
        .order("due_date")
        .execute()
        .data
    )


def update_assignment(
    user_id: str,
    assignment_id: str,
    data: AssignmentUpdate,
):
    payload = data.model_dump(mode="json", exclude_unset=True)

    if not payload:
        return []

    return (
        supabase.table("assignments")
        .update(payload)
        .eq("id", assignment_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )


def delete_assignment(user_id: str, assignment_id: str):
    try:
        result = (
            supabase.table("assignments")
            .delete()
            .eq("id", assignment_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data

    except Exception as e:
        print("Delete assignment error:", repr(e))
        raise