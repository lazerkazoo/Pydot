import os

# Only run if this file is executed directly, not imported
if __name__ == "__main__":
    if os.name == "nt":  # Windows
        CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
    else:  # Linux, macOS, etc.
        CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

    if not os.path.exists(CONFIG_DIR):
        print("Configuration directory not found. Running initial setup...")
        from init_setup import InitialSetup

        setup = InitialSetup()
        setup.update_ui()
    else:
        from project_manager import App

        app = App()
