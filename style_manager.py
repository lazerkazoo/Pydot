import json
import os
from tkinter import *
from tkinter.ttk import Style

# Configuration paths
if os.name == "nt":  # Windows
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
else:  # Linux, macOS, etc.
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
THEMES_FILE = os.path.join(CONFIG_DIR, "themes.json")

# Load default theme
try:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        theme = config["theme"]
except (FileNotFoundError, KeyError):
    theme = "vs_code_dark"


class StyleManager:
    def __init__(self, theme_name: str = theme):
        self.themes: dict[str, dict[str, str]]
        self.current_theme: dict[str, str]
        self.ttk_style: Style

        try:
            with open(THEMES_FILE, "r") as f:
                self.themes = json.load(f)
        except FileNotFoundError:
            with open(os.path.join("data", "themes.json"), "r") as f:
                self.themes = json.load(f)

        self.current_theme = self.themes[theme_name]

        self.ttk_style = Style()

    def apply_to(self, widget):
        if isinstance(widget, (Tk, Toplevel)):
            widget.configure(
                bg=self.current_theme["bg_primary"],
            )
        elif isinstance(widget, Label):
            widget.configure(
                bg=self.current_theme["bg_secondary"],
                fg=self.current_theme["text_primary"],
            )
        elif isinstance(widget, Button):
            widget.configure(
                bg=self.current_theme["accent"],
                fg=self.current_theme["text_primary"],
                activebackground=self.current_theme["accent"],
                activeforeground=self.current_theme["text_primary"],
                borderwidth=0,
                relief="flat",
            )
        elif isinstance(widget, Entry):
            widget.configure(
                bg=self.current_theme["bg_tertiary"],
                fg=self.current_theme["text_primary"],
                insertbackground=self.current_theme["text_primary"],
                selectbackground=self.current_theme["accent"],
                selectforeground=self.current_theme["text_primary"],
                borderwidth=1,
                relief="solid",
            )
        elif isinstance(widget, Frame):
            widget.configure(
                bg=self.current_theme["bg_secondary"],
            )
        elif isinstance(widget, LabelFrame):
            widget.configure(
                bg=self.current_theme["bg_secondary"],
                fg=self.current_theme["text_primary"],
            )
        elif isinstance(widget, Text):
            widget.configure(
                bg=self.current_theme["bg_primary"],
                fg=self.current_theme["text_primary"],
                insertbackground=self.current_theme["text_primary"],
                selectbackground=self.current_theme["accent"],
                selectforeground=self.current_theme["text_primary"],
            )
        elif isinstance(widget, Checkbutton):
            widget.configure(
                bg=self.current_theme["bg_primary"],
                fg=self.current_theme["text_primary"],
            )
        elif isinstance(widget, Listbox):
            widget.configure(
                bg=self.current_theme["bg_primary"],
                fg=self.current_theme["text_primary"],
                selectbackground=self.current_theme["accent"],
                selectforeground=self.current_theme["text_primary"],
            )

    def apply_to_combobox(self):
        self.ttk_style.theme_use("default")
        self.ttk_style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.current_theme["bg_tertiary"])],
            selectbackground=[("readonly", self.current_theme["accent"])],
            selectforeground=[("readonly", self.current_theme["text_primary"])],
        )
        self.ttk_style.configure(
            "TCombobox",
            fieldbackground=self.current_theme["bg_tertiary"],
            background=self.current_theme["bg_secondary"],
            foreground=self.current_theme["text_primary"],
            arrowcolor=self.current_theme["text_primary"],
            bordercolor=self.current_theme["border"],
            lightcolor=self.current_theme["accent"],
            darkcolor=self.current_theme["accent"],
        )
