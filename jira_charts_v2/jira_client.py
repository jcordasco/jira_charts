class JiraClient:
    def __init__(self, auth_manager, jira_base_url):
        self.auth_manager = auth_manager
        self.base_url = jira_base_url

    def get(self, path, params=None):
        url = f"{self.base_url}/{path}"
        session = self.auth_manager.get_session()
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_myself(self):
        return self.get("rest/api/3/myself")
