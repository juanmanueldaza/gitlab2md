# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-22

### Added
- Initial release
- Convert GitLab profile data to Markdown files for LLM analysis
- Support for 13 data categories:
  - Profile (name, bio, job title, organization, website)
  - Owned projects (name, description, visibility, stars, forks, topics)
  - Member projects (projects where user is a member)
  - Merge requests (title, state, status breakdown)
  - Issues (title, state, labels)
  - Groups (group memberships and contributions)
  - Events (activity summary, action types)
  - Starred projects (starred repositories)
  - Snippets (code snippets with visibility)
  - SSH keys (key titles, creation/expiration dates)
  - GPG keys (key IDs, creation dates)
  - Memberships (groups and projects with access levels)
  - Contributed projects (projects user contributed to)
- CLI with authenticated user detection via `glab`
- Group contribution tracking with `--groups` option
- Custom output directory support
- SOLID architecture for extensibility
- Security features (path traversal protection, input validation)
- Comprehensive test suite with 100+ tests

[Unreleased]: https://github.com/juanmanueldaza/gitlab2md/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/juanmanueldaza/gitlab2md/releases/tag/v0.1.0
