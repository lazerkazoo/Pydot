import json
import os
from tkinter import Tk, LabelFrame, Button
from tkinter.ttk import Combobox
from style_manager import StyleManager

if os.name == "nt":
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
else:
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")


class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.pad = 5
        self.style_manager = StyleManager()
        self.load_settings()

    def load_settings(self):
        try:
            with open(os.path.join(CONFIG_DIR, "config.json"), "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}

    def save_settings(self):
        self.settings["theme"] = self.style_manager.current_theme
        with open(os.path.join(CONFIG_DIR, "config.json"), "w") as f:
            json.dump(self.settings, f, indent=4)

    def open_settings(self):
        def set_theme(theme_name: str):
            for theme, data in self.style_manager.themes.items():
                if data["name"] == theme_name:
                    self.style_manager.current_theme = theme
                    break

        popup = Tk()
        popup.title("Settings")
        popup.geometry("400x300")
        popup.resizable(False, False)

        theme_frame = LabelFrame(popup, text="Theme")
        theme_cb = Combobox(
            theme_frame,
            state="readonly",
            values=[theme["name"] for theme in self.style_manager.themes.values()],
        )
        theme_cb.set(self.style_manager.current_theme["name"])

        apply_btn = Button(popup, text="Apply", command=self.save_settings)

        self.style_manager.apply_to(popup)
        self.style_manager.apply_to(theme_frame)
        self.style_manager.apply_to_combobox()
        self.style_manager.apply_to(apply_btn)

        theme_frame.pack(fill="x", padx=self.pad, pady=self.pad)
        theme_cb.pack(fill="x", padx=self.pad, pady=self.pad)
        apply_btn.pack(fill="x", padx=self.pad, pady=self.pad)

        theme_cb.bind(
            "<<ComboboxSelected>>",
            lambda event: set_theme(theme_cb.get()),
        )

        popup.mainloop()
