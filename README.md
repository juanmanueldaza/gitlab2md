```
█████████████████████████████████████████████████████████

   ██████  ██ ▄▄▄█████▓ ██       █████  ██████
 ▒██    ▒ ██ ▓  ██▒ ▓▒██▒     ██▒ ██▒██    ▒
 ▒ ▓██▄  ██▒ ▓██░ ▒░██░     ██░ ██░ ▓██▄
   ▒   ██░██░ ▓██▓ ░ ▒██░   ▒██████░   ▒   ██▒
 ▒█████▒ ░██░ ▒██▒ ░ ░█████░ ▒████░ ▒██████▒
 ▒ ▒▓▒ ▒ ░ ██  ██      ░ ███  ██   ██  ░ ▒▓▒ ▒ ░
 ░ ░▒  ░ ░ ██░ ██░     ░  ███ ██   ██░ ░ ░▒  ░ ░
 ░  ░  ░   ░ ░  ░          █ ░ ░       ░  ░  ░
       ░   ░  ░                     ░         ░

  GitLab → Markdown. Your data, your LLM, your rules.

█████████████████████████████████████████████████████████
```
# gitlab2md

[![PyPI version](https://img.shields.io/pypi/v/gitlab2md)](https://pypi.org/project/gitlab2md/)
[![Python versions](https://img.shields.io/pypi/pyversions/gitlab2md)](https://pypi.org/project/gitlab2md/)
[![License](https://img.shields.io/pypi/l/gitlab2md)](https://github.com/juanmanueldaza/gitlab2md/blob/main/LICENSE)
[![PyPI Downloads](https://img.shields.io/pypi/dm/gitlab2md?style=flat-square)](https://pypi.org/project/gitlab2md/)
[![GitHub stars](https://img.shields.io/github/stars/juanmanueldaza/gitlab2md?style=flat-square)](https://github.com/juanmanueldaza/gitlab2md)
[![CI](https://github.com/juanmanueldaza/gitlab2md/actions/workflows/ci.yml/badge.svg)](https://github.com/juanmanueldaza/gitlab2md/actions/workflows/ci.yml)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat-square)](https://github.com/juanmanueldaza/gitlab2md/issues)
[![Good First Issues](https://img.shields.io/github/issues/juanmanueldaza/gitlab2md/good%20first%20issue?style=flat-square&label=good%20first%20issues)](https://github.com/juanmanueldaza/gitlab2md/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

Convert GitLab profile data to clean Markdown files - the ideal format for LLM analysis.

## Why Markdown?

Markdown is the lingua franca of AI tools. Once your GitLab data is in `.md` format, you can:

- **Upload to [NotebookLM](https://notebooklm.google.com/)** and have conversations about your development history
- **Use [Claude Projects](https://claude.ai)** to analyze patterns across your contributions
- **Feed to [Obsidian](https://obsidian.md/)** with AI plugins for a personal developer knowledge base
- **Run local LLMs** (Ollama, LM Studio) for completely private analysis

### Example Prompts

Once your GitLab data is in an LLM, try asking:

| Question | Data Used |
|----------|-----------|
| "What technologies do I work with most?" | projects.md, merge_requests.md |
| "Summarize my contribution patterns" | events.md, merge_requests.md |
| "What open source projects have I contributed to?" | contributed_projects.md |
| "Analyze my merge request review patterns" | merge_requests.md |
| "What groups am I most active in?" | groups.md, memberships.md |
| "Generate a developer portfolio summary" | All files |
| "What are my most starred projects?" | starred.md |

## Installation

**Recommended** (using pipx - installs in isolated environment):
```bash
pipx install gitlab2md
```

Or with pip (in a virtual environment):
```bash
pip install gitlab2md
```

> **Note**: On modern Linux systems (Debian, Ubuntu 23.04+, Fedora), use `pipx` to avoid the "externally-managed-environment" error.

## Prerequisites

- [GitLab CLI (glab)](https://gitlab.com/gitlab-org/cli) installed and authenticated
- Python 3.13+

### Installing glab

```bash
# macOS
brew install glab

# Ubuntu/Debian
sudo apt install glab

# Or via pipx
pipx install glab
```

Then authenticate:
```bash
glab auth login
```

## Usage

```bash
# Use authenticated user
gitlab2md

# Specify a username
gitlab2md juanmanueldaza

# Include group contributions
gitlab2md juanmanueldaza --groups colmena-project,another-group

# Custom output directory
gitlab2md juanmanueldaza -o ./my_gitlab_data
```

Then drag the output folder into your favorite AI tool.

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `username` | GitLab username (optional, uses authenticated user if omitted) | - |
| `-o, --output` | Output directory | `gitlab_export` |
| `--groups` | Comma-separated list of groups to include contributions from | - |

## LLM Tools That Work Great With This

| Tool | Type | Best For |
|------|------|----------|
| [NotebookLM](https://notebooklm.google.com/) | Cloud | Conversational analysis, audio summaries |
| [Claude Projects](https://claude.ai) | Cloud | Deep analysis, long context |
| [ChatGPT](https://chat.openai.com) | Cloud | General analysis, quick insights |
| [Obsidian](https://obsidian.md/) + AI plugins | Local | Personal knowledge base, linked notes |
| [Open Notebook](https://github.com/Open-Notebook/Open-Notebook) | Local/Cloud | 16+ AI models, open source |
| [Ollama](https://ollama.ai/) | Local | Private, offline analysis |

## Output Files

Creates 13 markdown files in the output directory:

### Profile & Projects
- `profile.md` - User profile (name, bio, job title, organization, website)
- `projects.md` - Owned projects with stars, forks, visibility, topics
- `member_projects.md` - Projects where user is a member (excludes own)
- `contributed_projects.md` - Projects user has contributed to

### Activity & Contributions
- `merge_requests.md` - MR history with state, labels, and status breakdown
- `issues.md` - Issues created with state and labels
- `events.md` - Recent activity summary and action types
- `groups.md` - Group memberships and commit contributions

### Network & Social
- `starred.md` - Starred projects
- `memberships.md` - Groups and projects with access levels
- `snippets.md` - Code snippets with visibility

### Security
- `ssh_keys.md` - SSH key titles and expiration dates
- `gpg_keys.md` - GPG key IDs and creation dates

## Architecture

This project follows SOLID principles for maintainability:

- **Single Responsibility**: Each parser/formatter handles one data section
- **Open/Closed**: Add new parsers via `@register_parser` decorator without modifying core code
- **Liskov Substitution**: All parsers implement the `SectionParser` protocol
- **Interface Segregation**: Focused protocols for extractors, parsers, formatters, and writers
- **Dependency Inversion**: Converter depends on abstractions, not implementations

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

GPL-2.0 - see [LICENSE](LICENSE) for details.
