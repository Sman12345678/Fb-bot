import os
import importlib

# Dynamically import each Python file in the CMD directory
for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        globals()[module_name] = importlib.import_module(f"CMD.{module_name}")
