# ClickUp Task Creator - Development Plan 📋

## Overview

The ClickUp Task Creator is a Python application that enables efficient task creation in ClickUp directly from email messages. Users can copy an email URL and use it to automatically create a new ClickUp task, with custom fields intelligently populated using Google Gemini AI summarization of the email content.

## Requirements

### Functional Requirements

1. **Email URL Input**
   - Accept a URL/URI of an email message
   - Support multiple email platforms (Gmail, Outlook, etc.)
   - Parse email content from the provided URL

2. **Email Content Extraction**
   - Extract email subject, body, sender, date, and attachments
   - Parse email metadata
   - Handle various email formats and encodings

3. **AI-Powered Summarization**
   - Use Google Gemini API to generate intelligent email summaries
   - Extract key information from email content:
     - Task title (from subject or summarized content)
     - Description/details
     - Priority level
     - Due date (if mentioned in email)
     - Custom fields (based on email context)
   - Support graceful fallback when AI is unavailable

4. **ClickUp Task Creation**
   - Create tasks in ClickUp via API v2
   - Populate custom fields based on:
     - Extracted email metadata
     - AI-generated summaries
     - User-defined field mappings
   - Support task assignment
   - Add email content as task attachments
   - Link email sender information

5. **Configuration & Customization**
   - Configurable custom field mappings
   - Task list selection
   - Priority mapping rules
   - User authentication (ClickUp API, Email, Gemini)
   - Multiple email platform support

6. **User Interface**
   - Interactive CLI with Rich formatting
   - Configuration prompts
   - Task preview before creation
   - Success/error feedback
   - Logging and debugging

### Non-Functional Requirements

- Cross-platform compatibility (Windows, macOS, Linux)
- Secure credential management (1Password integration)
- Modular architecture (following SOLID principles)
- Comprehensive error handling
- Rate limit handling
- Timeout management

## Architecture

### Directory Structure

```yaml
clickup_task_creator/
├── main.py                    # CLI entry point, venv handoff, config assembly
├── config.py                  # Config dataclass, enums, constants, email platform defs
├── auth.py                    # Authentication chain (1Password, env vars, manual input)
├── api_client.py              # ClickUp API client (GET, POST, PUT requests)
├── email_client.py            # Email content extraction (Gmail, Outlook, etc.)
├── ai_summary.py              # Gemini API integration for email analysis
├── task_creator.py            # Core task creation workflow & field mapping
├── mappers.py                 # Email field mappers, custom field builders
├── logger_config.py           # Rich-enhanced logging setup
├── version.py                 # Version info (__version__, __description__)
├── requirements.txt           # Dependency manifest
├── tests/                     # Unit & integration tests
│   ├── test_config.py
│   ├── test_auth.py
│   ├── test_email_client.py
│   ├── test_api_client.py
│   ├── test_ai_summary.py
│   ├── test_task_creator.py
│   └── test_main.py
├── output/                    # Created task details (JSON logs)
├── README.md                  # User documentation
└── CHANGELOG.md               # Version history
```

### Core Components

#### 1. **config.py**

- `ClickUpTaskConfig`: Configuration dataclass
  - `api_key`: ClickUp API token
  - `gemini_api_key`: Google Gemini API key
  - `workspace_name`: Target workspace
  - `space_name`: Target space
  - `list_name`: Target list
  - `custom_field_mappings`: Dict of field name → extraction rules
  - `enable_ai_summary`: Boolean to enable/disable AI
  - `email_platform`: Type of email (GMAIL, OUTLOOK, etc.)
- `EmailPlatform`: Enum for supported email systems
- `CustomFieldType`: Enum for custom field types (TEXT, DATE, DROPDOWN, CHECKBOX)
- `EmailContent`: Dataclass for parsed email data
- Constants for API endpoints, timeout values

#### 2. **email_client.py**

- `EmailClient` (Protocol): Interface for email extraction
- `GmailClient`: Extract email from Gmail URLs
  - Parse `?msgid=` parameter
  - Fetch email via Gmail API or web scraping fallback
  - Extract subject, body, sender, date, attachments
- `OutlookClient`: Extract email from Outlook URLs
  - Parse message ID from URL
  - Fetch email content
- `EmailExtractor`: Factory pattern for creating appropriate client
- Methods:
  - `extract_email(url: str) -> EmailContent`
  - `get_email_summary(email_content: EmailContent) -> str`

#### 3. **api_client.py** (Enhanced from Task Extractor)

- `ClickUpAPIClient`: Extend with POST/PUT support
- New methods:
  - `post(endpoint: str, data: dict) -> Any`: Create resources
  - `put(endpoint: str, data: dict) -> Any`: Update resources
  - `get_custom_fields(list_id: str) -> List[dict]`: Fetch field schema
  - `get_lists(space_id: str) -> List[dict]`: Get available lists
