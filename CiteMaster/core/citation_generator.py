"""Citation format generator supporting APA, MLA, Chicago, IEEE formats."""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

from utils.logger import get_logger
from utils.config import Config
from core.models import CitationEntry

logger = get_logger()


class CitationTemplateError(Exception):
    """Raised when there is an error with citation templates."""
    pass


class CitationGenerator:
    """Generates citations in various academic formats."""

    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"

    DEFAULT_TEMPLATES = {
        "apa": {
            "article": "{author_last}, {author_initial}. ({year}). {title}. {journal}, {volume}({number}), {pages}. {doi}",
            "book": "{author_last}, {author_initial}. ({year}). {title}. {publisher}.",
            "incollection": "{author_last}, {author_initial}. ({year}). {title}. In {editor} (Ed.), {booktitle} (pp. {pages}). {publisher}.",
            "inproceedings": "{author_last}, {author_initial}. ({year}). {title}. In {booktitle} (pp. {pages}).",
            "phdthesis": "{author_last}, {author_initial}. ({year}). {title} [Doctoral dissertation, {school}].",
            "misc": "{author_last}, {author_initial}. ({year}). {title}. {url}"
        },
        "mla": {
            "article": "{author}. \"{title}.\" {journal}, vol. {volume}, no. {number}, {year}, pp. {pages}.",
            "book": "{author}. {title}. {publisher}, {year}.",
            "incollection": "{author}. \"{title}.\" {booktitle}, edited by {editor}, {publisher}, {year}, pp. {pages}.",
            "inproceedings": "{author}. \"{title}.\" {booktitle}, {year}, pp. {pages}.",
            "phdthesis": "{author}. \"{title}.\" {school}, {year}.",
            "misc": "{author}. {title}. {year}. {url}"
        },
        "chicago": {
            "article": "{author}. \"{title}.\" {journal} {volume}, no. {number} ({year}): {pages}.",
            "book": "{author}. {title}. {publisher}, {year}.",
            "incollection": "{author}. \"{title}.\" In {booktitle}, edited by {editor}, {pages}. {publisher}, {year}.",
            "inproceedings": "{author}. \"{title}.\" Paper presented at {booktitle}, {year}.",
            "phdthesis": "{author}. \"{title}.\" PhD diss., {school}, {year}.",
            "misc": "{author}. {title}. {year}. {url}"
        },
        "ieee": {
            "article": "[{index}] {author}, \"{title},\" {journal}, vol. {volume}, no. {number}, pp. {pages}, {year}.",
            "book": "[{index}] {author}, {title}. {publisher}, {year}.",
            "incollection": "[{index}] {author}, \"{title},\" in {booktitle}, {editor}, Ed. {publisher}, {year}, pp. {pages}.",
            "inproceedings": "[{index}] {author}, \"{title},\" in {booktitle}, {year}, pp. {pages}.",
            "phdthesis": "[{index}] {author}, \"{title},\" Ph.D. dissertation, {school}, {year}.",
            "misc": "[{index}] {author}, {title}. {year}. {url}"
        }
    }

    def __init__(self, config: Config):
        self.config = config
        self.templates_dir = Path(config.get("templates_dir", "templates"))
        self._templates: Dict[str, Dict[str, str]] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load templates from files or use defaults."""
        try:
            self._templates = dict(self.DEFAULT_TEMPLATES)

            if self.templates_dir.exists():
                for format_file in self.templates_dir.glob("*.yaml"):
                    format_name = format_file.stem.lower()
                    try:
                        with open(format_file, "r", encoding=self.config.output_encoding) as f:
                            custom_templates = yaml.safe_load(f)
                            if isinstance(custom_templates, dict):
                                self._templates[format_name] = {
                                    **self._templates.get(format_name, {}),
                                    **custom_templates
                                }
                                logger.info(f"Loaded custom templates for {format_name}")
                    except Exception as e:
                        logger.warning(f"Failed to load template {format_file}: {e}")
            else:
                logger.info("No custom templates directory found, using defaults")

        except Exception as e:
            logger.exception("Failed to load citation templates", e)
            raise CitationTemplateError(f"Failed to load templates: {e}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported citation formats."""
        return sorted(self._templates.keys())

    def _format_author_apa(self, author: str) -> str:
        """Format author names for APA style."""
        if not author:
            return ""

        authors = []
        parts = author.split(" and ")

        for part in parts[:3]:
            part = part.strip()
            if "," in part:
                last, first = part.split(",", 1)
                last = last.strip()
                first = first.strip()
                initials = " ".join([n[0].upper() + "." for n in first.split() if n])
                authors.append(f"{last}, {initials}")
            else:
                name_parts = part.split()
                if len(name_parts) >= 2:
                    last = name_parts[-1]
                    first = " ".join(name_parts[:-1])
                    initials = " ".join([n[0].upper() + "." for n in first.split() if n])
                    authors.append(f"{last}, {initials}")
                else:
                    authors.append(part)

        if len(parts) > 3:
            authors.append("et al.")

        return ", ".join(authors)

    def _format_author_mla(self, author: str) -> str:
        """Format author names for MLA style."""
        if not author:
            return ""

        parts = author.split(" and ")
        if len(parts) == 1:
            part = parts[0].strip()
            if "," not in part:
                name_parts = part.split()
                if len(name_parts) >= 2:
                    last = name_parts[-1]
                    first = " ".join(name_parts[:-1])
                    return f"{last}, {first}"
            return part

        authors = []
        for i, part in enumerate(parts):
            part = part.strip()
            if i == 0:
                if "," not in part:
                    name_parts = part.split()
                    if len(name_parts) >= 2:
                        last = name_parts[-1]
                        first = " ".join(name_parts[:-1])
                        authors.append(f"{last}, {first}")
                    else:
                        authors.append(part)
                else:
                    authors.append(part)
            else:
                if "," in part:
                    last, first = part.split(",", 1)
                    authors.append(f"{first.strip()} {last.strip()}")
                else:
                    authors.append(part)

        if len(authors) == 2:
            return " and ".join(authors)
        elif len(authors) > 2:
            return authors[0] + ", et al."

        return ", ".join(authors)

    def _format_author_chicago(self, author: str) -> str:
        """Format author names for Chicago style."""
        return self._format_author_mla(author)

    def _format_author_ieee(self, author: str) -> str:
        """Format author names for IEEE style."""
        if not author:
            return ""

        authors = []
        parts = author.split(" and ")

        for part in parts:
            part = part.strip()
            if "," in part:
                last, first = part.split(",", 1)
                last = last.strip()
                first = first.strip()
                initials = " ".join([n[0].upper() + "." for n in first.split() if n])
                authors.append(f"{initials} {last}")
            else:
                name_parts = part.split()
                if len(name_parts) >= 2:
                    last = name_parts[-1]
                    first = " ".join(name_parts[:-1])
                    initials = " ".join([n[0].upper() + "." for n in first.split() if n])
                    authors.append(f"{initials} {last}")
                else:
                    authors.append(part)

        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return " and ".join(authors)
        else:
            return ", ".join(authors[:-1]) + ", and " + authors[-1]

    def _get_template(self, format_name: str, entry_type: str) -> str:
        """Get the appropriate template for the format and entry type."""
        format_name = format_name.lower()
        entry_type = entry_type.lower()

        if format_name not in self._templates:
            raise CitationTemplateError(
                f"Unsupported citation format: {format_name}. "
                f"Supported formats: {', '.join(self.get_supported_formats())}"
            )

        format_templates = self._templates[format_name]
        template = format_templates.get(entry_type) or format_templates.get("misc")

        if not template:
            raise CitationTemplateError(
                f"No template found for format '{format_name}' and entry type '{entry_type}'"
            )

        return template

    def _build_context(self, entry: CitationEntry, format_name: str, index: int = 0) -> Dict[str, str]:
        """Build context dictionary for template rendering."""
        ctx = {
            "citation_key": entry.citation_key,
            "title": entry.title,
            "year": str(entry.year) if entry.year else "n.d.",
            "journal": entry.journal or "",
            "booktitle": entry.booktitle or "",
            "publisher": entry.publisher or "",
            "school": entry.school or "",
            "institution": entry.institution or "",
            "volume": entry.volume or "",
            "number": entry.number or "",
            "pages": entry.pages or "",
            "chapter": entry.chapter or "",
            "edition": entry.edition or "",
            "address": entry.address or "",
            "editor": entry.editor or "",
            "translator": entry.translator or "",
            "doi": entry.doi or "",
            "url": entry.url or "",
            "issn": entry.issn or "",
            "isbn": entry.isbn or "",
            "note": entry.note or "",
            "month": entry.month or "",
            "index": str(index),
        }

        format_name = format_name.lower()
        if format_name == "apa":
            ctx["author"] = self._format_author_apa(entry.author)
            ctx["author_last"] = entry.get_first_author_lastname()
            first_author = entry.get_authors_list()[0] if entry.get_authors_list() else ""
            if "," in first_author:
                _, first = first_author.split(",", 1)
                ctx["author_initial"] = " ".join([n[0].upper() + "." for n in first.split() if n])
            else:
                name_parts = first_author.split()
                if len(name_parts) >= 2:
                    first = " ".join(name_parts[:-1])
                    ctx["author_initial"] = " ".join([n[0].upper() + "." for n in first.split() if n])
                else:
                    ctx["author_initial"] = ""
        elif format_name == "mla":
            ctx["author"] = self._format_author_mla(entry.author)
        elif format_name == "chicago":
            ctx["author"] = self._format_author_chicago(entry.author)
        elif format_name == "ieee":
            ctx["author"] = self._format_author_ieee(entry.author)
        else:
            ctx["author"] = entry.author

        return ctx

    def generate(self, entry: CitationEntry, format_name: Optional[str] = None, index: int = 0) -> str:
        """Generate a citation in the specified format."""
        try:
            format_name = format_name or self.config.default_citation_format
            format_name = format_name.lower()

            template = self._get_template(format_name, entry.entry_type)
            context = self._build_context(entry, format_name, index)

            result = template

            for key, value in context.items():
                placeholder = "{" + key + "}"
                if placeholder in result:
                    result = result.replace(placeholder, value)

            result = result.replace("()", "").replace("  ", " ")
            result = result.replace(" .", ".").replace(" ,", ",")
            result = result.strip(" ,.:;-")

            while "  " in result:
                result = result.replace("  ", " ")

            if not result.endswith("."):
                result += "."

            logger.debug(f"Generated {format_name} citation for {entry.citation_key}")
            return result

        except CitationTemplateError:
            raise
        except Exception as e:
            logger.exception(f"Failed to generate {format_name} citation", e)
            raise CitationTemplateError(f"Failed to generate citation: {e}")

    def generate_bibliography(self, entries: List[CitationEntry], format_name: Optional[str] = None) -> List[str]:
        """Generate a complete bibliography for a list of entries."""
        format_name = format_name or self.config.default_citation_format
        citations = []

        for i, entry in enumerate(entries, 1):
            try:
                citation = self.generate(entry, format_name, i)
                citations.append(citation)
            except Exception as e:
                logger.warning(f"Skipping entry {entry.citation_key}: {e}")
                citations.append(f"[{entry.citation_key}] Error: {e}")

        logger.info(f"Generated bibliography with {len(citations)} entries in {format_name} format")
        return citations

    def generate_inline_citation(self, entry: CitationEntry, format_name: Optional[str] = None) -> str:
        """Generate an inline/parenthetical citation."""
        format_name = format_name or self.config.default_citation_format
        format_name = format_name.lower()

        author = entry.get_first_author_lastname()
        year = str(entry.year) if entry.year else "n.d."

        try:
            if format_name == "apa":
                return f"({author}, {year})"
            elif format_name == "mla":
                return f"({author} {entry.pages or ''})".strip()
            elif format_name == "chicago":
                return f"({author} {year}, {entry.pages or ''})".strip()
            elif format_name == "ieee":
                return "[?]"
            else:
                return f"({author}, {year})"
        except Exception as e:
            logger.exception("Failed to generate inline citation", e)
            return f"({entry.citation_key})"

    def generate_all_formats(self, entry: CitationEntry) -> Dict[str, str]:
        """Generate citations in all supported formats."""
        results = {}
        for fmt in self.get_supported_formats():
            try:
                results[fmt] = self.generate(entry, fmt)
            except Exception as e:
                results[fmt] = f"Error: {e}"
        return results
