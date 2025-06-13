import os
import importlib
import logging

logger = logging.getLogger(__name__)

# Dictionary to store registered chart functions
chart_registry = {}

def register_chart(name):
    """
    Decorator to register a chart function in the chart registry.
    
    Args:
        name: The name of the chart, used to identify it when generating charts
        
    Returns:
        Decorator function that registers the chart
    """
    def decorator(func):
        chart_registry[name] = func
        return func
    return decorator

def get_registered_charts():
    """Get a list of all registered chart names."""
    return list(chart_registry.keys())

def run_chart(name, *args, **kwargs):
    """
    Run a registered chart function.
    
    Args:
        name: The name of the chart to run
        *args, **kwargs: Arguments to pass to the chart function
        
    Returns:
        The result of the chart function
        
    Raises:
        ValueError: If the chart is not found in the registry
    """
    if name not in chart_registry:
        raise ValueError(f"Chart '{name}' not found. Available charts: {', '.join(get_registered_charts())}")
    return chart_registry[name](*args, **kwargs)

def auto_import_charts():
    """
    Automatically import all chart modules from the charts directory.
    This allows charts to be registered dynamically without having to
    manually import each chart module.
    """
    charts_dir = os.path.join(os.path.dirname(__file__), "charts")

    if not os.path.exists(charts_dir):
        logger.warning(f"Charts directory not found at {charts_dir}")
        return

    for filename in os.listdir(charts_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"charts.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
                logger.info(f"Successfully loaded chart module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to import chart module {module_name}: {e}")
