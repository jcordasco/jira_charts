import os
import sys
import requests
import webbrowser
import threading
import urllib.parse
import secrets
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import Config

# Global variable to store the authorization response
authorization_response = None

class DirectOAuthRedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_response
        print(f"\n=== RECEIVED CALLBACK ===")
        print(f"Path: {self.path}")
        print(f"Headers: {self.headers}")
        
        authorization_response = self.path
        
        # Check if the callback contains an error
        if "error=" in self.path:
            error_message = f"<h1>Authentication Error</h1><p>Error in OAuth callback: {self.path}</p>"
            print(f"Error in OAuth callback: {self.path}")
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(error_message.encode('utf-8'))
        else:
            success_message = "<h1>Authentication Complete</h1><p>You can close this window and return to the application.</p>"
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(success_message.encode('utf-8'))
            
    def log_message(self, format, *args):
        # Override to provide more detailed logging
        print(f"DirectOAuthRedirectHandler: {format % args}")

def direct_oauth_debug():
    """
    Debug the OAuth flow with Atlassian using direct HTTP requests.
    This script will:
    1. Start the authorization flow with a direct HTTP request
    2. Capture the authorization code
    3. Make a token request with a direct HTTP request
    4. Test the token with a direct HTTP request
    """
    global authorization_response
    
    print("=== Atlassian OAuth Flow Direct Debugging ===")
    
    # Print configuration
    print(f"\n=== CONFIGURATION ===")
    print(f"Client ID: {Config.CLIENT_ID}")
    print(f"Client Secret: {Config.CLIENT_SECRET[:5]}...")  # Only show first few chars
    print(f"Redirect URI: {Config.REDIRECT_URI}")
    print(f"Auth URL: {Config.AUTH_URL}")
    print(f"Token URL: {Config.TOKEN_URL}")
    print(f"Scope: {Config.SCOPE}")
    
    # Step 1: Start authorization flow
    print(f"\n=== STEP 1: AUTHORIZATION REQUEST ===")
    
    # Generate a random state
    state = secrets.token_hex(16)
    
    # Generate authorization URL
    auth_params = {
        "client_id": Config.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.REDIRECT_URI,
        "scope": Config.SCOPE,
        "state": state,
        "audience": "api.atlassian.com",
        "prompt": "consent"
    }
    
    auth_url = f"{Config.AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    print(f"Authorization URL: {auth_url}")
    
    # Start HTTP server to receive callback
    parsed_redirect = Config.REDIRECT_URI.split('/')
    port = int(parsed_redirect[2].split(':')[1])
    server_address = ('', port)
    print(f"Starting HTTP server on port {port} to receive OAuth callback...")
    httpd = HTTPServer(server_address, DirectOAuthRedirectHandler)
    
    # Open browser and wait for callback
    print("Opening browser for authorization...")
    webbrowser.open(auth_url)
    
    server_thread = threading.Thread(target=httpd.handle_request)
    server_thread.start()
    server_thread.join()
    
    if not authorization_response:
        print("Error: No authorization response received.")
        return
    
    # Step 2: Extract authorization code
    print(f"\n=== STEP 2: EXTRACT AUTHORIZATION CODE ===")
    full_redirect_uri = f"{Config.REDIRECT_URI}{authorization_response}"
    print(f"Full redirect URI: {full_redirect_uri}")
    
    parsed_url = urllib.parse.urlparse(full_redirect_uri)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        print(f"Error: No authorization code found in callback. Query params: {query_params}")
        return
        
    auth_code = query_params['code'][0]
    print(f"Authorization code: {auth_code[:10]}...")
    
    # Step 3: Request token
    print(f"\n=== STEP 3: TOKEN REQUEST ===")
    
    # Prepare token request data
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': Config.REDIRECT_URI,
        'client_id': Config.CLIENT_ID,
        'client_secret': Config.CLIENT_SECRET
    }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    print(f"Token request URL: {Config.TOKEN_URL}")
    print(f"Token request data: {token_data}")
    print(f"Token request headers: {headers}")
    
    # Make token request
    try:
        print("\nSending token request...")
        token_response = requests.post(
            Config.TOKEN_URL,
            data=token_data,
            headers=headers
        )
        
        print(f"Response status: {token_response.status_code}")
        print(f"Response headers: {token_response.headers}")
        
        if token_response.status_code == 200:
            token = token_response.json()
            print(f"Token response: {token.keys()}")
            if 'access_token' in token:
                print(f"Access token: {token['access_token'][:10]}...")
                print("Token request successful!")
                
                # Save token to file for inspection
                token_file = "direct_debug_token.json"
                with open(token_file, "w") as f:
                    json.dump(token, f, indent=2)
                print(f"Token saved to {token_file}")
                
                # Step 4: Test the token
                print("\n=== STEP 4: TEST TOKEN ===")
                test_headers = {
                    "Authorization": f"Bearer {token['access_token']}",
                    "Accept": "application/json"
                }
                
                print("Testing token with a request to Atlassian API...")
                print(f"Request URL: https://api.atlassian.com/oauth/token/accessible-resources")
                print(f"Request headers: {test_headers}")
                
                test_response = requests.get(
                    "https://api.atlassian.com/oauth/token/accessible-resources",
                    headers=test_headers
                )
                print(f"Test response status: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    resources = test_response.json()
                    print(f"Found {len(resources)} accessible resources:")
                    for resource in resources:
                        print(f"  - {resource.get('name', 'Unnamed')} ({resource.get('url', 'No URL')})")
                    print("Token test successful!")
                    
                    # Save resources to file for inspection
                    resources_file = "direct_debug_resources.json"
                    with open(resources_file, "w") as f:
                        json.dump(resources, f, indent=2)
                    print(f"Resources saved to {resources_file}")
                else:
                    print(f"Test response: {test_response.text}")
            else:
                print("Error: No access_token in response")
                print(f"Full response: {token}")
        else:
            print(f"Token request failed: {token_response.text}")
    except Exception as e:
        print(f"Error making token request: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    direct_oauth_debug()
