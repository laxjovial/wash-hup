from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import redis as Redis
from dotenv import load_dotenv
load_dotenv()

# Redis configuration (Sync)
REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
else:
    redis = Redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        decode_responses=True,
        username="default",
        password=os.getenv("REDIS_PASSWORD"),
    )

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRESQL_DB_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")

# Use a dummy URL for testing if not provided to avoid crash during import
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

# Only create tables if not in a testing environment
if os.getenv("ENV") != "testing":
    Base.metadata.create_all(engine)
