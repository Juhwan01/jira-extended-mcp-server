"""Jira Extended MCP Server - 27 tools for full Jira Cloud integration."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastmcp import Context, FastMCP

from .client import JiraClient

# ---------------------------------------------------------------------------
# Lifespan: manage JiraClient lifecycle
# ---------------------------------------------------------------------------


@dataclass
class AppContext:
    jira: JiraClient


@asynccontextmanager
async def lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    client = JiraClient()
    try:
        yield AppContext(jira=client)
    finally:
        await client.close()


mcp = FastMCP(
    "Jira Extended",
    instructions=(
        "Full-featured Jira Cloud MCP server. "
        "Supports issue CRUD, bulk operations, transitions, "
        "issue links, releases, sprints, comments, and more."
    ),
    lifespan=lifespan,
)


def _jira(ctx: Context) -> JiraClient:
    """Extract JiraClient from lifespan context."""
    return ctx.request_context.lifespan_context.jira


# ---------------------------------------------------------------------------
# Helper: build issue fields dict
# ---------------------------------------------------------------------------


def _build_issue_fields(
    jira: JiraClient,
    *,
    project: str,
    issue_type: str,
    summary: str,
    description: str | None = None,
    assignee_id: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    parent: str | None = None,
    fix_versions: list[str] | None = None,
    components: list[str] | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    story_points: float | None = None,
    custom_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build Jira issue fields payload."""
    fields: dict[str, Any] = {
        "project": {"key": project},
        "issuetype": {"name": issue_type},
        "summary": summary,
    }

    if description:
        fields["description"] = description
    if assignee_id:
        fields["assignee"] = {"id": assignee_id}
    if priority:
        fields["priority"] = {"name": priority}
    if labels:
        fields["labels"] = labels
    if parent:
        fields["parent"] = {"key": parent}
    if fix_versions:
        fields["fixVersions"] = [{"name": v} for v in fix_versions]
    if components:
        fields["components"] = [{"name": c} for c in components]
    if start_date:
        fields[jira.start_date_field] = start_date
    if due_date:
        fields["duedate"] = due_date
    if story_points is not None:
        fields["story_points"] = story_points
    if custom_fields:
        fields.update(custom_fields)

    return fields


