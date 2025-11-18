# ClickUp Task Creator 📧➡️📋

A powerful, cross-platform Python application for creating ClickUp tasks directly from email URLs with AI-powered field population using Google Gemini.

![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Version](https://img.shields.io/badge/version-0.01-green.svg)
![Rich](https://img.shields.io/badge/rich-14.0%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🔗 **Email URL Input**: Paste an email URL (Gmail, Outlook, etc.) to create a task
- 📧 **Email Extraction**: Automatically extract email content, metadata, and attachments
- 🤖 **AI Summaries**: Optional Google Gemini AI integration for intelligent email analysis
- 🎯 **Smart Field Population**: Automatically populate ClickUp custom fields based on email content
- 🔐 **Secure Authentication**: Multiple authentication methods including 1Password integration
- 🎨 **Beautiful UI**: Rich console interfaces with panels, prompts, and styled output
- 📋 **Interactive Preview**: Review and confirm task details before creation
- 🌐 **Cross-Platform**: Works on Windows, macOS, and Linux
- ⚡ **Modern Architecture**: Clean, modular design following SOLID principles

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- ClickUp API token
- Optional: 1Password CLI or SDK for secure credential management
- Optional: Google Gemini API key for AI email analysis
- Optional: Gmail/Outlook API credentials for email extraction

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/J-MaFf/clickup_task_creator.git
   cd clickup_task_creator
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**

   On Windows:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   On macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your credentials** (choose one method):
   - Command line: `python main.py --api-key YOUR_CLICKUP_API_KEY --gemini-api-key YOUR_GEMINI_KEY`
   - Environment variables: `export CLICKUP_API_KEY=YOUR_KEY` and `export GEMINI_API_KEY=YOUR_KEY`
   - 1Password: Store in 1Password with reference `op://Home Server/ClickUp personal API token/credential`

### Basic Usage

```bash
# Run with interactive prompts
python main.py

# Create task from specific email URL
python main.py --email-url "https://mail.google.com/mail/u/0/#inbox/..."

# Enable AI analysis
python main.py --email-url "..." --ai-summary

# Interactive mode with preview before creation
python main.py --email-url "..." --interactive

# Specify target workspace, space, and list
python main.py --workspace "MyWorkspace" --space "MySpace" --list "Tasks"
```

## 🔧 Development Workflow

- Install deps via `pip install -r requirements.txt`
- Run the creator with `python main.py`
- Override defaults with CLI flags: `--email-url`, `--api-key`, `--gemini-api-key`, `--workspace`, `--space`, `--list`, `--ai-summary`, `--interactive`
- Authentication falls back in this order: CLI flag → env var → 1Password SDK → 1Password CLI → manual prompt
- Logging comes from `logger_config.setup_logging`; pass `use_rich=False` for plain output or a `log_file` path to persist logs

## 📖 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--email-url` | Email URL to process | Prompted if not specified |
| `--api-key` | ClickUp API key | From environment or 1Password |
| `--gemini-api-key` | Google Gemini API key | From 1Password or environment |
| `--workspace` | Workspace name | Prompted if not specified |
| `--space` | Space name | Prompted if not specified |
| `--list` | List name | Prompted if not specified |
| `--ai-summary` | Enable AI email analysis | Prompted if not specified |
| `--interactive` | Show preview before creation | `False` |
| `--email-platform` | Email platform: `GMAIL`, `OUTLOOK` | Auto-detect from URL |

## 🏗️ Architecture

```text
clickup_task_creator/
├── main.py                    # CLI entry, venv handoff, config assembly, auth chain
├── config.py                  # Config dataclass, enums, EmailContent/EmailAnalysis
├── auth.py                    # 1Password SDK/CLI loader with structured logging
├── api_client.py              # ClickUp API client (GET, POST, PUT with 30s timeout)
├── email_client.py            # Email extraction protocol & platform implementations
├── ai_summary.py              # Gemini analysis with retry/backoff and graceful fallback
├── task_creator.py            # Main workflow, TaskBuilder, field mapping
├── mappers.py                 # Email field extraction, custom field builders
├── logger_config.py           # Rich-enhanced logging setup
├── version.py                 # Version metadata
├── requirements.txt           # Dependency manifest
├── PLAN.md                    # Detailed development plan
├── CHANGELOG.md               # Version history
└── tests/                     # Unit and integration tests
    ├── test_config.py
    ├── test_auth.py
    ├── test_email_client.py
    ├── test_api_client.py
    ├── test_ai_summary.py
    ├── test_task_creator.py
    └── test_main.py
```

### Key Components

- **`main.py`**: Builds `ClickUpTaskConfig`, orchestrates auth fallback, and manages CLI interaction.
- **`ClickUpTaskConfig` & `EmailContent`**: Enum-backed config and structured data classes for configuration and email data.
- **`ClickUpTaskCreator`**: Orchestrates the complete workflow: email extraction → AI analysis → task creation.
- **`EmailClient` protocol**: Extensible interface for email platform implementations (Gmail, Outlook, etc.).
- **`TaskBuilder`**: Constructs ClickUp API payloads with intelligent field mapping from email data.
- **`ai_summary.analyze_email`**: Talks to Google Gemini (`gemini-2.5-flash-lite`), parses structured JSON output, and falls back gracefully.
- **`logger_config.setup_logging`**: Installs Rich tracebacks and optional file logging.

## 🤖 AI Integration

Optional Google Gemini AI integration provides:

- Intelligent email analysis and summarization
- Automatic title suggestion from email content
- Priority level extraction
- Due date detection from email text
- Key action items identification
- Automatic rate limiting and retry logic
- Graceful fallback if AI is unavailable

Enable AI analysis:

```bash
python main.py --ai-summary --gemini-api-key YOUR_KEY
```

Implementation details:

- Uses `gemini-2.5-flash-lite` via the official `google-generativeai` SDK
- Retries up to three times on 429s, parsing `retryDelay` hints when available
- Falls back to basic email parsing when the SDK is missing or key is unavailable
- Returns structured `EmailAnalysis` with confidence scores

## 🛠️ Requirements

### Core Dependencies

- `requests>=2.25.0` - HTTP client for ClickUp API and email extraction
- `rich>=14.0.0` - Beautiful console interfaces
- `google-generativeai>=0.8.0` - Google Gemini AI integration

### Optional Dependencies

- `onepassword-sdk>=0.3.1` - Secure credential management
- `google-auth>=2.0.0` - Gmail API authentication
- `beautifulsoup4>=4.9.0` - Email web scraping fallback
- `selenium>=4.0.0` - Browser-based email extraction fallback

## 📊 Data Flow

```
User Input (Email URL)
        ↓
[Email Client] → Extract email content
        ↓
[AI Summary] → Analyze email (if enabled)
        ↓
[Task Builder] → Build ClickUp task payload
        ↓
[Interactive Preview] (if enabled) → User confirms
        ↓
[ClickUp API Client] → POST task to ClickUp
        ↓
Return task ID and link
```

## 🔐 Authentication

### ClickUp API Key

Store in 1Password for reuse:

- Reference: `op://Home Server/ClickUp personal API token/credential`

Retrieve in priority order:

1. `--api-key` CLI argument
2. `CLICKUP_API_KEY` environment variable
3. 1Password SDK (requires `OP_SERVICE_ACCOUNT_TOKEN`)
4. 1Password CLI (requires `op` command)
5. Manual prompt

### Gemini API Key

Store in 1Password:

- Reference: `op://Home Server/nftoo3gsi3wpx7z5bdmcsvr7p4/credential`

Retrieve same priority as ClickUp key, or set `GEMINI_API_KEY` environment variable.

## 🐛 Troubleshooting

### Common Issues

**Authentication Errors:**

- Verify your ClickUp API key is valid
- Check 1Password integration setup
- Ensure environment variables are set correctly

**Email Extraction Fails:**

- Verify email URL is correct and accessible
- Check email platform support (Gmail, Outlook)
- Enable fallback web scraping if API unavailable

**AI Analysis Unavailable:**

- Check Gemini API key is valid
- Verify internet connectivity
- Check rate limits (AI summaries auto-retry with backoff)

**Task Creation Fails:**

- Verify custom field names match ClickUp schema
- Check workspace/space/list names exist
- Ensure user has permissions to create tasks

### Debug Mode

Enable detailed logging:

```bash
python main.py --log-level DEBUG --log-file debug.log
```

## 🧪 Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## 📝 Development Workflow

### Add a New Email Platform

1. Create client class in `email_client.py` implementing `EmailClient` protocol
2. Add `EmailPlatform` enum value in `config.py`
3. Implement URL parsing and content extraction
4. Update factory/router logic
5. Add tests in `tests/test_email_client.py`

### Add Custom Field Mapping

1. Define in `config.py` under `CUSTOM_FIELD_MAPPINGS`
2. Implement extraction logic in `mappers.py`
3. Validate field type matches ClickUp schema
4. Test with sample emails

### Extend AI Analysis

1. Update prompt in `ai_summary.py`
2. Adjust `EmailAnalysis` dataclass if new fields needed
3. Update `TaskBuilder` to handle new fields
4. Test with various email formats

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/new-feature`
3. Follow the existing code style and architecture patterns
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful console output
- Uses [1Password SDK](https://github.com/1Password/onepassword-sdk-python) for secure credential management
- Powered by [Google Gemini AI](https://ai.google.dev/) for intelligent email analysis
- Integrates with [ClickUp API v2](https://clickup.com/api) for task management

---

Made with ❤️ for productivity and beautiful code
