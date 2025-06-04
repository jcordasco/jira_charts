import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLIENT_ID = os.getenv("CLIENT_ID")
    AUTH_URL = os.getenv("AUTH_URL")
    TOKEN_URL = os.getenv("TOKEN_URL")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    SCOPE = os.getenv("SCOPE", "offline_access read:jira-user read:jira-work")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
