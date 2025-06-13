# Jira Charts v2

A Python application for generating charts from Jira data using OAuth 2.0 authentication.

## Authentication Troubleshooting

If you encounter the "build: authorization header missing" error during OAuth authentication, follow these steps to diagnose and fix the issue:

### 1. Create a New OAuth App

If you're experiencing authentication issues, the best solution is often to create a new OAuth app with the correct configuration:

```bash
cd jira_charts_v2
python create_new_oauth_app.py
```

This interactive script will:
- Guide you through creating a new Atlassian OAuth app
- Help you configure the correct permissions and callback URL
- Update your .env file with the new credentials
- Test the new configuration

### 2. Check Your OAuth Configuration

This script checks your OAuth configuration and provides guidance on how to fix common issues:

```bash
cd jira_charts_v2
python check_oauth_config.py
```

This will:
- Check your local OAuth configuration in the .env file
- Provide guidance on how to check your Atlassian OAuth app configuration
- Suggest fixes for common issues
- Offer to open the Atlassian developer console
- Generate a test authorization URL

### 3. Run the Direct OAuth Debug Script

This script provides the most detailed debugging information about the OAuth flow using direct HTTP requests:

```bash
cd jira_charts_v2
python direct_oauth_debug.py
```

This will:
- Start the OAuth authorization flow with direct HTTP requests
- Capture the authorization code
- Make a token request with detailed logging
- Test the token if successful
- Save the token and resources to files for inspection

### 4. Run the Standard Debug Script

This script provides debugging information using the OAuth2Session library:

```bash
cd jira_charts_v2
python debug_oauth.py
```

This will:
- Start the OAuth authorization flow
- Capture the authorization code
- Make a token request with detailed logging
- Test the token if successful

### 5. Run the Authentication Test

This script tests the authentication flow in isolation:

```bash
cd jira_charts_v2
python test_auth.py
```

This will:
- Delete any existing token file
- Trigger a fresh authentication flow
- Test the token by making a request to the Atlassian API

### 6. Check Your .env Configuration

Ensure your `.env` file has the correct OAuth credentials:

```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
AUTH_URL=https://auth.atlassian.com/authorize
TOKEN_URL=https://auth.atlassian.com/oauth/token
REDIRECT_URI=http://localhost:5000/callback
SCOPE=offline_access read:jira-user read:jira-work
JIRA_BASE_URL=https://your-instance.atlassian.net
OAUTHLIB_INSECURE_TRANSPORT=1
TOKEN_FILE="token.json"
```

### 7. Common Issues and Solutions

#### Authorization Header Missing

The "build: authorization header missing" error can appear in two places:

1. **In the browser during authorization**: This indicates an issue with the Atlassian OAuth service itself. Possible causes:
   - The OAuth app configuration in Atlassian might be incorrect
   - The redirect URI might not match exactly what's configured in Atlassian
   - The client ID or client secret might be incorrect
   - The Atlassian OAuth app might not have the required permissions

   **Solution**: The easiest solution is to use the `create_new_oauth_app.py` script to create a new OAuth app with the correct configuration:
   ```bash
   python create_new_oauth_app.py
   ```
   
   Alternatively, you can use the `check_oauth_config.py` script to verify your existing configuration:
   ```bash
   python check_oauth_config.py
   ```

2. **In API responses**: This indicates an issue with how the token is being used. Possible causes:
   - The OAuth token request doesn't include the correct headers
   - The token response doesn't contain an access_token
   - The Authorization header isn't being properly set in API requests

The fixes implemented in this version:
- Using direct HTTP requests for the OAuth flow instead of relying on libraries
- Explicitly adding Authorization headers to all API requests
- Using a more robust token request method
- Adding detailed error handling and debugging
- Providing multiple debugging scripts to isolate the issue
- Adding a configuration checker to verify your Atlassian OAuth app setup

#### Port Already in Use

If you see an error about the port being in use:
- Change the port number in your REDIRECT_URI (e.g., from 5000 to 5001)
- Update the same port in your Atlassian OAuth app configuration

#### Invalid Client Secret

If you see an "invalid client" error:
- Verify your CLIENT_ID and CLIENT_SECRET are correct
- Ensure your REDIRECT_URI exactly matches what's configured in your Atlassian OAuth app

## Running the Application

To generate a chart:

```bash
cd jira_charts_v2
python cli.py generate-chart --chart gantt --jql "project = PROJ AND status != Done"
```

Or filter by sprint:

```bash
python cli.py generate-chart --chart gantt --sprint "Sprint Name"
```

## Additional Options

- `--save filename.png`: Save the chart to a file
- `--export data.csv`: Export the processed data to CSV
- `--limit 200`: Limit the number of issues fetched
