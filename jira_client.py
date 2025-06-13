import requests

class JiraClient:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.session = self.auth_manager.get_session()

        # Discover accessible resources (cloud instances)
        self.cloud_id, self.site_url = self._discover_resources()

    def _discover_resources(self):
        url = "https://api.atlassian.com/oauth/token/accessible-resources"
        response = self.session.get(url)
        response.raise_for_status()
        resources = response.json()

        if not resources:
            raise ValueError("No accessible Jira resources found for this token.")

        # For simplicity, just use the first authorized Jira instance
        for resource in resources:
            if resource["id"] and resource["url"]:
                print(f"Connected to Jira Cloud site: {resource['url']}")
                return resource["id"], resource["url"]

        raise ValueError("No Jira Cloud sites found.")

    def get(self, path, params=None):
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/{path}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_myself(self):
        return self.get("myself")
    
    def get_raw(self, path, params=None):
        # Ensure path starts with a slash to create a valid URL
        if not path.startswith('/'):
            path = '/' + path
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}{path}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response
    
    def find_sprint_id_by_name(self, sprint_name):
        """
        Find a sprint ID by its name by searching across all boards.
        
        Args:
            sprint_name: Name of the sprint to find
            
        Returns:
            Sprint ID if found, None otherwise
        """
        # Get all boards - note we use a different URL format for Agile API
        url = f"rest/agile/1.0/board"
        response = self.get_raw(url)
        boards_response = response.json()
        boards = boards_response.get("values", [])

        if not boards:
            raise ValueError("No boards found for sprint lookup.")

        for board in boards:
            board_id = board["id"]

            # Lookup sprints on this board
            sprint_url = f"rest/agile/1.0/board/{board_id}/sprint"
            sprint_response = self.get_raw(sprint_url)
            sprints_response = sprint_response.json()
            sprints = sprints_response.get("values", [])

            for sprint in sprints:
                if sprint["name"] == sprint_name:
                    return sprint["id"]

        return None
