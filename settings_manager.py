import json
import os
from tkinter import Button, Entry, LabelFrame, Tk, messagebox
from tkinter.filedialog import askdirectory
from tkinter.ttk import Combobox

from style_manager import StyleManager

if os.name == "nt":
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
else:
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

start_in = os.path.expanduser("~")


class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.pad = 2
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
        def browse_for_dir(event=None):
            popup.withdraw()
            dir = askdirectory(initialdir=start_in)
            if not dir:
                return

            dir_en.delete(0, "end")
            update_default_dir()
            popup.deiconify()
            dir_en.insert(0, dir)
            update_default_dir()

        def update_default_dir(event=None):
            self.settings["default_project_location"] = dir_en.get()
            with open(os.path.join(CONFIG_DIR, "config.json"), "w") as f:
                json.dump(self.settings, f, indent=4)

        def update_theme(event=None):
            theme = theme_combo.get()
            for i in self.style_manager.themes:
                if self.style_manager.themes[i]["name"] == theme:
                    theme = i
                    break
            self.settings["theme"] = theme
            with open(os.path.join(CONFIG_DIR, "config.json"), "w") as f:
                json.dump(self.settings, f, indent=4)

            popup.withdraw()
            messagebox.showinfo("Restart", "To see the theme change restart pydot.")
            popup.deiconify()

        popup = Tk()
        popup.title("Settings")
        popup.geometry("300x200")
        popup.resizable(False, False)

        theme_frame = LabelFrame(popup, text="Change Theme")
        theme_combo = Combobox(theme_frame, state="readonly")
        themes = []
        for i in self.style_manager.themes:
            themes.append(self.style_manager.themes[i]["name"])
        theme_combo["values"] = themes
        theme_combo.set(self.style_manager.themes[self.settings["theme"]]["name"])

        change_dir_frame = LabelFrame(popup, text="Change Default Project Directory")
        dir_en = Entry(change_dir_frame)
        dir_en.insert(0, self.settings["default_project_location"])
        browse_for_dir_btn = Button(
            change_dir_frame, text="Browse", command=browse_for_dir
        )

        self.style_manager.apply_to(popup)
        self.style_manager.apply_to(theme_frame)
        self.style_manager.apply_to_combobox()
        self.style_manager.apply_to(change_dir_frame)
        self.style_manager.apply_to(dir_en)
        self.style_manager.apply_to(browse_for_dir_btn)

        theme_frame.pack(padx=self.pad, pady=self.pad, fill="x")
        theme_combo.pack(padx=self.pad, pady=self.pad, fill="x")

        theme_combo.bind("<<ComboboxSelected>>", update_theme)

        change_dir_frame.pack(padx=self.pad, pady=self.pad, fill="x")
        dir_en.pack(padx=self.pad, pady=self.pad, fill="x")
        browse_for_dir_btn.pack(padx=self.pad, pady=self.pad, fill="x")

        dir_en.bind("<FocusIn>", update_default_dir)
        dir_en.bind("<KeyPress>", update_default_dir)

        popup.mainloop()
