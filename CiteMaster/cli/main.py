"""CiteMaster command-line interface using Typer."""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from utils.config import Config, ConfigError
from utils.validators import ValidationError
from utils.file_ops import FileOperationError
from core.library import CitationLibrary, LibraryError
from core.citation_generator import CitationGenerator, CitationTemplateError
from core.graph_builder import GraphBuilder
from parsers.bibtex_parser import BibTeXParseError, BibTeXValidationError

logger = get_logger()
console = Console()

app = typer.Typer(
    name="citemaster",
    help="📚 CiteMaster - Academic Citation Management & Literature Search System",
    add_completion=False,
    no_args_is_help=True
)

config_app = typer.Typer(help="Manage configuration")
library_app = typer.Typer(help="Manage citation library")
import_app = typer.Typer(help="Import references")
export_app = typer.Typer(help="Export references")
cite_app = typer.Typer(help="Generate citations")
search_app = typer.Typer(help="Search and filter references")
graph_app = typer.Typer(help="Citation graph operations")

app.add_typer(config_app, name="config")
app.add_typer(library_app, name="library")
app.add_typer(import_app, name="import")
app.add_typer(export_app, name="export")
app.add_typer(cite_app, name="cite")
app.add_typer(search_app, name="search")
app.add_typer(graph_app, name="graph")

_config: Optional[Config] = None
_library: Optional[CitationLibrary] = None
_generator: Optional[CitationGenerator] = None
_graph_builder: Optional[GraphBuilder] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        try:
            _config = Config()
            logger.set_level(_config.get("log_level", "INFO"))
        except ConfigError as e:
            console.print(f"[red]✗ Configuration error: {e}[/red]")
            raise typer.Exit(code=1)
    return _config


def get_library() -> CitationLibrary:
    """Get the global library instance."""
    global _library
    if _library is None:
        try:
            config = get_config()
            _library = CitationLibrary(config)
        except LibraryError as e:
            console.print(f"[red]✗ Library error: {e}[/red]")
            raise typer.Exit(code=1)
    return _library


def get_generator() -> CitationGenerator:
    """Get the global citation generator instance."""
    global _generator
    if _generator is None:
        try:
            config = get_config()
            _generator = CitationGenerator(config)
        except CitationTemplateError as e:
            console.print(f"[red]✗ Citation generator error: {e}[/red]")
            raise typer.Exit(code=1)
    return _generator


def get_graph_builder() -> GraphBuilder:
    """Get the global graph builder instance."""
    global _graph_builder
    if _graph_builder is None:
        try:
            config = get_config()
            _graph_builder = GraphBuilder(config)
        except Exception as e:
            console.print(f"[red]✗ Graph builder error: {e}[/red]")
            raise typer.Exit(code=1)
    return _graph_builder


@app.callback()
def main(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output")
):
    """Global options for CiteMaster."""
    if config_path:
        global _config
        try:
            _config = Config(config_path)
        except ConfigError as e:
            console.print(f"[red]✗ Configuration error: {e}[/red]")
            raise typer.Exit(code=1)

    if verbose:
        logger.set_level("DEBUG")
    elif quiet:
        logger.set_level("ERROR")


# ===== Config Commands =====

@config_app.command("show")
def config_show():
    """Show current configuration."""
    config = get_config()
    table = Table(title="📋 Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in sorted(config._config.items()):
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        table.add_row(key, str(value))

    console.print(table)
    console.print(f"\n[dim]Config file: {config.config_path}[/dim]")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value")
):
    """Set a configuration value."""
    try:
        config = get_config()

        if key == "max_file_size_mb":
            value = int(value)
        elif key == "supported_formats":
            value = [v.strip() for v in value.split(",")]
        elif key == "required_fields":
            value = [v.strip() for v in value.split(",")]

        config.set(key, value)
        console.print(f"[green]✓ Set {key} = {value}[/green]")
    except (ConfigError, ValueError) as e:
        console.print(f"[red]✗ Failed to set config: {e}[/red]")
        raise typer.Exit(code=1)


@config_app.command("reload")
def config_reload():
    """Reload configuration from file."""
    try:
        global _config
        _config = None
        get_config()
        console.print("[green]✓ Configuration reloaded[/green]")
    except ConfigError as e:
        console.print(f"[red]✗ Failed to reload config: {e}[/red]")
        raise typer.Exit(code=1)


# ===== Library Commands =====

