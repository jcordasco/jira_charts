import argparse
import os
import logging
import pandas as pd
from chart_registry_v2 import auto_import_charts, get_registered_charts, run_chart
from jira_client import JiraClient
from auth_manager import AuthManager
from jira_parser_v2 import JiraParserV2
from query_engine import run_query
from utils import project_path
from field_structure_exporter import fetch_field_definitions, extract_field_structure_with_names, export_structure_to_file
from config_manager import get_default_mapping, set_default_mapping, DEFAULT_MAPPING_FALLBACK
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_query_source_arguments(subparser):
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument("--jql", type=str, help="JQL query string")
    group.add_argument("--sprint", type=str, help="Sprint name to query")

def add_export_argument(subparser):
    subparser.add_argument("--export", help="Optional: Export results to CSV file")

def add_chart_arguments(subparser):
    subparser.add_argument("--chart", help="Generate a chart of the specified type")
    subparser.add_argument("--save", help="Save the chart to the specified file (PNG, PDF, SVG, etc.)")

def add_field_mapping_argument(subparser):
    subparser.add_argument(
        "--field-mapping",
        type=str,
        default=None,
        help="Path to field mapping JSON file (default uses saved profile or field_mappings.json)"
    )

def main():
    # Import charts dynamically
    auto_import_charts()
    available_charts = get_registered_charts()
    
    parser = argparse.ArgumentParser(description="Jira Charts v2 CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Test authentication command
    subparsers.add_parser("test-auth", help="Test OAuth authentication")

    # Query command
    query_parser = subparsers.add_parser("query", help="Run JQL query")
    add_query_source_arguments(query_parser)
    query_parser.add_argument("--limit", type=int, default=None, help="Optional limit (default: fetch all)")
    add_export_argument(query_parser)
    add_field_mapping_argument(query_parser)
    add_chart_arguments(query_parser)

    # Field structure export command
    field_parser = subparsers.add_parser("export-field-structure", help="Export sample field structure from search result")
    field_parser.add_argument("--jql", required=True, help="Sample JQL query to analyze field structure")
    field_parser.add_argument("--output", required=True, help="Output file path for field structure JSON")

    # Set default mapping command
    mapping_parser = subparsers.add_parser("set-default-mapping", help="Set default field mapping file")
    mapping_parser.add_argument("--file", required=True, help="Field mapping filename, or 'default' to reset")

    # Parse arguments
    args = parser.parse_args()

    # Validate configuration
    Config.validate()

    # Initialize authentication
    auth = AuthManager(
        client_id=Config.CLIENT_ID,
        client_secret=Config.CLIENT_SECRET,
        token_url=Config.TOKEN_URL,
        auth_url=Config.AUTH_URL,
        redirect_uri=Config.REDIRECT_URI,
        scope=Config.SCOPE,
        token_path=Config.TOKEN_FILE
    )

    # Create Jira client
    jira = JiraClient(auth)

    if args.command == "test-auth":
        user = jira.get_myself()
        print(f"Successfully authenticated as: {user.get('displayName')}")

    elif args.command == "query":
        field_mapping_file = args.field_mapping or get_default_mapping()
        parser_v2 = JiraParserV2(project_path(field_mapping_file))

        # Execute query based on JQL or sprint
        if args.sprint:
            logger.info(f"Querying sprint: {args.sprint}")
            sprint_jql = f'sprint = "{args.sprint}"'
            logger.info(f"Using JQL: {sprint_jql}")
            df = run_query(jira, parser_v2, sprint_jql, limit=args.limit)
        elif args.jql:
            logger.info(f"Executing JQL: {args.jql}")
            df = run_query(jira, parser_v2, args.jql, limit=args.limit)

        # Display results
        print(df.head())
        print(f"\nTotal records fetched: {len(df)}")

        # Generate chart if requested
        chart_displayed = False
        if args.chart:
            if args.chart in available_charts:
                logger.info(f"Generating {args.chart} chart...")
                result_df = run_chart(args.chart, df, export_path=args.save)
                
                # Track if chart was displayed rather than saved
                if not args.save:
                    chart_displayed = True
                
                # If the chart function returns a modified dataframe, use it for export
                if isinstance(result_df, pd.DataFrame):
                    df = result_df
            else:
                logger.error(f"Chart '{args.chart}' not found. Available charts: {', '.join(available_charts)}")

        # Export results if requested
        if args.export:
            df.to_csv(args.export, index=False)
            logger.info(f"Exported {len(df)} rows to {args.export}")
            
        # If a chart was displayed (not saved to file), pause to keep the window open
        if chart_displayed:
            input("Chart displayed. Press Enter to close the window and exit...")

    elif args.command == "export-field-structure":
        field_definitions = fetch_field_definitions(jira)
        raw_results = jira.get("search", params={"jql": args.jql, "maxResults": 1})
        issues = raw_results.get("issues", [])
        if not issues:
            logger.warning("No matching issues found to analyze structure.")
            return

        sample_issue = issues[0]
        structure = extract_field_structure_with_names(sample_issue, field_definitions)
        export_structure_to_file(structure, args.output)
        logger.info(f"Exported field structure to: {args.output}")

    elif args.command == "set-default-mapping":
        set_default_mapping(args.file)
        logger.info(f"Default field mapping set to: {args.file if args.file != 'default' else DEFAULT_MAPPING_FALLBACK}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
