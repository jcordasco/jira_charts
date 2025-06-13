import os
import sys
import webbrowser
import urllib.parse
import secrets
import time
from config import Config

def create_new_oauth_app():
    """
    Guide the user through creating a new Atlassian OAuth app and updating their .env file.
    This script will:
    1. Open the Atlassian developer console
    2. Guide the user through creating a new OAuth app
    3. Help the user update their .env file with the new credentials
    """
    print("=== Atlassian OAuth App Creation Guide ===")
    
    # Step 1: Open the Atlassian developer console
    print("\n=== STEP 1: OPEN ATLASSIAN DEVELOPER CONSOLE ===")
    print("Opening the Atlassian developer console in your browser...")
    webbrowser.open("https://developer.atlassian.com/console/myapps/")
    
    input("Press Enter once you've logged in to the Atlassian developer console...")
    
    # Step 2: Create a new OAuth app
    print("\n=== STEP 2: CREATE A NEW OAUTH APP ===")
    print("1. Click on 'Create' button")
    print("2. Select 'OAuth 2.0 integration'")
    print("3. Enter a name for your app (e.g., 'Jira Charts')")
    print("4. Click 'Create'")
    
    input("Press Enter once you've created the app...")
    
    # Step 3: Configure the OAuth app
    print("\n=== STEP 3: CONFIGURE THE OAUTH APP ===")
    print("1. In the left sidebar, click on 'Authorization'")
    print("2. Set the following:")
    
    # Generate a random port between 5000 and 5999
    port = secrets.randbelow(1000) + 5000
    redirect_uri = f"http://localhost:{port}/callback"
    
    print(f"   - Callback URL: {redirect_uri}")
    print("   - Authorization type: Classic")
    print("3. Click 'Save changes'")
    
    input("Press Enter once you've configured the callback URL...")
    
    # Step 4: Add permissions
    print("\n=== STEP 4: ADD PERMISSIONS ===")
    print("1. In the left sidebar, click on 'Permissions'")
    print("2. Add the following permissions:")
    print("   - Jira API: Read")
    print("   - Jira platform REST API: Read")
    print("   - Offline access: Read")
    print("3. Click 'Save changes'")
    
    input("Press Enter once you've added the permissions...")
    
    # Step 5: Get the client ID and secret
    print("\n=== STEP 5: GET CLIENT ID AND SECRET ===")
    print("1. In the left sidebar, click on 'Settings'")
    print("2. Copy the 'Client ID'")
    client_id = input("Enter the Client ID: ")
    
    print("3. Click on 'View client secret'")
    client_secret = input("Enter the Client Secret: ")
    
    # Step 6: Update the .env file
    print("\n=== STEP 6: UPDATE .ENV FILE ===")
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    env_template_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env_template")
    
    if os.path.exists(env_file):
        print(f"Backing up existing .env file to .env.bak...")
        os.rename(env_file, f"{env_file}.bak")
    
    # Create a new .env file
    print(f"Creating new .env file...")
    
    # Start with the template if it exists
    env_content = ""
    if os.path.exists(env_template_file):
        with open(env_template_file, "r") as f:
            env_content = f.read()
    
    # Update or add the OAuth configuration
    env_lines = env_content.split("\n")
    updated_lines = []
    
    # Variables to update
    updates = {
        "CLIENT_ID": client_id,
        "CLIENT_SECRET": client_secret,
        "AUTH_URL": "https://auth.atlassian.com/authorize",
        "TOKEN_URL": "https://auth.atlassian.com/oauth/token",
        "REDIRECT_URI": redirect_uri,
        "SCOPE": "offline_access read:jira-user read:jira-work",
        "OAUTHLIB_INSECURE_TRANSPORT": "1",
        "TOKEN_FILE": "token.json"
    }
    
    # Track which variables have been updated
    updated_vars = set()
    
    # Update existing variables
    for line in env_lines:
        if line.strip() and "=" in line:
            var_name = line.split("=")[0].strip()
            if var_name in updates:
                updated_lines.append(f"{var_name}={updates[var_name]}")
                updated_vars.add(var_name)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Add any variables that weren't updated
    for var_name, value in updates.items():
        if var_name not in updated_vars:
            updated_lines.append(f"{var_name}={value}")
    
    # Write the updated content to the .env file
    with open(env_file, "w") as f:
        f.write("\n".join(updated_lines))
    
    print(f".env file updated with new OAuth configuration.")
    
    # Step 7: Test the configuration
    print("\n=== STEP 7: TEST THE CONFIGURATION ===")
    print("Would you like to test the new OAuth configuration? (y/n)")
    choice = input().lower()
    if choice == "y" or choice == "yes":
        print("\nRunning the OAuth configuration checker...")
        time.sleep(1)
        
        # Import the check_oauth_config module and run it
        try:
            # Add the current directory to the Python path
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            
            # Force reload of the Config module to pick up the new .env values
            import importlib
            importlib.reload(sys.modules["config"])
            
            # Import and run the check_oauth_config module
            from check_oauth_config import check_oauth_config
            check_oauth_config()
        except Exception as e:
            print(f"Error running the OAuth configuration checker: {e}")
            print("Please run 'python check_oauth_config.py' manually.")
    
    print("\n=== OAUTH APP CREATION COMPLETE ===")
    print("Your new Atlassian OAuth app has been created and configured.")
    print("You can now try running the application again:")
    print(f"python cli.py generate-chart --chart gantt --sprint \"Your Sprint Name\"")

if __name__ == "__main__":
    create_new_oauth_app()
