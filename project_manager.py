import json
import os
import shutil
from tkinter import *
from tkinter.filedialog import askdirectory

from editor import GameEditor
from style_manager import StyleManager

# Configuration paths
if os.name == "nt":  # Windows
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "pydot")
else:  # Linux, macOS, (unix).
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pydot")

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
THEMES_FILE = os.path.join(CONFIG_DIR, "themes.json")
RECENT_PROJECTS_FILE = os.path.join(CONFIG_DIR, "recent_projects.json")


# Project directory
global start_dir

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)
    start_dir = config["default_project_location"]
    f.close()

if not os.path.exists(start_dir):
    os.makedirs(start_dir, exist_ok=True)
start_dir = os.path.join(start_dir, "PyDot")
if not os.path.exists(start_dir):
    os.makedirs(start_dir, exist_ok=True)

global directory
directory = start_dir


class App:
    def __init__(self):
        self.win = Tk()
        self.win.title("PyDot")
        self.win.resizable(False, False)

        # Initialize style manager for testing
        self.style = StyleManager()
        self.style.apply_to(self.win)

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

        recent_projects_listbox = Listbox(self.win)

        with open(RECENT_PROJECTS_FILE, "r") as f:
            self.recent_projects = json.load(f)
            f.close()

        for project in reversed(self.recent_projects):
            if os.path.exists(project):
                recent_projects_listbox.insert(END, os.path.basename(project))
            else:
                self.recent_projects.pop(project)
            with open(RECENT_PROJECTS_FILE, "w") as f:
                json.dump(self.recent_projects, f)
                f.close()

        top_bar.grid(padx=pad, pady=pad, row=0, column=0, columnspan=1, sticky="we")
        new_project_btn.pack(padx=pad, side="left", expand=True, fill="x")
        open_project_btn.pack(padx=pad, side="left", expand=True, fill="x")
        recent_projects_listbox.grid(
            padx=pad, pady=pad, row=1, column=0, columnspan=1, sticky="wens"
        )

        self.style.apply_to(top_bar)
        self.style.apply_to(new_project_btn)
        self.style.apply_to(open_project_btn)
        self.style.apply_to(recent_projects_listbox)

        self.win.bind("<Control-n>", lambda event: self.create_new_project())
        self.win.bind("<Control-o>", lambda event: self.open_existing_project())

        recent_projects_listbox.bind(
            "<Double-1>",
            lambda event: self.force_open_existing_project(
                recent_projects_listbox.get(recent_projects_listbox.curselection())
            ),
        )

        self.win.mainloop()

    def create_new_project(self):
        with open(os.path.join("data", "stuff_to_make.json")) as f:
            data = json.load(f)
            dirs_to_make = data["dirs_to_make"]
            files_to_copy = data["files_to_copy"]
            f.close()

        def browse():
            global directory, start_dir
            popup.withdraw()
            directory = askdirectory(initialdir=start_dir)
            popup.deiconify()
            location_en.delete(0, END)
            location_en.insert(0, f"{directory}/")
            popup.focus_set()
            popup.lift()

        def create():
            global directory
            directory += f"/{name_en.get()}"
            if directory != "" or directory != os.path.join("()", ""):
                try:
                    os.mkdir(directory)
                except FileExistsError:
                    print("Project already exists, open project")
                    self.force_open_existing_project(directory)
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
                    for dir in dirs_to_make["no"]:
                        os.mkdir(f"{directory}/{dir}")
                    for file in files_to_copy["no"]:
                        if os.path.exists(f"{directory}/{file[1]}"):
                            os.remove(f"{directory}/{file[1]}")
                        shutil.copy(file[0], f"{directory}/{file[1]}")

                name = name_en.get()
                self.win.destroy()
                self.recent_projects[directory] = name
                with open(RECENT_PROJECTS_FILE, "w") as f:
                    json.dump(self.recent_projects, f, indent=4)
                    f.close()
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
            popup,
            text="Copy Pydot Specific Classes (recommended)?",
            variable=copy_classes,
        )

        self.style.apply_to(popup)
        self.style.apply_to(name_lbl)
        self.style.apply_to(name_en)
        self.style.apply_to(location_lbl)
        self.style.apply_to(location_en)
        self.style.apply_to(location_btn)
        self.style.apply_to(create_btn)
        self.style.apply_to(copy_classes_check)

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
        global start_dir
        directory = askdirectory(title="Select Project Directory", initialdir=start_dir)
        project_name = os.path.basename(directory)
        self.win.destroy()
        GameEditor(project_name, directory)

        self.recent_projects[directory] = project_name

        with open(RECENT_PROJECTS_FILE, "w") as f:
            json.dump(self.recent_projects, f, indent=4)
            f.close()

    def force_open_existing_project(self, name: str):
        self.win.destroy()
        GameEditor(name, os.path.join(start_dir, name))

        self.recent_projects[(os.path.join(start_dir, name))] = name

        with open(RECENT_PROJECTS_FILE, "w") as f:
            json.dump(self.recent_projects, f, indent=4)
            f.close()


if __name__ == "__main__":
    app = App()
