import os
import json
import threading
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
from requests import HTTPError

# Load env variables
load_dotenv()

CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("JIRA_REDIRECT_URI")
AUTHORIZATION_BASE_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"
API_BASE_URL = "https://api.atlassian.com"
SCOPES = ["read:jira-work", "offline_access"]

TOKEN_FILE = "token.json"
CLOUD_FILE = "cloud.json"

# OAuth Callback Server
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
        return

def start_http_server():
    server = HTTPServer(("127.0.0.1", 5000), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

# OAuth 2 authorization flow
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

    cloud_id = fetch_cloud_id(token)
    save_cloud_id(cloud_id)

    return token

# Token persistence
def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=4)

def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

# Cloud ID persistence
def save_cloud_id(cloud_id):
    with open(CLOUD_FILE, "w") as f:
        json.dump({"cloud_id": cloud_id}, f)

def load_cloud_id():
    if os.path.exists(CLOUD_FILE):
        with open(CLOUD_FILE, "r") as f:
            return json.load(f)["cloud_id"]
    return None

# Manual refresh token handling (direct requests)
def refresh_token(token):
    print("Refreshing token...")
    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': token['refresh_token']
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    refreshed_token = response.json()
    save_token(refreshed_token)
    return refreshed_token

def get_token():
    token = load_token()
    if token:
        return token
    return oauth_flow()

# Cloud ID discovery
def fetch_cloud_id(token):
    oauth = OAuth2Session(CLIENT_ID, token=token)
    response = oauth.get(f"{API_BASE_URL}/oauth/token/accessible-resources")
    response.raise_for_status()
    cloud_ids = response.json()
    if not cloud_ids:
        raise Exception("No accessible Jira resources found.")
    return cloud_ids[0]["id"]

# Main API request with refresh handling and optional pagination
def api_request(endpoint, method="GET", params=None, data=None, paginate=False):
    token = get_token()
    cloud_id = load_cloud_id()
    if not cloud_id:
        cloud_id = fetch_cloud_id(token)
        save_cloud_id(cloud_id)

    url = f"{API_BASE_URL}/ex/jira/{cloud_id}/rest/api/3/{endpoint}"
    oauth = OAuth2Session(CLIENT_ID, token=token)

    try:
        if not paginate:
            response = oauth.request(method, url, params=params, json=data)
            response.raise_for_status()
            return response.json()

        # Pagination logic
        all_issues = []
        start_at = 0
        max_results = 100

        while True:
            paged_params = dict(params or {})
            paged_params.update({
                "startAt": start_at,
                "maxResults": max_results
            })

            response = oauth.request(method, url, params=paged_params, json=data)
            response.raise_for_status()
            result = response.json()

            issues = result.get("issues", [])
            all_issues.extend(issues)

            total = result.get("total", 0)
            start_at += max_results

            if start_at >= total:
                break

        return {"issues": all_issues}

    except HTTPError as e:
        if e.response.status_code == 401:
            token = refresh_token(token)
            oauth = OAuth2Session(CLIENT_ID, token=token)
            response = oauth.request(method, url, params=params, json=data)
            response.raise_for_status()
            return response.json()
        else:
            raise
