# Contributing to gitlab2md

Thank you for your interest in contributing to gitlab2md! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/juanmanueldaza/gitlab2md.git
   cd gitlab2md
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

This project uses:
- **Ruff** for linting and formatting
- **Pyright** for type checking
- Line length: 88 characters
- Target: Python 3.13+

Run checks before submitting:
```bash
ruff check .
ruff format .
pyright
pytest
```

## Architecture

The project follows SOLID principles:

- **Single Responsibility**: Each parser/formatter handles one section
- **Open/Closed**: Add new parsers via `@register_parser` decorator
- **Liskov Substitution**: All parsers implement `SectionParser` protocol
- **Interface Segregation**: Focused protocols for each component
- **Dependency Inversion**: Converter depends on protocols, not implementations

### Adding a New Parser

1. Create a file in `src/gitlab2md/parsers/`
2. Implement the `SectionParser` protocol
3. Use `@register_parser` decorator
4. Create matching formatter in `src/gitlab2md/formatters/`

Example:
```python
from gitlab2md.parsers.base import BaseParser
from gitlab2md.registry import register_parser

@register_parser
class MyNewParser(BaseParser):
    section_key = "my_section"

    def parse(self, data: dict) -> dict:
        # Parse logic here
        return {}
```

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Write tests** for new functionality
3. **Update documentation** if needed
4. **Ensure all checks pass** (ruff, pyright, pytest)
5. **Submit a PR** with a clear description

### PR Checklist

- [ ] Code follows the project style
- [ ] Tests added/updated
- [ ] Documentation updated (if applicable)
- [ ] All CI checks pass

## Reporting Bugs

When reporting bugs, please include:
- Python version
- Operating system
- `glab` CLI version
- Steps to reproduce
- Expected vs actual behavior

## Feature Requests

Feature requests are welcome! Please:
- Check existing issues first
- Describe the use case
- Explain why it would benefit others

## Questions?

Feel free to open an issue for questions or discussions.
