import os
import shutil
import subprocess
import json
from tkinter import Button, Label, Tk
from tkinter.ttk import Combobox

from style_manager import StyleManager

# Configuration paths
if os.name == "nt":  # Windows
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
else:  # Linux, macOS, etc.
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
THEMES_FILE = os.path.join(CONFIG_DIR, "themes.json")

RECENT_PROJECTS_FILE = os.path.join(CONFIG_DIR, "recent_projects.json")

# Default config
config = {"theme": "vs_code_dark"}


class InitialSetup:
    def __init__(self):
        self.style = StyleManager()

        self.popup = Tk()

        self.next_btn = Button(self.popup, text="Next", command=self.next_step)
        self.back_btn = Button(self.popup, text="Back", command=self.back_step)
        self.skip_btn = Button(self.popup, text="Skip", command=self.skip_step)
        self.finish_btn = Button(self.popup, text="Finish", command=self.finish_step)
        self.download_btn = Button(
            self.popup, text="Download", command=self.download_dependencies
        )

        self.theme_combo = Combobox(self.popup, values=list(self.style.themes.keys()))
        self.theme_combo["state"] = "readonly"
        self.theme_combo.bind("<<ComboboxSelected>>", self.preview_theme)
        self.theme_combo.set(config["theme"])

        self.steps = {
            1: {
                "title": "Welcome to Pydot",
                "description": "Pydot is a Python-based IDE for Pygame development.",
                "visible": [
                    self.next_btn,
                ],
                "bound": self.next_step,
            },
            2: {
                "title": "Download Dependencies",
                "description": "Pydot requires some dependencies to be installed.",
                "visible": [
                    self.skip_btn,
                    self.back_btn,
                    self.download_btn,
                ],
                "bound": self.download_dependencies,
            },
            3: {
                "title": "Choose Theme",
                "description": "Choose a theme for Pydot.",
                "visible": [
                    self.theme_combo,
                    self.skip_btn,
                    self.back_btn,
                    self.next_btn,
                ],
                "bound": self.next_step,
            },
            4: {
                "title": "Finished",
                "description": "Pydot has been installed. You can now start using it.",
                "visible": [
                    self.back_btn,
                    self.finish_btn,
                ],
                "bound": self.finish_step,
            },
        }

        self.current_step = 1

        self.style.apply_to(self.popup)
        self.style.apply_to(self.next_btn)
        self.style.apply_to(self.back_btn)
        self.style.apply_to(self.skip_btn)
        self.style.apply_to(self.finish_btn)
        self.style.apply_to(self.download_btn)
        self.style.apply_to_combobox()

    def next_step(self):
        self.current_step += 1
        self.update_ui()

    def back_step(self):
        self.current_step -= 1
        self.update_ui()

    def skip_step(self):
        self.current_step += 1
        self.update_ui()

    def download_dependencies(self):
        try:
            subprocess.run(["pip", "install", "-r", "requirements.txt"])
        except Exception as e:
            print(f"Error downloading dependencies: {e}")
        self.next_step()

    def finish_step(self):
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)
        shutil.copyfile("themes.json", THEMES_FILE)
        config["theme"] = self.theme_combo.get()
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
            f.close()
        with open(RECENT_PROJECTS_FILE, "w") as f:
            json.dump([], f)
            f.close()
        self.popup.destroy()
        subprocess.run(["python", "main.py"])

    def update_ui(self):
        for widget in self.popup.winfo_children():
            if isinstance(widget, (Button, Combobox)):
                widget.pack_forget()
            else:
                widget.destroy()

        step = self.steps[self.current_step]
        self.popup.title(step["title"])
        self.popup.geometry("400x200")
        self.popup.resizable(False, False)

        desc = Label(self.popup, text=step["description"], wraplength=350)
        self.style.apply_to(desc)
        desc.pack(pady=10)

        for widget in reversed(step["visible"]):
            if isinstance(widget, Button):
                widget.pack(side="bottom", pady=3, padx=3)
            elif isinstance(widget, Combobox):
                widget.pack(side="top", pady=3, padx=3, fill="x")

        self.popup.bind("<Return>", lambda event: step["bound"]())
        self.center_window()
        self.popup.mainloop()

    def center_window(self):
        self.popup.update_idletasks()

        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()

        window_width = self.popup.winfo_width()
        window_height = self.popup.winfo_height()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.popup.geometry(f"+{x}+{y}")

    def preview_theme(self, event=None):
        selected_theme = self.theme_combo.get()
        if selected_theme and selected_theme in self.style.themes:
            self.style.current_theme = self.style.themes[selected_theme]

            try:
                self.style.apply_to(self.popup)
                for widget in self.popup.winfo_children():
                    self.style.apply_to(widget)
                self.style.apply_to_combobox()
            except Exception as e:
                print(f"Error applying theme preview: {e}")


if __name__ == "__main__":
    app = InitialSetup()
    app.update_ui()
