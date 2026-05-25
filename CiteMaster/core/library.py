"""Citation library management for CiteMaster."""

from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict

from utils.logger import get_logger
from utils.config import Config
from utils.file_ops import FileManager, FileOperationError
from utils.validators import CitationValidator, ValidationError
from parsers.bibtex_parser import BibTeXParser
from core.models import CitationEntry, LibraryStats, SearchResult

logger = get_logger()


class LibraryError(Exception):
    """Raised when library operations fail."""
    pass


class CitationLibrary:
    """Manages a collection of citation entries."""

    def __init__(self, config: Config):
        self.config = config
        self.file_manager = FileManager(config)
        self.parser = BibTeXParser(config)
        self.validator = CitationValidator()
        self._entries: Dict[str, CitationEntry] = {}
        self._load()

    def _load(self) -> None:
        """Load library from JSON file."""
        try:
            lib_path = self.config.library_path
            if lib_path.exists():
                data = self.file_manager.read_json(lib_path)
                entries_data = data.get("entries", {})

                for key, entry_data in entries_data.items():
                    try:
                        entry = CitationEntry.from_dict(entry_data, validate=False)
                        self._entries[key] = entry
                    except Exception as e:
                        logger.warning(f"Skipping invalid entry {key}: {e}")

                logger.info(f"Loaded {len(self._entries)} entries from {lib_path}")
            else:
                logger.info(f"No existing library found at {lib_path}, starting empty")
                self._entries = {}

        except FileOperationError as e:
            logger.error(f"Failed to load library: {e}")
            self._entries = {}
        except Exception as e:
            logger.exception("Unexpected error loading library", e)
            self._entries = {}

    def save(self, backup: bool = True) -> None:
        """Save library to JSON file."""
        try:
            lib_path = self.config.library_path

            if backup and lib_path.exists():
                self.file_manager.backup_file(lib_path)

            data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": list(self._entries.values())[0].created_at if self._entries else None,
                    "updated_at": max([e.updated_at for e in self._entries.values()]) if self._entries else None,
                    "total_entries": len(self._entries)
                },
                "entries": {key: entry.to_dict() for key, entry in self._entries.items()}
            }

            self.file_manager.write_json(lib_path, data)
            logger.info(f"Saved {len(self._entries)} entries to {lib_path}")

        except Exception as e:
            logger.exception("Failed to save library", e)
            raise LibraryError(f"Failed to save library: {e}")

    def export_bibtex(self, output_path: Optional[Path] = None) -> Path:
        """Export library to BibTeX file."""
        try:
            output_path = Path(output_path) if output_path else self.config.bibtex_path
            entries = [entry.to_dict() for entry in self._entries.values()]
            self.parser.write_file(output_path, entries)
            logger.info(f"Exported {len(entries)} entries to {output_path}")
            return output_path
        except Exception as e:
            logger.exception("Failed to export BibTeX", e)
            raise LibraryError(f"Failed to export BibTeX: {e}")

    def import_bibtex(self, input_path: Path, validate: bool = True, merge: bool = True) -> tuple:
        """Import entries from a BibTeX file."""
        try:
            entries, errors, warnings = self.parser.import_entries(input_path, validate=False)

            imported = 0
            skipped = 0
            import_errors = list(errors)

            for entry_data in entries:
                try:
                    key = entry_data.get("citation_key", "")

                    if validate:
                        valid, validation_errors = self.validator.validate_entry(entry_data)
                        if not valid:
                            import_errors.extend([f"{key}: {err}" for err in validation_errors])
                            skipped += 1
                            continue

                    entry = CitationEntry.from_dict(entry_data, validate=validate)

                    if key in self._entries and not merge:
                        skipped += 1
                        continue

                    if key in self._entries and merge:
                        existing = self._entries[key]
                        entry.created_at = existing.created_at

                    self._entries[key] = entry
                    imported += 1

                except ValidationError as e:
                    import_errors.append(str(e))
                    skipped += 1
                except Exception as e:
                    logger.exception(f"Failed to import entry", e)
                    import_errors.append(str(e))
                    skipped += 1

            if imported > 0:
                self.save()

            logger.info(f"Import complete: {imported} imported, {skipped} skipped, {len(import_errors)} errors")
            return imported, skipped, import_errors, warnings

        except Exception as e:
            logger.exception("Failed to import BibTeX", e)
            raise LibraryError(f"Failed to import BibTeX: {e}")

    def add_entry(self, entry_data: Dict[str, Any], validate: bool = True) -> CitationEntry:
        """Add a new entry to the library."""
        try:
            if not entry_data.get("citation_key"):
                entry_data["citation_key"] = self.validator.generate_citation_key(
                    entry_data.get("author", ""),
                    entry_data.get("year", ""),
                    entry_data.get("title", "")
                )

            key = entry_data["citation_key"]

            if key in self._entries:
                raise LibraryError(f"Entry with key '{key}' already exists")

            entry = CitationEntry.from_dict(entry_data, validate=validate)
            self._entries[key] = entry
            self.save()

            logger.info(f"Added entry: {key}")
            return entry

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Failed to add entry", e)
            raise LibraryError(f"Failed to add entry: {e}")

    def update_entry(self, key: str, updates: Dict[str, Any], validate: bool = True) -> CitationEntry:
        """Update an existing entry."""
        try:
            if key not in self._entries:
                raise LibraryError(f"Entry '{key}' not found")

            existing = self._entries[key]
            existing_dict = existing.to_dict()

            for field, value in updates.items():
                existing_dict[field] = value

            if "citation_key" in updates and updates["citation_key"] != key:
                new_key = updates["citation_key"]
                if new_key in self._entries:
                    raise LibraryError(f"Entry with key '{new_key}' already exists")
                del self._entries[key]
                existing_dict["citation_key"] = new_key
                key = new_key

            updated = CitationEntry.from_dict(existing_dict, validate=validate)
            self._entries[key] = updated
            self.save()

            logger.info(f"Updated entry: {key}")
            return updated

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Failed to update entry", e)
            raise LibraryError(f"Failed to update entry: {e}")

    def delete_entry(self, key: str) -> None:
        """Delete an entry from the library."""
        try:
            if key not in self._entries:
                raise LibraryError(f"Entry '{key}' not found")

            del self._entries[key]

            for entry in self._entries.values():
                entry.remove_citation(key)
                entry.remove_cited_by(key)

            self.save()
            logger.info(f"Deleted entry: {key}")

        except Exception as e:
            logger.exception("Failed to delete entry", e)
            raise LibraryError(f"Failed to delete entry: {e}")

    def get_entry(self, key: str) -> Optional[CitationEntry]:
        """Get an entry by key."""
        return self._entries.get(key)

    def get_all_entries(self) -> List[CitationEntry]:
        """Get all entries sorted by citation key."""
        return sorted(self._entries.values(), key=lambda e: e.citation_key.lower())

    def search(self, query: str, fields: Optional[List[str]] = None) -> List[SearchResult]:
        """Search entries matching a query."""
        if not query:
            return [SearchResult(entry=e, score=1.0) for e in self.get_all_entries()]

        query_lower = query.lower()
        results = []

        for entry in self._entries.values():
            score = 0.0
            matched = []

            search_targets = {
                "citation_key": entry.citation_key,
                "title": entry.title,
                "author": entry.author,
                "year": str(entry.year) if entry.year else "",
                "journal": entry.journal or "",
                "booktitle": entry.booktitle or "",
                "publisher": entry.publisher or "",
                "keywords": entry.keywords or "",
                "abstract": entry.abstract or "",
                "tags": " ".join(entry.tags),
            }

            if fields:
                search_targets = {k: v for k, v in search_targets.items() if k in fields}

            for field, value in search_targets.items():
                if query_lower in str(value).lower():
                    score += 1.0
                    matched.append(field)
                    if field == "citation_key":
                        score += 2.0
                    if field == "title":
                        score += 1.5

            if entry.matches_query(query):
                score += 0.5

            if score > 0:
                results.append(SearchResult(entry=entry, score=score, matched_fields=matched))

        results.sort(key=lambda r: r.score, reverse=True)
        logger.info(f"Search for '{query}' returned {len(results)} results")
        return results

    def filter_by_author(self, author: str) -> List[CitationEntry]:
        """Filter entries by author."""
        author_lower = author.lower()
        return [
            entry for entry in self._entries.values()
            if author_lower in entry.author.lower()
        ]

    def filter_by_year(self, year: int) -> List[CitationEntry]:
        """Filter entries by year."""
        return [
            entry for entry in self._entries.values()
            if entry.year == year
        ]

    def filter_by_year_range(self, start: int, end: int) -> List[CitationEntry]:
        """Filter entries by year range."""
        return [
            entry for entry in self._entries.values()
            if entry.year and start <= entry.year <= end
        ]

    def filter_by_journal(self, journal: str) -> List[CitationEntry]:
        """Filter entries by journal."""
        journal_lower = journal.lower()
        return [
            entry for entry in self._entries.values()
            if entry.journal and journal_lower in entry.journal.lower()
        ]

    def filter_by_tag(self, tag: str) -> List[CitationEntry]:
        """Filter entries by tag."""
        tag_lower = tag.lower()
        return [
            entry for entry in self._entries.values()
            if tag_lower in [t.lower() for t in entry.tags]
        ]

    def filter_by_type(self, entry_type: str) -> List[CitationEntry]:
        """Filter entries by type."""
        entry_type_lower = entry_type.lower()
        return [
            entry for entry in self._entries.values()
            if entry.entry_type.lower() == entry_type_lower
        ]

    def group_by_author(self) -> Dict[str, List[CitationEntry]]:
        """Group entries by author."""
        groups = defaultdict(list)
        for entry in self._entries.values():
            authors = entry.get_authors_list()
            for author in authors:
                author_normalized = author.strip()
                groups[author_normalized].append(entry)
        return dict(groups)

    def group_by_year(self) -> Dict[int, List[CitationEntry]]:
        """Group entries by year."""
        groups = defaultdict(list)
        for entry in self._entries.values():
            if entry.year:
                groups[entry.year].append(entry)
        return dict(sorted(groups.items()))

    def group_by_journal(self) -> Dict[str, List[CitationEntry]]:
        """Group entries by journal."""
        groups = defaultdict(list)
        for entry in self._entries.values():
            journal = entry.journal or "Unknown"
            groups[journal].append(entry)
        return dict(groups)

    def group_by_tag(self) -> Dict[str, List[CitationEntry]]:
        """Group entries by tag."""
        groups = defaultdict(list)
        for entry in self._entries.values():
            for tag in entry.tags:
                groups[tag].append(entry)
        return dict(groups)

    def add_citation_relation(self, from_key: str, to_key: str) -> None:
        """Add a citation relation between two entries."""
        if from_key not in self._entries:
            raise LibraryError(f"Source entry '{from_key}' not found")
        if to_key not in self._entries:
            raise LibraryError(f"Target entry '{to_key}' not found")

        self._entries[from_key].add_citation(to_key)
        self._entries[to_key].add_cited_by(from_key)
        self.save()
        logger.info(f"Added citation relation: {from_key} -> {to_key}")

    def remove_citation_relation(self, from_key: str, to_key: str) -> None:
        """Remove a citation relation between two entries."""
        if from_key in self._entries:
            self._entries[from_key].remove_citation(to_key)
        if to_key in self._entries:
            self._entries[to_key].remove_cited_by(from_key)
        self.save()
        logger.info(f"Removed citation relation: {from_key} -> {to_key}")

    def get_statistics(self) -> LibraryStats:
        """Get library statistics."""
        stats = LibraryStats()
        stats.total_entries = len(self._entries)

        years = []

        for entry in self._entries.values():
            stats.entries_by_type[entry.entry_type] = stats.entries_by_type.get(entry.entry_type, 0) + 1

            if entry.year:
                stats.entries_by_year[entry.year] = stats.entries_by_year.get(entry.year, 0) + 1
                years.append(entry.year)

            for author in entry.get_authors_list():
                stats.entries_by_author[author] = stats.entries_by_author.get(author, 0) + 1

            if entry.journal:
                stats.entries_by_journal[entry.journal] = stats.entries_by_journal.get(entry.journal, 0) + 1

            for tag in entry.tags:
                stats.entries_by_tag[tag] = stats.entries_by_tag.get(tag, 0) + 1

            stats.total_citations += len(entry.citations)
            stats.total_cited_by += len(entry.cited_by)

        if years:
            stats.date_range = (min(years), max(years))

        return stats

    def clear(self) -> None:
        """Clear all entries from the library."""
        if self._entries:
            self.file_manager.backup_file(self.config.library_path)
            self._entries.clear()
            self.save()
            logger.info("Library cleared")

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    def __iter__(self):
        return iter(self._entries.values())
