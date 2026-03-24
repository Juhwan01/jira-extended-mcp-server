<p align="center">
  <h1 align="center">Jira Extended MCP Server</h1>
  <p align="center">
    <strong>Full-featured Jira Cloud integration for AI agents</strong><br />
    27 tools &middot; Bulk ops &middot; Rich text &middot; Sprints &middot; Releases &middot; Issue links
  </p>
  <p align="center">
    <a href="#-quick-start"><strong>Quick Start</strong></a> &middot;
    <a href="#-use-cases"><strong>Use Cases</strong></a> &middot;
    <a href="#-available-tools"><strong>Tools</strong></a> &middot;
    <a href="#%EF%B8%8F-configuration"><strong>Configuration</strong></a>
  </p>
</p>

<p align="center">
  <a href="https://pypi.org/project/jira-extended-mcp/"><img alt="PyPI" src="https://img.shields.io/pypi/v/jira-extended-mcp?style=flat-square" /></a>
  <a href="https://modelcontextprotocol.io"><img alt="MCP" src="https://img.shields.io/badge/MCP-v1.0-blue?style=flat-square" /></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" /></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" /></a>
</p>

---

> Built by **Moobean Team** — because existing Jira MCP integrations don't support `parent`, `fixVersions`, `startDate`, `dueDate`, issue links, or release management.

## Why This Server?

| | jira-mcp (npm) | AIRIS Gateway | **Jira Extended** |
|---|---|---|---|
| Issue CRUD | Read-only | Create/Update | **Full CRUD + Bulk** |
| Parent / Sub-task | - | - | **Supported** |
| fixVersions | - | - | **Supported** |
| startDate / dueDate | - | - | **Supported** |
| Issue Links | - | - | **Supported** |
| Release Management | - | - | **4 tools** |
| Sprint Management | - | Partial | **2 tools** |
| Rich Text | - | Plain text only | **Wiki markup** |
| Bulk Operations | - | - | **50 issues/call** |
| Total Tools | 2 | 18 | **27** |

## Use Cases

AI 에이전트에게 자연어로 요청하면 됩니다:

**이슈 관리**
> "KAN 프로젝트에 에픽 하나 만들어줘. 제목은 '사용자 인증 시스템', 시작일 4월 1일, 마감일 4월 30일"

> "KAN-42 에픽 아래에 스토리 5개 만들어줘: 로그인, 회원가입, 비밀번호 재설정, 소셜 로그인, 2FA"

> "KAN 프로젝트에서 '진행 중' 상태인 이슈 다 보여줘"

**벌크 작업**
> "이 스프린트 백로그 10개 이슈를 한번에 '완료'로 전환해줘"

> "v2.0 릴리스에 포함된 이슈 목록 보여줘"

**릴리스 & 스프린트**
> "KAN 프로젝트에 v2.1.0 릴리스를 만들어줘. 릴리스 날짜는 5월 15일"

> "현재 활성 스프린트에 KAN-50, KAN-51 이슈를 옮겨줘"

**이슈 링크**
> "KAN-10이 KAN-20을 블록하고 있다고 링크 걸어줘"

**리치 텍스트 (위키 마크업)**
> "이슈 설명에 h2 제목이랑 불릿 리스트 넣어서 만들어줘"

