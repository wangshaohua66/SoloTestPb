"""Data validation utilities for CiteMaster."""

import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from utils.logger import get_logger

logger = get_logger()


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


class BibTeXValidationError(ValidationError):
    """Raised when BibTeX validation fails."""
    pass


class CitationValidator:
    """Validates citation data and BibTeX entries."""

    BIBTEX_ENTRY_TYPES = {
        "article", "book", "booklet", "conference", "inbook",
        "incollection", "inproceedings", "manual", "mastersthesis",
        "misc", "phdthesis", "proceedings", "techreport", "unpublished"
    }

    REQUIRED_FIELDS = {
        "article": ["author", "title", "journal", "year"],
        "book": ["author", "title", "publisher", "year"],
        "booklet": ["title"],
        "conference": ["author", "title", "booktitle", "year"],
        "inbook": ["author", "title", "chapter", "pages", "publisher", "year"],
        "incollection": ["author", "title", "booktitle", "publisher", "year"],
        "inproceedings": ["author", "title", "booktitle", "year"],
        "manual": ["title"],
        "mastersthesis": ["author", "title", "school", "year"],
        "misc": [],
        "phdthesis": ["author", "title", "school", "year"],
        "proceedings": ["title", "year"],
        "techreport": ["author", "title", "institution", "year"],
        "unpublished": ["author", "title", "note"]
    }

    NAME_PATTERN = re.compile(r'^[\w\s\-\',.]{1,200}$', re.UNICODE)
    YEAR_PATTERN = re.compile(r'^\d{3,4}$')
    KEY_PATTERN = re.compile(r'^[\w\-:]+$')

    LATEX_SPECIAL_CHARS = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}'
    }

    @classmethod
    def validate_author(cls, author: str) -> Tuple[bool, Optional[str]]:
        """Validate and normalize author name format."""
        if not author or not isinstance(author, str):
            return False, "Author name must be a non-empty string"

        author = author.strip()
        if len(author) < 2:
            return False, "Author name too short"

        if not cls.NAME_PATTERN.match(author):
            return False, f"Author name contains invalid characters: {author}"

        return True, None

    @classmethod
    def validate_year(cls, year: Any) -> Tuple[bool, Optional[str], Optional[int]]:
        """Validate year is a valid integer."""
        if year is None:
            return False, "Year is required", None

        if isinstance(year, int):
            year_str = str(year)
        elif isinstance(year, str):
            year_str = year.strip()
            if not year_str:
                return False, "Year cannot be empty", None
        else:
            return False, f"Invalid year type: {type(year)}", None

        if not cls.YEAR_PATTERN.match(year_str):
            return False, f"Invalid year format: {year_str}", None

        year_int = int(year_str)
        current_year = datetime.now().year
        if year_int < 1000 or year_int > current_year + 5:
            return False, f"Year {year_int} is out of reasonable range (1000-{current_year + 5})", None

        return True, None, year_int

    @classmethod
    def validate_entry_type(cls, entry_type: str) -> Tuple[bool, Optional[str]]:
        """Validate BibTeX entry type."""
        if not entry_type:
            return False, "Entry type is required"

        entry_type = entry_type.strip().lower()
        if entry_type not in cls.BIBTEX_ENTRY_TYPES:
            return False, f"Unknown BibTeX entry type: {entry_type}. Valid types: {sorted(cls.BIBTEX_ENTRY_TYPES)}"

        return True, None

    @classmethod
    def validate_citation_key(cls, key: str) -> Tuple[bool, Optional[str]]:
        """Validate BibTeX citation key."""
        if not key or not isinstance(key, str):
            return False, "Citation key must be a non-empty string"

        key = key.strip()
        if not key:
            return False, "Citation key cannot be empty"

        if not cls.KEY_PATTERN.match(key):
            return False, f"Invalid citation key: {key}. Use only letters, numbers, hyphens, underscores, and colons."

        return True, None

    @classmethod
    def validate_required_fields(cls, entry_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate that required fields for the entry type are present."""
        entry_type = entry_type.strip().lower()
        required = cls.REQUIRED_FIELDS.get(entry_type, ["author", "title", "year"])

        missing = []
        for field in required:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)

        return (len(missing) == 0), missing

    @classmethod
    def escape_latex_special_chars(cls, text: str) -> str:
        """Escape special LaTeX characters in text."""
        if not isinstance(text, str):
            return text

        result = text
        for char, replacement in cls.LATEX_SPECIAL_CHARS.items():
            result = result.replace(char, replacement)

        return result

    @classmethod
    def unescape_latex_special_chars(cls, text: str) -> str:
        """Unescape LaTeX special characters in text."""
        if not isinstance(text, str):
            return text

        result = text
        for char, replacement in sorted(cls.LATEX_SPECIAL_CHARS.items(), key=lambda x: len(x[1]), reverse=True):
            result = result.replace(replacement, char)

        return result

    @classmethod
    def validate_entry(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a complete citation entry."""
        errors = []

        entry_type = data.get("entry_type", "misc")
        valid, error = cls.validate_entry_type(entry_type)
        if not valid:
            errors.append(error)

        key = data.get("citation_key", "")
        valid, error = cls.validate_citation_key(key)
        if not valid:
            errors.append(error)

        author = data.get("author", "")
        valid, error = cls.validate_author(author)
        if not valid:
            errors.append(error)

        year = data.get("year")
        valid, error, year_int = cls.validate_year(year)
        if not valid:
            errors.append(error)
        else:
            data["year"] = year_int

        valid, missing = cls.validate_required_fields(entry_type, data)
        if not valid:
            errors.append(f"Missing required fields: {', '.join(missing)}")

        title = data.get("title", "")
        if not title or not isinstance(title, str) or not title.strip():
            errors.append("Title is required")

        return (len(errors) == 0), errors

    @classmethod
    def normalize_name(cls, name: str) -> str:
        """Normalize author name format."""
        if not name:
            return ""

        name = name.strip()

        if "," in name:
            return name

        parts = name.split()
        if len(parts) >= 2:
            last = parts[-1]
            first = " ".join(parts[:-1])
            return f"{last}, {first}"

        return name

    @classmethod
    def generate_citation_key(cls, author: str, year: Any, title: str) -> str:
        """Generate a citation key from author, year, and title."""
        author = cls.normalize_name(author)

        last_name = author.split(",")[0].strip() if "," in author else author.split()[-1] if author.split() else "unknown"
        last_name = re.sub(r'[^a-zA-Z0-9]', '', last_name).lower()

        year_str = str(year) if year else "xxxx"

        first_word = ""
        if title:
            words = re.findall(r'[\w]+', title)
            stopwords = {'a', 'an', 'the', 'of', 'in', 'on', 'for', 'and', 'or', 'to'}
            for word in words:
                if word.lower() not in stopwords:
                    first_word = word.lower()
                    break

        key_parts = [p for p in [last_name, year_str, first_word] if p]
        key = "_".join(key_parts)

        key = re.sub(r'[^a-zA-Z0-9_:-]', '', key)

        return key or "unknown_entry"
