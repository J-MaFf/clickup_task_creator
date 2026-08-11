# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure setup
- Core module placeholders (main.py, config.py, auth.py, etc.)
- Test suite foundation
- Requirements.txt with all dependencies
- .gitignore for Python project
- Documentation files (README.md, PLAN.md)

### Changed
- `claude.yml` now calls the shared reusable Claude workflow in [J-MaFf/.github](https://github.com/J-MaFf/.github) instead of carrying its own copy ([#47](https://github.com/J-MaFf/clickup_task_creator/pull/47))

### Fixed
- Fixed `UnboundLocalError` in `ClickUpAPIClient._request()` when a request failed before a response existed (connection errors, SSL failures, too many redirects); these now raise `APIError` as intended ([#60](https://github.com/J-MaFf/clickup_task_creator/pull/60))
- Fixed retry logic consulting the previous attempt's status code when a later attempt failed at the connection level ([#60](https://github.com/J-MaFf/clickup_task_creator/pull/60))

## [0.1.0] - 2025-11-18

### Added
- Project initialization
- Directory structure setup
- Placeholder modules for all core components
- Basic configuration system
- Authentication chain framework
- Email extraction protocol
- AI summary integration framework
- Task creation workflow foundation
- Rich console UI helpers
- Comprehensive test suite structure

[Unreleased]: https://github.com/J-MaFf/clickup_task_creator/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/J-MaFf/clickup_task_creator/releases/tag/v0.1.0
