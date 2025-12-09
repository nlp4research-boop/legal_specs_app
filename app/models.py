from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    name_ar = Column(String)
    name_en = Column(String)

    nodes = relationship("Node", back_populates="category")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    spec_code = Column(String, index=True)
    spec_id = Column(String, unique=True, nullable=True)
    title = Column(String)
    path = Column(String)

    category = relationship("Category", back_populates="nodes")
    versions = relationship(
        "ContentVersion",
        back_populates="node",
        order_by="ContentVersion.version.desc()",
    )


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), index=True)
    version = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    content_json = Column(Text)

    node = relationship("Node", back_populates="versions")
