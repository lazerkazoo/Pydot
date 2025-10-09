import json
import os
import shutil
from tkinter import *
from tkinter.filedialog import askdirectory

from editor import GameEditor
from style_manager import StyleManager

# Configuration paths
if os.name == "nt":  # Windows
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "PyDot")
else:  # Linux, macOS, (unix).
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "PyDot")

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
THEMES_FILE = os.path.join(CONFIG_DIR, "themes.json")

# Project directory
global start_in
start_in = os.path.expanduser("~")
if os.name == "nt":  # Windows
    start_in = os.path.join(start_in, "Documents")
else:  # Linux, macOS, (unix).
    start_in = os.path.join(start_in, "Projects")

if not os.path.exists(start_in):
    os.makedirs(start_in, exist_ok=True)
start_in = os.path.join(start_in, "PyDot")
if not os.path.exists(start_in):
    os.makedirs(start_in, exist_ok=True)

global directory
directory = start_in


class App:
    def __init__(self):
        self.win = Tk()
        self.win.title("PyDot")
        self.win.resizable(False, False)

        # Initialize style manager for testing
        self.style = StyleManager()
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

        top_bar.grid(padx=pad, pady=pad, row=0, column=0, columnspan=1, sticky="we")
        new_project_btn.pack(padx=pad, side="left", expand=True, fill="x")
        open_project_btn.pack(padx=pad, side="left", expand=True, fill="x")

        self.style.apply_to_frame(top_bar)
        self.style.apply_to_button(new_project_btn)
        self.style.apply_to_button(open_project_btn)

        self.win.bind("<Control-n>", lambda event: self.create_new_project())
        self.win.bind("<Control-o>", lambda event: self.open_existing_project())

        self.win.mainloop()

    def create_new_project(self):
        with open("stuff_to_make.json") as f:
            data = json.load(f)
            dirs_to_make = data["dirs_to_make"]
            files_to_copy = data["files_to_copy"]

        def browse():
            global directory, start_in
            popup.withdraw()
            directory = askdirectory(initialdir=start_in)
            popup.deiconify()
            location_en.delete(0, END)
            location_en.insert(0, f"{directory}/")
            popup.focus_set()
            popup.lift()

        def create():
            global directory
            directory += f"/{name_en.get()}"
            if directory != "":
                print(copy_classes.get())

                os.mkdir(directory)

                if copy_classes.get():
                    for dir in dirs_to_make["no"]:
                        os.mkdir(f"{directory}/{dir}")
                    for dir in dirs_to_make["yes"]:
                        os.mkdir(f"{directory}/{dir}")
                    for file in files_to_copy["no"]:
                        if os.path.exists(f"{directory}/{file[1]}"):
                            os.remove(f"{directory}/{file[1]}")
                        shutil.copy(file[0], f"{directory}/{file[1]}")
                    for file in files_to_copy["yes"]:
                        if os.path.exists(f"{directory}/{file[1]}"):
                            os.remove(f"{directory}/{file[1]}")
                        shutil.copy(file[0], f"{directory}/{file[1]}")
                else:
                    # Create directories from only "no" list
                    for dir in dirs_to_make["no"]:
                        os.mkdir(f"{directory}/{dir}")
                    # Copy files from only "no" list
                    for file in files_to_copy["no"]:
                        if os.path.exists(f"{directory}/{file[1]}"):
                            os.remove(f"{directory}/{file[1]}")
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
        location_en.insert(0, directory)
        location_btn = Button(popup, text="Browse", command=browse)

        create_btn = Button(popup, text="Create", command=create)

        copy_classes = BooleanVar(value=True)
        copy_classes_check = Checkbutton(
            popup, text="Copy Pydot Specific Classes?", variable=copy_classes
        )

        self.style.apply_to_window(popup)
        self.style.apply_to_label(name_lbl)
        self.style.apply_to_entry(name_en)
        self.style.apply_to_label(location_lbl)
        self.style.apply_to_entry(location_en)
        self.style.apply_to_button(location_btn)
        self.style.apply_to_button(create_btn)
        self.style.apply_to_checkbox(copy_classes_check)

        name_lbl.pack(padx=self.pad, pady=self.pad, side="top", expand=True, fill="x")
        name_en.pack(padx=self.pad, pady=self.pad, side="top", expand=True, fill="x")

        copy_classes_check.pack(
            padx=self.pad, pady=self.pad, side="bottom", expand=True, fill="x"
        )
        create_btn.pack(padx=self.pad, pady=self.pad, side="bottom", fill="x")
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
        popup.bind("<Escape>", lambda event: popup.destroy())

        popup.focus_set()
        popup.mainloop()

    def open_existing_project(self):
        global start_in, directory
        directory = askdirectory(title="Select Project Directory", initialdir=start_in)
        if directory:
            # Get project name from directory path
            project_name = os.path.basename(directory)
            self.win.destroy()
            GameEditor(project_name, directory)


if __name__ == "__main__":
    # Create config directory if it doesn't exist
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)

    # Copy themes.json to config directory if it doesn't exist
    if not os.path.exists(THEMES_FILE):
        with open("themes.json", "r") as src:
            themes_data = json.load(src)
        with open(THEMES_FILE, "w") as dst:
            json.dump(themes_data, dst, indent=2)

    # Run initial setup if config.json doesn't exist
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"theme": "vs_code_dark"}, f, indent=4)
        from init_setup import InitialSetup

        InitialSetup()

    app = App()
