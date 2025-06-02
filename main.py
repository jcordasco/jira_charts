import argparse
import json
from config import load_config, update_config, save_config
from dotenv import load_dotenv
from jira_client import api_request
from jira_parser import parse_issues_to_dataframe
from charts_bokeh import gantt_chart_for_sprint_bokeh

DEFAULT_CONFIG = {
    "jira_url": "",
    "client_id": "",
    "redirect_uri": "http://localhost:5000/callback"
}

def configure(args):
    updates = {}
    if args.jira_url:
        updates["jira_url"] = args.jira_url
    if args.client_id:
        updates["client_id"] = args.client_id
    if args.redirect_uri:
        updates["redirect_uri"] = args.redirect_uri

    if not updates:
        print("No configuration values provided.")
        return

    update_config(**updates)
    print("Configuration updated.")

def show_config(args):
    config = load_config()
    print("Current configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

def reset_config(args):
    save_config(DEFAULT_CONFIG)
    print("Configuration reset to defaults.")

def query(args):
    try:
        if args.sprint_name:
            jql = f'Sprint = "{args.sprint_name}"'
            print(f"Running Sprint name query: {jql}")
        elif args.jql:
            jql = args.jql
            print(f"Running JQL query: {jql}")
        else:
            print("You must supply either --jql or --sprint-name")
            return

        result = api_request(
            endpoint="search",
            params={"jql": jql},
            paginate=True
        )
        df = parse_issues_to_dataframe(result)
        print(df)

        if args.export:
            df.to_csv(args.export, index=False)
            print(f"Exported results to {args.export}")

    except Exception as e:
        print(f"Error running query: {e}")

def discover_fields(args):
    print(f"Discovering fields with JQL: {args.jql}")
    try:
        result = api_request(
            endpoint="search",
            params={"jql": args.jql, "maxResults": 1},
            paginate=False
        )

        issue = result["issues"][0]
        fields = issue.get("fields", {})

        for key, value in fields.items():
            short_value = str(value)
            if len(short_value) > 200:
                short_value = short_value[:200] + "..."
            print(f"{key}: {short_value}")

    except Exception as e:
        print(f"Error discovering fields: {e}")

def run_chart(args):
    gantt_chart_for_sprint_bokeh(args.sprint_name, export_path=args.export)

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Jira Charts CLI Tool")
    subparsers = parser.add_subparsers(dest='command')

    # configure command
    configure_parser = subparsers.add_parser('configure', help='Set up Jira config')
    configure_parser.add_argument('--jira-url')
    configure_parser.add_argument('--client-id')
    configure_parser.add_argument('--redirect-uri')
    configure_parser.set_defaults(func=configure)

    # show-config command
    show_parser = subparsers.add_parser('show-config', help='Display current configuration')
    show_parser.set_defaults(func=show_config)

    # reset-config command
    reset_parser = subparsers.add_parser('reset-config', help='Reset configuration to defaults')
    reset_parser.set_defaults(func=reset_config)

    # query command
    query_parser = subparsers.add_parser('query', help='Run JQL query')
    query_parser.add_argument('--jql', help='Run raw JQL query')
    query_parser.add_argument('--sprint-name', help='Sprint name to query using JQL')
    query_parser.add_argument('--export', help='Export results to CSV file')
    query_parser.set_defaults(func=query)

    # discover-fields command
    discover_parser = subparsers.add_parser('discover-fields', help='Discover field keys from Jira')
    discover_parser.add_argument('--jql', required=True)
    discover_parser.set_defaults(func=discover_fields)

    # chart command
    chart_parser = subparsers.add_parser('chart', help='Generate Gantt chart for a sprint')
    chart_parser.add_argument('--sprint-name', required=True, help='Sprint name for Gantt chart')
    chart_parser.add_argument('--export', help='Optional path to export chart data to CSV')
    chart_parser.set_defaults(func=run_chart)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
