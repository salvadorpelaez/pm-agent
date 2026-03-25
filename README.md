# PM Agent — Multi-Agent AI Workflow for Project Managers

A multi-agent AI system that pulls live JIRA data, analyzes sprint health, identifies risks, and delivers stakeholder-ready reports to Pumble — automatically, every Monday morning.

Built with the Anthropic Claude API and deployed via GitHub Actions.

---

## What It Does

Three specialized AI agents run in sequence every Monday at 9am Pacific:

1. **Sprint Planner** — reads all JIRA tickets and summarizes sprint status by category
2. **Risk Analyst** — identifies unassigned tickets, high-priority blockers, and stalled items
3. **Status Reporter** — writes a concise, stakeholder-ready update and posts it to Pumble

No manual work required. The team sees the report in Pumble at the start of every week.

---

## Architecture

```
JIRA Cloud (API)
      ↓
jira_client.py   — fetches and formats live ticket data
      ↓
crew.py          — runs 3 sequential AI agents via Claude Sonnet
      ↓
notifier.py      — posts final report to Pumble via webhook
      ↓
Pumble Channel   — team receives stakeholder update
```

Scheduled via **GitHub Actions** — runs entirely in the cloud, no local machine needed.

---

## Tech Stack

- **Python 3.12**
- **Anthropic Claude Sonnet** — reasoning engine for all three agents
- **JIRA Cloud REST API v3** — live ticket data source
- **Pumble Incoming Webhooks** — report delivery
- **GitHub Actions** — scheduling and cloud execution
- **uv** — Python package management

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/salvadorpelaez/pm-agent.git
cd pm-agent
```

### 2. Install dependencies

```bash
pip install uv
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
JIRA_URL=https://your-instance.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_jira_api_token
PUMBLE_WEBHOOK_URL=your_pumble_webhook_url
JIRA_PROJECT_KEY=YOUR_PROJECT_KEY
```

### 4. Run

```bash
uv run python main.py
```

---

## GitHub Actions (Automated Schedule)

The workflow runs every Monday at 9am Pacific automatically.

To trigger a manual run:
1. Go to the **Actions** tab in this repo
2. Select **Weekly PM Report**
3. Click **Run workflow**

Secrets are stored in GitHub repository settings — never in code.

---

## Project Structure

```
pm-agent/
├── main.py          # Entry point
├── crew.py          # Three AI agents (Planner, Risk Analyst, Reporter)
├── jira_client.py   # JIRA API client
├── notifier.py      # Pumble webhook notifier
├── .env.example     # Environment variable template
├── pyproject.toml   # Dependencies
└── .github/
    └── workflows/
        └── weekly-report.yml  # GitHub Actions schedule
```

---

## Sample Output

```
🔴 Sprint Status Update | SCRUM Board

Sprint Health: 2 of 5 tickets in progress. 1 completed. 2 not started.

Progress Highlights
• SCRUM-3 (Stakeholder review follow-up) — In Progress
• SCRUM-1 (Q2 product requirements) — In Progress
• SCRUM-2 (Update sprint backlog) — Done

Top Risks & Blockers
• SCRUM-4 (Compliance milestone) — unassigned, high priority
• SCRUM-5 (Database re-architecture) — not started, no owner

Recommended Next Actions
• Assign owner to SCRUM-4 today — compliance deadline may be fixed
• Scope SCRUM-5 before next sprint planning
• Run standup to surface any hidden blockers
```

---

## Why This Exists

Built as a portfolio project to demonstrate multi-agent AI workflow design applied to real PM problems — sprint health monitoring, risk detection, and stakeholder communication automation.

Maps to compliance-heavy environments (medtech, pharma, enterprise) where consistent, traceable status reporting is a requirement, not a nice-to-have.
