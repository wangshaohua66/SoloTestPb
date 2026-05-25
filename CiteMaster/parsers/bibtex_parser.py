"""BibTeX parser for CiteMaster with robust error handling."""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

from utils.logger import get_logger
from utils.validators import CitationValidator, BibTeXValidationError
from utils.config import Config
from utils.file_ops import FileManager

logger = get_logger()


@dataclass
class ParseWarning:
    """Represents a warning encountered during parsing."""
    line_number: int
    message: str
    context: str = ""


@dataclass
class ParseError:
    """Represents an error encountered during parsing."""
    line_number: int
    message: str
    context: str = ""


class BibTeXParseError(Exception):
    """Raised when BibTeX parsing fails."""

    def __init__(self, message: str, errors: Optional[List[ParseError]] = None,
                 warnings: Optional[List[ParseWarning]] = None):
        super().__init__(message)
        self.errors = errors or []
        self.warnings = warnings or []


class BibTeXParser:
    """Parses and generates BibTeX files with robust error handling."""

    ENTRY_PATTERN = re.compile(
        r'@(\w+)\s*\{([^,]+),',
        re.IGNORECASE
    )

    FIELD_LINE_PATTERN = re.compile(
        r'^\s*(\w+)\s*=\s*',
        re.IGNORECASE
    )

    COMMENT_PATTERN = re.compile(r'^\s*(%.*|@comment\{.*?\})$', re.DOTALL | re.IGNORECASE)
    PREAMBLE_PATTERN = re.compile(r'@preamble\{(.*?)\}', re.DOTALL | re.IGNORECASE)
    STRING_PATTERN = re.compile(r'@string\{(\w+)\s*=\s*\{(.*?)\}\s*\}', re.DOTALL | re.IGNORECASE)

    def __init__(self, config: Config):
        self.config = config
        self.file_manager = FileManager(config)
        self.validator = CitationValidator()
        self._string_macros: Dict[str, str] = {}

    def _strip_braces(self, text: str) -> str:
        """Remove outer braces from BibTeX field values."""
        if not text:
            return ""
        text = text.strip()
        while len(text) >= 2 and text.startswith('{') and text.endswith('}'):
            inner = text[1:-1]
            balance = 0
            valid = True
            for c in inner:
                if c == '{':
                    balance += 1
                elif c == '}':
                    balance -= 1
                if balance < 0:
                    valid = False
                    break
            if valid and balance == 0:
                text = inner.strip()
            else:
                break
        return text

    def _expand_macros(self, text: str) -> str:
        """Expand @string macros in text."""
        result = text
        for name, value in self._string_macros.items():
            pattern = re.compile(r'\b' + re.escape(name) + r'\b')
            result = pattern.sub(value, result)
        return result

    def _parse_field_value(self, value: str) -> str:
        """Parse and clean a BibTeX field value."""
        if value is None:
            return ""

        value = self._strip_braces(value)
        value = self._expand_macros(value)
        value = self.validator.unescape_latex_special_chars(value)
        value = value.replace('~', ' ')
        value = re.sub(r'\s+', ' ', value).strip()

        return value

    def _extract_entries(self, content: str) -> Tuple[List[str], List[ParseWarning]]:
        """Extract individual BibTeX entries from content."""
        warnings = []
        entries = []
        lines = content.split('\n')

        brace_balance = 0
        entry_start = -1
        current_entry_lines: List[str] = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if not stripped or stripped.startswith('%'):
                continue

            if stripped.startswith('@string{') or stripped.startswith('@STRING{'):
                match = self.STRING_PATTERN.match('\n'.join(lines[i-1:]))
                if match:
                    name, value = match.groups()
                    self._string_macros[name.strip()] = self._parse_field_value(value)
                    continue

            if stripped.startswith('@preamble{') or stripped.startswith('@PREAMBLE{'):
                continue

            if stripped.startswith('@') and not stripped.startswith('@comment'):
                if brace_balance > 0:
                    warnings.append(ParseWarning(
                        line_number=i,
                        message="Possible unclosed entry before new entry starts",
                        context=stripped[:50]
                    ))

                brace_balance = 0
                entry_start = i
                current_entry_lines = [line]

                for c in line:
                    if c == '{':
                        brace_balance += 1
                    elif c == '}':
                        brace_balance -= 1

                if brace_balance == 0 and entry_start > 0:
                    entries.append('\n'.join(current_entry_lines))
                    entry_start = -1
                    current_entry_lines = []
                continue

            if entry_start > 0:
                current_entry_lines.append(line)

                for c in line:
                    if c == '{':
                        brace_balance += 1
                    elif c == '}':
                        brace_balance -= 1

                if brace_balance == 0:
                    entries.append('\n'.join(current_entry_lines))
                    entry_start = -1
                    current_entry_lines = []
                elif brace_balance < 0:
                    warnings.append(ParseWarning(
                        line_number=i,
                        message="Extra closing brace encountered",
                        context=stripped[:50]
                    ))

        if entry_start > 0:
            warnings.append(ParseWarning(
                line_number=len(lines),
                message=f"Unclosed entry starting at line {entry_start}",
                context='\n'.join(current_entry_lines[:3])
            ))

        return entries, warnings

    def _parse_single_entry(self, entry_text: str, line_offset: int = 0) -> Tuple[Optional[Dict[str, Any]], List[ParseError], List[ParseWarning]]:
        """Parse a single BibTeX entry."""
        errors = []
        warnings = []
        entry: Dict[str, Any] = {}

        try:
            entry_text = entry_text.strip()
            lines = entry_text.split('\n')

            if not lines:
                errors.append(ParseError(
                    line_number=line_offset + 1,
                    message="Empty entry",
                    context=""
                ))
                return None, errors, warnings

            first_line = lines[0].strip()
            match = self.ENTRY_PATTERN.match(first_line)

            if not match:
                errors.append(ParseError(
                    line_number=line_offset + 1,
                    message="Invalid BibTeX entry format",
                    context=first_line[:100]
                ))
                return None, errors, warnings

            entry_type = match.group(1).strip().lower()
            citation_key = match.group(2).strip()

            valid, error = self.validator.validate_entry_type(entry_type)
            if not valid:
                errors.append(ParseError(
                    line_number=line_offset + 1,
                    message=error or "Invalid entry type",
                    context=entry_type
                ))

            valid, error = self.validator.validate_citation_key(citation_key)
            if not valid:
                errors.append(ParseError(
                    line_number=line_offset + 1,
                    message=error or "Invalid citation key",
                    context=citation_key
                ))

            entry["entry_type"] = entry_type
            entry["citation_key"] = citation_key

            fields = self._parse_fields(lines[1:], line_offset + 1)

            for field_name, field_value, line_num in fields:
                field_name = field_name.strip().lower()
                field_value = self._parse_field_value(field_value)

                if field_name in entry:
                    warnings.append(ParseWarning(
                        line_number=line_num,
                        message=f"Duplicate field '{field_name}', using last value",
                        context=field_name
                    ))

                entry[field_name] = field_value

            if "year" in entry:
                valid, error, year_int = self.validator.validate_year(entry["year"])
                if not valid:
                    errors.append(ParseError(
                        line_number=line_offset + 1,
                        message=error or "Invalid year",
                        context=str(entry["year"])
                    ))
                else:
                    entry["year"] = year_int

            if "author" in entry:
                valid, error = self.validator.validate_author(entry["author"])
                if not valid:
                    warnings.append(ParseWarning(
                        line_number=line_offset + 1,
                        message=error or "Invalid author format",
                        context=entry["author"][:50]
                    ))

            if errors:
                return None, errors, warnings

            valid, validation_errors = self.validator.validate_entry(entry)
            if not valid:
                for err in validation_errors:
                    errors.append(ParseError(
                        line_number=line_offset + 1,
                        message=err,
                        context=citation_key
                    ))
                return None, errors, warnings

            entry["author"] = self.validator.normalize_name(entry.get("author", ""))

            return entry, errors, warnings

        except Exception as e:
            logger.exception("Unexpected error parsing BibTeX entry", e)
            errors.append(ParseError(
                line_number=line_offset + 1,
                message=f"Unexpected error: {e}",
                context=entry_text[:50]
            ))
            return None, errors, warnings

    def _parse_fields(self, lines: List[str], start_line: int) -> List[Tuple[str, str, int]]:
        """Parse fields from entry lines."""
        fields = []
        current_field_name = None
        current_field_value = []
        current_line_num = start_line
        brace_balance = 0
        in_quotes = False
        field_start_line = start_line

        for i, line in enumerate(lines):
            line_num = start_line + i
            stripped = line.strip()

            if not stripped or stripped.startswith('%'):
                continue

            if stripped == '}':
                break

            field_match = self.FIELD_LINE_PATTERN.match(line)

            if field_match and brace_balance == 0 and not in_quotes:
                if current_field_name is not None:
                    value = ''.join(current_field_value)
                    value = self._clean_field_value(value)
                    fields.append((current_field_name, value, field_start_line))

                current_field_name = field_match.group(1)
                field_start_line = line_num
                current_field_value = []
                rest_of_line = line[field_match.end():]

                for c in rest_of_line:
                    if c == '"':
                        in_quotes = not in_quotes
                    elif c == '{' and not in_quotes:
                        brace_balance += 1
                    elif c == '}' and not in_quotes:
                        brace_balance -= 1
                    current_field_value.append(c)

                if rest_of_line.rstrip().endswith(',') and brace_balance == 0 and not in_quotes:
                    value = ''.join(current_field_value)
                    value = self._clean_field_value(value)
                    fields.append((current_field_name, value, field_start_line))
                    current_field_name = None
                    current_field_value = []
            else:
                if current_field_name is not None:
                    for c in line:
                        if c == '"':
                            in_quotes = not in_quotes
                        elif c == '{' and not in_quotes:
                            brace_balance += 1
                        elif c == '}' and not in_quotes:
                            brace_balance -= 1
                        current_field_value.append(c)
                    current_field_value.append('\n')

                    end_of_entry = False
                    line_check = line.rstrip()
                    if line_check.endswith('}') and brace_balance == 0 and not in_quotes:
                        end_of_entry = True
                    elif line_check.endswith('},') and brace_balance == 0 and not in_quotes:
                        end_of_entry = True

                    if end_of_entry:
                        value = ''.join(current_field_value)
                        value = self._clean_field_value(value)
                        fields.append((current_field_name, value, field_start_line))
                        current_field_name = None
                        current_field_value = []

        if current_field_name is not None:
            value = ''.join(current_field_value)
            value = self._clean_field_value(value)
            fields.append((current_field_name, value, field_start_line))

        return fields

    def _clean_field_value(self, value: str) -> str:
        """Clean a field value by removing trailing commas and whitespace."""
        if not value:
            return ""

        value = value.strip()

        if value.endswith(','):
            value = value[:-1].strip()

        if value.endswith('}') and not value.startswith('{'):
            open_count = value.count('{')
            close_count = value.count('}')
            while close_count > open_count and value.endswith('}'):
                value = value[:-1].rstrip()
                close_count -= 1

        return value.strip()

    def parse(self, bibtex_content: str) -> Tuple[List[Dict[str, Any]], List[ParseError], List[ParseWarning]]:
        """Parse BibTeX content and return list of entries."""
        self._string_macros.clear()
        all_entries: List[Dict[str, Any]] = []
        all_errors: List[ParseError] = []
        all_warnings: List[ParseWarning] = []

        try:
            entries_text, parse_warnings = self._extract_entries(bibtex_content)
            all_warnings.extend(parse_warnings)

            for i, entry_text in enumerate(entries_text):
                line_offset = i * 10
                entry, errors, warnings = self._parse_single_entry(entry_text, line_offset)

                all_errors.extend(errors)
                all_warnings.extend(warnings)

                if entry is not None:
                    all_entries.append(entry)

            logger.info(f"Parsed {len(all_entries)} entries from BibTeX with {len(all_errors)} errors and {len(all_warnings)} warnings")

            return all_entries, all_errors, all_warnings

        except Exception as e:
            logger.exception("Fatal error parsing BibTeX", e)
            raise BibTeXParseError(f"Fatal error parsing BibTeX: {e}")

    def parse_file(self, file_path: Path) -> Tuple[List[Dict[str, Any]], List[ParseError], List[ParseWarning]]:
        """Parse a BibTeX file."""
        file_path = Path(file_path)

        try:
            content = self.file_manager.read_text(file_path)
            return self.parse(content)

        except Exception as e:
            logger.exception(f"Failed to parse BibTeX file {file_path}", e)
            raise BibTeXParseError(f"Failed to parse {file_path}: {e}")

    def _format_field(self, name: str, value: Any) -> str:
        """Format a single field for BibTeX output."""
        if value is None or value == "":
            return ""

        value_str = str(value)
        value_str = self.validator.escape_latex_special_chars(value_str)

        return f"  {name} = {{{value_str}}}"

    def generate_entry(self, data: Dict[str, Any]) -> str:
        """Generate a BibTeX entry string from data."""
        try:
            entry_type = data.get("entry_type", "misc").lower()
            citation_key = data.get("citation_key", "")

            if not citation_key:
                citation_key = self.validator.generate_citation_key(
                    data.get("author", ""),
                    data.get("year", ""),
                    data.get("title", "")
                )

            valid, error = self.validator.validate_citation_key(citation_key)
            if not valid:
                raise BibTeXValidationError(error or "Invalid citation key")

            fields = []
            field_order = [
                "author", "title", "journal", "booktitle", "publisher",
                "school", "institution", "year", "month", "volume",
                "number", "pages", "chapter", "edition", "series",
                "address", "editor", "translator", "doi", "url",
                "issn", "isbn", "keywords", "abstract", "note"
            ]

            for field in field_order:
                if field in data and data[field]:
                    fields.append(self._format_field(field, data[field]))

            for key, value in data.items():
                if key not in ["entry_type", "citation_key"] + field_order and value:
                    fields.append(self._format_field(key, value))

            fields_str = ",\n".join(fields)
            entry = f"@{entry_type}{{{citation_key},\n{fields_str}\n}}\n"

            return entry

        except Exception as e:
            logger.exception("Failed to generate BibTeX entry", e)
            raise BibTeXParseError(f"Failed to generate BibTeX entry: {e}")

    def generate_bibtex(self, entries: List[Dict[str, Any]]) -> str:
        """Generate complete BibTeX content from list of entries."""
        try:
            lines = ["% BibTeX file generated by CiteMaster", "% " + "=" * 50, ""]

            for entry in entries:
                entry_str = self.generate_entry(entry)
                lines.append(entry_str)
                lines.append("")

            content = "\n".join(lines)
            logger.info(f"Generated BibTeX with {len(entries)} entries")
            return content

        except Exception as e:
            logger.exception("Failed to generate BibTeX", e)
            raise BibTeXParseError(f"Failed to generate BibTeX: {e}")

    def write_file(self, file_path: Path, entries: List[Dict[str, Any]]) -> None:
        """Write entries to a BibTeX file."""
        try:
            content = self.generate_bibtex(entries)
            self.file_manager.write_text(file_path, content)
            logger.info(f"Wrote {len(entries)} entries to {file_path}")
        except Exception as e:
            logger.exception(f"Failed to write BibTeX file {file_path}", e)
            raise BibTeXParseError(f"Failed to write {file_path}: {e}")

    def import_entries(self, source_path: Path, validate: bool = True) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        """Import entries from a BibTeX file with validation."""
        entries, errors, warnings = self.parse_file(source_path)

        error_messages = [f"Line {e.line_number}: {e.message}" for e in errors]
        warning_messages = [f"Line {w.line_number}: {w.message}" for w in warnings]

        if validate and errors:
            logger.warning(f"Found {len(errors)} errors during import")
            raise BibTeXValidationError(
                f"Import failed with {len(errors)} errors: " + "; ".join(error_messages[:5])
            )

        return entries, error_messages, warning_messages
