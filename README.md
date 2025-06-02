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
git clone https://github.com/jcordasco/jira_charts.git
cd jira_charts

### 2. Create virtual environment

```bash
python -m venv .venv

Activate the environment:

- On Windows:

```bash
.venv\Scripts\activate

- On macOS/Linux:

```bash
source .venv/bin/activate

### 3. Install Requirements

```bash
pip install -r requirements.txt

## Configuration
### Register an OAuth app on Atlassian Developer

