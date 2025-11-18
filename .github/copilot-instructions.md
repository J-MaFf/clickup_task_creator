# Copilot Instructions: ClickUp Task Creator

## Overview

The ClickUp Task Creator is a Python CLI application that creates ClickUp tasks directly from email URLs. It extracts email content, optionally uses Google Gemini AI to analyze and summarize the email, and automatically populates custom ClickUp task fields with intelligent data.

## Architecture & Data Flow

### Entry Point
- **`main.py`**: CLI orchestrates authentication, config, email URL input, AI analysis, task creation, and result display.

### Core Modules
- **`config.py`**: Enum-based config (`ClickUpTaskConfig`), `EmailContent` and `EmailAnalysis` dataclasses, custom field mapping definitions, constants.
- **`auth.py`**: Multi-fallback API key retrieval for ClickUp and Gemini (CLI → env → 1Password SDK/CLI → prompt).
- **`api_client.py`**: Extended ClickUp API client with POST/PUT support, custom field schema retrieval, list discovery, error handling.
- **`email_client.py`**: Protocol-based email extraction (`EmailClient` protocol), platform-specific implementations (Gmail, Outlook), URL parsing, fallback strategies.
- **`ai_summary.py`**: Google Gemini AI integration for email analysis, returns structured `EmailAnalysis` with title/description/priority/due_date/key_points.
- **`task_creator.py`**: `ClickUpTaskCreator` orchestrator, `TaskBuilder` for payload construction, field validation, API integration.
- **`mappers.py`**: Email field extraction, custom field mapping, type conversion, data transformation utilities.
- **`logger_config.py`**: Logging setup for debug and file output (reused pattern from Task Extractor).

### Data Flow
```
Email URL Input
    ↓
[Email Client] → Extract EmailContent
    ↓
[AI Summary] (optional) → Generate EmailAnalysis
    ↓
[Task Builder] → Build ClickUp task payload
    ↓
[Interactive Preview] (if enabled) → User confirms
    ↓
[ClickUp API Client] → POST /task endpoint
    ↓
Return task creation result (ID, URL, etc.)
```

## Key Patterns & Conventions

### Configuration & Enums
- All config uses enums (e.g., `EmailPlatform.GMAIL`, `CustomFieldType.TEXT`), but string fallbacks are supported for CLI compatibility.
- `ClickUpTaskConfig` dataclass contains all runtime configuration.
- `EmailContent` dataclass holds parsed email metadata (subject, body, sender, date, attachments).
- `EmailAnalysis` dataclass holds AI-extracted insights (title, description, priority, due_date, key_points, confidence).

### Protocol-Based Design
- Use `EmailClient` protocol for structural typing; enables testing, mocking, and platform extensibility.
- Implement specific clients (GmailClient, OutlookClient) by protocol; add factories in email_client.py.
- Use `APIClient` protocol pattern from Task Extractor; ClickUpAPIClient implements it.

### Authentication Chain
- API key retrieval priority: CLI arg → env var → 1Password SDK → CLI fallback → manual prompt.
- Use `load_secret_with_fallback()` from `auth.py` for both ClickUp and Gemini keys.
- 1Password references:
  - ClickUp: `op://Home Server/ClickUp personal API token/credential`
  - Gemini: `op://Home Server/nftoo3gsi3wpx7z5bdmcsvr7p4/credential` (or user-specific)

### Email Extraction
- Each platform (Gmail, Outlook) has URL parsing logic specific to its format.
- Fallback to web scraping (BeautifulSoup) if API access unavailable.
- Parse and sanitize email content; handle encoding edge cases.
- Extract metadata: sender, subject, body, date, attachments.

### AI Integration
- Optional Gemini summaries via `ai_summary.analyze_email()`.
- Returns structured JSON from Gemini; parse into `EmailAnalysis`.
- Implement retry logic for 429 rate limit responses with exponential backoff.
- Graceful fallback to basic extraction if AI unavailable or key missing.
- Use prompt engineering for consistent, JSON-parseable output.

