import os
import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    def __init__(self):
        self.url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")
        self.auth = HTTPBasicAuth(self.email, self.token)
        self.headers = {"Accept": "application/json"}

    def get_issues(self, max_results=50):
        payload = {
            "jql": f"project = {self.project_key} ORDER BY updated DESC",
            "maxResults": max_results,
            "fields": ["summary", "status", "priority", "assignee", "description", "created", "updated", "issuetype"]
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        response = requests.post(
            f"{self.url}/rest/api/3/search/jql",
            headers=headers,
            auth=self.auth,
            json=payload
        )
        response.raise_for_status()
        return response.json().get("issues", [])

    def format_issues_for_agents(self, issues):
        formatted = []
        for issue in issues:
            fields = issue["fields"]
            formatted.append({
                "key": issue["key"],
                "summary": fields.get("summary", ""),
                "status": fields.get("status", {}).get("name", "Unknown"),
                "priority": fields.get("priority", {}).get("name", "None"),
                "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
                "issue_type": fields.get("issuetype", {}).get("name", ""),
                "created": fields.get("created", "")[:10],
                "updated": fields.get("updated", "")[:10],
            })
        return formatted
