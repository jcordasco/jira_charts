import json
import pandas as pd
from utils import extract_simple_path

class JiraParserV2:
    def __init__(self, field_mapping_path):
        """
        Initialize the parser with a field mapping file.
        
        Args:
            field_mapping_path: Path to the JSON file containing field mappings
        """
        self.field_map = self._load_field_mapping(field_mapping_path)
        print(f"Loaded field mappings: {list(self.field_map.keys())}")

    def _load_field_mapping(self, path):
        """Load field mappings from a JSON file."""
        with open(path, "r") as f:
            return json.load(f)

    def parse_issues(self, issues):
        """
        Parse a list of Jira issues into a structured format based on field mappings.
        
        Args:
            issues: List of Jira issue objects
            
        Returns:
            pandas.DataFrame: DataFrame containing the parsed issues
        """
        parsed = []
        for issue in issues:
            fields = issue.get("fields", {})
            parsed_issue = {"Key": issue.get("key")}
            for output_field, mapping in self.field_map.items():
                value = self._extract_field(fields, mapping)
                parsed_issue[output_field] = value
            parsed.append(parsed_issue)
        return self._to_dataframe(parsed)

    def _extract_field(self, fields, mapping):
        """
        Extract a field value from Jira issue fields based on the mapping.
        
        Args:
            fields: Dictionary of issue fields
            mapping: String path or dictionary with extraction rules
            
        Returns:
            The extracted field value
        """
        if isinstance(mapping, str):
            return extract_simple_path(fields, mapping)

        elif isinstance(mapping, dict):
            path = mapping.get("path")
            mapping_type = mapping.get("type", "scalar")
            raw_value = extract_simple_path(fields, path)

            if mapping_type == "list" and isinstance(raw_value, list):
                subfield = mapping.get("field")
                return [item.get(subfield) for item in raw_value if item and subfield in item]

            return raw_value

        else:
            return None

    def _to_dataframe(self, data):
        """Convert parsed issues to a pandas DataFrame."""
        return pd.DataFrame(data)