- Error handling for rate limiting (429 responses)
- Retry logic with exponential backoff

#### 4. **ai_summary.py** (Enhanced from Task Extractor)

- `analyze_email(email_content: EmailContent, gemini_api_key: str) -> EmailAnalysis`
- `EmailAnalysis` dataclass:
  - `title`: Suggested task title
  - `description`: Task description/summary
  - `priority`: Extracted priority (Low/Normal/High/Urgent)
  - `due_date`: Extracted due date (if mentioned)
  - `key_points`: List of important action items
  - `confidence`: Confidence score for extraction
- Retry logic for rate limiting (429)
- Graceful fallback to basic extraction
- Support for structured JSON output from Gemini

#### 5. **task_creator.py** (Main workflow)

- `ClickUpTaskCreator`: Orchestrator class
  - `create_task_from_email(email_url: str) -> dict`
  - Workflow:
       1. Parse email URL
       2. Extract email content
       3. Run AI analysis (optional)
       4. Build custom fields dict
       5. Validate task data
       6. Call ClickUp API to create task
       7. Return task details/link
- `TaskBuilder`: Helper for constructing task payloads
  - Map email fields to ClickUp custom fields
  - Handle type conversions
  - Validate required fields
- Methods:
  - `build_task_payload(email: EmailContent, analysis: EmailAnalysis) -> dict`
  - `validate_payload(payload: dict) -> bool`

#### 6. **mappers.py**

- `map_email_field(email_field: str, field_type: CustomFieldType) -> Any`
- `extract_priority(email_content: EmailContent) -> str`
- `extract_due_date(email_content: EmailContent) -> Optional[str]`
- `build_custom_field_value(value: str, field_type: CustomFieldType) -> Any`
- Prompt helpers:
  - `get_email_url_input() -> str`
  - `get_task_title_input(suggestion: str) -> str`
  - `get_confirmation_input(task_payload: dict) -> bool`

#### 7. **main.py**

- CLI argument parsing:
  - `--email-url`: Email URL to process
  - `--api-key`: ClickUp API key
  - `--gemini-api-key`: Gemini API key
  - `--workspace`: Workspace name
  - `--space`: Space name
  - `--list`: List name
  - `--ai-summary`: Enable AI analysis
  - `--interactive`: Show preview before creation
  - `--email-platform`: Email platform type
- Authentication chain:
     1. CLI arguments
     2. Environment variables
     3. 1Password SDK
     4. 1Password CLI
     5. Manual prompts
- Orchestration:
  - Display header/welcome
  - Load configuration
  - Create task
  - Display results

#### 8. **logger_config.py**

- Reuse from Task Extractor
- Configure Rich logging
- Support log files
- DEBUG/INFO/ERROR levels

## Data Flow

```text
User Input (Email URL)
        ↓
[Email Client] → Extract email content
        ↓
[AI Summary] → Analyze email (if enabled)
        ↓
[Task Builder] → Build ClickUp task payload
        ↓
[Interactive Preview] (optional) → User confirms
        ↓
[ClickUp API Client] → POST task to ClickUp
        ↓
Return task link/ID
```

## Implementation Phases

### Phase 1: Foundation (Core Infrastructure)

- [ ] Set up project structure and files
- [ ] Implement `config.py` with ClickUpTaskConfig
- [ ] Implement `auth.py` with fallback chain
- [ ] Implement `api_client.py` with POST/PUT methods
- [ ] Implement `logger_config.py` (reuse from extractor)
- [ ] Add `version.py` and `requirements.txt`

### Phase 2: Email Extraction

- [ ] Implement `email_client.py` with protocols
- [ ] Implement Gmail URL parsing
- [ ] Implement Outlook URL parsing
- [ ] Add email content extraction logic
- [ ] Create fallback for web scraping
- [ ] Write tests for email clients

### Phase 3: AI Integration

- [ ] Implement `ai_summary.py` email analysis
- [ ] Define `EmailAnalysis` dataclass
- [ ] Add Gemini API integration
- [ ] Implement retry logic for rate limiting
- [ ] Add fallback to basic extraction
- [ ] Write tests for AI summarization

### Phase 4: Task Creation

- [ ] Implement `task_creator.py` main workflow
- [ ] Implement `TaskBuilder` class
- [ ] Implement `mappers.py` field mapping
- [ ] Add custom field validation
- [ ] Handle ClickUp API responses
- [ ] Write comprehensive tests

### Phase 5: CLI & User Experience

