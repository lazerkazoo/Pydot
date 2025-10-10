import os
import subprocess

# Only run if this file is executed directly, not imported
if __name__ == "__main__":
    if os.name == "nt":  # Windows
        CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
    else:  # Linux, macOS, etc.
        CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

    if not os.path.exists(CONFIG_DIR):
        subprocess.run(["python", "init_setup.py"])
    else:
        subprocess.run(["python", "project_manager.py"])
