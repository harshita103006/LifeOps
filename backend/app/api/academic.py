
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.profile import get_user_client
from app.schemas.academic import AssignmentCreate, AssignmentUpdate

router = APIRouter(prefix="/api/academic", tags=["Academic Agent"])


@router.post("/assignments", status_code=status.HTTP_201_CREATED)
def add_assignment(
    data: AssignmentCreate,
    auth=Depends(get_user_client),
):
    client, user = auth

    try:
        result = (
            client.table("assignments")
            .insert({
                **data.model_dump(mode="json"),
                "user_id": str(user.id),
            })
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Assignment could not be created.",
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print("Create assignment error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Could not create assignment.",
        )


@router.get("/assignments")
def list_assignments(auth=Depends(get_user_client)):
    client, user = auth

    try:
        result = (
            client.table("assignments")
            .select("*")
            .eq("user_id", str(user.id))
            .order("due_date")
            .execute()
        )

        return result.data or []

    except Exception as e:
        print("List assignments error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve assignments.",
        )


@router.patch("/assignments/{assignment_id}")
def edit_assignment(
    assignment_id: UUID,
    data: AssignmentUpdate,
    auth=Depends(get_user_client),
):
    client, user = auth
    payload = data.model_dump(mode="json", exclude_unset=True)

    if not payload:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update.",
        )

    try:
        result = (
            client.table("assignments")
            .update(payload)
            .eq("id", str(assignment_id))
            .eq("user_id", str(user.id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Assignment not found for this user.",
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print("Update assignment error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Could not update assignment.",
        )


@router.delete("/assignments/{assignment_id}")
def remove_assignment(
    assignment_id: UUID,
    auth=Depends(get_user_client),
):
    client, user = auth

    print("DELETE assignment ID:", assignment_id)
    print("Logged-in user ID:", user.id)

    try:
        result = (
            client.table("assignments")
            .delete()
            .eq("id", str(assignment_id))
            .eq("user_id", str(user.id))
            .execute()
        )

        if not result.data:
            print("Delete returned no rows. Check assignment ID and user_id.")
            raise HTTPException(
                status_code=404,
                detail="Assignment not found for this user.",
            )

        return {"message": "Assignment deleted successfully."}

    except HTTPException:
        raise
    except Exception as e:
        print("Delete assignment error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Could not delete assignment.",
        )
