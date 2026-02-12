from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, JSON
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

# ─── Sources ─────────────────────────────────────────────────────
class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url: str
    type: str = Field(default="rss")  # rss, scraper
    status: str = Field(default="online")
    last_checked: Optional[datetime] = None
    is_active: bool = Field(default=True)

    articles: List["Article"] = Relationship(back_populates="source")

# ─── Articles ────────────────────────────────────────────────────
class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    subtitle: Optional[str] = None
    url: str = Field(unique=True, index=True)
    content: str
    author: str = Field(default="Redação")
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    source_id: Optional[int] = Field(default=None, foreign_key="source.id")
    source: Optional[Source] = Relationship(back_populates="articles")
    
    analysis: Optional["Analysis"] = Relationship(back_populates="article")
    embedding: Optional["Embedding"] = Relationship(back_populates="article")

# ─── Analysis ────────────────────────────────────────────────────
class Analysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="article.id")
    
    is_fake: bool = Field(default=False)
    confidence: float
    reasoning: str
    markers: List[str] = Field(default=[], sa_column=Column(JSON))
    scores: dict = Field(default={}, sa_column=Column(JSON))
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    article: Article = Relationship(back_populates="analysis")

# ─── Embeddings ──────────────────────────────────────────────────
class Embedding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="article.id")
    
    # 768 dimensions for Gemini Embeddings
    vector: List[float] = Field(sa_column=Column(Vector(768)))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    article: Article = Relationship(back_populates="embedding")

# ─── Verifications (History) ─────────────────────────────────────
class Verification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(index=True)  # From Clerk
    claim: str
    verdict: str  # VERDADEIRO, FALSO, INCONCLUSIVO
    confidence: float
    evidence: List[int] = Field(default=[], sa_column=Column(JSON))  # List of Article IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