@library_app.command("add")
def library_add(
    title: str = typer.Option(..., "--title", "-t", help="Paper title"),
    author: str = typer.Option(..., "--author", "-a", help="Author names (separated by 'and')"),
    year: int = typer.Option(..., "--year", "-y", help="Publication year"),
    entry_type: str = typer.Option("article", "--type", help="Entry type (article, book, inproceedings, etc.)"),
    journal: Optional[str] = typer.Option(None, "--journal", "-j", help="Journal name"),
    booktitle: Optional[str] = typer.Option(None, "--booktitle", help="Book title for inproceedings/incollection"),
    publisher: Optional[str] = typer.Option(None, "--publisher", help="Publisher name"),
    school: Optional[str] = typer.Option(None, "--school", help="School for thesis"),
    institution: Optional[str] = typer.Option(None, "--institution", help="Institution for tech report"),
    month: Optional[str] = typer.Option(None, "--month", help="Publication month"),
    volume: Optional[str] = typer.Option(None, "--volume", help="Journal volume"),
    number: Optional[str] = typer.Option(None, "--number", help="Issue number"),
    pages: Optional[str] = typer.Option(None, "--pages", help="Page range"),
    chapter: Optional[str] = typer.Option(None, "--chapter", help="Chapter number"),
    edition: Optional[str] = typer.Option(None, "--edition", help="Edition"),
    series: Optional[str] = typer.Option(None, "--series", help="Series name"),
    address: Optional[str] = typer.Option(None, "--address", help="Publisher address"),
    editor: Optional[str] = typer.Option(None, "--editor", help="Editor names"),
    translator: Optional[str] = typer.Option(None, "--translator", help="Translator names"),
    doi: Optional[str] = typer.Option(None, "--doi", help="DOI"),
    url: Optional[str] = typer.Option(None, "--url", help="URL"),
    issn: Optional[str] = typer.Option(None, "--issn", help="ISSN"),
    isbn: Optional[str] = typer.Option(None, "--isbn", help="ISBN"),
    keywords: Optional[str] = typer.Option(None, "--keywords", help="Keywords (comma-separated)"),
    abstract: Optional[str] = typer.Option(None, "--abstract", help="Abstract"),
    note: Optional[str] = typer.Option(None, "--note", help="Additional notes"),
    key: Optional[str] = typer.Option(None, "--key", help="Citation key (auto-generated if not provided)"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip validation")
):
    """Add a new entry to the library."""
    try:
        library = get_library()

        entry_data = {
            "citation_key": key,
            "entry_type": entry_type,
            "title": title,
            "author": author,
            "year": year,
            "journal": journal,
            "booktitle": booktitle,
            "publisher": publisher,
            "school": school,
            "institution": institution,
            "month": month,
            "volume": volume,
            "number": number,
            "pages": pages,
            "chapter": chapter,
            "edition": edition,
            "series": series,
            "address": address,
            "editor": editor,
            "translator": translator,
            "doi": doi,
            "url": url,
            "issn": issn,
            "isbn": isbn,
            "keywords": keywords,
            "abstract": abstract,
            "note": note
        }

        entry = library.add_entry(entry_data, validate=not no_validate)
        console.print(f"[green]✓ Added entry: {entry.citation_key}[/green]")
        console.print(f"  Title: {entry.title}")
        console.print(f"  Author: {entry.author}")
        console.print(f"  Year: {entry.year}")
        console.print(f"  Type: {entry.entry_type}")

    except (LibraryError, ValidationError) as e:
        console.print(f"[red]✗ Failed to add entry: {e}[/red]")
        raise typer.Exit(code=1)


@library_app.command("update")
def library_update(
    key: str = typer.Argument(..., help="Citation key of entry to update"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Paper title"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author names (separated by 'and')"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Publication year"),
    entry_type: Optional[str] = typer.Option(None, "--type", help="Entry type (article, book, etc.)"),
    journal: Optional[str] = typer.Option(None, "--journal", "-j", help="Journal name"),
    booktitle: Optional[str] = typer.Option(None, "--booktitle", help="Book title for inproceedings/incollection"),
    publisher: Optional[str] = typer.Option(None, "--publisher", help="Publisher name"),
    school: Optional[str] = typer.Option(None, "--school", help="School for thesis"),
    institution: Optional[str] = typer.Option(None, "--institution", help="Institution for tech report"),
    month: Optional[str] = typer.Option(None, "--month", help="Publication month"),
    volume: Optional[str] = typer.Option(None, "--volume", help="Journal volume"),
    number: Optional[str] = typer.Option(None, "--number", help="Issue number"),
    pages: Optional[str] = typer.Option(None, "--pages", help="Page range"),
    chapter: Optional[str] = typer.Option(None, "--chapter", help="Chapter number"),
    edition: Optional[str] = typer.Option(None, "--edition", help="Edition"),
    series: Optional[str] = typer.Option(None, "--series", help="Series name"),
    address: Optional[str] = typer.Option(None, "--address", help="Publisher address"),
    editor: Optional[str] = typer.Option(None, "--editor", help="Editor names"),
    translator: Optional[str] = typer.Option(None, "--translator", help="Translator names"),
    doi: Optional[str] = typer.Option(None, "--doi", help="DOI"),
    url: Optional[str] = typer.Option(None, "--url", help="URL"),
    issn: Optional[str] = typer.Option(None, "--issn", help="ISSN"),
    isbn: Optional[str] = typer.Option(None, "--isbn", help="ISBN"),
    keywords: Optional[str] = typer.Option(None, "--keywords", help="Keywords (comma-separated)"),
    abstract: Optional[str] = typer.Option(None, "--abstract", help="Abstract"),
    note: Optional[str] = typer.Option(None, "--note", help="Additional notes"),
    new_key: Optional[str] = typer.Option(None, "--new-key", help="New citation key"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip validation")
):
    """Update an existing entry."""
    try:
        library = get_library()

        updates: Dict[str, Any] = {}
        if title is not None:
            updates["title"] = title
        if author is not None:
            updates["author"] = author
        if year is not None:
            updates["year"] = year
        if entry_type is not None:
            updates["entry_type"] = entry_type
        if journal is not None:
            updates["journal"] = journal
        if booktitle is not None:
            updates["booktitle"] = booktitle
        if publisher is not None:
            updates["publisher"] = publisher
        if school is not None:
            updates["school"] = school
        if institution is not None:
            updates["institution"] = institution
        if month is not None:
            updates["month"] = month
        if volume is not None:
            updates["volume"] = volume
        if number is not None:
            updates["number"] = number
        if pages is not None:
            updates["pages"] = pages
        if chapter is not None:
            updates["chapter"] = chapter
        if edition is not None:
            updates["edition"] = edition
        if series is not None:
            updates["series"] = series
        if address is not None:
            updates["address"] = address
        if editor is not None:
            updates["editor"] = editor
        if translator is not None:
            updates["translator"] = translator
        if doi is not None:
            updates["doi"] = doi
        if url is not None:
            updates["url"] = url
        if issn is not None:
            updates["issn"] = issn
        if isbn is not None:
            updates["isbn"] = isbn
        if keywords is not None:
            updates["keywords"] = keywords
        if abstract is not None:
            updates["abstract"] = abstract
        if note is not None:
            updates["note"] = note
        if new_key is not None:
            updates["citation_key"] = new_key

        if not updates:
            console.print("[yellow]⚠ No updates specified[/yellow]")
            raise typer.Exit(code=0)

        entry = library.update_entry(key, updates, validate=not no_validate)
        console.print(f"[green]✓ Updated entry: {entry.citation_key}[/green]")
        for field, value in updates.items():
            if field == "citation_key":
                continue
            display_value = str(value)[:50] + ("..." if len(str(value)) > 50 else "")
            console.print(f"  [dim]{field}:[/dim] {display_value}")

    except (LibraryError, ValidationError) as e:
        console.print(f"[red]✗ Failed to update entry: {e}[/red]")
        raise typer.Exit(code=1)


@library_app.command("delete")
def library_delete(
    key: str = typer.Argument(..., help="Citation key of entry to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation")
):
    """Delete an entry from the library."""
    try:
        library = get_library()
        entry = library.get_entry(key)

        if not entry:
            console.print(f"[red]✗ Entry '{key}' not found[/red]")
            raise typer.Exit(code=1)

        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete '{key}'?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(code=0)

        library.delete_entry(key)
        console.print(f"[green]✓ Deleted entry: {key}[/green]")

    except LibraryError as e:
        console.print(f"[red]✗ Failed to delete entry: {e}[/red]")
        raise typer.Exit(code=1)


@library_app.command("list")
def library_list(
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of entries to show"),
    sort_by: str = typer.Option("key", "--sort", help="Sort by: key, year, author, title")
):
    """List all entries in the library."""
    library = get_library()
    entries = library.get_all_entries()

    if sort_by == "year":
        entries.sort(key=lambda e: e.year or 0, reverse=True)
    elif sort_by == "author":
        entries.sort(key=lambda e: e.author.lower())
    elif sort_by == "title":
        entries.sort(key=lambda e: e.title.lower())

    entries = entries[:limit]

    table = Table(title=f"📚 Library ({len(library)} entries)", show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Author", style="green")
    table.add_column("Year", style="yellow", justify="center")
    table.add_column("Type", style="magenta")

    for entry in entries:
        title = entry.title[:60] + "..." if len(entry.title) > 60 else entry.title
        author = entry.author[:30] + "..." if len(entry.author) > 30 else entry.author
        table.add_row(
            entry.citation_key,
            title,
            author,
            str(entry.year or "N/A"),
            entry.entry_type
        )

    console.print(table)


@library_app.command("show")
def library_show(
    key: str = typer.Argument(..., help="Citation key of entry to show")
):
    """Show detailed information about an entry."""
    library = get_library()
    entry = library.get_entry(key)

    if not entry:
        console.print(f"[red]✗ Entry '{key}' not found[/red]")
        raise typer.Exit(code=1)

    panel_content = Text()
    panel_content.append(f"📄 {entry.title}\n\n", style="bold white")
    panel_content.append(f"👤 Author: ", style="bold cyan")
    panel_content.append(f"{entry.author}\n")
    panel_content.append(f"📅 Year: ", style="bold cyan")
    panel_content.append(f"{entry.year or 'N/A'}\n")
    panel_content.append(f"📝 Type: ", style="bold cyan")
    panel_content.append(f"{entry.entry_type}\n")

    if entry.journal:
        panel_content.append(f"📰 Journal: ", style="bold cyan")
        panel_content.append(f"{entry.journal}\n")
    if entry.booktitle:
        panel_content.append(f"📚 Book Title: ", style="bold cyan")
        panel_content.append(f"{entry.booktitle}\n")
    if entry.publisher:
        panel_content.append(f"🏢 Publisher: ", style="bold cyan")
        panel_content.append(f"{entry.publisher}\n")
    if entry.school:
        panel_content.append(f"🎓 School: ", style="bold cyan")
        panel_content.append(f"{entry.school}\n")
    if entry.institution:
        panel_content.append(f"🏛️  Institution: ", style="bold cyan")
        panel_content.append(f"{entry.institution}\n")
    if entry.month:
        panel_content.append(f"📅 Month: ", style="bold cyan")
        panel_content.append(f"{entry.month}\n")
    if entry.volume:
        panel_content.append(f"📊 Volume: ", style="bold cyan")
        panel_content.append(f"{entry.volume}")
        if entry.number:
            panel_content.append(f" (Issue {entry.number})")
        panel_content.append("\n")
    if entry.number and not entry.volume:
        panel_content.append(f"🔢 Issue: ", style="bold cyan")
        panel_content.append(f"{entry.number}\n")
    if entry.pages:
        panel_content.append(f"📄 Pages: ", style="bold cyan")
        panel_content.append(f"{entry.pages}\n")
    if entry.chapter:
        panel_content.append(f"📖 Chapter: ", style="bold cyan")
        panel_content.append(f"{entry.chapter}\n")
    if entry.edition:
        panel_content.append(f"📚 Edition: ", style="bold cyan")
        panel_content.append(f"{entry.edition}\n")
    if entry.series:
        panel_content.append(f"📚 Series: ", style="bold cyan")
        panel_content.append(f"{entry.series}\n")
    if entry.address:
        panel_content.append(f"📍 Address: ", style="bold cyan")
        panel_content.append(f"{entry.address}\n")
    if entry.editor:
        panel_content.append(f"✏️  Editor: ", style="bold cyan")
        panel_content.append(f"{entry.editor}\n")
    if entry.translator:
        panel_content.append(f"🌍 Translator: ", style="bold cyan")
        panel_content.append(f"{entry.translator}\n")
    if entry.doi:
        panel_content.append(f"🔗 DOI: ", style="bold cyan")
        panel_content.append(f"{entry.doi}\n")
    if entry.url:
        panel_content.append(f"🌐 URL: ", style="bold cyan")
        panel_content.append(f"{entry.url}\n")
    if entry.issn:
        panel_content.append(f"🔢 ISSN: ", style="bold cyan")
        panel_content.append(f"{entry.issn}\n")
    if entry.isbn:
        panel_content.append(f"🔢 ISBN: ", style="bold cyan")
        panel_content.append(f"{entry.isbn}\n")
    if entry.keywords:
        panel_content.append(f"🔑 Keywords: ", style="bold cyan")
        panel_content.append(f"{entry.keywords}\n")
    if entry.abstract:
        panel_content.append(f"📝 Abstract: ", style="bold cyan")
        abstract = entry.abstract[:200] + ("..." if len(entry.abstract) > 200 else "")
        panel_content.append(f"{abstract}\n")
    if entry.note:
        panel_content.append(f"📝 Note: ", style="bold cyan")
        note = entry.note[:150] + ("..." if len(entry.note) > 150 else "")
        panel_content.append(f"{note}\n")
    if entry.tags:
        panel_content.append(f"🏷️  Tags: ", style="bold cyan")
        panel_content.append(f"{', '.join(entry.tags)}\n")
    if entry.citations:
        panel_content.append(f"📚 Cites: ", style="bold cyan")
        panel_content.append(f"{len(entry.citations)} papers\n")
    if entry.cited_by:
        panel_content.append(f"📖 Cited by: ", style="bold cyan")
        panel_content.append(f"{len(entry.cited_by)} papers\n")

    panel_content.append(f"\n🕒 Created: {entry.created_at}\n", style="dim")
    panel_content.append(f"🕒 Updated: {entry.updated_at}", style="dim")

    console.print(Panel(panel_content, title=f"[{entry.citation_key}]", border_style="cyan"))


@library_app.command("stats")
def library_stats():
    """Show library statistics."""
    library = get_library()
    stats = library.get_statistics()

    table = Table(title="📊 Library Statistics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Entries", str(stats.total_entries))
    table.add_row("Total Citations (outgoing)", str(stats.total_citations))
    table.add_row("Total Cited By (incoming)", str(stats.total_cited_by))

    if stats.date_range:
        table.add_row("Year Range", f"{stats.date_range[0]} - {stats.date_range[1]}")

    table.add_row("", "")
    table.add_row("Entries by Type", "")
    for entry_type, count in sorted(stats.entries_by_type.items()):
        table.add_row(f"  {entry_type}", str(count))

    if stats.entries_by_year:
        table.add_row("", "")
        table.add_row("Entries by Year", "")
        for year, count in sorted(stats.entries_by_year.items(), reverse=True)[:10]:
            table.add_row(f"  {year}", str(count))

    if stats.entries_by_author:
        table.add_row("", "")
        table.add_row("Top Authors", "")
        for author, count in sorted(stats.entries_by_author.items(), key=lambda x: x[1], reverse=True)[:5]:
            auth = author[:40] + "..." if len(author) > 40 else author
            table.add_row(f"  {auth}", str(count))

    if stats.entries_by_tag:
        table.add_row("", "")
        table.add_row("Top Tags", "")
        for tag, count in sorted(stats.entries_by_tag.items(), key=lambda x: x[1], reverse=True)[:5]:
            table.add_row(f"  {tag}", str(count))

    console.print(table)


@library_app.command("tag")
def library_tag(
    key: str = typer.Argument(..., help="Citation key"),
    tag: str = typer.Argument(..., help="Tag to add"),
    remove: bool = typer.Option(False, "--remove", "-r", help="Remove tag instead of adding")
):
    """Add or remove tags from an entry."""
    try:
        library = get_library()
        entry = library.get_entry(key)

        if not entry:
            console.print(f"[red]✗ Entry '{key}' not found[/red]")
            raise typer.Exit(code=1)

        if remove:
            entry.remove_tag(tag)
            console.print(f"[green]✓ Removed tag '{tag}' from {key}[/green]")
        else:
            entry.add_tag(tag)
            console.print(f"[green]✓ Added tag '{tag}' to {key}[/green]")

        library.save()

    except LibraryError as e:
        console.print(f"[red]✗ Failed to update tags: {e}[/red]")
        raise typer.Exit(code=1)


@library_app.command("clear")
def library_clear(
    force: bool = typer.Option(False, "--force", "-f", help="Clear without confirmation")
):
    """Clear all entries from the library."""
    library = get_library()

    if len(library) == 0:
        console.print("[yellow]ℹ Library is already empty[/yellow]")
        raise typer.Exit(code=0)

    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete ALL {len(library)} entries? This cannot be undone.")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(code=0)

    library.clear()
    console.print("[green]✓ Library cleared[/green]")


# ===== Import Commands =====

@import_app.command("bibtex")
def import_bibtex(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="Path to BibTeX file"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip validation"),
    no_merge: bool = typer.Option(False, "--no-merge", help="Skip duplicate entries instead of merging")
):
    """Import entries from a BibTeX file."""
    try:
        library = get_library()
        imported, skipped, errors, warnings = library.import_bibtex(
            input_path,
            validate=not no_validate,
            merge=not no_merge
        )

        console.print(f"[green]✓ Import complete[/green]")
        console.print(f"  Imported: {imported} entries")
        if skipped > 0:
            console.print(f"  Skipped: {skipped} entries")
        if errors:
            console.print(f"  [red]Errors: {len(errors)}[/red]")
            for err in errors[:5]:
                console.print(f"    - {err}")
            if len(errors) > 5:
                console.print(f"    ... and {len(errors) - 5} more")
        if warnings:
            console.print(f"  [yellow]Warnings: {len(warnings)}[/yellow]")
            for warn in warnings[:5]:
                console.print(f"    - {warn}")
            if len(warnings) > 5:
                console.print(f"    ... and {len(warnings) - 5} more")

    except (BibTeXParseError, BibTeXValidationError, LibraryError) as e:
        console.print(f"[red]✗ Import failed: {e}[/red]")
        raise typer.Exit(code=1)


# ===== Export Commands =====

@export_app.command("bibtex")
def export_bibtex(
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Export library to BibTeX format."""
    try:
        library = get_library()
        path = library.export_bibtex(output_path)
        console.print(f"[green]✓ Exported {len(library)} entries to {path}[/green]")
    except LibraryError as e:
        console.print(f"[red]✗ Export failed: {e}[/red]")
        raise typer.Exit(code=1)


@export_app.command("json")
def export_json(
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Export library to JSON format."""
    try:
        library = get_library()
        library.save(backup=False)
        path = output_path or library.config.library_path
        console.print(f"[green]✓ Exported {len(library)} entries to {path}[/green]")
    except LibraryError as e:
        console.print(f"[red]✗ Export failed: {e}[/red]")
        raise typer.Exit(code=1)


# ===== Citation Commands =====

@cite_app.command("generate")
def cite_generate(
    key: str = typer.Argument(..., help="Citation key"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Citation format (apa, mla, chicago, ieee)"),
    inline: bool = typer.Option(False, "--inline", help="Generate inline citation")
):
    """Generate a citation for an entry."""
    try:
        library = get_library()
        generator = get_generator()
        config = get_config()

        entry = library.get_entry(key)
        if not entry:
            console.print(f"[red]✗ Entry '{key}' not found[/red]")
            raise typer.Exit(code=1)

        fmt = format or config.default_citation_format

        if inline:
            citation = generator.generate_inline_citation(entry, fmt)
        else:
            citation = generator.generate(entry, fmt)

        console.print(f"\n[bold]{fmt.upper()} Format:[/bold]\n")
        console.print(Panel(citation, border_style="green"))

    except CitationTemplateError as e:
        console.print(f"[red]✗ Failed to generate citation: {e}[/red]")
        raise typer.Exit(code=1)


@cite_app.command("all")
def cite_all(
    key: str = typer.Argument(..., help="Citation key")
):
    """Generate citations in all supported formats."""
    try:
        library = get_library()
        generator = get_generator()

        entry = library.get_entry(key)
        if not entry:
            console.print(f"[red]✗ Entry '{key}' not found[/red]")
            raise typer.Exit(code=1)

        citations = generator.generate_all_formats(entry)

        for fmt, citation in citations.items():
            console.print(f"\n[bold magenta]{fmt.upper()}:[/bold magenta]")
            console.print(f"  {citation}\n")

    except CitationTemplateError as e:
        console.print(f"[red]✗ Failed to generate citations: {e}[/red]")
        raise typer.Exit(code=1)


@cite_app.command("bibliography")
def cite_bibliography(
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Citation format"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    keys: Optional[List[str]] = typer.Argument(None, help="Specific citation keys to include")
):
    """Generate a complete bibliography."""
    try:
        library = get_library()
        generator = get_generator()
        config = get_config()

        fmt = format or config.default_citation_format

        if keys:
            entries = [library.get_entry(k) for k in keys if library.get_entry(k)]
            missing = [k for k in keys if not library.get_entry(k)]
            if missing:
                console.print(f"[yellow]⚠ Missing entries: {', '.join(missing)}[/yellow]")
        else:
            entries = library.get_all_entries()

        bibliography = generator.generate_bibliography(entries, fmt)

        content = f"Bibliography ({fmt.upper()} format)\n"
        content += "=" * 60 + "\n\n"
        for i, citation in enumerate(bibliography, 1):
            content += f"{i}. {citation}\n\n"

        if output:
            with open(output, "w", encoding=config.output_encoding) as f:
                f.write(content)
            console.print(f"[green]✓ Bibliography written to {output}[/green]")
        else:
            console.print(Panel(content.strip(), title=f"Bibliography - {fmt.upper()}", border_style="cyan"))

    except CitationTemplateError as e:
        console.print(f"[red]✗ Failed to generate bibliography: {e}[/red]")
        raise typer.Exit(code=1)


@cite_app.command("formats")
def cite_formats():
    """List supported citation formats."""
    generator = get_generator()
    formats = generator.get_supported_formats()

    table = Table(title="📝 Supported Citation Formats", show_header=True, header_style="bold magenta")
    table.add_column("Format", style="cyan")
    table.add_column("Full Name", style="green")

    format_names = {
        "apa": "American Psychological Association",
        "mla": "Modern Language Association",
        "chicago": "Chicago Manual of Style",
        "ieee": "Institute of Electrical and Electronics Engineers"
    }

    for fmt in formats:
        table.add_row(fmt.upper(), format_names.get(fmt, fmt))

    console.print(table)


# ===== Search Commands =====

@search_app.command("query")
def search_query(
    query: str = typer.Argument(..., help="Search query"),
    fields: Optional[List[str]] = typer.Option(None, "--field", help="Specific fields to search"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum results")
):
    """Search entries matching a query."""
    library = get_library()
    results = library.search(query, fields)

    if not results:
        console.print(f"[yellow]ℹ No results found for '{query}'[/yellow]")
        raise typer.Exit(code=0)

    results = results[:limit]

    table = Table(title=f"🔍 Search Results ({len(results)} found)", show_header=True, header_style="bold magenta")
    table.add_column("Score", style="yellow", justify="right")
    table.add_column("Key", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Author", style="green")
    table.add_column("Year", style="magenta", justify="center")
    table.add_column("Matches", style="blue")

    for result in results:
        entry = result.entry
        title = entry.title[:50] + "..." if len(entry.title) > 50 else entry.title
        author = entry.author[:25] + "..." if len(entry.author) > 25 else entry.author
        matches = ", ".join(result.matched_fields) if result.matched_fields else "-"

        table.add_row(
            f"{result.score:.1f}",
            entry.citation_key,
            title,
            author,
            str(entry.year or "N/A"),
            matches
        )

    console.print(table)


@search_app.command("author")
def search_author(
    author: str = typer.Argument(..., help="Author name to search")
):
    """Filter entries by author."""
    library = get_library()
    entries = library.filter_by_author(author)

    if not entries:
        console.print(f"[yellow]ℹ No entries found for author '{author}'[/yellow]")
        raise typer.Exit(code=0)

    console.print(f"[green]✓ Found {len(entries)} entries by '{author}'[/green]\n")

    for entry in entries:
        console.print(f"  [{entry.citation_key}] {entry.title} ({entry.year})")


@search_app.command("year")
def search_year(
    year: int = typer.Argument(..., help="Year to filter by"),
    end_year: Optional[int] = typer.Option(None, "--to", help="End year for range search")
):
    """Filter entries by year or year range."""
    library = get_library()

    if end_year:
        entries = library.filter_by_year_range(year, end_year)
        label = f"{year}-{end_year}"
    else:
        entries = library.filter_by_year(year)
        label = str(year)

    if not entries:
        console.print(f"[yellow]ℹ No entries found for year {label}[/yellow]")
        raise typer.Exit(code=0)

    console.print(f"[green]✓ Found {len(entries)} entries from {label}[/green]\n")

    for entry in entries:
        console.print(f"  [{entry.citation_key}] {entry.author.split(',')[0]}: {entry.title}")


@search_app.command("journal")
def search_journal(
    journal: str = typer.Argument(..., help="Journal name to search")
):
    """Filter entries by journal."""
    library = get_library()
    entries = library.filter_by_journal(journal)

    if not entries:
        console.print(f"[yellow]ℹ No entries found in journal '{journal}'[/yellow]")
        raise typer.Exit(code=0)

    console.print(f"[green]✓ Found {len(entries)} entries in '{journal}'[/green]\n")

    for entry in entries:
        console.print(f"  [{entry.citation_key}] {entry.author.split(',')[0]} ({entry.year}): {entry.title}")


@search_app.command("tag")
def search_tag(
    tag: str = typer.Argument(..., help="Tag to filter by")
):
    """Filter entries by tag."""
    library = get_library()
    entries = library.filter_by_tag(tag)

    if not entries:
        console.print(f"[yellow]ℹ No entries found with tag '{tag}'[/yellow]")
        raise typer.Exit(code=0)

    console.print(f"[green]✓ Found {len(entries)} entries tagged '{tag}'[/green]\n")

    for entry in entries:
        console.print(f"  [{entry.citation_key}] {entry.author.split(',')[0]} ({entry.year}): {entry.title}")


@search_app.command("type")
def search_type(
    entry_type: str = typer.Argument(..., help="Entry type to filter by")
):
    """Filter entries by entry type."""
    library = get_library()
    entries = library.filter_by_type(entry_type)

    if not entries:
        console.print(f"[yellow]ℹ No entries found with type '{entry_type}'[/yellow]")
        raise typer.Exit(code=0)

    console.print(f"[green]✓ Found {len(entries)} entries of type '{entry_type}'[/green]\n")

    for entry in entries:
        console.print(f"  [{entry.citation_key}] {entry.author.split(',')[0]} ({entry.year}): {entry.title}")


@search_app.command("group")
def search_group(
    group_by: str = typer.Argument(..., help="Group by: author, year, journal, tag")
):
    """Group entries by category."""
    library = get_library()

    if group_by == "author":
        groups = library.group_by_author()
        title = "👥 Grouped by Author"
    elif group_by == "year":
        groups = library.group_by_year()
        title = "📅 Grouped by Year"
    elif group_by == "journal":
        groups = library.group_by_journal()
        title = "📰 Grouped by Journal"
    elif group_by == "tag":
        groups = library.group_by_tag()
        title = "🏷️  Grouped by Tag"
    else:
        console.print(f"[red]✗ Invalid group by option: {group_by}[/red]")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]{title}[/bold]\n")

    for key, entries in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        console.print(f"[cyan]{key}[/cyan] ({len(entries)} entries):")
        for entry in entries[:3]:
            console.print(f"  • {entry.citation_key}: {entry.title[:50]}...")
        if len(entries) > 3:
            console.print(f"  ... and {len(entries) - 3} more")
        console.print()


# ===== Graph Commands =====

@graph_app.command("build")
def graph_build(
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output HTML file path")
):
    """Build and visualize the citation graph."""
    try:
        library = get_library()
        builder = get_graph_builder()
        config = get_config()

        entries = library.get_all_entries()
        graph = builder.build_graph(entries)
        output_path = builder.visualize(graph, output)

        summary = graph.get_summary()

        table = Table(title="📊 Citation Graph Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Nodes", str(summary["total_nodes"]))
        table.add_row("Total Edges", str(summary["total_edges"]))
        table.add_row("Connected Components", str(summary["connected_components"]))
        table.add_row("Average Degree", f"{summary['avg_degree']:.2f}")
        table.add_row("Isolated Nodes", str(summary["isolated_nodes"]))
        if summary["largest_component_size"]:
            table.add_row("Largest Component", str(summary["largest_component_size"]))

        console.print(table)
        console.print(f"\n[green]✓ Citation graph visualization saved to:[/green] {output_path}")
        console.print(f"[dim]Open this file in your web browser to view the interactive graph[/dim]")
        console.print(f"[yellow]💡 Tip: If no network access, the page will automatically show a static offline view[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Failed to build graph: {e}[/red]")
        raise typer.Exit(code=1)


@graph_app.command("text")
def graph_text():
    """Generate a text-based citation graph overview."""
    try:
        library = get_library()
        builder = get_graph_builder()

        entries = library.get_all_entries()
        graph = builder.build_graph(entries)
        text_graph = builder.generate_text_graph(graph)

        console.print(Panel(text_graph, title="📈 Citation Graph Overview", border_style="cyan"))

    except Exception as e:
        console.print(f"[red]✗ Failed to generate text graph: {e}[/red]")
        raise typer.Exit(code=1)


@graph_app.command("citation")
def graph_citation(
    from_key: str = typer.Argument(..., help="Citing entry key"),
    to_key: str = typer.Argument(..., help="Cited entry key"),
    remove: bool = typer.Option(False, "--remove", "-r", help="Remove citation relation")
):
    """Add or remove a citation relation between two entries."""
    try:
        library = get_library()

        if remove:
            library.remove_citation_relation(from_key, to_key)
            console.print(f"[green]✓ Removed citation: {from_key} -> {to_key}[/green]")
        else:
            library.add_citation_relation(from_key, to_key)
            console.print(f"[green]✓ Added citation: {from_key} -> {to_key}[/green]")

    except LibraryError as e:
        console.print(f"[red]✗ Failed to update citation relation: {e}[/red]")
        raise typer.Exit(code=1)


@graph_app.command("path")
def graph_path(
    start: str = typer.Argument(..., help="Start entry key"),
    end: str = typer.Argument(..., help="End entry key"),
    max_depth: int = typer.Option(5, "--max-depth", help="Maximum search depth")
):
    """Find a citation path between two entries."""
    try:
        library = get_library()
        builder = get_graph_builder()

        entries = library.get_all_entries()
        graph = builder.build_graph(entries)

        path = graph.find_path(start, end, max_depth)

        if not path:
            console.print(f"[yellow]ℹ No path found between '{start}' and '{end}' within {max_depth} steps[/yellow]")
            raise typer.Exit(code=0)

        console.print(f"[green]✓ Found path ({len(path) - 1} steps):[/green]\n")
        for i, key in enumerate(path):
            entry = library.get_entry(key)
            if entry:
                prefix = "  " if i == 0 else "  ↓ "
                console.print(f"{prefix}[cyan]{key}[/cyan]: {entry.author.split(',')[0]} ({entry.year}) - {entry.title[:60]}")
            else:
                console.print(f"  {key}: [Not found]")

    except Exception as e:
        console.print(f"[red]✗ Failed to find path: {e}[/red]")
        raise typer.Exit(code=1)


@graph_app.command("top")
def graph_top(
    n: int = typer.Option(10, "--number", "-n", help="Number of entries to show"),
    cited: bool = typer.Option(True, "--cited", help="Show most cited"),
    citing: bool = typer.Option(False, "--citing", help="Show most citing")
):
    """Show top cited or citing entries."""
    try:
        library = get_library()
        builder = get_graph_builder()

        entries = library.get_all_entries()
        graph = builder.build_graph(entries)

        if citing:
            top_entries = graph.get_top_citing(n)
            title = f"📊 Top {n} Most Citing Papers"
            metric = "cites"
        else:
            top_entries = graph.get_top_cited(n)
            title = f"📊 Top {n} Most Cited Papers"
            metric = "cited_by"

        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="yellow", justify="right")
        table.add_column("Key", style="cyan")
        table.add_column("Author", style="green")
        table.add_column("Year", style="magenta", justify="center")
        table.add_column(metric.capitalize(), style="red", justify="right")

        for i, node in enumerate(top_entries, 1):
            count = node.citation_count if citing else node.cited_by_count
            table.add_row(
                str(i),
                node.key,
                node.author.split(',')[0][:30],
                str(node.year or "N/A"),
                str(count)
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Failed to get top entries: {e}[/red]")
        raise typer.Exit(code=1)


def run():
    """Run the CLI application."""
    try:
        app()
    except Exception as e:
        logger.exception("Uncaught exception", e)
        console.print(f"[red]✗ An unexpected error occurred: {e}[/red]")
        console.print("[dim]Check the log file for details[/dim]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    run()
