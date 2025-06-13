import json
import logging

logger = logging.getLogger(__name__)

def fetch_field_definitions(jira):
    """
    Fetch field definitions from Jira to get field names and types.
    
    Args:
        jira: JiraClient instance
        
    Returns:
        Dictionary mapping field IDs to field definitions
    """
    fields_response = jira.get("field")
    field_dict = {}
    
    for field in fields_response:
        field_dict[field.get("id")] = field
        
    return field_dict

def extract_simple_path(data, path):
    """
    Extract a value from a nested dictionary using a dot-separated path.
    
    Args:
        data: Dictionary to extract from
        path: Dot-separated path (e.g., "fields.summary")
        
    Returns:
        Extracted value or None if path doesn't exist
    """
    parts = path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current.get(part)
        else:
            return None
            
    return current

def extract_field_structure_with_names(issue, field_definitions):
    """
    Extract the structure of fields from a sample issue with field names.
    
    Args:
        issue: Jira issue object
        field_definitions: Dictionary of field definitions from fetch_field_definitions
        
    Returns:
        Dictionary with field structure and names
    """
    structure = {}
    fields = issue.get("fields", {})
    
    for field_id, value in fields.items():
        field_def = field_definitions.get(field_id, {})
        field_name = field_def.get("name", field_id)
        
        if isinstance(value, dict):
            field_type = "object"
            field_value = value
        elif isinstance(value, list):
            field_type = "array"
            field_value = value
        else:
            field_type = "scalar"
            field_value = value
            
        structure[field_id] = {
            "name": field_name,
            "type": field_type,
            "value": field_value,
            "path": f"fields.{field_id}"
        }
        
    return structure

def export_structure_to_file(structure, output_path):
    """
    Export field structure to a JSON file.
    
    Args:
        structure: Field structure dictionary
        output_path: Path to save the JSON file
    """
    with open(output_path, 'w') as f:
        json.dump(structure, f, indent=2, default=str)
