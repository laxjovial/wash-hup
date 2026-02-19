import os
import sys
import pytest
from sqlalchemy import Column, String

# Custom Mock for Geometry
class MockGeometry(String):
    def __init__(self, *args, **kwargs):
        super().__init__()

# We need to mock geoalchemy2 before it's used
import geoalchemy2
geoalchemy2.Geometry = MockGeometry

os.environ["ENV"] = "testing"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from main import app
from app.api.dependencies import get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    # We need to import models so they are registered with Base
    from app.models.auth import user
    from app.models.client import profile, wash, payment
    from app.models.washer import profile, transaction, reward
    from app.models.admin import prices, profile, rewards

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture
def admin_token(client, db):
    from app.models.auth.user import User
    from app.models.admin.profile import AdminProfile
    from app.core.security import bcrypt_context, create_access_token
    from datetime import timedelta
    from uuid import uuid4

    user_id = "admin-user-id"
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        hashed_password = bcrypt_context.hash("adminpassword")
        user = User(
            id=user_id,
            fullname="Admin User",
            email="admin@example.com",
            hashed_password=hashed_password,
            role="admin",
            phone_number="1234567890"
        )
        db.add(user)
        db.flush()

        admin_prof = db.query(AdminProfile).filter(AdminProfile.user_id == user_id).first()
        if not admin_prof:
            profile = AdminProfile(
                id=str(uuid4()),
                user_id=user_id,
                user_role="admin"
            )
            db.add(profile)
        db.commit()

    token = create_access_token(
        email=user.email,
        user_id=user_id,
        role="admin",
        expires_delta=timedelta(minutes=15)
    )
    return token
