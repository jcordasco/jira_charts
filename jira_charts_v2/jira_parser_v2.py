import json
from utils import extract_simple_path

class JiraParserV2:
    def __init__(self, field_mapping_path):
        self.field_map = self._load_field_mapping(field_mapping_path)
        print(f"Loaded field mappings: {list(self.field_map.keys())}")

    def _load_field_mapping(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def parse_issues(self, issues):
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
        import pandas as pd
        return pd.DataFrame(data)
