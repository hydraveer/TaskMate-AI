from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List

from database import init_db, get_db, DbSession
from schemas import (
    UserCreate, UserResponse, UserLogin,
    TaskCreate, TaskResponse, TaskUpdate,
    Token, ChatRequest, ChatResponse
)
import user_crud, crud
from auth import (
    create_access_token,
    get_current_user_id,
    verify_password
)
from ai_agent import chat_with_ai

# Lifespan: runs on startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("✓ Database initialized")
    yield
    # Shutdown (cleanup if needed)

# Create FastAPI app
app = FastAPI(
    title = "TaskMate AI",
    description = "AI-powered task management assistant",
    version = "1.0.0",
    lifespan = lifespan
)

# Add CORS middleware (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def login(db: DbSession, login_data: OAuth2PasswordRequestForm = Depends()):
    
    user = user_crud.authenticate_user(
        db=db,
        email=login_data.username,
        password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# "username" field in Swagger = your email address
@app.post("/token", response_model=Token, include_in_schema=False)
def swagger_token(
    db: DbSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = user_crud.authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user", response_model=UserResponse)
def get_current_user(
    db: DbSession,
    user_id: int = Depends(get_current_user_id)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    return user

@app.post("/task", response_model = TaskResponse, status_code = status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: DbSession,
    user_id: int = Depends(get_current_user_id)
):
    task = crud.create_task(
        db = db,
        user_id = user_id,
        title = task_data.title,
        description = task_data.description,
        due_date = task_data.due_date,
        priority = task_data.priority
    )

    return task

@app.get("/tasks", response_model = List[TaskResponse])
def get_all_tasks(
    db: DbSession,
    completed: Optional[bool] = None,
    user_id: int = Depends(get_current_user_id)
):
    tasks = crud.get_all_tasks(
        db,
        user_id = user_id,
        completed = completed
    )
    return tasks

@app.get("/task/{task_id}", response_model = TaskResponse)
def get_task_by_id(
    db: DbSession,
    task_id: int,
    user_id:int = Depends(get_current_user_id)
):
    task = crud.get_task_by_id(
        db, task_id, user_id
    )
    if not task:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Task not found"
        )
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task_endpoint(
    db: DbSession,
    task_id: int,
    task_data: TaskUpdate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Update task (only if it belongs to current user)
    
    What it does:
    1. Get user_id from token
    2. Update task (checks ownership!)
    3. Return updated task or 404
    """
    task = crud.update_task(
        db=db,
        task_id=task_id,
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        completed=task_data.completed,
        priority=task_data.priority
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    db: DbSession,
    task_id: int,
    user_id:int = Depends(get_current_user_id)
):
    """
    Delete task (only if it belongs to current user)
    
    What it does:
    1. Get user_id from token
    2. Delete task (checks ownership!)
    3. Return 204 No Content or 404
    """
    success = crud.delete_task(db, task_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return None

@app.post("/ai/chat", response_model=ChatResponse)
def ai_chat(
    chat_request: ChatRequest,
    db: DbSession,
    user_id: int = Depends(get_current_user_id)
):
    response = chat_with_ai(
        message = chat_request.message,
        db=db,
        user_id=user_id
    )
    return {
        "response": response
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
