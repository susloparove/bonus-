from fastapi import APIRouter, Depends, HTTPException
from .models import UserCreate
from .utils import hash_password, verify_password, create_access_token
from .utils import get_user_by_username, write_json, read_json

router = APIRouter()

@router.post("/login")
def login(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["id"]})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register")
def register(user_data: UserCreate):
    users = read_json("data/users.json")
    if any(u["username"] == user_data.username for u in users):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user_data.password)
    new_user = {
        "id": len(users) + 1,
        "username": user_data.username,
        "password_hash": hashed_password,
        "role": user_data.role
    }
    users.append(new_user)
    write_json("data/users.json", users)
    return {"status": "success"}