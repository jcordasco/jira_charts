import argparse
from config import Config
from auth_manager import AuthManager
from jira_client import JiraClient
from jira_parser_v2 import JiraParserV2
from query_engine import run_query
from utils import project_path
from field_structure_exporter import fetch_field_definitions, extract_field_structure_with_names, export_structure_to_file
from config_manager import get_default_mapping, set_default_mapping, DEFAULT_MAPPING_FALLBACK
import pandas as pd

def add_query_source_arguments(subparser):
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument("--jql", type=str, help="JQL query string")
    group.add_argument("--sprint", type=str, help="Sprint name to query")

def add_export_argument(subparser):
    subparser.add_argument("--export", help="Optional: Export results to CSV file")

def add_field_mapping_argument(subparser):
    subparser.add_argument(
        "--field-mapping",
        type=str,
        default=None,
        help="Path to field mapping JSON file (default uses saved profile or field_mappings.json)"
    )

def main():
    parser = argparse.ArgumentParser(description="Jira Charts v2 CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("test-auth", help="Test OAuth authentication")

    query_parser = subparsers.add_parser("query", help="Run JQL query")
    add_query_source_arguments(query_parser)
    query_parser.add_argument("--limit", type=int, default=None, help="Optional limit (default: fetch all)")
    add_export_argument(query_parser)
    add_field_mapping_argument(query_parser)

    field_parser = subparsers.add_parser("export-field-structure", help="Export sample field structure from search result")
    field_parser.add_argument("--jql", required=True, help="Sample JQL query to analyze field structure")
    field_parser.add_argument("--output", required=True, help="Output file path for field structure JSON")

    mapping_parser = subparsers.add_parser("set-default-mapping", help="Set default field mapping file")
    mapping_parser.add_argument("--file", required=True, help="Field mapping filename, or 'default' to reset")

    args = parser.parse_args()

    Config.validate()

    auth = AuthManager(
        client_id=Config.CLIENT_ID,
        client_secret=Config.CLIENT_SECRET,
        token_url=Config.TOKEN_URL,
        auth_url=Config.AUTH_URL,
        redirect_uri=Config.REDIRECT_URI,
        scope=Config.SCOPE
    )

    jira = JiraClient(auth)

    if args.command == "test-auth":
        user = jira.get_myself()
        print(f"Successfully authenticated as: {user.get('displayName')}")

    elif args.command == "query":
        field_mapping_file = args.field_mapping or get_default_mapping()
        parser_v2 = JiraParserV2(project_path(field_mapping_file))

        if args.jql:
            jql = args.jql
        elif args.sprint:
            jql = f'sprint = "{args.sprint}"'

        df = run_query(jira, parser_v2, jql, limit=args.limit)
        print(df.head())
        print(f"\nTotal records fetched: {len(df)}")

        if args.export:
            df.to_csv(args.export, index=False)
            print(f"Exported {len(df)} rows to {args.export}")

    elif args.command == "export-field-structure":
        field_definitions = fetch_field_definitions(jira)
        raw_results = jira.get("search", params={"jql": args.jql, "maxResults": 1})
        issues = raw_results.get("issues", [])
        if not issues:
            print("No matching issues found to analyze structure.")
            return

        sample_issue = issues[0]
        structure = extract_field_structure_with_names(sample_issue, field_definitions)
        export_structure_to_file(structure, args.output)
        print(f"Exported field structure to: {args.output}")

    elif args.command == "set-default-mapping":
        set_default_mapping(args.file)
        print(f"Default field mapping set to: {args.file if args.file != 'default' else DEFAULT_MAPPING_FALLBACK}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
