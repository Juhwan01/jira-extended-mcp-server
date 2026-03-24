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

<p align="center">
  <a href="README.ko.md">한국어</a> | English
</p>

---

> Built by **Moobean Team** — a lightweight, Jira-only MCP server focused on getting things done with minimal setup.

## What Makes This Different

- **Jira-only, zero bloat** — No Confluence, no extra modules. One `uvx` command and you're running.
- **Wiki markup support** — Uses Jira REST API v2, so `*bold*`, `h2. Title`, `* bullet` just work. No ADF JSON hassle.
- **Bulk operations** — Create up to 50 issues or transition multiple issues in a single call.
- **Full release lifecycle** — Create, update, delete versions and assign issues to releases.
- **Issue links** — Block, relate, duplicate, clone — with create, query, and delete support.

## Comparison

> **Note:** Feature data is based on each project's README and documentation as of March 2026. Features may have changed since then.

| | [jira-mcp](https://github.com/CamdenClark/jira-mcp) | [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) | [Atlassian Rovo MCP](https://github.com/atlassian/atlassian-mcp-server) | **Jira Extended** |
|---|---|---|---|---|
| Scope | Jira only | Jira + Confluence | Jira + Confluence + Compass | Jira only |
| Issue CRUD | Read-only | Full CRUD | Full CRUD | Full CRUD |
| Bulk Create | - | Supported | Supported | **50 issues/call** |
| Bulk Transition | - | - | - | **Supported** |
| Parent / Sub-task | - | Supported | Supported | Supported |
| fixVersions | - | Supported | Supported | Supported |
| startDate / dueDate | - | Supported | Supported | Supported |
| Issue Links | - | Supported | - | Supported |
| Release Management | - | - | - | **4 tools** |
| Sprint Management | - | Supported | - | Supported |
| Rich Text | - | Markdown → ADF | ADF | **Wiki markup (v2 API)** |
| Setup | npm | pip / Docker | OAuth (cloud-hosted) | **`uvx` one-liner** |
| Total Jira Tools | 2 | ~30 (Jira portion) | ~25 (Jira portion) | 27 |
| Language | TypeScript | Python | Remote (SaaS) | Python |

## Use Cases

Just ask your AI agent in natural language:

**Issue Management**
> "Create an epic in the KAN project titled 'User Auth System', start date April 1st, due date April 30th"

> "Create 5 stories under KAN-42: Login, Sign Up, Password Reset, Social Login, 2FA"

> "Show me all 'In Progress' issues in the KAN project"

**Bulk Operations**
> "Transition all 10 backlog issues in this sprint to 'Done'"

> "Show me the issue list included in the v2.0 release"

**Releases & Sprints**
> "Create a v2.1.0 release in KAN project with release date May 15th"

> "Move KAN-50 and KAN-51 to the current active sprint"

**Issue Links**
> "Link KAN-10 as blocking KAN-20"

**Rich Text (Wiki Markup)**
> "Create an issue with h2 headings and bullet lists in the description"

## Quick Start

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python package manager — installs Python automatically if needed)
- [Jira API Token](https://id.atlassian.com/manage-profile/security/api-tokens)

### Step 1: Install uv

`uv` is a Python package manager. If you don't have it:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Get a Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Copy the token — you'll need it in the next step

### Step 3: Configure your AI client

Choose where to add the config:

| Scope | File | Effect |
|---|---|---|
| **Global** (recommended) | `~/.claude.json` | Available in all projects |
| **Project only** | `.mcp.json` in project root | Only in that project |

<details open>
<summary><b>Claude Code</b></summary>

**Easiest — one command:**
```bash
# macOS / Linux
claude mcp add jira-extended -s user \
  -e JIRA_URL=https://your-instance.atlassian.net \
  -e JIRA_EMAIL=your-email@example.com \
  -e JIRA_API_TOKEN=your-token \
  -- uvx jira-extended-mcp

# Windows — use uvx.exe (not uvx) to avoid .cmd wrapper issues
claude mcp add jira-extended -s user \
  -e JIRA_URL=https://your-instance.atlassian.net \
  -e JIRA_EMAIL=your-email@example.com \
  -e JIRA_API_TOKEN=your-token \
  -- uvx.exe jira-extended-mcp
```

> `-s user` installs globally. Omit it for project-only install.

**Or edit the config file manually:**

Open the file in a text editor:
```bash
# macOS / Linux
code ~/.claude.json    # or: nano ~/.claude.json

# Windows
notepad %USERPROFILE%\.claude.json
```

Add this content (create the file if it doesn't exist):
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

> **Windows users:** Use `"command": "uvx.exe"` instead of `"command": "uvx"`. The `uvx.cmd` wrapper on Windows breaks the MCP stdio transport.

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Open the config file in a text editor:
```bash
# macOS
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add or merge into the file:
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

> If the file already has other MCP servers, add the `"jira-extended": {...}` block inside the existing `"mcpServers"` object.
>
> **Windows users:** Use `"command": "uvx.exe"` instead of `"command": "uvx"`.

</details>

<details>
<summary><b>VS Code (GitHub Copilot)</b></summary>

Create `.vscode/mcp.json` in your project root:
```bash
mkdir -p .vscode
code .vscode/mcp.json
```

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

> Enable MCP: **Settings > Chat > MCP** must be checked. Works in Agent mode.
>
> **Windows users:** Use `"command": "uvx.exe"` instead of `"command": "uvx"`.

</details>

<details>
<summary><b>Cursor</b></summary>

Open the config file:
```bash
# macOS / Linux
code ~/.cursor/mcp.json

# Windows
notepad %USERPROFILE%\.cursor\mcp.json
```

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

> **Windows users:** Use `"command": "uvx.exe"` instead of `"command": "uvx"`.

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

### Step 4: Restart & verify

Restart your AI client, then ask:

> "Show my Jira projects"

If you see your project list, you're all set.

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
| **REST API v2** for issues/comments | v2 accepts wiki markup strings for rich text. v3 requires ADF JSON which strips formatting |
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