### Custom Field Mapping
- Define field mappings in config (e.g., `custom_field_mappings` dict).
- Each mapping specifies ClickUp field ID, field type, and extraction rule.
- Validate field types before posting to API.
- Support TEXT, DATE, DROPDOWN, CHECKBOX, NUMBER types.
- Fetch field schema from ClickUp API to validate against list configuration.

### Rich UI & Prompts
- All user interaction (prompts, tables, previews, progress) uses Rich.
- Implement helpers in `mappers.py`: `get_email_url_input()`, `get_task_title_input()`, `get_confirmation_input()`.
- Show task preview before creation (if interactive mode enabled).
- Display success/error messages with Rich panels.

### Error Handling
- Always raise specific exceptions (e.g., `EmailExtractionError`, `APIError`, `TaskCreationError`).
- Never use bare except; catch and log specific exceptions.
- Provide user-friendly error messages via Rich console.
- Implement retry logic for transient failures (network, rate limit).
- Log API request/response details for debugging.

### Type Hints
- Use modern Python type hints everywhere (`list[str]`, `str | None`).
- Type hint function arguments and return types.
- Use dataclasses for structured data.

### File Output
- Log task creation results to `output/` (JSON with task ID, URL, timestamp).
- Use consistent naming: `CreatedTask_<timestamp>.json`.
- Create output directory if it doesn't exist.

## Developer Workflows

### Run the App
```bash
python main.py
python main.py --email-url "https://mail.google.com/mail/u/0/#inbox/..."
python main.py --email-url "..." --ai-summary --interactive
```

### Add a New Email Platform
1. Create new client class in `email_client.py` implementing `EmailClient` protocol.
2. Add `EmailPlatform` enum value in `config.py`.
3. Add URL parsing and extraction logic specific to the platform.
4. Update factory in `email_client.py` to instantiate your client.
5. Test with real URLs from that platform.

### Add a Custom Field Mapping
1. Define in `config.py` under `CUSTOM_FIELD_MAPPINGS`.
2. Implement extraction logic in `mappers.py`.
3. Validate field type matches ClickUp schema.
4. Test with sample emails.

### Extend Task Builder
- Modify `TaskBuilder.build_task_payload()` to add new field extraction.
- Update `TaskBuilder.validate_payload()` to enforce required fields.
- Ensure type conversion matches ClickUp API expectations.

### Add Authentication Method
- Extend `auth.py` with new fallback step.
- Update CLI in `main.py` to expose the new option.
- Keep fallback chain order consistent with Task Extractor.

### Debug
- Use `logger_config.setup_logging(logging.DEBUG)` for verbose output.
- Pass `log_file="debug.log"` to persist debug logs.
- Check logs for API request details, email parsing issues, AI response parsing.

## Integration Points

### ClickUp API v2
- All task data via ClickUp API v2 endpoints.
- POST `/team/{team_id}/task` to create tasks.
- GET `/list/{list_id}/field` to fetch custom field schema.
- GET `/space/{space_id}/list` to discover lists.
- Robust error handling for rate limits (429), auth errors (401), bad requests (400).

### Email Platforms
- **Gmail**: Requires Gmail API key or token; fallback to web scraping.
- **Outlook**: Requires Outlook API auth or web scraping fallback.
- URL parsing to extract message IDs; fetch via API or web scraping.

### Google Gemini AI
- Optional email analysis via `google-generativeai` SDK.
- Model: `gemini-2.5-flash-lite`.
- Structured JSON output (title, description, priority, due_date, key_points).
- Rate limit handling (429 with retry-after parsing).

### 1Password
- Secure API key storage and retrieval.
- SDK preferred (requires `OP_SERVICE_ACCOUNT_TOKEN`).
- CLI fallback (`op read` command).

### Rich
- All console UI (panels, tables, prompts, progress bars).
- Beautiful error messages and task previews.

## Examples

