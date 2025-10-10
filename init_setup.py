from tkinter import Tk, Button, Label
from tkinter.ttk import Combobox
import json
import os
from style_manager import StyleManager

# Configuration paths
if os.name == "nt":  # Windows
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
else:  # Linux, macOS, etc.
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
THEMES_FILE = os.path.join(CONFIG_DIR, "themes.json")

# Load themes and config
with open(THEMES_FILE, "r") as f:
    themes = json.load(f)

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)


class InitialSetup:
    def __init__(self):
        self.steps = [
            {
                "title": "Welcome to PyDot",
                "description": "Pydot is a simple, user-friendly IDE for creating games with Pygame.",
            },
            {
                "title": "Select Theme",
                "description": "Select a theme for PyDot.",
            },
        ]
        self.step = 0
        self.popup = Tk()
        self.popup.geometry("400x200")
        self.popup.resizable(False, False)

        self.label = Label(self.popup, text="")
        self.next_btn = Button(
            self.popup,
            text="Next",
            command=self.next_step,
        )

        self.theme_combo = None

        self.style = StyleManager()
        self.style.apply_to_window(self.popup)
        self.style.apply_to_button(self.next_btn)
        self.style.apply_to_label(self.label)

        self.label.pack(padx=10, pady=10)
        self.next_btn.pack(side="bottom", padx=10, pady=10)

        self.show_step()
        self.popup.mainloop()

    def show_step(self):
        current_step = self.steps[self.step]
        self.popup.title(current_step["title"])
        self.label.config(text=current_step["description"])

        if self.theme_combo:
            self.theme_combo.pack_forget()
            self.theme_combo = None
        if current_step["title"] == "Select Theme":
            self.theme_combo = Combobox(self.popup)
            self.theme_combo.pack(padx=10, pady=10)
            theme_names = [
                themes[key]["name"] for key in themes.keys() if key != "selected"
            ]
            self.theme_combo["values"] = theme_names
            self.theme_combo.current(0)
            self.theme_combo.config(state="readonly")
            self.style.apply_to_combobox(self.theme_combo)
            self.next_btn.config(text="Finish")
            self.theme_combo.bind(
                "<<ComboboxSelected>>", lambda event: self.preview_theme()
            )
        else:
            self.next_btn.config(text="Next")

    def preview_theme(self):
        selected_name = self.theme_combo.get()
        theme_key = None
        for key in themes.keys():
            if themes[key]["name"] == selected_name:
                theme_key = key
                break

        if not theme_key:
            return

        config["theme"] = theme_key
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

        # Pass the theme_key explicitly to StyleManager
        self.style = StyleManager(theme_key)
        self.style.apply_to_window(self.popup)
        self.style.apply_to_button(self.next_btn)
        self.style.apply_to_label(self.label)
        self.style.apply_to_combobox(self.theme_combo)

    def next_step(self):
        if self.step >= len(self.steps) - 1:
            self.finish()
        else:
            self.step += 1
            self.show_step()

    def finish(self):
        selected_name = self.theme_combo.get()
        theme_key = None
        for key in themes.keys():
            if themes[key]["name"] == selected_name:
                theme_key = key
                break

        config["theme"] = theme_key
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

        self.popup.destroy()
