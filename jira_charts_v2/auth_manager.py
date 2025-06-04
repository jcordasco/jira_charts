import os
import json
import time
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from requests_oauthlib import OAuth2Session

class OAuthRedirectHandler(BaseHTTPRequestHandler):
    authorization_response = None

    def do_GET(self):
        OAuthRedirectHandler.authorization_response = self.path
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Authentication complete. You can close this window.")

class AuthManager:
    def __init__(self, client_id, client_secret, token_url, auth_url, redirect_uri, scope, token_path="token.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.auth_url = auth_url
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.token_path = token_path

        self.session = None
        self.token = None

        self.load_token()

    def load_token(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, "r") as f:
                self.token = json.load(f)
            self.session = self._create_session(self.token)
            print("Loaded existing token from file.")
        else:
            print("No existing token found.")
            self.token = None
            self.session = None

    def save_token(self, token):
        with open(self.token_path, "w") as f:
            json.dump(token, f)
        self.token = token
        print("Token saved to file.")

    def _create_session(self, token=None):
        return OAuth2Session(
            client_id=self.client_id,
            token=token,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            auto_refresh_url=self.token_url,
            auto_refresh_kwargs={"client_id": self.client_id, "client_secret": self.client_secret},
            token_updater=self.save_token,
        )

    def token_expired(self):
        if not self.token:
            return True
        expires_at = self.token.get("expires_at")
        if not expires_at:
            return True
        return expires_at < time.time()

    def refresh_token(self):
        if not self.token:
            raise ValueError("No token available to refresh.")
        if not self.session:
            self.session = self._create_session(self.token)

        print("Attempting to refresh token...")
        extra = {"client_id": self.client_id, "client_secret": self.client_secret}
        new_token = self.session.refresh_token(self.token_url, refresh_token=self.token.get('refresh_token'), **extra)
        self.save_token(new_token)
        self.session = self._create_session(new_token)
        print("Token refreshed.")

    def authenticate(self):
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )

        auth_url, state = oauth.authorization_url(self.auth_url)
        print(f"Opening browser to: {auth_url}")
        webbrowser.open(auth_url)

        parsed_redirect = self.redirect_uri.split('/')
        port = int(parsed_redirect[2].split(':')[1])
        server_address = ('', port)
        httpd = HTTPServer(server_address, OAuthRedirectHandler)

        server_thread = threading.Thread(target=httpd.handle_request)
        server_thread.start()
        server_thread.join()

        authorization_response = f"{self.redirect_uri}{OAuthRedirectHandler.authorization_response}"

        token = oauth.fetch_token(
            self.token_url,
            authorization_response=authorization_response,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        self.save_token(token)
        self.session = self._create_session(token)

    def get_session(self):
        if self.token_expired():
            try:
                self.refresh_token()
            except Exception as e:
                print(f"Refresh failed: {e}")
                self.authenticate()

        if not self.session:
            self.authenticate()

        return self.session
