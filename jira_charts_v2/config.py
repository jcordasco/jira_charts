import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    AUTH_URL = os.getenv("AUTH_URL")
    TOKEN_URL = os.getenv("TOKEN_URL")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    SCOPE = os.getenv("SCOPE", "offline_access read:jira-user read:jira-work")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")

    @classmethod
    def validate(cls):
        missing = []
        for attr in ["CLIENT_ID", "CLIENT_SECRET", "AUTH_URL", "TOKEN_URL", "REDIRECT_URI", "JIRA_BASE_URL"]:
            if not getattr(cls, attr):
                missing.append(attr)
        if missing:
            raise ValueError(f"Missing required config values: {', '.join(missing)}")

# Handle insecure transport for local development
if os.getenv("OAUTHLIB_INSECURE_TRANSPORT") == "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
