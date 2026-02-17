from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime, timezone
from .profile import WasherProfile




# class RewardWasher(Base):
#     __tablename__ = "reward_washers"

#     id = Column(String, primary_key=True, index=True)
#     reward_id = Column(String, ForeignKey("rewards.id"))
#     washer_id = Column(String, ForeignKey("washer_profile.id"))

#     rewards = relationship("Reward", back_populates="achieved_washers")

# class ClaimRequest(Base):
#     __tablename__ = "claim_requests"

#     id = Column(String, primary_key=True, index=True)
#     reward_id = Column(String, ForeignKey("rewards.id"))

#     address = Column(String)
#     city = Column(String)
#     state = Column(String)
#     phone_number = Column(String)




# from sqlalchemy import Column, Integer, String, ForeignKey, Table
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# # Association table (no model class needed in most cases)
# post_tag = Table(
#     "post_tag",
#     Base.metadata,
#     Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
#     Column("tag_id",  Integer, ForeignKey("tags.id"),  primary_key=True),
# )

# class Post(Base):
#     __tablename__ = "posts"
    
#     id: Mapped[int] = mapped_column(primary_key=True)
#     title: Mapped[str]
    
#     # Many-to-many
#     tags: Mapped[list["Tag"]] = relationship(
#         "Tag",
#         secondary=post_tag,           # ← key part
#         back_populates="posts"
#     )

# class Tag(Base):
#     __tablename__ = "tags"
    
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(unique=True)
    
#     posts: Mapped[list["Post"]] = relationship(
#         "Post",
#         secondary=post_tag,
#         back_populates="tags"
#     )