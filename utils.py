import os

def project_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

def extract_simple_path(data, path):
    for part in path.split('.'):
        if isinstance(data, dict):
            data = data.get(part)
        else:
            return None
    return data

