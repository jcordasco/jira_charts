import argparse
import json
from config import load_config, update_config, save_config
from dotenv import load_dotenv
from jira_client import api_request

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
    print(f"Running JQL: {args.jql}")
    try:
        result = api_request(
            endpoint="search",
            params={"jql": args.jql, "maxResults": 10}
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error running query: {e}")

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
    query_parser.add_argument('--jql', required=True)
    query_parser.set_defaults(func=query)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
