import os
import shutil
import subprocess
import json
from tkinter import Button, Label, Tk, messagebox
from tkinter.ttk import Combobox

from style_manager import StyleManager

# Configuration paths
if os.name == "nt":  # Windows
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
else:  # Linux, macOS, etc.
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

to_save = os.path.join(os.path.expanduser("~"), "PydotProjects")
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

        self.browse_btn = Button(
            self.popup, text="Browse", command=self.browse_location
        )

        self.theme_combo = Combobox(self.popup)
        self.theme_combo["state"] = "readonly"
        self.theme_combo.bind("<<ComboboxSelected>>", self.preview_theme)
        themes = []
        for theme in self.style.themes.values():
            themes.append(theme["name"])
        self.theme_combo["values"] = themes
        self.theme_combo.set(themes[0])

        self.to_save = to_save

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
                    self.back_btn,
                    self.next_btn,
                ],
                "bound": self.next_step,
            },
            4: {
                "title": "Choose Save Location",
                "description": f"Choose where to save your projects. Default is {to_save}.",
                "visible": [
                    self.browse_btn,
                    self.back_btn,
                    self.next_btn,
                ],
                "bound": self.next_step,
            },
            5: {
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
        self.style.apply_to(self.browse_btn)
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
            messagebox.showinfo("error", str(e))
        self.next_step()

    def finish_step(self):
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)
        shutil.copyfile(os.path.join("data", "themes.json"), THEMES_FILE)
        for theme, data in self.style.themes.items():
            if data["name"] == self.theme_combo.get():
                config["theme"] = theme
                break
        config["default_project_location"] = self.to_save
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
            f.close()
        with open(RECENT_PROJECTS_FILE, "w") as f:
            json.dump({}, f)
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

        self.desc = Label(self.popup, text=step["description"], wraplength=350)
        self.style.apply_to(self.desc)
        self.desc.pack(pady=10)

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
        for theme, data in self.style.themes.items():
            if data["name"] == self.theme_combo.get():
                self.style.current_theme = self.style.themes[theme]
                break

        self.style.apply_to(self.popup)
        self.style.apply_to(self.next_btn)
        self.style.apply_to(self.back_btn)
        self.style.apply_to(self.skip_btn)
        self.style.apply_to(self.finish_btn)
        self.style.apply_to(self.browse_btn)
        self.style.apply_to(self.download_btn)
        self.style.apply_to(self.desc)
        self.style.apply_to_combobox()

    def browse_location(self):
        from tkinter.filedialog import askdirectory

        selected_dir = askdirectory(initialdir=os.path.expanduser("~"))
        if not selected_dir or selected_dir == os.path.join("()", ""):
            return
        self.to_save = selected_dir
        self.next_step()
