from sqlalchemy.orm import Session
from src.models import Task
from datetime import datetime
from typing import List, Optional


def create_task(
    db: Session,
    user_id: int,
    title: str,
    description: Optional[str]=None,
    due_date: Optional[datetime]=None,
    priority: str = "medium"
) -> Task:
    """Create a new task"""
    task = Task(
        title = title,
        description = description,
        due_date = due_date,
        priority = priority,
        user_id = user_id
    )

    db.add(task)
    db.commit()

    db.refresh(task)
    return task

def get_all_tasks(
    db: Session,
    user_id: int,
    completed: Optional[bool] = None
) -> List[Task]:
    """Get all tasks for a specific user"""
    query = db.query(Task).filter(Task.user_id == user_id)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    return query.order_by(Task.due_date.asc()).all()

def get_task_by_id(
    db: Session, 
    task_id: int,
    user_id: int
) -> Optional[task]:
    """Get task only if it belongs to user"""
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()

def update_task(
    db: Session,
    task_id : int,
    user_id: int,
    title: str,
    description: Optional[str] = None,
    due_completed: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[str] = None
) ->Optional[Task]:
    """Update task only if it belongs to user"""
    task = get_task_by_id(db, task_id, user_id)
    if not task:
        None
    
    if title is not None:
        task.title = title
    
    if description is not None:
        task.description = description
    
    if due_completed is not None:
        task.due_completed = due_completed
    
    if completed is not None:
        task.completed = completed

        if completed:
            task.completed_at = datetime.utcnow()

    if priority is not None:
        task.priority = priority
    
    db.commit()
    db.refresh(task)

    return task
    
    
def delete_task(
    db: Session,
    task_id: int,
    user_id:int
) -> bool:
    """Delete task only if it belongs to user"""
    task  = get_task_by_id(db, task_id, user_id)

    if not task:
        return False
    db.delete(task)
    db.commit()
    return True

def search_tasks(
    db: Session,
    user_id: int,
    query: str
) ->List[Task]:
    """Search tasks for specific user."""
    return db.query(Task).filter(
        Task.user_id == user_id,
        (Task.title.contains(query)) | (Task.description.contains(query))
    ).all()