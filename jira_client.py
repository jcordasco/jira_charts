import os
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

# Load environment variables
load_dotenv()

# Load from .env file
CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("JIRA_REDIRECT_URI")
AUTHORIZATION_BASE_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"
API_BASE_URL = "https://api.atlassian.com"
SCOPES = ["read:jira-work", "offline_access"]

# File to persist token
TOKEN_FILE = "token.json"

# HTTP Server for callback
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if "code" in query_params:
            self.server.auth_code = query_params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Authorization complete. You can close this window.')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing authorization code.')

    def log_message(self, format, *args):
        return  # Silence server logs

def start_http_server():
    server = HTTPServer(("127.0.0.1", 5000), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

# OAuth flow
def oauth_flow():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    authorization_url, state = oauth.authorization_url(AUTHORIZATION_BASE_URL)

    print("Opening browser for authorization...")
    print(f"If browser does not open, visit this URL manually:\n{authorization_url}")
    webbrowser.open(authorization_url)

    httpd = start_http_server()
    while not hasattr(httpd, "auth_code"):
        pass
    httpd.shutdown()

    code = httpd.auth_code
    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        code=code
    )
    save_token(token)
    return token

# Save token to file
def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=4)

# Load token from file
def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

# Refresh token if needed
def refresh_token_if_needed(token):
    if token and 'refresh_token' in token:
        extra = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}
        oauth = OAuth2Session(CLIENT_ID, token=token)
        if oauth.token['expires_in'] < 60:
            print("Refreshing token...")
            token = oauth.refresh_token(TOKEN_URL, refresh_token=token['refresh_token'], **extra)
            save_token(token)
    return token

# Get valid token (load, refresh or start new flow)
def get_token():
    token = load_token()
    if token:
        return refresh_token_if_needed(token)
    return oauth_flow()

# Generic API request wrapper
def api_request(endpoint, method="GET", params=None, data=None):
    token = get_token()
    oauth = OAuth2Session(CLIENT_ID, token=token)

    # First we need cloud ID
    cloud_ids = oauth.get(f"{API_BASE_URL}/oauth/token/accessible-resources").json()
    if not cloud_ids:
        raise Exception("No accessible Jira resources found.")
    cloud_id = cloud_ids[0]["id"]

    url = f"{API_BASE_URL}/ex/jira/{cloud_id}/rest/api/3/{endpoint}"

    response = oauth.request(method, url, params=params, json=data)

    if response.status_code >= 400:
        raise Exception(f"API request failed: {response.status_code} {response.text}")

    return response.json()

# Simple test function
if __name__ == "__main__":
    # Example JQL query: project = YOURPROJECT
    jql = 'project = TEST'

    result = api_request(
        endpoint="search",
        params={"jql": jql, "maxResults": 10}
    )

    print(json.dumps(result, indent=2))
