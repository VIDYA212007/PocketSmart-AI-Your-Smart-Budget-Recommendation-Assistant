from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta
from models import Token, UserCreate, UserInDB
from auth import (authenticate_user, create_access_token, get_password_hash,
                  fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "disabled": False
    }
    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, request: Request,
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response

@router.get("/session-info")
async def session_info(current_user: UserInDB = Depends(get_current_active_user)):
    return {
        "status": "active",
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "logged_in": True
    }

@router.get("/session-data")
async def session_data(current_user: UserInDB = Depends(get_current_active_user)):
    from state import recommendation_history
    user_history = recommendation_history[current_user.username]
    return {
        "username": current_user.username,
        "total_recommendations": len(user_history),
        "recent": user_history[-5:]
    }