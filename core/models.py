from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class NewsArticle(BaseModel):
    title: str = Field(..., alias="titulo")
    subtitle: Optional[str] = Field(None, alias="subtitulo")
    author: str = Field("Redação", alias="autor")
    publish_date: Optional[str] = Field(None, alias="data_publicacao")
    url: HttpUrl
    content: str = Field(..., alias="corpo_do_texto")
    credibility_score: Optional[float] = Field(None)
    status: str = Field("UNCHECKED", alias="status_verificacao")

    class Config:
        populate_by_name = True

class DetectionScores(BaseModel):
    factual_consistency: int = Field(..., ge=0, le=10)
    linguistic_bias: int = Field(..., ge=0, le=10)
    sensationalism: int = Field(..., ge=0, le=10)
    source_credibility: int = Field(..., ge=0, le=10)

class FakeNewsDetection(BaseModel):
    is_fake: bool
    confidence_score: float
    reasoning: str
    detected_markers: List[str]
    scores: DetectionScores
    timestamp: datetime = Field(default_factory=datetime.now)