```bash
# Basic: Prompt for email URL
python main.py

# With email URL and AI summary
python main.py --email-url "https://mail.google.com/..." --ai-summary

# Interactive mode with custom workspace
python main.py --email-url "..." --workspace "MyWorkspace" --space "MySpace" --list "Tasks" --interactive

# With API keys from command line
python main.py --api-key YOUR_CLICKUP_KEY --gemini-api-key YOUR_GEMINI_KEY

# Without AI summary
python main.py --email-url "..." --no-ai-summary
```

## Building Executables

- PyInstaller spec file: `ClickUpTaskCreator.spec` (to be created).
- Build with: `.venv\Scripts\pyinstaller.exe ClickUpTaskCreator.spec --distpath .\dist\v<version>`
- Requires PyInstaller 6.16+: `pip install pyinstaller`.
- Output: Single-file executable with all dependencies bundled.
- Test with sample emails before distribution.

## Testing Strategy

- **Unit tests**: Mock email clients, AI API, ClickUp API. Test field mapping, payload building, validation.
- **Integration tests**: Real (or fixture) email URLs, real ClickUp API (optional, with cleanup).
- **Edge cases**:
  - Empty email bodies
  - Missing custom fields
  - API failures and rate limiting
  - Network timeouts
  - Invalid email URLs
  - Malformed email content
  - AI API unavailable or key missing

## Extension Playbook

### Add Email Field Extraction
1. Define extraction logic in `mappers.py`.
2. Add to custom field mapping in `config.py`.
3. Test with sample emails.

### New Custom Field Type
1. Add `CustomFieldType` enum value in `config.py`.
2. Implement type conversion in `TaskBuilder.build_task_payload()`.
3. Add validation in `TaskBuilder.validate_payload()`.

### New Email Platform
1. Create client class in `email_client.py` (implement `EmailClient` protocol).
2. Add `EmailPlatform` enum value in `config.py`.
3. Add URL parsing and content extraction.
4. Update factory/router logic.
5. Test with real URLs.

### Enhanced AI Analysis
1. Update prompt in `ai_summary.py`.
2. Adjust `EmailAnalysis` dataclass if new fields needed.
3. Update `TaskBuilder` to handle new analysis fields.

### Custom Field Schema Validation
1. Fetch field schema in `task_creator.py` before task creation.
2. Validate custom field values against schema.
3. Warn user of mismatches; optionally skip invalid fields.

## Dependencies

### Core
- `requests>=2.25.0` – HTTP requests for ClickUp/email APIs
- `rich>=14.0.0` – Beautiful CLI UI
- `google-generativeai>=0.8.0` – Gemini AI integration

### Optional
- `onepassword-sdk>=0.3.1` – Secure credential management
- `google-auth>=2.0.0` – Gmail API authentication
- `beautifulsoup4>=4.9.0` – Email web scraping fallback
- `selenium>=4.0.0` – Browser-based email extraction (advanced fallback)

### Development
- `pytest>=7.0.0` – Testing framework
- `pytest-cov>=4.0.0` – Code coverage
- `black>=22.0.0` – Code formatting
- `pyinstaller>=6.16.0` – Build executables

## Version Bumping & Releases

1. Update `version.py` with new `__version__` and metadata.
2. Add entry to `CHANGELOG.md` summarizing changes.
3. Create release branch: `git checkout -b release/v<version>`.
4. Commit version changes, tag with `git tag v<version>`.
5. Build executable with PyInstaller spec.
6. Create GitHub release with notes and executable attachment.

## Performance Considerations

- Email extraction should complete in < 2 seconds (API) or < 10 seconds (web scraping).
- AI analysis typically takes 3–5 seconds (Gemini API latency).
- Task creation via ClickUp API < 2 seconds.
- Total flow: < 15 seconds for typical case.
- Implement timeouts (30 seconds) for all API calls.
- Cache custom field schema locally to avoid repeated API calls.

## Security & Privacy

- Never hardcode API keys; always use CLI args, env vars, or 1Password.
- Don't log full email bodies; log only extracted fields.
- Validate email URLs before processing.
- Sanitize user input before passing to Gemini or ClickUp API.
- Respect email privacy; handle PII carefully.
- Store credentials in 1Password, never in config files.
- Use HTTPS for all API calls.

