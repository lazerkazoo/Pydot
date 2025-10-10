import json
import os
import re
import subprocess
import shutil
from keyword import kwlist
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import Combobox, Style

from style_manager import StyleManager
from syntax_highlighter import SyntaxHighlighter


class GameEditor:
    def __init__(self, name: str, directory: str):
        self.win = Tk()
        self.win.attributes("-zoomed", True)
        self.win.title(name)
        self.directory = directory
        self.current_file = None
        self.game_process = None
        self.output_thread = None

        self.name = name

        # Autocomplete setup
        self.autocomplete_popup = None
        self.autocomplete_listbox = None
        self.autocomplete_suggestions = []
        self.setup_autocomplete_data()

        self.pad = 5
        pad = self.pad

        self.style_manager = StyleManager()
        self.style_manager.apply_to(self.win)

        self.style = Style(self.win)

        top_bar = Frame(self.win, height=48)

        new_btn = Button(top_bar, text="New", command=self.new_file)

        open_btn = Button(top_bar, text="Open", command=self.open_file)

        save_btn = Button(top_bar, text="Save", command=self.save_file)

        compile_btn = Button(top_bar, text="Compile", command=self.compile)

        start_btn = Button(top_bar, text="Debug", command=self.debug)

        text_frame = Frame(self.win)
        self.text_editor = Text(text_frame, wrap="none", tabs="0.85c")
        scrollbar = Scrollbar(text_frame, command=self.text_editor.yview)

        # Style Stuff
        self.style_manager.apply_to(top_bar)
        self.style_manager.apply_to(new_btn)
        self.style_manager.apply_to(open_btn)
        self.style_manager.apply_to(save_btn)
        self.style_manager.apply_to(start_btn)
        self.style_manager.apply_to(compile_btn)
        self.style_manager.apply_to(text_frame)
        self.style_manager.apply_to(self.text_editor)

        # Syntax Highlighting
        self.highlighter = SyntaxHighlighter(
            self.text_editor, "python", self.style_manager.current_theme
        )

        self.text_editor.config(yscrollcommand=scrollbar.set)

        # pack stuff 2 top bar
        new_btn.pack(side="left", padx=pad)
        open_btn.pack(side="left", padx=pad)
        save_btn.pack(side="left", padx=pad)
        start_btn.pack(side="right", padx=pad)
        compile_btn.pack(side="right", padx=pad)

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
        self.win.bind("<F5>", lambda event: self.debug())
        self.win.bind("<Control-Shift-C>", lambda event: self.compile())

        # Auto-completion key bindings
        self.text_editor.bind("(", lambda event: self.close("(", event))
        self.text_editor.bind("[", lambda event: self.close("[", event))
        self.text_editor.bind("{", lambda event: self.close("{", event))
        self.text_editor.bind('"', lambda event: self.close('"', event))
        self.text_editor.bind("'", lambda event: self.close("'", event))
        self.text_editor.bind("<Control-space>", lambda event: self.show_autocomplete())
        self.text_editor.bind("<KeyRelease>", self.on_key_release)
        self.text_editor.bind("<Control-Tab>", lambda event: self.show_snippet_menu())
        self.text_editor.bind("<Return>", self.auto_indentation)
        self.text_editor.bind("<Tab>", self.insert_spaces)

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
            content = f.read()
            self.text_editor.insert(1.0, content)
            self.current_file = file_path
            self.highlighter.highlight()

    def force_open_file(self, file: str):
        if not self.directory:
            return

        with open(f"{self.directory}/{file}", "r") as f:
            self.text_editor.delete(1.0, END)
            content = f.read()
            self.text_editor.insert(1.0, content)
            self.current_file = f"{self.directory}/{file}"
            self.highlighter.highlight()

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

    def new_file(self):
        pad = self.pad

        # Define types dictionary at the method level for proper scope
        types = {
            "Python": [".py", "/scripts/custom/"],
            "Pydot Class": [".py", "/scripts/custom/"],
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

            if os.path.exists(f"{self.directory}/scripts/built_in"):
                file_content = f"""import pygame as pydot                            
from scripts.built_in.text import Text
from scripts.built_in.button import Button
from scripts.built_in.sprite_manager import Sprite
from scripts.built_in.sprite_manager import SheetAnimManager
from scripts.built_in.sprite_manager import SpriteFromSheet


class {class_name}:
    def __init__(self):
        # runs when the class is created
        pass

    def run(self):
        # always runs
        pass"""
            else:
                file_content = f"""import pygame as pydot


class {class_name}:
    def __init__(self):
        # runs when the class is created
        pass

    def run(self):
        # always runs
        pass"""

            with open(new_file_path, "w") as f:
                if selected_type == "Python":
                    f.write(f"import pygame as pydot")
                elif selected_type == "Pydot Class":
                    f.write(file_content)
                elif selected_type == "Json":
                    f.write("{}")
                else:
                    f.write("")

            if selected_type == "Pydot Class" and os.path.exists(main_file_path):
                with open(main_file_path, "r") as r:
                    content = r.read()

                import_line = f"from scripts.custom.{file} import {class_name}\n"
                if import_line not in content:
                    updated_content = import_line + content

                    with open(main_file_path, "w") as w:
                        w.write(updated_content)

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

            type_cb = Combobox(popup)
            type_cb.set("Pydot Class")
            type_cb["values"] = ["Pydot Class", "Python", "Json", "Any"]
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

            # Bindings
            popup.bind("<Return>", lambda event: on_create())
            name_en.bind("<Return>", lambda event: on_create())

            self.style_manager.apply_to(popup)
            self.style_manager.apply_to(name_lbl)
            self.style_manager.apply_to(name_en)
            self.style_manager.apply_to(create_btn)
            self.style_manager.apply_to(cancel_btn)
            self.style_manager.apply_to_combobox(type_cb)

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

            self.style_manager.apply_to(popup)
            self.style_manager.apply_to(save)
            self.style_manager.apply_to(ok)
            self.style_manager.apply_to(cancel)

            save.pack(expand=True, fill="x", padx=pad, pady=pad)
            ok.pack(expand=True, fill="x", padx=pad, pady=pad)
            cancel.pack(expand=True, fill="x", padx=pad, pady=pad)

            popup.bind(
                "<Return>",
                lambda event: [self.save_file(), popup.destroy(), create_new()],
            )

            popup.mainloop()

    def debug(self):
        self.save_file()
        subprocess.run(["python", f"{self.directory}/game.py"])

    def close(self, char: str, event):
        chars = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        closing_char = chars.get(char, "")

        if closing_char:
            cursor_pos = self.text_editor.index(INSERT)
            self.text_editor.insert(cursor_pos, closing_char)
            line, col = cursor_pos.split(".")
            new_pos = f"{line}.{int(col)}"
            self.text_editor.mark_set(INSERT, new_pos)

        return None

    def setup_autocomplete_data(self):
        try:
            with open("autocomplete_data.json", "r") as f:
                data = json.load(f)

            self.python_keywords = data.get("python_keywords", kwlist)
            self.python_builtins = data.get("python_builtins", [])
            self.pydot_functions = data.get("pydot_functions", [])
            self.pydot_constants = data.get("pydot_constants", [])
            self.pydot_modules = data.get("pydot_modules", [])
            self.common_patterns = data.get("common_patterns", [])
            self.code_snippets = data.get("code_snippets", {})
        except FileNotFoundError:
            # Fallback to basic data if config file doesn't exist
            self.python_keywords = kwlist
            self.python_builtins = [
                "print",
                "input",
                "len",
                "range",
                "int",
                "str",
                "float",
                "bool",
                "list",
                "dict",
                "tuple",
                "set",
            ]
            self.pydot_functions = [
                "pygame.init",
                "pygame.quit",
                "pygame.display.set_mode",
                "pygame.event.get",
            ]
            self.pydot_constants = []
            self.pydot_modules = []
            self.common_patterns = []
            self.code_snippets = {}

    def hide_autocomplete(self, event=None):
        if self.autocomplete_popup:
            self.autocomplete_popup.destroy()
            self.autocomplete_popup = None
            self.autocomplete_listbox = None

    def insert_suggestion(self, event=None):
        if not self.autocomplete_listbox:
            return "break"

        # Get the selected item from the listbox
        selection = self.autocomplete_listbox.curselection()
        if not selection:
            return "break"

        # Get the selected suggestion
        suggestion = self.autocomplete_suggestions[selection[0]]

        # Get the current cursor position and line content
        cursor_pos = self.text_editor.index(INSERT)
        line_start = self.text_editor.index(f"{cursor_pos} linestart")
        line_text = self.text_editor.get(line_start, cursor_pos)

        # Find the start of the current word
        word_start = cursor_pos
        while (
            word_start > line_start
            and self.text_editor.get(f"{word_start}-1c", word_start).isalnum()
            or self.text_editor.get(f"{word_start}-1c", word_start) == "."
        ):
            word_start = f"{word_start}-1c"

        # Delete the partial word and insert the suggestion
        indent = ""
        for char in line_text:
            if char == " ":
                indent += char

        self.text_editor.delete(line_start, cursor_pos)
        self.text_editor.insert(line_start, indent + suggestion)

        # Move cursor to the end of the inserted suggestion
        self.text_editor.mark_set(INSERT, f"{word_start}+{len(suggestion)}c")

        # Hide the autocomplete popup
        self.hide_autocomplete()

        return "break"

    def on_key_release(self, event):
        # Hide autocomplete for Escape
        if event.keysym == "Escape":
            self.hide_autocomplete()
            return

        # Don't show autocomplete for navigation/control keys
        if event.keysym in [
            "Up",
            "Down",
            "Left",
            "Right",
            "Return",
            "Tab",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R",
            "Shift_L",
            "Shift_R",
        ]:
            return

        # Get current word being typed
        current_word = self.get_current_word()

        # Show autocomplete if word is at least 2 characters
        if len(current_word) >= 2:
            self.show_autocomplete(current_word)
        else:
            self.hide_autocomplete()

        self.highlighter.highlight()

    def handle_return(self, event=None):
        if self.autocomplete_popup:
            self.insert_suggestion()
            self.hide_autocomplete()
            return "break"
        else:
            self.auto_indentation()
            return "continue"

    def get_current_word(self):
        cursor_pos = self.text_editor.index(INSERT)
        line_start = cursor_pos.split(".")[0] + ".0"
        line_text = self.text_editor.get(line_start, cursor_pos)

        # Find the start of the current word
        word_start = len(line_text)
        for i in range(len(line_text) - 1, -1, -1):
            if line_text[i].isalnum() or line_text[i] in ["_", "."]:
                word_start = i
            else:
                break

        return line_text[word_start:]

    def get_suggestions(self, partial_word):
        suggestions = []
        partial_lower = partial_word.lower()

        # Add Python keywords
        for kw in self.python_keywords:
            if kw.startswith(partial_lower):
                suggestions.append(kw)

        # Add Python built-ins
        for builtin in self.python_builtins:
            if builtin.startswith(partial_lower):
                suggestions.append(builtin)

        # Add pygame functions
        for func in self.pydot_functions:
            if func.lower().startswith(partial_lower):
                suggestions.append(func)

        # Add pygame constants
        for const in self.pydot_constants:
            if const.lower().startswith(partial_lower):
                suggestions.append(const)

        # Add pygame modules
        for module in self.pydot_modules:
            if module.lower().startswith(partial_lower):
                suggestions.append(module)

        # Add common patterns
        for pattern in self.common_patterns:
            if pattern.lower().startswith(partial_lower):
                suggestions.append(pattern)

        # Add context-specific suggestions
        context_suggestions = self.get_context_suggestions(partial_word)
        suggestions.extend(context_suggestions)

        # Add code snippets that match
        for snippet_name in self.code_snippets:
            if snippet_name.lower().startswith(partial_lower):
                suggestions.append(f"snippet:{snippet_name}")

        return sorted(list(set(suggestions)))

    def get_context_suggestions(self, partial_word):
        suggestions = []
        content = self.text_editor.get(1.0, END)

        # Find class names
        class_pattern = r"class\s+(\w+)"
        classes = re.findall(class_pattern, content)
        for cls in classes:
            if cls.lower().startswith(partial_word.lower()):
                suggestions.append(cls)

        # Find function names
        func_pattern = r"def\s+(\w+)"
        functions = re.findall(func_pattern, content)
        for func in functions:
            if func.lower().startswith(partial_word.lower()):
                suggestions.append(func)

        # Find variable names (simple heuristic)
        var_pattern = r"(\w+)\s*="
        variables = re.findall(var_pattern, content)
        for var in variables:
            if (
                var.lower().startswith(partial_word.lower())
                and var not in self.python_keywords
            ):
                suggestions.append(var)

        return suggestions

    def show_autocomplete(self, partial_word=None):
        if partial_word is None:
            partial_word = self.get_current_word()

        if not partial_word:
            self.hide_autocomplete()
            return

        suggestions = self.get_suggestions(partial_word)

        if not suggestions:
            self.hide_autocomplete()
            return

        self.autocomplete_suggestions = suggestions

        # Create popup if it doesn't exist
        if not self.autocomplete_popup:
            self.autocomplete_popup = Toplevel(self.win)
            self.autocomplete_popup.wm_overrideredirect(True)

            self.autocomplete_listbox = Listbox(
                self.autocomplete_popup,
                height=min(8, len(suggestions)),
                selectmode=SINGLE,
                exportselection=False,
            )
            self.autocomplete_listbox.pack()

            # Bind events
            self.autocomplete_listbox.bind("<Double-Button-1>", self.insert_suggestion)
            self.autocomplete_listbox.bind("<Return>", self.insert_suggestion)
            self.autocomplete_popup.bind("<Escape>", self.hide_autocomplete)

            self.style_manager.apply_to(self.autocomplete_popup)
            self.style_manager.apply_to(self.autocomplete_listbox)

            # Handle navigation keys
            self.text_editor.bind("<Down>", self.navigate_suggestions)
            self.text_editor.bind("<Up>", self.navigate_suggestions)
            self.text_editor.bind("<Return>", self.handle_return)

        # Clear and populate listbox
        if self.autocomplete_listbox:
            self.autocomplete_listbox.delete(0, END)
            for suggestion in suggestions:
                self.autocomplete_listbox.insert(END, suggestion)

            # Select first item
            if suggestions:
                self.autocomplete_listbox.selection_set(0)

        # Position popup
        self.position_autocomplete_popup()

        # Apply styling
        self.style_manager.apply_to(self.autocomplete_listbox)

    def position_autocomplete_popup(self):
        if not self.autocomplete_popup:
            return

        # Get cursor position in text widget
        cursor_pos = self.text_editor.index(INSERT)
        bbox = self.text_editor.bbox(cursor_pos)

        if bbox:
            x, y, width, height = bbox
            # Get text widget's position relative to root window
            text_x = self.text_editor.winfo_rootx()
            text_y = self.text_editor.winfo_rooty()

            # Position popup below cursor
            popup_x = text_x + x
            popup_y = text_y + y + height + 5

            self.autocomplete_popup.geometry(f"+{popup_x}+{popup_y}")

    def navigate_suggestions(self, event):
        if not self.autocomplete_popup or not self.autocomplete_listbox:
            return

        current_selection = self.autocomplete_listbox.curselection()
        if not current_selection:
            return

        current_index = current_selection[0]

        if event.keysym == "Down":
            new_index = min(current_index + 1, self.autocomplete_listbox.size() - 1)
        else:  # Up
            new_index = max(current_index - 1, 0)

        self.autocomplete_listbox.selection_clear(0, END)
        self.autocomplete_listbox.selection_set(new_index)
        self.autocomplete_listbox.see(new_index)

        return "break"  # Prevent default newline behavior

    def insert_spaces(self, event):
        self.text_editor.insert(INSERT, "    ")
        return "break"  # Prevent default tab behavior

    def show_snippet_menu(self):
        if not self.code_snippets:
            return

        snippet_popup = Toplevel(self.win)
        snippet_popup.title("Code Snippets")
        snippet_popup.geometry("400x300")

        # Create listbox with snippets
        snippet_listbox = Listbox(snippet_popup, selectmode=SINGLE)
        snippet_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for snippet_name in self.code_snippets.keys():
            snippet_listbox.insert(END, snippet_name)

        def insert_selected_snippet():
            selection = snippet_listbox.curselection()
            if selection:
                snippet_name = snippet_listbox.get(selection[0])
                snippet_code = self.code_snippets[snippet_name]

                # Insert at current cursor position
                cursor_pos = self.text_editor.index(INSERT)
                self.text_editor.insert(cursor_pos, snippet_code)
                snippet_popup.destroy()

        # Add insert button
        insert_btn = Button(
            snippet_popup, text="Insert", command=insert_selected_snippet
        )
        insert_btn.pack(pady=5)

        # Bindings
        snippet_listbox.bind("<Double-Button-1>", lambda e: insert_selected_snippet())
        snippet_listbox.bind("<Return>", lambda e: insert_selected_snippet())
        snippet_listbox.bind("<Tab>", lambda e: insert_selected_snippet())

        # Apply styling
        self.style_manager.apply_to(snippet_popup)
        self.style_manager.apply_to(snippet_listbox)
        self.style_manager.apply_to(insert_btn)

        # Focus and center
        snippet_popup.focus_set()
        snippet_popup.transient(self.win)
        snippet_popup.grab_set()

    def auto_indentation(self, event):
        current_pos = self.text_editor.index(INSERT)
        current_line = self.text_editor.get(
            f"{current_pos.split('.')[0]}.0", current_pos
        )

        indent_level = 0
        spaces_count = 0

        for char in current_line:
            if char == " ":
                spaces_count += 1
                if spaces_count % 4 == 0:
                    indent_level += 1
            elif char == "\t":
                indent_level += 1
                spaces_count = 0
            else:
                break

        stripped_line = current_line.strip()
        if stripped_line.endswith(":"):
            indent_level += 1
        indent_str = "    " * indent_level
        self.text_editor.insert(INSERT, f"\n{indent_str}")

        return "break"

    def compile(self):
        def confirm():
            self.save_file()
            spec_path = os.path.join(self.directory, "game.spec")

            game_path = "game.py"
            assets_path = "assets"
            data_path = "data"
            python_files = []
            for root, _, files in os.walk(self.directory):
                for file in files:
                    if file.endswith(".py"):
                        python_files.append(
                            os.path.relpath(os.path.join(root, file), self.directory)
                        )

            datas = []

            datas.append((assets_path, assets_path))

            datas.append((data_path, data_path))

            for py_file in python_files:
                target_dir = os.path.dirname(py_file)
                if target_dir:
                    datas.append((py_file, target_dir))

            datas_str = "[\n"
            for src, dst in datas:
                datas_str += f"    ('{src}', '{dst}'),\n"
            datas_str += "]"

            spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{game_path}'],
    pathex=['{self.directory}'],
    binaries=[],
    datas={datas_str},
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='game',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True
)
"""

            with open(spec_path, "w") as f:
                f.write(spec_content)

            try:
                for dir_name in ["build", "dist"]:
                    dir_path = os.path.join(self.directory, dir_name)
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)

                result = subprocess.run(
                    ["pyinstaller", "--noconfirm", spec_path],
                    cwd=self.directory,
                    capture_output=True,
                    text=True,
                )

            except Exception as e:
                print(f"Error during compilation: {e}")
            finally:
                if os.path.exists(spec_path):
                    os.remove(spec_path)
                if os.path.exists(os.path.join(self.directory, "build")):
                    shutil.rmtree(os.path.join(self.directory, "build"))
                if os.path.exists(os.path.join(self.directory, "dist")):
                    shutil.move(
                        os.path.join(self.directory, "dist", "game"),
                        os.path.join(self.directory, self.name),
                    )
                    shutil.rmtree(os.path.join(self.directory, "dist"))
                popup.destroy()

        popup = Toplevel(self.win)

        popup.title("Compile Game")
        popup.resizable(False, False)

        label = Label(
            popup,
            text="Are you sure you want to compile the game (this will take a while)?",
        )
        confirm_btn = Button(popup, text="Confirm", command=confirm)
        cancel_btn = Button(popup, text="Cancel", command=popup.destroy)

        self.style_manager.apply_to(popup)
        self.style_manager.apply_to(label)
        self.style_manager.apply_to(confirm_btn)
        self.style_manager.apply_to(cancel_btn)

        label.pack(pady=10, padx=10)
        confirm_btn.pack(pady=10, padx=10)
        cancel_btn.pack(pady=10, padx=10)

        popup.focus_set()
        popup.bind("<Escape>", lambda event: popup.destroy())

        popup.wait_window(popup)
