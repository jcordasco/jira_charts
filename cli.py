import argparse
import logging
from auth_manager import AuthManager
from jira_client import JiraClient
from jira_parser_v2 import JiraParserV2
from config import Config
from chart_registry_v2 import run_chart
from query_engine import run_query

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Jira Charts CLI (v2)")
    subparsers = parser.add_subparsers(dest="command")

    chart_parser = subparsers.add_parser("generate-chart", help="Generate charts")
    chart_parser.add_argument("--chart", required=True, help="Chart type")
    chart_parser.add_argument("--jql", help="JQL query to fetch data")
    chart_parser.add_argument("--sprint", help="Sprint name to query")
    chart_parser.add_argument("--limit", type=int, default=100, help="Max results")
    chart_parser.add_argument("--field-mapping", default="field_mappings.json", help="Field mapping file")
    chart_parser.add_argument("--export", help="Export final processed dataframe (CSV)")
    chart_parser.add_argument("--save", help="Save chart image (PNG/HTML/etc)")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s")

    auth = AuthManager(
        Config.CLIENT_ID,
        Config.CLIENT_SECRET,
        Config.AUTH_URL,
        Config.TOKEN_URL,
        Config.REDIRECT_URI,
        Config.SCOPE,
        Config.TOKEN_FILE
    )
    jira = JiraClient(auth)
    parser_v2 = JiraParserV2(args.field_mapping)

    if args.sprint and not args.jql:
        sprint_field = parser_v2.field_map.get("Sprint")
        if sprint_field:
            args.jql = f'"{sprint_field}" = "{args.sprint}"'
        else:
            raise ValueError("Sprint field mapping not found.")

    if not args.jql:
        raise ValueError("You must specify --jql or --sprint.")

    df = run_query(jira, parser_v2, args.jql, limit=args.limit)
    processed_df = run_chart(args.chart, df, export_path=args.save)

    if args.export and processed_df is not None:
        processed_df.to_csv(args.export, index=False)
        logger.info(f"Exported dataframe to: {args.export}")

if __name__ == "__main__":
    main()