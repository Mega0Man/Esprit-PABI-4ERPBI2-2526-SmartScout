from database import SessionLocal
from models import User
from auth import get_password_hash
import json

def test_signup():
    db = SessionLocal()
    try:
        username = "testuser"
        password = "password"
        role = "group_leader"
        national_id = "12345678"
        
        # Check if exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"User {username} already exists.")
            return

        new_user = User(
            username=username,
            role=role,
            national_id=national_id,
            password_hash=get_password_hash(password)
        )
        db.add(new_user)
        db.commit()
        print(f"Successfully created user {username}")
    except Exception as e:
        db.rollback()
        print(f"Failed to create user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_signup()
