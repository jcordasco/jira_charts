import os
import importlib
import logging

logger = logging.getLogger(__name__)

chart_registry = {}

def register_chart(name):
    def decorator(func):
        chart_registry[name] = func
        return func
    return decorator

def get_registered_charts():
    return list(chart_registry.keys())

def run_chart(name, *args, **kwargs):
    if name not in chart_registry:
        raise ValueError(f"Chart '{name}' not found")
    return chart_registry[name](*args, **kwargs)

def auto_import_charts():
    charts_dir = os.path.join(os.path.dirname(__file__), "charts")

    for filename in os.listdir(charts_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"charts.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
                logger.info(f"Successfully loaded chart module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to import chart module {module_name}: {e}")
