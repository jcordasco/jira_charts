import os
import json
import logging
from utils import project_path

logger = logging.getLogger(__name__)

# Default mapping file if no custom mapping is specified
DEFAULT_MAPPING_FALLBACK = "field_mappings.json"

# File to store configuration settings
CONFIG_FILE = "config.json"

def get_default_mapping():
    """
    Get the path to the default field mapping file.
    
    Returns:
        str: Path to the default field mapping file
    """
    try:
        if os.path.exists(project_path(CONFIG_FILE)):
            with open(project_path(CONFIG_FILE), 'r') as f:
                config = json.load(f)
                default_mapping = config.get('default_mapping')
                if default_mapping and os.path.exists(project_path(default_mapping)):
                    return default_mapping
                else:
                    logger.warning(f"Default mapping file '{default_mapping}' not found, using fallback")
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    
    return DEFAULT_MAPPING_FALLBACK

def set_default_mapping(mapping_file):
    """
    Set the default field mapping file.
    
    Args:
        mapping_file: Path to the field mapping file, or 'default' to reset to default
    """
    config = {}
    
    # Load existing config if it exists
    if os.path.exists(project_path(CONFIG_FILE)):
        try:
            with open(project_path(CONFIG_FILE), 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    # Set or reset the default mapping
    if mapping_file == 'default':
        if 'default_mapping' in config:
            del config['default_mapping']
    else:
        # Verify the mapping file exists
        if not os.path.exists(project_path(mapping_file)):
            raise ValueError(f"Mapping file '{mapping_file}' not found")
        
        config['default_mapping'] = mapping_file
    
    # Save the updated config
    with open(project_path(CONFIG_FILE), 'w') as f:
        json.dump(config, f, indent=2)
