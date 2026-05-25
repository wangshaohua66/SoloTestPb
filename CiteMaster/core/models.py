"""Data models for CiteMaster."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.validators import CitationValidator, ValidationError
from utils.logger import get_logger

logger = get_logger()


@dataclass
class CitationEntry:
    """Represents a single citation entry."""

    citation_key: str
    entry_type: str = "misc"
    title: str = ""
    author: str = ""
    year: Optional[int] = None
    journal: Optional[str] = None
    booktitle: Optional[str] = None
    publisher: Optional[str] = None
    school: Optional[str] = None
    institution: Optional[str] = None
    month: Optional[str] = None
    volume: Optional[str] = None
    number: Optional[str] = None
    pages: Optional[str] = None
    chapter: Optional[str] = None
    edition: Optional[str] = None
    series: Optional[str] = None
    address: Optional[str] = None
    editor: Optional[str] = None
    translator: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    issn: Optional[str] = None
    isbn: Optional[str] = None
    keywords: Optional[str] = None
    abstract: Optional[str] = None
    note: Optional[str] = None
    citations: List[str] = field(default_factory=list)
    cited_by: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], validate: bool = True) -> "CitationEntry":
        """Create a CitationEntry from a dictionary."""
        try:
            entry_data = {}
            extra = {}

            field_names = {f.name for f in cls.__dataclass_fields__.values()}

            for key, value in data.items():
                if key in field_names:
                    entry_data[key] = value
                else:
                    extra[key] = value

            if extra:
                entry_data["extra"] = extra

            entry = cls(**entry_data)

            if validate:
                entry.validate()

            logger.debug(f"Created CitationEntry: {entry.citation_key}")
            return entry

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Failed to create CitationEntry from dict", e)
            raise ValidationError(f"Failed to create entry: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        data = asdict(self)
        if data.get("extra"):
            extra = data.pop("extra")
            data.update(extra)
        return data

    def validate(self) -> None:
        """Validate the entry data."""
        data = self.to_dict()
        validator = CitationValidator()
        valid, errors = validator.validate_entry(data)

        if not valid:
            message = "; ".join(errors)
            logger.error(f"Validation failed for {self.citation_key}: {message}")
            raise ValidationError(message)

        self.author = validator.normalize_name(self.author)
        self.updated_at = datetime.now().isoformat()

    def get_authors_list(self) -> List[str]:
        """Split author string into individual author names."""
        if not self.author:
            return []

        authors = []
        parts = self.author.split(" and ")

        for part in parts:
            part = part.strip()
            if part:
                authors.append(part)

        return authors

    def get_first_author_lastname(self) -> str:
        """Get the last name of the first author."""
        authors = self.get_authors_list()
        if not authors:
            return ""

        first_author = authors[0]
        if "," in first_author:
            return first_author.split(",")[0].strip()

        parts = first_author.split()
        return parts[-1] if parts else ""

    def matches_query(self, query: str) -> bool:
        """Check if entry matches a search query (case-insensitive)."""
        if not query:
            return True

        query = query.lower()
        search_fields = [
            self.citation_key, self.title, self.author,
            str(self.year) if self.year else "",
            self.journal or "", self.booktitle or "",
            self.publisher or "", self.keywords or "",
            self.abstract or "", self.doi or "",
            " ".join(self.tags), " ".join(self.citations),
            " ".join(self.cited_by)
        ]

        for field in search_fields:
            if query in str(field).lower():
                return True

        for key, value in self.extra.items():
            if query in str(key).lower() or query in str(value).lower():
                return True

        return False

    def add_citation(self, cited_key: str) -> None:
        """Add a citation reference to another entry."""
        if cited_key and cited_key not in self.citations:
            self.citations.append(cited_key)
            self.updated_at = datetime.now().isoformat()
            logger.debug(f"Added citation from {self.citation_key} to {cited_key}")

    def remove_citation(self, cited_key: str) -> None:
        """Remove a citation reference."""
        if cited_key in self.citations:
            self.citations.remove(cited_key)
            self.updated_at = datetime.now().isoformat()
            logger.debug(f"Removed citation from {self.citation_key} to {cited_key}")

    def add_cited_by(self, citing_key: str) -> None:
        """Add a reference to an entry that cites this one."""
        if citing_key and citing_key not in self.cited_by:
            self.cited_by.append(citing_key)
            self.updated_at = datetime.now().isoformat()
            logger.debug(f"Added cited_by {citing_key} to {self.citation_key}")

    def remove_cited_by(self, citing_key: str) -> None:
        """Remove a cited_by reference."""
        if citing_key in self.cited_by:
            self.cited_by.remove(citing_key)
            self.updated_at = datetime.now().isoformat()
            logger.debug(f"Removed cited_by {citing_key} from {self.citation_key}")

    def add_tag(self, tag: str) -> None:
        """Add a tag to the entry."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
            logger.debug(f"Added tag '{tag}' to {self.citation_key}")

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the entry."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now().isoformat()
            logger.debug(f"Removed tag '{tag}' from {self.citation_key}")


@dataclass
class SearchResult:
    """Represents a search result."""
    entry: CitationEntry
    score: float = 0.0
    matched_fields: List[str] = field(default_factory=list)


@dataclass
class LibraryStats:
    """Statistics for a citation library."""
    total_entries: int = 0
    entries_by_type: Dict[str, int] = field(default_factory=dict)
    entries_by_year: Dict[int, int] = field(default_factory=dict)
    entries_by_author: Dict[str, int] = field(default_factory=dict)
    entries_by_journal: Dict[str, int] = field(default_factory=dict)
    entries_by_tag: Dict[str, int] = field(default_factory=dict)
    total_citations: int = 0
    total_cited_by: int = 0
    date_range: Optional[tuple] = None
