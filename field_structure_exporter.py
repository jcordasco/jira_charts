import json

def fetch_field_definitions(jira):
    """
    Retrieve field definitions from Jira.
    """
    response = jira.get_raw("/rest/api/3/field")
    fields = response.json()

    field_map = {}

    for field in fields:
        field_id = field.get("id")
        field_name = field.get("name")
        schema_type = field.get("schema", {}).get("type", "unknown")
        field_map[field_id] = {
            "name": field_name,
            "type": schema_type
        }

    return field_map

def analyze_field_structure(data):
    """
    Recursively analyze the structure of fields inside a Jira issue.
    """
    if isinstance(data, dict):
        children = []
        for key, value in data.items():
            child_structure = analyze_field_structure(value)
            children.append({
                "id": key,
                "type": type_of(value),
                "children": child_structure if child_structure else None
            })
        return children if children else None

    elif isinstance(data, list):
        if data:
            return analyze_field_structure(data[0])
        else:
            return None
    else:
        return None

def type_of(value):
    if value is None:
        return "null"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int) or isinstance(value, float):
        return "number"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "unknown"

def extract_field_structure_with_names(sample_issue, field_definitions):
    """
    Merge real structure with field definitions.
    """
    fields = sample_issue.get("fields", {})
    structure = []

    for field_id, field_value in fields.items():
        field_children = analyze_field_structure(field_value)

        field_meta = field_definitions.get(field_id, {"name": "(unknown)", "type": type_of(field_value)})

        structure.append({
            "id": field_id,
            "name": field_meta["name"],
            "type": field_meta["type"],
            "children": field_children
        })

    return structure

def export_structure_to_file(structure, output_file):
    with open(output_file, "w") as f:
        json.dump(structure, f, indent=4)
