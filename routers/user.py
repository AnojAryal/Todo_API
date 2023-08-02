from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import database, schemas, models
from hashing import Hashing

router = APIRouter(prefix="/users", tags=["Users"])
get_db = database.get_db


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    new_user = models.User(
        name=user.name, email=user.email, password=Hashing.bcrypt(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}")
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
    return user
