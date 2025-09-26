from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ArxivAuthor(BaseModel):
    name: str = Field(..., description="Author full name")


class ArxivPaper(BaseModel):
    id: str = Field(..., description="arXiv identifier or entry URL")
    title: str
    summary: str
    url: str = Field(..., description="Canonical HTML URL")
    pdf_url: Optional[str] = Field(None, description="Direct PDF URL if available")
    published: datetime
    updated: Optional[datetime] = None
    authors: List[ArxivAuthor] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)

    @field_validator("published", mode="before")
    @classmethod
    def parse_published(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str) and v:
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                # arXiv often uses RFC 3339-like with TZ; try fallback
                return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
        raise ValueError("Invalid published date")

    @field_validator("updated", mode="before")
    @classmethod
    def parse_updated(cls, v):
        if v is None or isinstance(v, datetime):
            return v
        if isinstance(v, str) and v:
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                try:
                    return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    return None
        return None

    @classmethod
    def from_agno(cls, raw: dict) -> "ArxivPaper":
        # Expected keys from agno.tools.arxiv.search_arxiv:
        # id, title, summary, url, pdf_url, published, updated?, authors(list[str] or list[dict]), categories(list[str])
        authors_raw = raw.get("authors") or []
        authors = []
        for a in authors_raw:
            if isinstance(a, dict) and "name" in a:
                authors.append(ArxivAuthor(name=a["name"]))
            elif isinstance(a, str):
                authors.append(ArxivAuthor(name=a))
        return cls(
            id=str(raw.get("id") or raw.get("entry_id") or raw.get("url")),
            title=(raw.get("title") or "").strip(),
            summary=(raw.get("summary") or "").strip(),
            url=str(raw.get("url") or raw.get("id")),
            pdf_url=raw.get("pdf_url"),
            published=raw.get("published", datetime(year=1900, month=1, day=1)),
            updated=raw.get("updated"),
            authors=authors,
            categories=[str(c) for c in (raw.get("categories") or [])],
        )


class ArxivSearchResponse(BaseModel):
    query: str
    total_found: int = 0
    items: List[ArxivPaper] = Field(default_factory=list)
    pdf_urls: List[str | None] = Field(default_factory=list)

    @classmethod
    def from_agno_items(cls, query: str, items: List[dict]) -> "ArxivSearchResponse":
        parsed = [ArxivPaper.from_agno(it) for it in items]
        pdf_urls = [paper.pdf_url for paper in parsed]
        return cls(query=query, total_found=len(parsed), items=parsed, pdf_urls=pdf_urls)
