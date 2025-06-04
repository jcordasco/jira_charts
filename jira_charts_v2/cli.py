import argparse
from config import Config
from auth_manager import AuthManager
from jira_client import JiraClient
from jira_parser_v2 import JiraParserV2
import pandas as pd

# Reusable argument groups
def add_jql_arguments(subparser):
    subparser.add_argument("--jql", required=True, help="JQL query string")
    subparser.add_argument("--limit", type=int, default=100, help="Max results (default 100)")

def add_export_argument(subparser):
    subparser.add_argument("--export", help="Optional: Export results to CSV file")

# Shared Jira query function
def run_query(jira, parser, jql, limit=100):
    results = jira.get("rest/api/3/search", params={"jql": jql, "maxResults": limit})
    issues = results.get("issues", [])
    df = parser.parse_issues(issues)
    return df

def main():
    parser = argparse.ArgumentParser(description="Jira Charts v2 CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("test-auth", help="Test OAuth authentication")

    query_parser = subparsers.add_parser("query", help="Run JQL query")
    add_jql_arguments(query_parser)
    add_export_argument(query_parser)

    args = parser.parse_args()

    # Initialize auth + client
    auth = AuthManager(
        client_id=Config.CLIENT_ID,
        token_url=Config.TOKEN_URL,
        auth_url=Config.AUTH_URL,
        redirect_uri=Config.REDIRECT_URI,
        scope=Config.SCOPE
    )

    jira = JiraClient(auth, Config.JIRA_BASE_URL)
    parser_v2 = JiraParserV2("field_mappings.json")

    if args.command == "test-auth":
        user = jira.get_myself()
        print("✅ Successfully authenticated as:", user.get("displayName"))

    elif args.command == "query":
        df = run_query(jira, parser_v2, args.jql, limit=args.limit)
        print(df.head())

        if args.export:
            df.to_csv(args.export, index=False)
            print(f"✅ Exported {len(df)} rows to {args.export}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
