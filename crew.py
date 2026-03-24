import os
import anthropic
from jira_client import JiraClient
from notifier import send_to_pumble


class Agent:
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def run(self, prompt: str) -> str:
        print(f"\n[{self.role}] thinking...\n")
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=f"You are a {self.role}. {self.backstory} Your goal: {self.goal}",
            messages=[{"role": "user", "content": prompt}]
        )
        result = message.content[0].text
        print(f"[{self.role}] done.\n")
        return result


class PMCrew:
    def __init__(self):
        self.jira = JiraClient()

        self.planner = Agent(
            role="Sprint Planner",
            goal="Analyze JIRA tickets and summarize sprint status.",
            backstory="You are an experienced PM who reads JIRA tickets and quickly understands sprint health."
        )

        self.risk_analyst = Agent(
            role="Risk Analyst",
            goal="Identify risks in the current sprint — overdue items, unassigned tickets, high-priority blockers.",
            backstory="You are a risk-focused PM who spots issues before they become problems."
        )

        self.reporter = Agent(
            role="Status Reporter",
            goal="Write a concise stakeholder-ready status update based on sprint analysis and risk findings.",
            backstory="You are a PM communications expert who turns raw data into clear updates for leadership."
        )

    def run(self):
        print("Fetching JIRA issues...")
        issues = self.jira.get_issues()
        formatted = self.jira.format_issues_for_agents(issues)

        if not formatted:
            print("No issues found in JIRA. Add some tickets to your SCRUM project first.")
            return

        issues_text = "\n".join([
            f"- [{i['key']}] {i['summary']} | Status: {i['status']} | Priority: {i['priority']} | Assignee: {i['assignee']} | Updated: {i['updated']}"
            for i in formatted
        ])

        # Agent 1: Sprint Planner
        sprint_summary = self.planner.run(f"""Analyze these JIRA tickets and provide a sprint summary:

{issues_text}

Group tickets by status. Highlight what is in progress and what is done.""")

        # Agent 2: Risk Analyst
        risk_assessment = self.risk_analyst.run(f"""Based on this sprint summary, identify risks:

{sprint_summary}

Raw tickets:
{issues_text}

Identify:
1. High-priority tickets not yet started
2. Tickets with no assignee
3. Items that appear stalled or overdue
4. Overall risk level: Low / Medium / High""")

        # Agent 3: Status Reporter
        final_report = self.reporter.run(f"""Write a concise Pumble status update based on:

SPRINT SUMMARY:
{sprint_summary}

RISK ASSESSMENT:
{risk_assessment}

Include:
- Sprint health summary (1-2 sentences)
- Key progress highlights
- Top risks or blockers
- Recommended next actions

Keep it under 300 words. Use bullet points. Start with an emoji status indicator.""")

        print("\n=== FINAL REPORT ===")
        print(final_report)

        send_to_pumble(final_report)