def _format_issue(issue: dict[str, Any], jira: JiraClient) -> dict[str, Any]:
    """Format a Jira issue response for readability."""
    fields = issue.get("fields", {})
    result: dict[str, Any] = {
        "key": issue.get("key"),
        "id": issue.get("id"),
        "summary": fields.get("summary"),
        "status": (fields.get("status") or {}).get("name"),
        "issue_type": (fields.get("issuetype") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "assignee": (fields.get("assignee") or {}).get("displayName"),
        "reporter": (fields.get("reporter") or {}).get("displayName"),
        "labels": fields.get("labels", []),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
    }

    if fields.get("parent"):
        result["parent"] = {
            "key": fields["parent"].get("key"),
            "summary": fields["parent"].get("fields", {}).get("summary"),
        }

    if fields.get("fixVersions"):
        result["fix_versions"] = [
            {"id": v.get("id"), "name": v.get("name")}
            for v in fields["fixVersions"]
        ]

    if fields.get("description"):
        result["description"] = fields["description"]

    if fields.get("duedate"):
        result["due_date"] = fields["duedate"]

    start_date = fields.get(jira.start_date_field)
    if start_date:
        result["start_date"] = start_date

    if fields.get("issuelinks"):
        result["links"] = [
            {
                "id": link.get("id"),
                "type": (link.get("type") or {}).get("name"),
                "inward": (link.get("inwardIssue") or {}).get("key"),
                "outward": (link.get("outwardIssue") or {}).get("key"),
            }
            for link in fields["issuelinks"]
        ]

    if fields.get("components"):
        result["components"] = [
            c.get("name") for c in fields["components"]
        ]

    return result


# ===========================================================================
# 1. Issue CRUD
# ===========================================================================


@mcp.tool()
async def create_issue(
    project: str,
    issue_type: str,
    summary: str,
    description: str | None = None,
    assignee_id: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    parent: str | None = None,
    fix_versions: list[str] | None = None,
    components: list[str] | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    story_points: float | None = None,
    custom_fields: dict[str, Any] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a Jira issue with full field support including parent, fixVersions, dates.

    Args:
        project: Project key (e.g., "KAN")
        issue_type: Issue type name (e.g., "Task", "Story", "Bug", "Epic")
        summary: Issue title
        description: Plain text description (supports Jira wiki markup for rich text)
        assignee_id: Atlassian account ID of assignee
        priority: Priority name (e.g., "High", "Medium", "Low")
        labels: List of label strings
        parent: Parent issue key for sub-tasks or stories under epics (e.g., "KAN-1")
        fix_versions: List of version names (e.g., ["v1.0.0"])
        components: List of component names
        start_date: Start date in YYYY-MM-DD format
        due_date: Due date in YYYY-MM-DD format
        story_points: Story point estimate
        custom_fields: Dict of custom field IDs to values
    """
    jira = _jira(ctx)
    fields = _build_issue_fields(
        jira,
        project=project,
        issue_type=issue_type,
        summary=summary,
        description=description,
        assignee_id=assignee_id,
        priority=priority,
        labels=labels,
        parent=parent,
        fix_versions=fix_versions,
        components=components,
        start_date=start_date,
        due_date=due_date,
        story_points=story_points,
        custom_fields=custom_fields,
    )
    return await jira.post("/rest/api/2/issue", json={"fields": fields})


@mcp.tool()
async def create_issues_bulk(
    issues: list[dict[str, Any]],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create multiple issues in bulk (max 50 per request).

    Args:
        issues: List of issue objects. Each must have: project, issue_type, summary.
                Optional: description, assignee_id, priority, labels, parent,
                fix_versions, components, start_date, due_date, custom_fields.
    """
    jira = _jira(ctx)
    issue_updates = []
    for item in issues[:50]:
        fields = _build_issue_fields(
            jira,
            project=item["project"],
            issue_type=item["issue_type"],
            summary=item["summary"],
            description=item.get("description"),
            assignee_id=item.get("assignee_id"),
            priority=item.get("priority"),
            labels=item.get("labels"),
            parent=item.get("parent"),
            fix_versions=item.get("fix_versions"),
            components=item.get("components"),
            start_date=item.get("start_date"),
            due_date=item.get("due_date"),
            story_points=item.get("story_points"),
            custom_fields=item.get("custom_fields"),
        )
        issue_updates.append({"fields": fields})

    return await jira.post(
        "/rest/api/2/issue/bulk", json={"issueUpdates": issue_updates}
    )


@mcp.tool()
async def get_issue(
    issue_key: str,
    fields: str | None = None,
    expand: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get detailed information about a Jira issue.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
        fields: Comma-separated field names to include (default: all)
        expand: Comma-separated expansions (e.g., "changelog,transitions")
    """
    jira = _jira(ctx)
    params: dict[str, Any] = {}
    if fields:
        params["fields"] = fields
    if expand:
        params["expand"] = expand

    result = await jira.get(
        f"/rest/api/2/issue/{issue_key}", params=params or None
    )
    if isinstance(result, dict) and "key" in result:
        return _format_issue(result, jira)
    return result


@mcp.tool()
async def update_issue(
    issue_key: str,
    summary: str | None = None,
    description: str | None = None,
    assignee_id: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    fix_versions: list[str] | None = None,
    components: list[str] | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    parent: str | None = None,
    story_points: float | None = None,
    custom_fields: dict[str, Any] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Update an existing Jira issue. Only provided fields are changed.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
        summary: New summary
        description: New description (plain text, supports Jira wiki markup for rich text)
        assignee_id: New assignee account ID
        priority: New priority name
        labels: Replace all labels
        fix_versions: Replace all fix versions (list of version names)
        components: Replace all components
        start_date: New start date (YYYY-MM-DD)
        due_date: New due date (YYYY-MM-DD)
        parent: New parent issue key
        story_points: New story point estimate
        custom_fields: Dict of custom field IDs to values
    """
    jira = _jira(ctx)
    fields: dict[str, Any] = {}

    if summary is not None:
        fields["summary"] = summary
    if description is not None:
        fields["description"] = description
    if assignee_id is not None:
        fields["assignee"] = {"id": assignee_id}
    if priority is not None:
        fields["priority"] = {"name": priority}
    if labels is not None:
        fields["labels"] = labels
    if fix_versions is not None:
        fields["fixVersions"] = [{"name": v} for v in fix_versions]
    if components is not None:
        fields["components"] = [{"name": c} for c in components]
    if start_date is not None:
        fields[jira.start_date_field] = start_date
    if due_date is not None:
        fields["duedate"] = due_date
    if parent is not None:
        fields["parent"] = {"key": parent}
    if story_points is not None:
        fields["story_points"] = story_points
    if custom_fields:
        fields.update(custom_fields)

    if not fields:
        return {"error": "No fields to update"}

    return await jira.put(
        f"/rest/api/2/issue/{issue_key}", json={"fields": fields}
    )


@mcp.tool()
async def delete_issue(
    issue_key: str,
    delete_subtasks: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Delete a Jira issue.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
        delete_subtasks: Also delete subtasks (default: True)
    """
    jira = _jira(ctx)
    params = {"deleteSubtasks": str(delete_subtasks).lower()}
    return await jira.delete(
        f"/rest/api/2/issue/{issue_key}", params=params
    )


@mcp.tool()
async def search_issues(
    jql: str,
    fields: str = "summary,status,assignee,priority,issuetype,parent,fixVersions,labels",
    max_results: int = 50,
    next_page_token: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search Jira issues using JQL.

    Args:
        jql: JQL query string (e.g., 'project = KAN AND status = "To Do"')
        fields: Comma-separated fields to return
        max_results: Maximum results (1-100, default 50)
        next_page_token: Token for next page (from previous response)
    """
    jira = _jira(ctx)
    payload: dict[str, Any] = {
        "jql": jql,
        "fields": [f.strip() for f in fields.split(",")],
        "maxResults": min(max_results, 100),
    }
    if next_page_token:
        payload["nextPageToken"] = next_page_token

    result = await jira.post("/rest/api/3/search/jql", json=payload)

    if isinstance(result, dict) and "issues" in result:
        formatted: dict[str, Any] = {
            "max_results": result.get("maxResults", 50),
            "issues": [
                _format_issue(issue, jira) for issue in result["issues"]
            ],
        }
        if result.get("total") is not None:
            formatted["total"] = result["total"]
        if result.get("nextPageToken"):
            formatted["next_page_token"] = result["nextPageToken"]
        return formatted
    return result


# ===========================================================================
# 2. Transitions
# ===========================================================================


@mcp.tool()
async def get_transitions(
    issue_key: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get available status transitions for an issue.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
    """
    jira = _jira(ctx)
    result = await jira.get(
        f"/rest/api/2/issue/{issue_key}/transitions"
    )
    if isinstance(result, dict) and "transitions" in result:
        return {
            "transitions": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "to_status": t.get("to", {}).get("name"),
                }
                for t in result["transitions"]
            ]
        }
    return result


@mcp.tool()
async def transition_issue(
    issue_key: str,
    transition_name: str | None = None,
    transition_id: str | None = None,
    comment: str | None = None,
    resolution: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Transition an issue to a new status.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
        transition_name: Transition name (e.g., "In Progress", "Done"). Used to auto-find ID.
        transition_id: Transition ID (takes priority over name)
        comment: Optional comment to add during transition
        resolution: Optional resolution name (e.g., "Done") for closing transitions
    """
    jira = _jira(ctx)

    tid = transition_id
    if not tid and transition_name:
        transitions = await jira.get(
            f"/rest/api/2/issue/{issue_key}/transitions"
        )
        if isinstance(transitions, dict) and "transitions" in transitions:
            for t in transitions["transitions"]:
                if t["name"].lower() == transition_name.lower():
                    tid = t["id"]
                    break
        if not tid:
            return {
                "error": f"Transition '{transition_name}' not found",
                "available": [
                    t["name"]
                    for t in transitions.get("transitions", [])
                ],
            }

    if not tid:
        return {"error": "Either transition_name or transition_id is required"}

    payload: dict[str, Any] = {"transition": {"id": tid}}

    if comment:
        payload["update"] = {
            "comment": [{"add": {"body": comment}}]
        }

    if resolution:
        payload.setdefault("fields", {})["resolution"] = {"name": resolution}

    return await jira.post(
        f"/rest/api/2/issue/{issue_key}/transitions", json=payload
    )


@mcp.tool()
async def bulk_transition(
    issue_keys: list[str],
    transition_name: str,
    comment: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Transition multiple issues to a new status.

    Args:
        issue_keys: List of issue keys (e.g., ["KAN-1", "KAN-2"])
        transition_name: Target transition name (e.g., "Done")
        comment: Optional comment for all transitions
    """
    results: dict[str, Any] = {"success": [], "failed": []}
    for key in issue_keys:
        result = await transition_issue(
            issue_key=key,
            transition_name=transition_name,
            comment=comment,
            ctx=ctx,
        )
        if isinstance(result, dict) and result.get("error"):
            results["failed"].append({"key": key, "error": result["error"]})
        else:
            results["success"].append(key)

    return results


# ===========================================================================
# 3. Issue Links
# ===========================================================================


@mcp.tool()
async def link_issues(
    inward_issue: str,
    outward_issue: str,
    link_type: str = "Relates",
    comment: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a link between two issues.

    Args:
        inward_issue: Inward issue key (e.g., "KAN-1")
        outward_issue: Outward issue key (e.g., "KAN-2")
        link_type: Link type name (e.g., "Blocks", "Relates", "Duplicate", "Cloners")
        comment: Optional comment
    """
    jira = _jira(ctx)
    payload: dict[str, Any] = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue},
        "outwardIssue": {"key": outward_issue},
    }
    if comment:
        payload["comment"] = {"body": comment}

    return await jira.post("/rest/api/2/issueLink", json=payload)


@mcp.tool()
async def get_issue_links(
    issue_key: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get all links for an issue.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
    """
    jira = _jira(ctx)
    result = await jira.get(
        f"/rest/api/2/issue/{issue_key}",
        params={"fields": "issuelinks"},
    )
    if isinstance(result, dict) and "fields" in result:
        links = result["fields"].get("issuelinks", [])
        return {
            "issue_key": issue_key,
            "links": [
                {
                    "id": link.get("id"),
                    "type": (link.get("type") or {}).get("name"),
                    "inward_description": (link.get("type") or {}).get("inward"),
                    "outward_description": (link.get("type") or {}).get("outward"),
                    "inward_issue": (link.get("inwardIssue") or {}).get("key"),
                    "outward_issue": (link.get("outwardIssue") or {}).get("key"),
                }
                for link in links
            ],
        }
    return result


@mcp.tool()
async def delete_issue_link(
    link_id: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Delete an issue link by its ID.

    Args:
        link_id: The link ID (get from get_issue_links)
    """
    jira = _jira(ctx)
    return await jira.delete(f"/rest/api/2/issueLink/{link_id}")


# ===========================================================================
# 4. Release / Version Management
# ===========================================================================


@mcp.tool()
async def get_versions(
    project_key: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get all versions/releases for a project.

    Args:
        project_key: Project key (e.g., "KAN")
    """
    jira = _jira(ctx)
    result = await jira.get(
        f"/rest/api/3/project/{project_key}/versions"
    )
    if isinstance(result, list):
        return {
            "versions": [
                {
                    "id": v.get("id"),
                    "name": v.get("name"),
                    "description": v.get("description"),
                    "start_date": v.get("startDate"),
                    "release_date": v.get("releaseDate"),
                    "released": v.get("released", False),
                    "archived": v.get("archived", False),
                }
                for v in result
            ]
        }
    return result


@mcp.tool()
async def create_version(
    project_key: str,
    name: str,
    description: str | None = None,
    start_date: str | None = None,
    release_date: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a new version/release in a project.

    Args:
        project_key: Project key (e.g., "KAN")
        name: Version name (e.g., "v1.0.0")
        description: Version description
        start_date: Start date (YYYY-MM-DD)
        release_date: Release date (YYYY-MM-DD)
    """
    jira = _jira(ctx)

    payload: dict[str, Any] = {
        "name": name,
        "project": project_key,
        "archived": False,
        "released": False,
    }
    if description:
        payload["description"] = description
    if start_date:
        payload["startDate"] = start_date
    if release_date:
        payload["releaseDate"] = release_date

    return await jira.post("/rest/api/3/version", json=payload)


@mcp.tool()
async def update_version(
    version_id: str,
    name: str | None = None,
    description: str | None = None,
    start_date: str | None = None,
    release_date: str | None = None,
    released: bool | None = None,
    archived: bool | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Update an existing version/release.

    Args:
        version_id: Version ID (get from get_versions)
        name: New version name
        description: New description
        start_date: New start date (YYYY-MM-DD)
        release_date: New release date (YYYY-MM-DD)
        released: Mark as released
        archived: Mark as archived
    """
    jira = _jira(ctx)
    payload: dict[str, Any] = {}

    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if start_date is not None:
        payload["startDate"] = start_date
    if release_date is not None:
        payload["releaseDate"] = release_date
    if released is not None:
        payload["released"] = released
    if archived is not None:
        payload["archived"] = archived

    if not payload:
        return {"error": "No fields to update"}

    return await jira.put(f"/rest/api/3/version/{version_id}", json=payload)


@mcp.tool()
async def delete_version(
    version_id: str,
    move_fix_issues_to: str | None = None,
    move_affected_issues_to: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Delete a version/release.

    Args:
        version_id: Version ID to delete
        move_fix_issues_to: Version ID to reassign fix version issues
        move_affected_issues_to: Version ID to reassign affected version issues
    """
    jira = _jira(ctx)
    params: dict[str, str] = {}
    if move_fix_issues_to:
        params["moveFixIssuesTo"] = move_fix_issues_to
    if move_affected_issues_to:
        params["moveAffectedIssuesTo"] = move_affected_issues_to

    return await jira.delete(
        f"/rest/api/3/version/{version_id}", params=params or None
    )


# ===========================================================================
# 5. Sprint Management (Agile API)
# ===========================================================================


@mcp.tool()
async def get_sprints(
    board_id: str,
    state: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get sprints for a board.

    Args:
        board_id: Board ID
        state: Filter by state: "future", "active", "closed" (default: all)
    """
    jira = _jira(ctx)
    params: dict[str, Any] = {}
    if state:
        params["state"] = state

    return await jira.get(
        f"/rest/agile/1.0/board/{board_id}/sprint",
        params=params or None,
    )


@mcp.tool()
async def move_to_sprint(
    sprint_id: str,
    issue_keys: list[str],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Move issues to a sprint.

    Args:
        sprint_id: Target sprint ID
        issue_keys: List of issue keys to move (e.g., ["KAN-1", "KAN-2"])
    """
    jira = _jira(ctx)
    return await jira.post(
        f"/rest/agile/1.0/sprint/{sprint_id}/issue",
        json={"issues": issue_keys},
    )


# ===========================================================================
# 6. Comments & Worklogs
# ===========================================================================


@mcp.tool()
async def add_comment(
    issue_key: str,
    body: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Add a comment to an issue.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
        body: Comment text (plain text, supports Jira wiki markup for rich text)
    """
    jira = _jira(ctx)
    return await jira.post(
        f"/rest/api/2/issue/{issue_key}/comment",
        json={"body": body},
    )


@mcp.tool()
async def get_comments(
    issue_key: str,
    max_results: int = 50,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get comments on an issue.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
        max_results: Maximum number of comments (default 50)
    """
    jira = _jira(ctx)
    result = await jira.get(
        f"/rest/api/2/issue/{issue_key}/comment",
        params={"maxResults": max_results, "orderBy": "-created"},
    )
    if isinstance(result, dict) and "comments" in result:
        return {
            "total": result.get("total", 0),
            "comments": [
                {
                    "id": c.get("id"),
                    "author": (c.get("author") or {}).get("displayName"),
                    "body": c.get("body", ""),
                    "created": c.get("created"),
                    "updated": c.get("updated"),
                }
                for c in result["comments"]
            ],
        }
    return result


@mcp.tool()
async def add_worklog(
    issue_key: str,
    time_spent: str,
    comment: str | None = None,
    started: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Add a worklog entry to an issue.

    Args:
        issue_key: Issue key (e.g., "KAN-123")
        time_spent: Time spent string (e.g., "2h 30m", "1d", "4h")
        comment: Work description
        started: Start time in ISO format (e.g., "2026-03-24T09:00:00.000+0000")
    """
    jira = _jira(ctx)

    parts = time_spent.lower().replace(",", " ").split()
    total_seconds = 0
    for part in parts:
        if part.endswith("d"):
            total_seconds += int(float(part[:-1]) * 8 * 3600)
        elif part.endswith("h"):
            total_seconds += int(float(part[:-1]) * 3600)
        elif part.endswith("m"):
            total_seconds += int(float(part[:-1]) * 60)
        elif part.endswith("s"):
            total_seconds += int(float(part[:-1]))

    if total_seconds == 0:
        return {"error": f"Could not parse time_spent: {time_spent}"}

    payload: dict[str, Any] = {"timeSpentSeconds": total_seconds}
    if comment:
        payload["comment"] = comment
    if started:
        payload["started"] = started

    return await jira.post(
        f"/rest/api/2/issue/{issue_key}/worklog", json=payload
    )


# ===========================================================================
# 7. Project, Board, Users, Metadata
# ===========================================================================


@mcp.tool()
async def get_projects(
    ctx: Context | None = None,
) -> dict[str, Any]:
    """List all accessible Jira projects."""
    jira = _jira(ctx)
    result = await jira.get("/rest/api/3/project")
    if isinstance(result, list):
        return {
            "projects": [
                {
                    "id": p.get("id"),
                    "key": p.get("key"),
                    "name": p.get("name"),
                    "project_type": p.get("projectTypeKey"),
                    "style": p.get("style"),
                }
                for p in result
            ]
        }
    return result


@mcp.tool()
async def get_project(
    project_key: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get detailed information about a project.

    Args:
        project_key: Project key (e.g., "KAN")
    """
    jira = _jira(ctx)
    return await jira.get(f"/rest/api/3/project/{project_key}")


@mcp.tool()
async def get_boards(
    project_key: str | None = None,
    board_type: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """List Jira boards.

    Args:
        project_key: Filter by project key
        board_type: Filter by type: "scrum", "kanban", "simple"
    """
    jira = _jira(ctx)
    params: dict[str, str] = {}
    if project_key:
        params["projectKeyOrId"] = project_key
    if board_type:
        params["type"] = board_type

    return await jira.get(
        "/rest/agile/1.0/board", params=params or None
    )


@mcp.tool()
async def get_current_user(
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get the currently authenticated Jira user."""
    jira = _jira(ctx)
    return await jira.get("/rest/api/3/myself")


@mcp.tool()
async def search_users(
    query: str,
    max_results: int = 25,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for Jira users by name or email.

    Args:
        query: Search string (name, email, or display name)
        max_results: Maximum results (default 25)
    """
    jira = _jira(ctx)
    result = await jira.get(
        "/rest/api/3/user/search",
        params={"query": query, "maxResults": max_results},
    )
    if isinstance(result, list):
        return {
            "users": [
                {
                    "account_id": u.get("accountId"),
                    "display_name": u.get("displayName"),
                    "email": u.get("emailAddress"),
                    "active": u.get("active"),
                }
                for u in result
            ]
        }
    return result


@mcp.tool()
async def get_createmeta(
    project_key: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get issue creation metadata for a project (available issue types and fields).

    Args:
        project_key: Project key (e.g., "KAN")
    """
    jira = _jira(ctx)
    return await jira.get(
        "/rest/api/2/issue/createmeta",
        params={"projectKeys": project_key, "expand": "projects.issuetypes.fields"},
    )


# ===========================================================================
# Entrypoint
# ===========================================================================


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
