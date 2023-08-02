from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import schemas


# Create database tables if they don't exist
models.Base.metadata.create_all(engine)

app = FastAPI()


# create new todo
@app.post("/todo", status_code=status.HTTP_201_CREATED, tags=["Todo"])
def create(todo: schemas.Todo, db: Session = Depends(get_db)):
    new_todo = models.Todo(title=todo.title, description=todo.description)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


# delete the selected id from db
@app.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Todo"])
def delete_todo(id, db: Session = Depends(get_db)):
    todo_del = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found"
        )
    db.delete(todo_del)
    db.commit()
    return "Successful"


# update the selected id
@app.put("/todo/{id}", status_code=status.HTTP_202_ACCEPTED, tags=["Todo"])
def update_todo(id, todo: schemas.Todo, db: Session = Depends(get_db)):
    existing_todo = db.query(models.Todo).filter(models.Todo.id == id)
    if not existing_todo.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found"
        )

    existing_todo.title = todo.title
    existing_todo.description = todo.description

    db.commit()
    return "Updated Succssfully"


# get all todo items
@app.get("/todo", status_code=status.HTTP_200_OK, tags=["Todo"])
def get_all(db: Session = Depends(get_db)):
    get_todo = db.query(models.Todo).all()
    return get_todo


# get todo by id
@app.get("/todo/{id}", tags=["Todo"])
def getby_id(id, db: Session = Depends(get_db)):
    todo_id = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} is not available",
        )
    return todo_id
