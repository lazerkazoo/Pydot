import os
import subprocess
import threading
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import Combobox, Style

from style_manager import StyleManager


class GameEditor:
    def __init__(self, name: str, directory: str) -> None:
        self.win = Tk()
        self.win.attributes("-zoomed", True)
        self.win.title(name)
        self.directory = directory
        self.current_file = None
        self.game_process = None
        self.output_thread = None

        self.pad = 5
        pad = self.pad

        self.style_manager = StyleManager()
        self.style_manager.apply_to_window(self.win)

        self.style = Style(self.win)

        top_bar = Frame(self.win, height=48)

        settings_btn = Button(top_bar, text="Settings", command=self.open_settings)

        new_btn = Button(top_bar, text="New", command=self.new_file)

        open_btn = Button(top_bar, text="Open", command=self.open_file)

        save_btn = Button(top_bar, text="Save", command=self.save_file)

        start_btn = Button(top_bar, text="Debug", command=self.debug)

        text_frame = Frame(self.win)
        self.text_editor = Text(text_frame, wrap="none", tabs="0.85c")
        scrollbar = Scrollbar(text_frame, command=self.text_editor.yview)

        self.console = Listbox(self.win, height=10)

        # Style Stuff
        self.style_manager.apply_to_frame(top_bar)
        self.style_manager.apply_to_button(settings_btn)
        self.style_manager.apply_to_button(new_btn)
        self.style_manager.apply_to_button(open_btn)
        self.style_manager.apply_to_button(save_btn)
        self.style_manager.apply_to_button(start_btn)
        self.style_manager.apply_to_frame(text_frame)
        self.style_manager.apply_to_text(self.text_editor)
        self.style_manager.apply_to_listbox(self.console)
        self.text_editor.config(yscrollcommand=scrollbar.set)

        # pack stuff 2 top bar
        settings_btn.pack(side="left", padx=pad)
        new_btn.pack(side="left", padx=pad)
        open_btn.pack(side="left", padx=pad)
        save_btn.pack(side="left", padx=pad)
        start_btn.pack(side="right", padx=pad)

        # pack stuff 2 window
        self.text_editor.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.win.grid_rowconfigure(1, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        top_bar.grid(row=0, column=0, sticky="ew", padx=pad, pady=pad)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=pad, pady=pad)

        # Key bindings
        self.win.bind("<Control-o>", lambda event: self.open_file())
        self.win.bind("<Control-s>", lambda event: self.save_file())
        self.win.bind("<Control-Shift-S>", lambda event: self.save_file_as())
        self.win.bind("<Control-n>", lambda event: self.new_file())
        self.win.bind("<Control-comma>", lambda event: self.open_settings())
        self.win.bind("<F5>", lambda event: self.debug())

        # Auto-completion key bindings
        self.text_editor.bind("(", lambda event: self.complete("(", event))
        self.text_editor.bind("[", lambda event: self.complete("[", event))
        self.text_editor.bind("{", lambda event: self.complete("{", event))
        self.text_editor.bind('"', lambda event: self.complete('"', event))
        self.text_editor.bind("'", lambda event: self.complete("'", event))

        # Make Key Binds Work
        self.text_editor.focus_set()

        self.force_open_file("main.py")

        self.win.mainloop()

    def open_file(self):
        file_path = askopenfilename(
            initialdir=self.directory,
            filetypes=[
                ("Python files", "*.py"),
                ("Json Files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        with open(file_path, "r") as f:
            self.text_editor.delete(1.0, END)
            self.text_editor.insert(1.0, f.read())
            self.current_file = file_path

    def force_open_file(self, file: str):
        if not self.directory:
            return

        with open(f"{self.directory}/{file}", "r") as f:
            self.text_editor.delete(1.0, END)
            self.text_editor.insert(1.0, f.read())
            self.current_file = f"{self.directory}/{file}"

    def save_file(self):
        text = self.text_editor.get(1.0, END)
        if self.current_file:
            with open(self.current_file, "w") as f:
                f.write(text)
        else:
            self.save_file_as()

    def save_file_as(self):
        text = self.text_editor.get(1.0, END)
        file_path = asksaveasfilename(
            initialdir=self.directory,
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("Json Files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(text)
                self.current_file = file_path
                filename = file_path.split("/")[-1]
                print(f"Saved as: {file_path}")
            except Exception as e:
                print(f"Error saving file: {e}")

    def open_settings(self):
        popup = Toplevel(self.win)

        self.style_manager.apply_to_window(popup)
        # Make the popup modal without starting a nested mainloop
        try:
            popup.transient(self.win)
            popup.grab_set()
            popup.focus_set()
            popup.lift()
        except Exception:
            pass

    def new_file(self):
        pad = self.pad

        # Define types dictionary at the method level for proper scope
        types = {
            "Python": [".py", "/scripts/custom/"],
            "Json": [".json", "/data/"],
            "Any": ["", "/scripts/"],
        }

        def create(file: str, type_cb):
            new_file_path = ""
            file = file.lower()

            if not file.strip():
                return

            class_name = file.capitalize()
            selected_type = type_cb.get()

            for i in types:
                if i == selected_type:
                    print(types[selected_type][0], types[selected_type][1])
                    if not os.path.exists(f"{self.directory}{types[selected_type][1]}"):
                        os.mkdir(f"{self.directory}{types[selected_type][1]}")
                    new_file_path = f"{self.directory}{types[selected_type][1]}{file}{types[selected_type][0]}"
                    break

            main_file_path = f"{self.directory}/main.py"

            # Create the new class file
            with open(new_file_path, "w") as f:
                if selected_type == "Python":
                    f.write(
                        f"import pygame as pydot\n\nclass {class_name}:\n    def __init__(self):\n        # put stuff here\n        pass"
                    )
                elif selected_type == "Json":
                    f.write("{}")
                else:
                    f.write("")  # Empty file for "Any" type

            # Update main.py to import the new class (only for Python files)
            if selected_type == "Python" and os.path.exists(main_file_path):
                with open(main_file_path, "r") as r:
                    content = r.read()

                # Add import line at the beginning
                import_line = f"from scripts.custom.{file} import {class_name}\n"
                if import_line not in content:
                    updated_content = import_line + content

                    with open(main_file_path, "w") as w:
                        w.write(updated_content)

            # Load the new file into the editor
            with open(new_file_path, "r") as f:
                self.text_editor.delete(1.0, END)
                self.text_editor.insert(1.0, f.read())
                self.current_file = new_file_path

        def create_new():
            def on_create():
                file_name = name_en.get().strip()
                if file_name:
                    create(file_name, type_cb)
                    popup.destroy()

            popup = Toplevel(self.win)
            popup.title("Create New File")

            type_var = StringVar()
            type_cb = Combobox(popup, textvariable=type_var)
            type_var.set("Python")
            type_cb["values"] = ["Python", "Json", "Any"]
            type_cb["state"] = "readonly"

            name_lbl = Label(popup, text="File Name:")
            name_en = Entry(popup)
            name_en.focus_set()

            create_btn = Button(
                popup,
                command=on_create,
                text="Create File",
            )

            cancel_btn = Button(popup, text="Cancel", command=popup.destroy)

            # Bind Enter key to create
            popup.bind("<Return>", lambda event: on_create())
            name_en.bind("<Return>", lambda event: on_create())

            self.style_manager.apply_to_window(popup)
            self.style_manager.apply_to_label(name_lbl)
            self.style_manager.apply_to_entry(name_en)
            self.style_manager.apply_to_button(create_btn)
            self.style_manager.apply_to_button(cancel_btn)

            type_cb.pack(pady=pad, fill="x")
            name_lbl.pack(pady=pad)
            name_en.pack(pady=pad, padx=pad, fill="x")
            create_btn.pack(side="left", padx=pad, pady=pad)
            cancel_btn.pack(side="right", padx=pad, pady=pad)

        if self.current_file:
            popup = Toplevel(self.win)

            save = Button(
                popup,
                command=lambda: [self.save_file(), popup.destroy(), create_new()],
                text="Save & Create",
            )
            ok = Button(
                popup, command=lambda: [popup.destroy(), create_new()], text="OK"
            )
            cancel = Button(popup, command=popup.destroy, text="Cancel")

            self.style_manager.apply_to_window(popup)
            self.style_manager.apply_to_button(save)
            self.style_manager.apply_to_button(ok)
            self.style_manager.apply_to_button(cancel)

            save.pack(expand=True, fill="x", padx=pad, pady=pad)
            ok.pack(expand=True, fill="x", padx=pad, pady=pad)
            cancel.pack(expand=True, fill="x", padx=pad, pady=pad)

            popup.mainloop()

    def debug(self):
        target_file = f"{self.directory}/game.py"
        self.console.insert(END, "Running the Game...")
        subprocess.run(["python", target_file])

    def complete(self, char: str, event) -> None:
        chars = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        closing_char = chars.get(char, "")

        if closing_char:
            cursor_pos = self.text_editor.index(INSERT)
            self.text_editor.insert(cursor_pos, char)
            self.text_editor.insert(f"{cursor_pos}+1c", closing_char)
            self.text_editor.mark_set(INSERT, f"{cursor_pos}+1c")
            return

        return
