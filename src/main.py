from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Import our modules
from src.database import init_db, get_db, DbSession
from src.schemas import (
    UserCreate, UserResponse, UserLogin,
    TaskCreate, TaskResponse, TaskUpdate,
    Token
)
from src import user_crud, crud
from src.auth import (
    create_access_token, 
    get_current_user_id,
    verify_password
)

# Create FastAPI app
app = FastAPI(
    title = "TaskMate AI",
    description = "AI-powered task management assistant",
    version = "1.0.0"
)

# Add CORS middleware (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("✓ Database initialized")

@app.get("/")
def root():
    return{
        "message": "Welcome to TaskMate AI!",
        "status": "ok"
    }

# ============= USER ROUTES =============

@app.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: DbSession):
    existing_user = user_crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already registered"
        )
    user = user_crud.create_user(
        db=db,
        email = user_data.email,
        password = user_data.password,
        name = user_data.name 
    )
    return user

@app.post("/login", response_model = Token)
def login(login_data: UserLogin, db: DbSession):
    
    existing_user = user_crud.get_user_by_email(db, login_data.email)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_crud.authenticate_user(
        db = db,
        email = login_data.email,
        password = login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type":"bearer"
    }
