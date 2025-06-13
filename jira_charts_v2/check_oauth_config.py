import os
import sys
import webbrowser
import urllib.parse
from config import Config

def check_oauth_config():
    """
    Check the OAuth configuration and provide guidance on how to fix common issues.
    This script will:
    1. Check the OAuth configuration in the .env file
    2. Provide guidance on how to check the Atlassian OAuth app configuration
    3. Suggest fixes for common issues
    """
    print("=== Atlassian OAuth Configuration Checker ===")
    
    # Check the OAuth configuration in the .env file
    print("\n=== CHECKING LOCAL CONFIGURATION ===")
    
    # Check CLIENT_ID
    if not Config.CLIENT_ID:
        print("❌ CLIENT_ID is missing or empty")
    else:
        print(f"✅ CLIENT_ID is set: {Config.CLIENT_ID[:5]}...")
    
    # Check CLIENT_SECRET
    if not Config.CLIENT_SECRET:
        print("❌ CLIENT_SECRET is missing or empty")
    else:
        print(f"✅ CLIENT_SECRET is set: {Config.CLIENT_SECRET[:5]}...")
    
    # Check REDIRECT_URI
    if not Config.REDIRECT_URI:
        print("❌ REDIRECT_URI is missing or empty")
    else:
        print(f"✅ REDIRECT_URI is set: {Config.REDIRECT_URI}")
        
        # Check if REDIRECT_URI is properly formatted
        if not Config.REDIRECT_URI.startswith("http://") and not Config.REDIRECT_URI.startswith("https://"):
            print("   ⚠️ REDIRECT_URI should start with http:// or https://")
        
        # Check if REDIRECT_URI includes a port
        if "localhost" in Config.REDIRECT_URI and ":" not in Config.REDIRECT_URI.split("//")[1].split("/")[0]:
            print("   ⚠️ REDIRECT_URI should include a port (e.g., http://localhost:5000/callback)")
    
    # Check AUTH_URL
    if not Config.AUTH_URL:
        print("❌ AUTH_URL is missing or empty")
    else:
        print(f"✅ AUTH_URL is set: {Config.AUTH_URL}")
        
        # Check if AUTH_URL is the correct Atlassian URL
        if Config.AUTH_URL != "https://auth.atlassian.com/authorize":
            print("   ⚠️ AUTH_URL should be https://auth.atlassian.com/authorize")
    
    # Check TOKEN_URL
    if not Config.TOKEN_URL:
        print("❌ TOKEN_URL is missing or empty")
    else:
        print(f"✅ TOKEN_URL is set: {Config.TOKEN_URL}")
        
        # Check if TOKEN_URL is the correct Atlassian URL
        if Config.TOKEN_URL != "https://auth.atlassian.com/oauth/token":
            print("   ⚠️ TOKEN_URL should be https://auth.atlassian.com/oauth/token")
    
    # Check SCOPE
    if not Config.SCOPE:
        print("❌ SCOPE is missing or empty")
    else:
        print(f"✅ SCOPE is set: {Config.SCOPE}")
        
        # Check if SCOPE includes the required scopes
        required_scopes = ["offline_access", "read:jira-user", "read:jira-work"]
        missing_scopes = [scope for scope in required_scopes if scope not in Config.SCOPE]
        if missing_scopes:
            print(f"   ⚠️ SCOPE is missing required scopes: {', '.join(missing_scopes)}")
    
    # Print guidance on how to check the Atlassian OAuth app configuration
    print("\n=== ATLASSIAN OAUTH APP CONFIGURATION ===")
    print("To check your Atlassian OAuth app configuration:")
    print("1. Go to https://developer.atlassian.com/console/myapps/")
    print("2. Select your OAuth app")
    print("3. Check the following settings:")
    print("   - Callback URL: Should exactly match your REDIRECT_URI")
    print("   - Permissions: Should include the required scopes")
    
    # Print guidance on how to fix common issues
    print("\n=== COMMON ISSUES AND FIXES ===")
    print("1. 'build: authorization header missing' error in browser:")
    print("   - This usually indicates an issue with your Atlassian OAuth app configuration")
    print("   - Ensure your Callback URL in Atlassian exactly matches your REDIRECT_URI")
    print("   - Try creating a new OAuth app in Atlassian and updating your .env file")
    
    print("\n2. Port already in use:")
    print("   - Change the port in your REDIRECT_URI (e.g., from 5000 to 5001)")
    print("   - Update the Callback URL in your Atlassian OAuth app to match")
    
    print("\n3. Invalid client error:")
    print("   - Ensure your CLIENT_ID and CLIENT_SECRET are correct")
    print("   - Try regenerating your client secret in Atlassian and updating your .env file")
    
    # Offer to open the Atlassian developer console
    print("\n=== NEXT STEPS ===")
    print("Would you like to open the Atlassian developer console to check your OAuth app configuration? (y/n)")
    choice = input().lower()
    if choice == "y" or choice == "yes":
        webbrowser.open("https://developer.atlassian.com/console/myapps/")
        print("Browser opened to Atlassian developer console.")
    
    # Offer to generate a test authorization URL
    print("\nWould you like to generate a test authorization URL? (y/n)")
    choice = input().lower()
    if choice == "y" or choice == "yes":
        # Generate a random state
        import secrets
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
        print(f"\nTest authorization URL: {auth_url}")
        
        print("\nWould you like to open this URL in your browser? (y/n)")
        choice = input().lower()
        if choice == "y" or choice == "yes":
            webbrowser.open(auth_url)
            print("Browser opened with test authorization URL.")

if __name__ == "__main__":
    check_oauth_config()
