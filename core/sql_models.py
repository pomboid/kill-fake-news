from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, JSON
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

# ─── Sources ─────────────────────────────────────────────────────
class Source(SQLModel, table=True):
    __tablename__ = "source"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # "G1", "UOL", "Folha", etc.
    display_name: str  # Nome para exibição no frontend
    website_url: str  # Homepage da fonte
    status: str = Field(default="online")  # "online" ou "offline"
    last_checked: Optional[datetime] = None
    is_active: bool = Field(default=True)

    # Relacionamentos
    feeds: List["RSSFeed"] = Relationship(back_populates="source")
    articles: List["Article"] = Relationship(back_populates="source")

# ─── RSS Feeds ───────────────────────────────────────────────────
class RSSFeed(SQLModel, table=True):
    __tablename__ = "rss_feed"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="source.id", index=True)

    feed_url: str = Field(unique=True, index=True)  # URL completa do RSS
    feed_type: str = Field(default="rss2")  # "rss2", "rss091", "atom", "sitemap"
    category: Optional[str] = None  # "tecnologia", "esportes", "política", etc.

    is_active: bool = Field(default=True)
    last_fetched: Optional[datetime] = None
    fetch_count: int = Field(default=0)
    error_count: int = Field(default=0)
    last_error: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relacionamentos
    source: Source = Relationship(back_populates="feeds")

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
    
    # Text Analysis
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(768)))
    
    source_id: Optional[int] = Field(default=None, foreign_key="source.id")
    source: Optional[Source] = Relationship(back_populates="articles")
    
    analysis: Optional["Analysis"] = Relationship(back_populates="article")
    # The relationship to the separate Embedding table is removed as the embedding is now directly on the Article model.
    # If a separate Embedding table is still desired for other reasons, the relationship name would need to be changed.

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
# Embedding class removed (using Article.embedding column)

# ─── Verifications (History) ─────────────────────────────────────
class Verification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(index=True)  # From Clerk
    claim: str
    verdict: str  # VERDADEIRO, FALSO, INCONCLUSIVO
    confidence: float
    evidence: List[int] = Field(default=[], sa_column=Column(JSON))  # List of Article IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
