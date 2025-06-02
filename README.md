
# Jira Charts

A portable command-line tool for pulling data from Jira Cloud (Atlassian) via OAuth 2.0 and generating project analytics and visualizations.

---

## Features

- OAuth 2.0 integration (Atlassian OAuth flow)
- JQL query support for flexible filtering
- Gantt chart reporting (Bokeh-based)
- Adaptive label placement (inside/outside Gantt bars)
- Inclusive end-date logic (matches Jira sprint behavior)
- Automatic swimlane stacking with overlap detection
- Red vertical line for current date
- CLI extensible architecture for multiple chart types
- Modular, version-controlled, portable across environments

---

## Installation

### 1. Clone this repo

```bash
git clone https://github.com/your-repo/jira_charts.git
cd jira_charts
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate the environment:

- On Windows:

```bash
.venv\Scripts\activate
```

- On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install requirements

```bash
pip install -r requirements.txt
```

---

## Configuration

### Register an OAuth app on Atlassian Developer

1. Go to: https://developer.atlassian.com/console/myapps/
2. Register your app.
3. Enable OAuth 2.0 (3LO).
4. Generate:
   - Client ID
   - Client Secret
   - Redirect URI (typically: http://localhost:5000/callback)

### Set configuration values via CLI

```bash
python main.py configure --jira-url https://your-instance.atlassian.net
python main.py configure --client-id your_client_id
python main.py configure --client-secret your_client_secret
python main.py configure --redirect-uri http://localhost:5000/callback
```

You can run `configure` multiple times to update individual values. All parameters are optional and stored into a local `.env` file.

## Usage

### Query Jira using JQL

```bash
python main.py query --jql "project = MYPROJECT AND statusCategory != Done"
```

### Query all issues from a sprint

```bash
python main.py query --sprint-name "Sprint 2025.06"
```
### Export query data to CSV

```bash
python main.py query --sprint-name "Sprint 2025.06" --export output.csv
```

---

### Generate a Gantt chart for a sprint

```bash
python main.py chart --sprint-name "Sprint 2025.06"
```

### Export chart data to CSV

```bash
python main.py chart --sprint-name "Sprint 2025.06" --export output.csv
```

OR 

```bash
python main.py query --sprint-name "Sprint 2025.06" --export output.csv
```

---

## Gantt Chart Details

- Swimlanes are grouped by team field.
- Overlapping issues are automatically assigned separate lanes.
- Fully inclusive end dates (bars include the full final date).
- Adaptive label placement:
  - Inside bar if wide enough.
  - Above bar if too narrow.
- Red vertical line drawn for the current date.
- Fully interactive HTML output using Bokeh.
- Data can be exported for external reporting pipelines.

---

## Roadmap

The CLI architecture allows rapid future expansion:

- Burnup charts
- Throughput charts
- Velocity charts
- Historical reporting
- Automated scheduled reports

---

## Security

- OAuth tokens are stored locally (not in Git)
- .env file safely stores credentials and tokens
- .gitignore automatically excludes sensitive files
- OAuth tokens only exist on your local machine after authentication

---

## Project Structure

```
jira_charts/
│
├── main.py           # CLI entrypoint
├── config.py         # Secure config management
├── auth.py           # OAuth 2.0 authentication flow
├── jira_client.py    # REST API client engine
├── jira_parser.py    # Response parsing to dataframe
├── charts_bokeh.py   # Gantt chart engine
├── burnup_chart.py   # (Planned future chart module)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## Dependencies

- Python 3.10+
- Bokeh
- Requests
- Pandas
- Requests-OAuthlib
- dotenv

---

## Git and Deployment

The following files and folders are automatically excluded from Git:

```
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.idea/
.vscode/
.venv/
```

This ensures credentials and local environment files are never committed.

---

## License

MIT License

---

## Summary

Jira Charts is designed to serve as a portable, extensible, self-contained Jira reporting engine that pulls live project data from Jira Cloud via OAuth and provides flexible charting pipelines directly from the command line. The architecture supports clean version control, secure credential storage, modular chart engines, and production-quality visualization output.
