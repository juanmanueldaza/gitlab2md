# AGENTS.md — Coding Standards for gitlab2md

This file documents the coding standards, conventions, and patterns used in the gitlab2md project. AI agents should follow these guidelines when contributing code.

## Tech Stack

| Aspect | Choice |
|--------|--------|
| Language | Python 3.13+ |
| Runtime deps | None (zero external dependencies) |
| Build system | hatchling |
| Package manager | uv (see `uv.lock`) |
| Linter / Formatter | Ruff (line-length: 88, target-version: py313) |
| Type checker | Pyright |
| Test framework | pytest |
| CI | GitHub Actions (ruff check, ruff format --check, pyright, pytest) |

## Project Layout

```
gitlab2md/
├── src/gitlab2md/          # Main package (src-layout)
│   ├── __init__.py          # Package metadata, public API exports
│   ├── __main__.py          # python -m entry point
│   ├── cli.py               # CLI argument parsing (argparse)
│   ├── converter.py         # Main orchestrator
│   ├── extractor.py         # GitLab API data extraction via glab CLI
│   ├── writer.py            # File output (MarkdownFileWriter, InMemoryWriter)
│   ├── protocols.py         # Abstract interfaces (Protocol classes)
│   ├── registry.py          # Decorator-based @register_parser / @register_formatter
│   ├── validation.py        # Input validation utilities
│   ├── constants.py         # All magic numbers / config values
│   ├── parsers/             # One file per parser
│   │   ├── __init__.py      # Re-exports all parser classes
│   │   ├── base.py          # BaseParser with shared utilities
│   │   ├── profile.py
│   │   └── ...
│   ├── formatters/          # One file per formatter
│   │   ├── __init__.py      # Re-exports all formatter classes
│   │   ├── base.py          # BaseFormatter with shared utilities
│   │   ├── profile.py
│   │   └── ...
├── tests/                   # Mirrors src/gitlab2md/ structure
│   ├── test_cli.py
│   ├── test_parsers.py
│   ├── test_formatters.py
│   ├── test_security.py
│   ├── test_solid.py
│   └── test_e2e.py
├── docs/                    # Documentation site (static HTML)
├── pyproject.toml           # Project config
├── README.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Architecture (SOLID)

The project strictly follows **SOLID principles**:

| Principle | Implementation |
|-----------|---------------|
| **Single Responsibility** | Each parser/formatter handles exactly one data section |
| **Open/Closed** | New parsers added via `@register_parser` decorator; no changes to core |
| **Liskov Substitution** | All parsers implement `SectionParser` protocol; all formatters implement `SectionFormatter` protocol |
| **Interface Segregation** | Separate focused protocols: `DataExtractor`, `SectionParser`, `SectionFormatter`, `OutputWriter` |
| **Dependency Inversion** | `Converter` depends on protocol abstractions, not concrete classes |

### Protocol-based design

All major components depend on `typing.Protocol` classes defined in `protocols.py`:
- `DataExtractor` — `.extract(username) -> dict`
- `SectionParser` — `.section_key`, `.parse(raw_data) -> Any`
- `SectionFormatter` — `.section_key`, `.output_filename`, `.format(parsed_data) -> str`
- `OutputWriter` — `.write(filename, content) -> Path`

### Registration pattern

New parsers and formatters register via decorators:
```python
from gitlab2md.registry import register_parser
from gitlab2md.parsers.base import BaseParser

@register_parser
class MyNewParser(BaseParser):
    section_key = "my_section"

    def parse(self, raw_data):
        ...
```

The `parsers/__init__.py` and `formatters/__init__.py` must import all classes so the decorators fire during import.

## Python Conventions

### Style & Formatting

- **Line length**: 88 characters (Ruff default)
- **Quotes**: Double quotes for strings (`"..."`)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped — standard library, third-party, local; sorted via Ruff (I rule)
- **Trailing commas**: Use for multi-line collections
- **Type hints**: Required on all function signatures and public class attributes
- **Return type**: `-> None` for procedures (no implicit Any)

### Naming

| Construct | Convention | Example |
|-----------|-----------|---------|
| Modules | `snake_case` | `merge_requests.py` |
| Classes | `PascalCase` | `MergeRequestsParser` |
| Functions/Methods | `snake_case` | `validate_gitlab_name` |
| Private methods | `_snake_case` (one underscore) | `_format_date` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_PAGE_SIZE` |
| Type variables | `T`, `K`, `V` (short) | `T` in `register_parser[T]` |

### Docstrings

- **Module docstrings**: Short description of the module's purpose
- **Class docstrings**: Description + Single Responsibility note
- **Method docstrings**: Google-style with `Args:`, `Returns:`, `Raises:` sections
- **No comments** explaining *what* the code does (the code should be self-documenting). Comments only explain *why*.

### Error handling

- Use specific exception types (`ValueError`, `RuntimeError`)
- Return early with guard clauses for None/empty checks
- In the CLI, catch broad `Exception` only at top level with sanitized messages (no stack trace exposure)
- In safe extract methods, catch `Exception` and return empty defaults (graceful degradation)

### Security patterns

- All user-controlled input validated through `validation.py` (no raw trust of usernames, group names, filenames)
- Path traversal prevented in `MarkdownFileWriter._validate_filename()` — checks `..`, null bytes, absolute paths, canonical resolution
- URLs sanitized in `BaseFormatter._sanitize_url()` — only `http`, `https`, `mailto` allowed
- Error messages sanitized — never expose raw subprocess stderr or stack traces to end users

## Testing Conventions

### Structure

- One test file per source module, placed in `tests/`
- Test classes mirror source classes: `TestProfileParser` tests `ProfileParser`
- Section separators in test files for readability:
  ```
  # =============================================================================
  # ProfileParser Tests
  # =============================================================================
  ```

### Patterns

- **Class organization** — each test class wraps a logical group of tests
- **`@pytest.fixture`** for repeated setup (e.g., `def parser(self) -> return ProfileParser()`)
- **Test method naming**: `test_<scenario>` — descriptive snake_case names
- **Arrange-Act-Assert** (Given-When-Then) within each test
- **Built-in fixtures**: `tmp_path` for temp directories, `capsys` for stdout/stderr capture
- **Mocking**: `unittest.mock.patch` for subprocess calls
- **No docstrings on test methods** unless the scenario is non-obvious
- **Test both success and edge cases**: empty data, None values, special characters, large inputs

### Running tests

```bash
ruff check .
ruff format .
pyright
pytest -v
```

## Git & PR Workflow

- Branch from `main` using naming convention: `feat/`, `fix/`, `docs/`, `refactor/`
- Commit messages: concise, imperative mood, no trailing period
- PRs follow `.github/PULL_REQUEST_TEMPLATE.md` — include description, related issue, checklist
- Ensure all CI checks (ruff, pyright, pytest) pass before opening PR

## Key Files Reference

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, tool config (ruff, pytest) |
| `src/gitlab2md/protocols.py` | Abstract interfaces for DI |
| `src/gitlab2md/registry.py` | Decorator-based registration system |
| `src/gitlab2md/constants.py` | Centralized configuration values |
| `src/gitlab2md/validation.py` | Shared input validation |
| `src/gitlab2md/parsers/base.py` | `BaseParser` with `_format_date`, `_safe_get`, `_parse_project` helpers |
| `src/gitlab2md/formatters/base.py` | `BaseFormatter` with `_escape_md`, `_sanitize_url`, `_truncate`, `_make_link` helpers |
