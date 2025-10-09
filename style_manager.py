import json
import os
from tkinter import Button, Checkbutton, Entry, Frame, Label, Listbox, Text, Tk
from tkinter.ttk import Combobox, Style

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
    def __init__(self, theme_name=theme):
        # Load themes from config directory or fallback to local
        try:
            with open(THEMES_FILE, "r") as f:
                self.themes = json.load(f)
        except FileNotFoundError:
            with open("themes.json", "r") as f:
                self.themes = json.load(f)

        self.current_theme = self.themes[theme_name]
        self.ttk_style = Style()

    def apply_to_window(self, window: Tk):
        window.configure(bg=self.current_theme["bg_primary"])

    def apply_to_frame(self, frame: Frame):
        frame.configure(bg=self.current_theme["bg_secondary"])

    def apply_to_button(self, button: Button):
        button.configure(
            bg=self.current_theme["accent_blue"],
            fg=self.current_theme["text_primary"],
            activebackground=self.current_theme["bg_accent"],
            activeforeground=self.current_theme["text_primary"],
            borderwidth=0,
            relief="flat",
        )

    def apply_to_label(self, label: Label):
        label.configure(
            bg=self.current_theme["bg_secondary"], fg=self.current_theme["text_primary"]
        )

    def apply_to_entry(self, entry: Entry):
        entry.configure(
            bg=self.current_theme["bg_tertiary"],
            fg=self.current_theme["text_primary"],
            insertbackground=self.current_theme["text_primary"],
            selectbackground=self.current_theme["accent_blue"],
            selectforeground=self.current_theme["text_primary"],
            borderwidth=1,
            relief="solid",
        )

    def apply_to_text(self, text: Text):
        text.configure(
            bg=self.current_theme["bg_primary"],
            fg=self.current_theme["text_primary"],
            insertbackground=self.current_theme["text_primary"],
            selectbackground=self.current_theme["accent_blue"],
            selectforeground=self.current_theme["text_primary"],
        )

    def apply_to_listbox(self, listbox: Listbox):
        listbox.configure(
            bg=self.current_theme["bg_primary"],
            fg=self.current_theme["text_primary"],
            selectbackground=self.current_theme["accent_blue"],
            selectforeground=self.current_theme["text_primary"],
        )

    def apply_to_checkbox(self, checkbox: Checkbutton):
        checkbox.configure(
            bg=self.current_theme["bg_primary"],
            fg=self.current_theme["text_primary"],
        )

    def apply_to_combobox(self, combobox: Combobox):
        # Configure ttk.Style for Combobox
        self.ttk_style.theme_use("default")

        # Map the colors for different states
        self.ttk_style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.current_theme["bg_tertiary"])],
            selectbackground=[("readonly", self.current_theme["accent_blue"])],
            selectforeground=[("readonly", self.current_theme["text_primary"])],
        )

        # Configure the normal state
        self.ttk_style.configure(
            "TCombobox",
            fieldbackground=self.current_theme["bg_tertiary"],
            background=self.current_theme["bg_secondary"],
            foreground=self.current_theme["text_primary"],
            arrowcolor=self.current_theme["text_primary"],
            bordercolor=self.current_theme["border"],
            lightcolor=self.current_theme["bg_accent"],
            darkcolor=self.current_theme["bg_accent"],
        )
