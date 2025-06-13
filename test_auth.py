import os
import sys
from auth_manager import AuthManager
from config import Config

def test_authentication():
    """
    Test the OAuth authentication flow with Atlassian.
    This script will:
    1. Initialize the AuthManager
    2. Delete any existing token file
    3. Trigger the authentication flow
    4. Test the token by making a request to the Atlassian API
    """
    print("=== Jira OAuth Authentication Test ===")
    
    # Load configuration
    print(f"Client ID: {Config.CLIENT_ID}")
    print(f"Redirect URI: {Config.REDIRECT_URI}")
    print(f"Auth URL: {Config.AUTH_URL}")
    print(f"Token URL: {Config.TOKEN_URL}")
    
    # Initialize AuthManager
    auth_manager = AuthManager(
        Config.CLIENT_ID,
        Config.CLIENT_SECRET,
        Config.TOKEN_URL,
        Config.AUTH_URL,
        Config.REDIRECT_URI,
        Config.SCOPE,
        Config.TOKEN_FILE
    )
    
    # Delete existing token if it exists
    if os.path.exists(Config.TOKEN_FILE):
        print(f"Deleting existing token file: {Config.TOKEN_FILE}")
        os.remove(Config.TOKEN_FILE)
    
    # Trigger authentication
    print("Starting authentication flow...")
    auth_manager.authenticate()
    
    # Test the token
    print("Testing token with a request to Atlassian API...")
    session = auth_manager.get_session()
    
    try:
        response = session.get("https://api.atlassian.com/oauth/token/accessible-resources")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            resources = response.json()
            print(f"Found {len(resources)} accessible resources:")
            for resource in resources:
                print(f"  - {resource.get('name', 'Unnamed')} ({resource.get('url', 'No URL')})")
            print("Authentication test successful!")
        else:
            print(f"Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing token: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_authentication()
