import pandas as pd

def run_query(jira, parser, jql, limit=None):
    """
    Execute a JQL query and return the results as a pandas DataFrame.
    
    Args:
        jira: JiraClient instance
        parser: JiraParser instance
        jql: JQL query string
        limit: Maximum number of issues to return (optional)
        
    Returns:
        pandas.DataFrame: DataFrame containing the parsed issues
    """
    all_issues = []
    start_at = 0
    page_size = 100  # Conservative default; Jira allows up to 1000 if you want to adjust later

    while True:
        results = jira.get(
            "search",
            params={"jql": jql, "maxResults": page_size, "startAt": start_at}
        )

        issues = results.get("issues", [])
        all_issues.extend(issues)

        total = results.get("total", 0)
        start_at += page_size

        if start_at >= total or not issues:
            break

        if limit and len(all_issues) >= limit:
            break

    if limit:
        all_issues = all_issues[:limit]

    df = parser.parse_issues(all_issues)
    return df

# Sprint queries are now handled directly through JQL in the CLI
