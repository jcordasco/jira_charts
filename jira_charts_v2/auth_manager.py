import os
import json
import time
from requests_oauthlib import OAuth2Session

class AuthManager:
    def __init__(self, client_id, token_url, auth_url, redirect_uri, scope, token_path="token.json"):
        self.client_id = client_id
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
            print("✅ Loaded existing token.")
        else:
            print("⚠ No existing token found.")
            self.token = None
            self.session = None

    def save_token(self, token):
        with open(self.token_path, "w") as f:
            json.dump(token, f)
        self.token = token
        print("💾 Token saved.")

    def _create_session(self, token=None):
        return OAuth2Session(
            client_id=self.client_id,
            token=token,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            auto_refresh_url=self.token_url,
            auto_refresh_kwargs={"client_id": self.client_id},
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
        if not self.session:
            self.session = self._create_session(self.token)
        print("🔄 Attempting to refresh token...")
        extra = {"client_id": self.client_id}
        new_token = self.session.refresh_token(self.token_url, refresh_token=self.token['refresh_token'], **extra)
        self.save_token(new_token)
        self.session = self._create_session(new_token)
        print("✅ Token refreshed.")

    def authenticate(self):
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        auth_url, state = oauth.authorization_url(self.auth_url, access_type="offline", prompt="consent")
        print(f"👉 Open this URL in browser to authenticate:\n{auth_url}")
        redirect_response = input("Paste the full redirect URL here: ").strip()
        token = oauth.fetch_token(
            self.token_url,
            authorization_response=redirect_response,
            client_id=self.client_id
        )
        self.save_token(token)
        self.session = self._create_session(token)

    def get_session(self):
        if self.token_expired():
            try:
                self.refresh_token()
            except Exception as e:
                print(f"⚠ Refresh failed: {e}")
                self.authenticate()
        if not self.session:
            self.authenticate()
        return self.session
