from sqlalchemy.orm import Session
from src.models import User
from src.auth import hash_password, verify_password
from typing import Optional


def create_user(db: Session, email: str, password: str, name: str) -> User:
    """Create a new user (signup)"""
    hashed_password = hash_password(password)
    
    user = User(
        email = email,
        name = name,
        hashed_password = hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find user by email"""
    return db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Find user by ID"""
    return db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user for login"""
    user = get_user_by_email(db, email)

    if not user:
        return None
    
    if not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def update_user(db: Session, user_id: int, name: Optional[str] = None) -> Optional[User]:
    """Update user details"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    if name is not None:
        user.name = name
    
    db.commit()
    db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int) -> bool:
    """Deactivate user (suspend account)"""
    user = get_user_by_id(db, user_id)

    if not user:
        return False
    user.is_active = False
    db.commit()
    return True

def delete_user(db: Session, user_id: int) -> bool:
    """Soft delete user"""
    user = get_user_by_id(db, user_id)

    if not user:
        return False
    user.is_deleted = True
    db.commit()

    return True

def reactivate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user