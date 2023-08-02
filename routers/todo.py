from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
import database, models, schemas, OAuth2


router = APIRouter(
    prefix="/todo", tags=["Todo"]
)  # Instantiate the APIRouter class with parentheses
get_db = database.get_db


# create new todo
@router.post("/", status_code=status.HTTP_201_CREATED)
def create(
    todo: schemas.Todo,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(OAuth2.get_current_user),
):
    new_todo = models.Todo(title=todo.title, description=todo.description)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


# delete the selected id from db
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(OAuth2.get_current_user),
):
    todo_del = db.query(models.Todo).filter(models.Todo.id == id).first()
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
    current_user: schemas.User = Depends(OAuth2.get_current_user),
):
    existing_todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not existing_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found"
        )

    existing_todo.title = todo.title
    existing_todo.description = todo.description

    db.commit()
    return "Updated Successfully"


# get all todo items
@router.get("/", status_code=status.HTTP_200_OK)
def get_all(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(OAuth2.get_current_user),
):
    get_todo = db.query(models.Todo).all()
    return get_todo


# get todo by id
@router.get("/{id}")
def getby_id(
    id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(OAuth2.get_current_user),
):
    todo_id = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} is not available",
        )
    return todo_id
