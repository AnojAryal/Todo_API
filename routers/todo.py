from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
import database, models, schemas
from JWTtoken import get_current_user, get_user_exception


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


# # update the selected id
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


# get all todo items
@router.get("/")
async def task(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todo).filter(models.Todo.user_id == user.get("id")).all()


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
