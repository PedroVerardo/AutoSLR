from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.dialects.postgresql import ARRAY
from ..database import Base
from pgvector.sqlalchemy import Vector

class Article(Base):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # user_id = Column(Integer)
    # project_id = Column(Integer)
    title = Column(String(1024), unique=True, nullable=False)
    upload_date = Column(Date)

    segments = relationship("Segment", back_populates="article")

class Segment(Base):
    __tablename__ = "segment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("article.id"))
    segment_title = Column(String(1024))
    segment_title_vector = Column(Vector(384), nullable=True)
    segment_text = Column( Text )

    article = relationship("Article", back_populates="segments")
    chunks = relationship("Chunk", back_populates="segment")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment_id = Column(Integer, ForeignKey("segment.id"))
    chunk_text = Column(Text)
    chunk_vector = Column(Vector(384), nullable=True)

    segment = relationship("Segment", back_populates="chunks")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # user_id = Column(Integer)
    # project_id = Column(Integer)
    article_id = Column(Integer, ForeignKey("article.id"))
    chat_title = Column(String(1024), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)