- [ ] Implement `main.py` CLI
- [ ] Add interactive prompts
- [ ] Create task preview
- [ ] Add success/error messages
- [ ] Implement logging
- [ ] Add configuration validation

### Phase 6: Testing & Documentation

- [ ] Write unit tests for all modules
- [ ] Add integration tests
- [ ] Create comprehensive README
- [ ] Document custom field mappings
- [ ] Create troubleshooting guide
- [ ] Add usage examples

### Phase 7: Polish & Distribution

- [ ] Error handling edge cases
- [ ] Performance optimization
- [ ] Add rate limit handling
- [ ] Create PyInstaller spec file
- [ ] Build executable
- [ ] Create release notes

## Key Implementation Details

### Email URL Parsing

**Gmail:**

- URL format: `https://mail.google.com/mail/u/0/#inbox/...`
- Extract message ID from URL parameter
- Use Gmail API (requires auth) or web scraping fallback

**Outlook:**

- URL format: `https://outlook.office.com/mail/...`
- Extract message ID
- Use Outlook REST API or web scraping fallback

**Fallback:** Web scraping with BeautifulSoup if APIs unavailable

### Custom Field Mapping

Example mapping configuration:

```python
CUSTOM_FIELD_MAPPINGS = {
    "Email From": {"type": "TEXT", "extractor": lambda e: e.sender},
    "Email Subject": {"type": "TEXT", "extractor": lambda e: e.subject},
    "Priority": {"type": "DROPDOWN", "extractor": "ai_priority"},
    "Due Date": {"type": "DATE", "extractor": "ai_due_date"},
    "Assigned To": {"type": "DROPDOWN", "extractor": "default_assignee"},
}
```

### AI Analysis Prompt

```text
Analyze this email and extract:
1. A concise task title (5-10 words)
2. Task description (1-2 sentences)
3. Priority level (Low/Normal/High/Urgent)
4. Due date (if mentioned)
5. Key action items (bullet list)

Return as JSON with keys: title, description, priority, due_date, key_points
```

### Error Handling Strategy

- **Email Extraction Failures**: Prompt user for manual title/description
- **AI Analysis Failures**: Fall back to basic email parsing
- **API Rate Limiting**: Retry with exponential backoff
- **Invalid Custom Fields**: Validate against list schema, warn user
- **Network Errors**: Log and provide retry option

## Dependencies

### Core

- `requests>=2.25.0` - HTTP requests
- `rich>=14.0.0` - Beautiful CLI
- `google-generativeai>=0.8.0` - Gemini API

### Optional

- `onepassword-sdk>=0.3.1` - Secure credentials
- `google-auth>=2.0.0` - Gmail API auth
- `beautifulsoup4>=4.9.0` - Email web scraping fallback
- `selenium>=4.0.0` - Browser-based email extraction fallback

### Development

- `pytest>=7.0.0` - Testing
- `pytest-cov>=4.0.0` - Coverage
- `black>=22.0.0` - Code formatting

## Testing Strategy

- **Unit Tests**: Mock APIs, test individual functions
- **Integration Tests**: Real API calls (optional, with fixtures)
- **Edge Cases**:
  - Empty email bodies
  - Missing fields
  - API failures
  - Rate limiting
  - Network timeouts
  - Invalid URLs
  - Malformed emails

## Security Considerations

1. **API Key Management**
   - Store in 1Password
   - Use environment variables
   - Never hardcode credentials
   - Mask keys in logs

2. **Email Privacy**
   - Don't store email bodies in logs
   - Delete temporary files
   - Validate email URLs
   - Respect user privacy

3. **AI API Safety**
   - Rate limiting
   - Input validation
   - Error handling
   - Retry limits

## Success Metrics

- ✅ Create tasks from email URLs
- ✅ Populate custom fields automatically
- ✅ AI analysis works > 90% of the time
- ✅ < 5 second task creation time
- ✅ Cross-platform compatibility
- ✅ Comprehensive error messages
- ✅ Test coverage > 80%

## Future Enhancements

1. **Batch Processing**: Create multiple tasks from email thread
2. **Email Forwarding**: Forward emails to special address to auto-create tasks
3. **Recurring Tasks**: Extract recurrence patterns from emails
4. **Task Linking**: Link related tasks from email references
5. **Webhook Integration**: Trigger from email server webhooks
6. **UI Desktop App**: PyQt/Tkinter GUI instead of CLI
7. **Mobile App**: Mobile wrapper for task creation
8. **Smart Attachment Handling**: Upload attachments to task
9. **Team Collaboration**: Auto-assign based on email recipients
10. **Analytics**: Track created tasks, success rates, timing

---

**Created**: November 18, 2025
**Project**: ClickUp Task Creator
**Status**: Planning Phase
