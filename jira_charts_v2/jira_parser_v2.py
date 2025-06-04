import json
import pandas as pd
from utils import project_path

class JiraParserV2:
    def __init__(self, field_mapping_path="field_mappings.json"):
        self.field_map = self._load_field_mapping(field_mapping_path)

    def _load_field_mapping(self, path):
        full_path = project_path(path)
        with open(full_path, "r") as f:
            mapping = json.load(f)
        print(f"Loaded field mappings: {list(mapping.keys())}")
        return mapping

    def _extract_field(self, issue, path):
        if not path:
            return None
        parts = path.split(".")
        value = issue
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return None

    def parse_issue(self, issue):
        fields = issue.get("fields", {})
        parsed_issue = {
            "Key": issue.get("key"),
        }

        for logical_field, json_path in self.field_map.items():
            parsed_issue[logical_field] = self._extract_field(issue, json_path)

        parsed_issue["IssueType"] = fields.get("issuetype", {}).get("name")
        parsed_issue["IssueTypeSubtask"] = fields.get("issuetype", {}).get("subtask")
        parsed_issue["IssueTypeHierarchy"] = fields.get("issuetype", {}).get("hierarchy", {}).get("level")

        return parsed_issue

    def parse_issues(self, issues):
        rows = [self.parse_issue(issue) for issue in issues]
        return pd.DataFrame(rows)
