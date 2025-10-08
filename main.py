import json
import os
import shutil
from tkinter import *
from tkinter.filedialog import askdirectory

from editor import GameEditor
from style_manager import StyleManager

with open("themes.json") as f:
    theme = json.load(f)["selected"]
    f.close()


class App:
    def __init__(self):
        self.win = Tk()
        self.win.title("PyDot")
        self.win.resizable(False, False)

        # Initialize style manager for testing
        self.style = StyleManager(theme)
        self.style.apply_to_window(self.win)

        self.pad = 2
        pad = self.pad

        top_bar = Frame(self.win, height=48)

        new_project_btn = Button(
            top_bar,
            text="New",
            command=self.create_new_project,
        )

        open_project_btn = Button(
            top_bar,
            text="Open",
            command=self.open_existing_project,
        )

        settings_btn = Button(top_bar, text="Settings", command=self.open_settings)

        top_bar.grid(padx=pad, pady=pad, row=0, column=0, columnspan=1, sticky="we")
        new_project_btn.pack(padx=pad, side="left", expand=True, fill="x")
        open_project_btn.pack(padx=pad, side="left", expand=True, fill="x")
        settings_btn.pack(padx=pad, side="right", expand=True, fill="x")

        self.style.apply_to_frame(top_bar)
        self.style.apply_to_button(new_project_btn)
        self.style.apply_to_button(open_project_btn)
        self.style.apply_to_button(settings_btn)

        self.win.bind("<Control-n>", lambda event: self.create_new_project())
        self.win.bind("<Control-o>", lambda event: self.open_existing_project())

        self.win.mainloop()

    def create_new_project(self):
        global directory
        directory = ""

        def browse():
            global directory
            popup.withdraw()
            directory = askdirectory()
            popup.deiconify()
            location_en.delete(0, END)
            location_en.insert(0, f"{directory}/")
            popup.focus_set()
            popup.lift()

        def create():
            global directory
            directory += f"/{name_en.get()}"
            if directory != "":
                dirs_to_make = [
                    "scripts",
                    "scripts/built_in",
                    "scripts/custom",
                    "assets",
                    "assets/sprites",
                    "assets/sfx",
                    "assets/music",
                ]
                files_to_copy = [
                    ("scripts/built_in/default_text.py", "scripts/built_in/text.py"),
                    (
                        "scripts/built_in/default_button.py",
                        "scripts/built_in/button.py",
                    ),
                    (
                        "scripts/built_in/default_sprite_manager.py",
                        "scripts/built_in/sprite_manager.py",
                    ),
                    ("scripts/default_game.py", "game.py"),
                    ("scripts/default_main.py", "main.py"),
                ]

                os.mkdir(directory)
                for dir in dirs_to_make:
                    os.mkdir(f"{directory}/{dir}")

                for file in files_to_copy:
                    shutil.copy(file[0], f"{directory}/{file[1]}")

                name = name_en.get()
                self.win.destroy()
                GameEditor(name, directory)
            else:
                err_popup = Toplevel(popup)
                err_popup.title("error")
                err_lbl = Label(err_popup, text="Directory or Name not set")
                ok = Button(err_popup, text="OK", command=err_popup.destroy)

                err_lbl.pack()
                ok.pack()
                err_popup.mainloop()

        popup = Toplevel(self.win)
        popup.title("New Project")

        name_lbl = Label(popup, text="Name:")
        name_en = Entry(popup)
        name_en.insert(0, "New Project")

        location_lbl = Label(popup, text="Location:")
        location_en = Entry(popup)
        location_btn = Button(popup, text="Browse", command=browse)

        create_btn = Button(popup, text="Create", command=create)

        self.style.apply_to_window(popup)
        self.style.apply_to_label(name_lbl)
        self.style.apply_to_entry(name_en)
        self.style.apply_to_label(location_lbl)
        self.style.apply_to_entry(location_en)
        self.style.apply_to_button(location_btn)
        self.style.apply_to_button(create_btn)

        name_lbl.pack(padx=self.pad, pady=self.pad, side="top", expand=True, fill="x")
        name_en.pack(padx=self.pad, pady=self.pad, side="top", expand=True, fill="x")

        create_btn.pack(
            padx=self.pad, pady=self.pad, side="bottom", expand=True, fill="x"
        )

        location_lbl.pack(
            padx=self.pad, pady=self.pad, side="top", expand=True, fill="x"
        )
        location_en.pack(
            padx=self.pad, pady=self.pad, side="left", expand=True, fill="x"
        )
        location_btn.pack(
            padx=self.pad, pady=self.pad, side="right", expand=True, fill="x"
        )

        popup.bind("<Return>", lambda event: create())

        popup.focus_set()
        popup.mainloop()

    def open_existing_project(self):
        directory = askdirectory(title="Select Project Directory")
        if directory:
            # Get project name from directory path
            project_name = os.path.basename(directory)
            self.win.destroy()
            GameEditor(project_name, directory)

    def open_settings(self):
        popup = Toplevel(self.win)


app = App()
