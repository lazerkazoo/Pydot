import json
from tkinter import *


class StyleManager:
    def __init__(self, theme_name="vs_code_dark"):
        with open("themes.json", "r") as f:
            self.themes = json.load(f)

        self.current_theme = self.themes[theme_name]

    def apply_to_window(self, window):
        window.configure(bg=self.current_theme["bg_primary"])

    def apply_to_frame(self, frame):
        frame.configure(bg=self.current_theme["bg_secondary"])

    def apply_to_button(self, button):
        button.configure(
            bg=self.current_theme["accent_blue"],
            fg=self.current_theme["text_primary"],
            activebackground=self.current_theme["bg_accent"],
            activeforeground=self.current_theme["text_primary"],
            borderwidth=0,
            relief="flat",
        )

    def apply_to_label(self, label):
        label.configure(
            bg=self.current_theme["bg_secondary"], fg=self.current_theme["text_primary"]
        )

    def apply_to_entry(self, entry):
        entry.configure(
            bg=self.current_theme["bg_tertiary"],
            fg=self.current_theme["text_primary"],
            insertbackground=self.current_theme["text_primary"],
            selectbackground=self.current_theme["accent_blue"],
            selectforeground=self.current_theme["text_primary"],
            borderwidth=1,
            relief="solid",
        )

    def apply_to_text(self, text):
        text.configure(
            bg=self.current_theme["bg_primary"],
            fg=self.current_theme["text_primary"],
            insertbackground=self.current_theme["text_primary"],
            selectbackground=self.current_theme["accent_blue"],
            selectforeground=self.current_theme["text_primary"],
        )

    def apply_to_listbox(self, listbox):
        listbox.configure(
            bg=self.current_theme["bg_primary"],
            fg=self.current_theme["text_primary"],
            selectbackground=self.current_theme["accent_blue"],
            selectforeground=self.current_theme["text_primary"],
        )