## Quick Start

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python package manager — installs Python automatically if needed)
- [Jira API Token](https://id.atlassian.com/manage-profile/security/api-tokens)

### Install

No clone needed. Just configure your AI client:

<details open>
<summary><b>Claude Code</b></summary>

**One-line install:**
```bash
claude mcp add jira-extended -e JIRA_URL=https://your-instance.atlassian.net -e JIRA_EMAIL=your-email@example.com -e JIRA_API_TOKEN=your-token -- uvx jira-extended-mcp
```

**Or add to** `.mcp.json` / `~/.claude.json`:
```json
{
  "mcpServers": {
    "jira-extended": {
      "command": "uvx",
      "args": ["jira-extended-mcp"],
      "env": {
        "JIRA_URL": "https://your-instance.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Add to `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "jira-extended": {
      "command": "uvx",
      "args": ["jira-extended-mcp"],
      "env": {
        "JIRA_URL": "https://your-instance.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

</details>

<details>
<summary><b>VS Code (GitHub Copilot)</b></summary>

Add to `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "jira-extended": {
      "command": "uvx",
      "args": ["jira-extended-mcp"],
      "env": {
        "JIRA_URL": "https://your-instance.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Make sure MCP is enabled under **Chat > MCP** in VS Code settings. Works in Agent mode.

</details>

<details>
<summary><b>Cursor</b></summary>

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "jira-extended": {
      "command": "uvx",
      "args": ["jira-extended-mcp"],
      "env": {
        "JIRA_URL": "https://your-instance.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

</details>

<details>
<summary><b>From source (development)</b></summary>

```bash
git clone https://github.com/moobean-team/jira-extended-mcp-server.git
cd jira-extended-mcp-server
uv pip install -e .
```

Then use `"command": "jira-extended-mcp"` instead of `"command": "uvx"` in your config.

</details>

### Done

Restart your AI client. The server starts automatically — no clone, no pip install, no venv needed.

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `JIRA_URL` | Yes | — | Jira Cloud instance URL |
| `JIRA_EMAIL` | Yes | — | Atlassian account email |
| `JIRA_API_TOKEN` | Yes | — | [API token](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_START_DATE_FIELD` | No | `customfield_10015` | Custom field ID for start date |

### Finding Your Start Date Field ID

The start date field ID varies per Jira instance. Use the `get_createmeta` tool for your project to see available fields, or:

```bash
curl -s -u email:token https://your-instance.atlassian.net/rest/api/2/field \
  | python -m json.tool | grep -i "start"
```

### Rich Text (Wiki Markup)

This server uses Jira REST API v2, which accepts **Jira wiki markup** strings for description and comment fields. Jira renders them as rich text automatically.

| Syntax | Renders as |
|---|---|
| `*bold*` | **bold** |
| `_italic_` | *italic* |
| `h2. Section Title` | H2 heading |
| `* item 1\n* item 2` | Bullet list |
| `# item 1\n# item 2` | Numbered list |
| `{code}print("hi"){code}` | Code block |
| `[Link Text\|https://url]` | Hyperlink |
| `\|col1\|col2\|\n\|a\|b\|` | Table |

Full reference: [Jira Wiki Markup](https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=texteffects)

## Available Tools

<details open>
<summary><b>Issue CRUD (6 tools)</b></summary>

| Tool | Description |
|---|---|
| `create_issue` | Create issue with full field support — parent, fixVersions, startDate, dueDate, story points, components, custom fields |
| `create_issues_bulk` | Bulk create up to 50 issues in a single API call |
| `get_issue` | Get issue details with formatted output |
| `update_issue` | Update any issue field (only changed fields are sent) |
| `delete_issue` | Delete issue with subtask handling |
| `search_issues` | JQL search with pagination and configurable fields |

</details>

<details>
<summary><b>Transitions (3 tools)</b></summary>

| Tool | Description |
|---|---|
| `get_transitions` | List available status transitions for an issue |
| `transition_issue` | Change issue status by name or ID, with optional comment |
| `bulk_transition` | Transition multiple issues at once |

</details>

<details>
<summary><b>Issue Links (3 tools)</b></summary>

| Tool | Description |
|---|---|
| `link_issues` | Create link between issues (Blocks, Relates, Duplicate, Cloners) |
| `get_issue_links` | Get all links for an issue with link type details |
| `delete_issue_link` | Remove a link by ID |

</details>

<details>
<summary><b>Release Management (4 tools)</b></summary>

| Tool | Description |
|---|---|
| `get_versions` | List project versions/releases |
| `create_version` | Create a new release with start/release dates |
| `update_version` | Update release details, mark as released/archived |
| `delete_version` | Delete a release with issue reassignment options |

</details>

<details>
<summary><b>Sprint Management (2 tools)</b></summary>

| Tool | Description |
|---|---|
| `get_sprints` | List sprints for a board (filter by active/future/closed) |
| `move_to_sprint` | Move issues to a target sprint |

</details>

<details>
<summary><b>Comments & Worklogs (3 tools)</b></summary>

| Tool | Description |
|---|---|
| `add_comment` | Add comment to an issue (supports wiki markup) |
| `get_comments` | Get issue comments with author and timestamps |
| `add_worklog` | Log work time with human-friendly format ("2h 30m", "1d") |

</details>

<details>
<summary><b>Project & Metadata (6 tools)</b></summary>

| Tool | Description |
|---|---|
| `get_projects` | List all accessible projects |
| `get_project` | Get project details |
| `get_boards` | List boards (scrum/kanban/simple) |
| `get_current_user` | Get authenticated user info |
| `search_users` | Search users by name/email |
| `get_createmeta` | Get available issue types and fields per project |

</details>

## Architecture

```
src/jira_extended_mcp/
├── server.py    # FastMCP server + 27 tool definitions
├── client.py    # Async Jira REST client (httpx + rate limit retry)
├── adf.py       # ADF fallback helpers (v3 response parsing)
└── __init__.py
```

**Key design decisions:**

| Decision | Why |
|---|---|
| **REST API v2** for issues/comments | v2 accepts wiki markup strings → rich text. v3 requires ADF JSON which strips formatting |
| **REST API v3** for metadata | Versions, projects, users don't have text fields — v3 is fine |
| **Agile API** for sprints/boards | Sprint ops are only available via `/rest/agile/1.0/` |
| **FastMCP lifespan** | `httpx.AsyncClient` pooled across tool calls, not per-request |
| **Structured errors** | Errors return `{error, status}` dicts so the LLM gets actionable feedback |
| **Configurable start date field** | `JIRA_START_DATE_FIELD` env var handles instance-specific custom field IDs |

## Development

```bash
git clone https://github.com/moobean-team/jira-extended-mcp-server.git
cd jira-extended-mcp-server
uv pip install -e .

# Run directly
jira-extended-mcp

# Or via module
python -m jira_extended_mcp.server
```

## Troubleshooting

<details>
<summary><b>"Missing required env vars"</b></summary>

Ensure `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` are set in your MCP config's `env` block. The server checks these on startup.

</details>

<details>
<summary><b>"Transition not found"</b></summary>

Jira transitions are workflow-specific. Use `get_transitions` first to see available transitions for the issue's current status. Transition names are case-insensitive.

</details>

<details>
<summary><b>Start date not saving</b></summary>

Your Jira instance may use a different custom field ID. Use `get_createmeta` to find the correct field, then set `JIRA_START_DATE_FIELD` env var.

</details>

<details>
<summary><b>Rate limited (429)</b></summary>

The server automatically retries up to 3 times using the `Retry-After` header. For bulk operations with 50+ issues, consider splitting into multiple calls.

</details>

<details>
<summary><b>Description shows as plain text</b></summary>

This server uses Jira REST API v2 which accepts wiki markup. Use Jira wiki syntax (`*bold*`, `h2. Title`, `* bullet`) instead of Markdown.

</details>

## License

[MIT](LICENSE) &copy; Moobean Team
