
from fastapi import APIRouter, Depends, HTTPException
from app.api.profile import get_user_client

router = APIRouter(
    prefix="/api/coordinator",
    tags=["Coordinator Agent"],
)


@router.post("/chat")
def coordinator_chat(
    message: str,
    auth=Depends(get_user_client),
):
    client, user = auth
    user_message = message.strip().lower()

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    academic_keywords = [
        "assignment",
        "deadline",
        "task",
        "homework",
    ]

    if any(word in user_message for word in academic_keywords):
        try:
            query = (
                client.table("assignments")
                .select("*")
                .eq("user_id", str(user.id))
            )

            if "pending" in user_message:
                query = query.eq("status", "pending")
            elif "completed" in user_message:
                query = query.eq("status", "completed")
            elif "in progress" in user_message:
                query = query.eq("status", "in_progress")

            result = query.order("due_date").execute()
            assignments = result.data or []

            return {
                "agent": "Academic Agent",
                "message": (
                    f"Found {len(assignments)} assignment(s)."
                    if assignments
                    else "No matching assignments found."
                ),
                "data": assignments,
            }

        except Exception as e:
            print("Coordinator academic query error:", repr(e))
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve assignments right now.",
            )

    return {
        "agent": "Coordinator Agent",
        "message": (
            "I can currently help with assignments, "
            "deadlines, and academic tasks."
        ),
        "data": [],
    }
