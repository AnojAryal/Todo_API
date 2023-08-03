import io
from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    HTTPException,
    UploadFile,
    File,
)
from typing import List, Optional
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import database, models, schemas
import tempfile
from JWTtoken import get_current_user, get_user_exception
import csv


router = APIRouter(
    prefix="/todo", tags=["Todo"]
)  # Instantiate the APIRouter class with parentheses
get_db = database.get_db


# Post API to create a new Todo item associated with the current user
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: schemas.Todo,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    new_todo = models.Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        user_id=user.get("id"),
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


# delete the selected id from db
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    id,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    todo_del = (
        db.query(models.Todo)
        .filter(models.Todo.id == id)
        .filter(models.Todo.user_id == user.get("id"))
        .first()
    )
    if not todo_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found"
        )
    db.delete(todo_del)
    db.commit()
    return "Successful"


# update the selected id
@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_todo(
    id,
    todo: schemas.Todo,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    model = (
        db.query(models.Todo)
        .filter(models.Todo.id == id)
        .filter(models.Todo.user_id == user.get("id"))
        .first()
    )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found"
        )

    model.title = todo.title
    model.description = todo.description
    model.completed = todo.completed

    db.commit()
    return "Updated Successfully"


# PATCH API to update the 'completed' field of a specific Todo item
@router.patch("/{id}/completed/", status_code=status.HTTP_202_ACCEPTED)
def update_todo_completed(
    id: int,
    completed: bool,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    model = (
        db.query(models.Todo)
        .filter(models.Todo.id == id)
        .filter(models.Todo.user_id == user.get("id"))
        .first()
    )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} not found or you don't have permission to update it",
        )

    model.completed = completed

    db.commit()
    return "Completed status updated successfully"


# get the user with conditions
@router.get("/")
async def task(
    completed: bool = None,
    search_query: Optional[str] = None,
    order_by: Optional[str] = "id",
    ascending: Optional[bool] = True,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        raise get_user_exception()

    # Base query to filter tasks based on  user
    query = db.query(models.Todo).filter(models.Todo.user_id == user.get("id"))

    # If search_query parameter is provided, filter based on title and description
    if search_query:
        search_pattern = (
            f"%{search_query.lower()}%"  # Convert the search query to lowercase
        )
        query = query.filter(
            func.lower(models.Todo.title).ilike(search_pattern)
            | func.lower(models.Todo.description).ilike(search_pattern)
        )

    # If completed parameter is provided, filter based on completion status
    if completed is not None:
        query = query.filter(models.Todo.completed == completed)

    # Determine the attribute to sort by and the sorting order
    allowed_order_by = ["id", "title", "description", "completed"]
    if order_by not in allowed_order_by:
        order_by = "id"

    if ascending:
        query = query.order_by(getattr(models.Todo, order_by))
    else:
        query = query.order_by(getattr(models.Todo, order_by).desc())

    # Execute the final query and return the results
    return query.all()


# get todo by id
@router.get("/{id}")
def getby_id(
    id,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    todo_id = (
        db.query(models.Todo)
        .filter(models.Todo.id == id)
        .filter(models.Todo.user_id == user.get("id"))
        .first()
    )
    if not todo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} is not available",
        )
    return todo_id


# export csv
@router.get("/csv-export/")
def export_to_csv(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    todos = db.query(models.Todo).filter(models.Todo.user_id == user.get("id")).all()
    if not todos:
        raise HTTPException(status_code=204, detail="No Todo items to export")

    response = Response(media_type="text/csv")
    response.headers["Content-Disposition"] = 'attachment; filename="tasks.csv"'

    fieldnames = ["id", "title", "description", "completed"]

    with io.StringIO() as csv_data:
        writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
        writer.writeheader()

        for todo in todos:
            todo_data = {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
            }
            writer.writerow(todo_data)

        # Creating a temporary file and writing the CSV data into it
        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv")
        temp_file.write(csv_data.getvalue())

    return FileResponse(temp_file.name, media_type="text/csv", filename="tasks.csv")


# CSV import
@router.post("/csv-import/")
def import_from_csv(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Read and process the uploaded CSV file
    decoded_file = file.file.read().decode("utf-8")
    csv_data = io.StringIO(decoded_file)
    reader = csv.DictReader(csv_data)

    for row in reader:
        todo_data = {
            "title": row["title"],
            "description": row["description"],
            "completed": row["completed"].lower()
            == "true",  # Convert string to boolean
            "user_id": user.get("id"),
        }
        todo = models.Todo(**todo_data)
        db.add(todo)

    db.commit()

    return {"message": "CSV import successful"}
