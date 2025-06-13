# Jira Charts v2

A command-line tool to query Jira issues via OAuth 2.0 and render visual charts.

## Features

- OAuth 2.0 authentication with token refresh
- JQL or sprint-based querying
- Customizable field mappings
- Dynamic chart loading system
- Export to CSV, PNG, or other formats

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env_template` to `.env` and configure with your Jira OAuth credentials:
   ```
   cp .env_template .env
   ```

## Authentication Setup

1. Create an OAuth 2.0 app in your Atlassian account
2. Set the required environment variables in `.env`:
   - `CLIENT_ID`: Your OAuth client ID
   - `CLIENT_SECRET`: Your OAuth client secret
   - `REDIRECT_URI`: Usually http://localhost:5000/callback
   - `JIRA_BASE_URL`: Your Jira instance URL

## Usage

### Test Authentication

```bash
python cli.py test-auth
```

### Query Jira and Export Results

```bash
# Using JQL
python cli.py query --jql "project = DEMO AND status != Done" --export results.csv

# Using sprint name
python cli.py query --sprint "Current Sprint" --limit 100 --export results.csv
```

### Generate Charts

```bash
# Generate Gantt chart and save to file
python cli.py query --jql "project = DEMO" --chart gantt --save chart.png

# Generate chart and export data
python cli.py query --sprint "Current Sprint" --chart gantt --export data.csv
```

### Field Mapping

```bash
# Export field structure from a sample issue
python cli.py export-field-structure --jql "project = DEMO" --output field_structure.json

# Set a default field mapping file
python cli.py set-default-mapping --file field_mappings.json
```

## Configuration

The application uses the following configuration:

- OAuth 2.0 credentials (client_id, client_secret)
- Authentication URLs (auth_url, token_url)
- Redirect URI for the OAuth flow
- Scope for Jira API access
- Base URL for your Jira instance

All configuration is managed through environment variables (loaded from `.env`).

## Field Mapping

Field mappings are defined in JSON format:

```json
{
  "Summary": "summary",
  "Status": "status.name",
  "Sprint": {
    "path": "customfield_10002",
    "type": "list",
    "field": "name"
  }
}
```

The mapping supports:
- Simple dot notation for nested fields (e.g., "status.name")
- Complex mappings for arrays and custom fields

## Adding New Charts

1. Create a new Python file in the `charts/` directory
2. Use the `@register_chart` decorator to register your chart function
3. Implement the chart function with the following signature:

```python
from chart_registry_v2 import register_chart

@register_chart("chart_name")
def my_chart(df, export_path=None):
    # Chart implementation
    # ...
    return processed_dataframe
```

## Troubleshooting

### OAuth Issues

- "No accessible Jira resources found for this token" - Check your OAuth app permissions
- Port conflicts - Change the port in REDIRECT_URI
- "Invalid refresh token" - Re-authenticate by deleting the token file

### Query Issues

- No results - Verify JQL syntax and permissions
- Missing fields - Check field mappings match your Jira configuration
