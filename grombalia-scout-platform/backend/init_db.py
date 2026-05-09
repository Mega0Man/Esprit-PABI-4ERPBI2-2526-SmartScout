from database import engine, SessionLocal
from models import Base, User
from auth import get_password_hash


def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()

    # Check if users already exist
    existing_users = db.query(User).count()
    if existing_users > 0:
        print("Database already initialized!")
        db.close()
        return

    # Create sample users
    # users = [
    #     {
    #         "username": "group_leader",
    #         "password": "password",
    #         "role": "group_leader",
    #         "national_id": "12345678"
    #     },
    #     {
    #         "username": "treasurer",
    #         "password": "password",
    #         "role": "treasurer",
    #         "national_id": "87654321"
    #     },
    #     {
    #         "username": "unit_leader",
    #         "password": "password",
    #         "role": "unit_leader",
    #         "national_id": "11223344"
    #     }
    # ]

    # for user_data in users:
    #     user = User(
    #         username=user_data["username"],
    #         password_hash=get_password_hash(user_data["password"]),
    #         role=user_data["role"],
    #         national_id=user_data.get("national_id")
    #     )
    #     db.add(user)

    # db.commit()
    db.close()
    print("Database tables ensured. No sample users added.")


if __name__ == "__main__":
    init_db()
