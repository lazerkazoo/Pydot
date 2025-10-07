from io import text_encoding
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import Style
from style_manager import StyleManager
import os, subprocess


class GameEditor:
    def __init__(self, name: str, directory: str) -> None:
        self.win = Tk()
        self.win.attributes("-zoomed", True)
        self.win.title(name)
        self.directory = directory
        self.current_file = None
        self.game_process = None

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

        start_btn = Button(top_bar, text="Start", command=self.start_game)

        stop_btn = Button(top_bar, text="Stop", command=self.stop_game)

        text_frame = Frame(self.win)

        self.text_editor = Text(text_frame, wrap="none")
        scrollbar = Scrollbar(text_frame, command=self.text_editor.yview)

        # Style Stuff
        self.style_manager.apply_to_frame(top_bar)
        self.style_manager.apply_to_button(settings_btn)
        self.style_manager.apply_to_button(new_btn)
        self.style_manager.apply_to_button(open_btn)
        self.style_manager.apply_to_button(save_btn)
        self.style_manager.apply_to_button(start_btn)
        self.style_manager.apply_to_button(stop_btn)
        self.style_manager.apply_to_frame(text_frame)
        self.style_manager.apply_to_text(self.text_editor)
        self.text_editor.config(yscrollcommand=scrollbar.set)

        # pack stuff 2 top bar
        settings_btn.pack(side="left", padx=pad)
        new_btn.pack(side="left", padx=pad)
        open_btn.pack(side="left", padx=pad)
        save_btn.pack(side="left", padx=pad)
        start_btn.pack(side="right", padx=pad)
        stop_btn.pack(side="right", padx=pad)

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

        # Make Key Binds Work
        self.text_editor.focus_set()

        self.force_open_file("main.py")

        self.win.mainloop()

    def open_file(self):
        file_path = askopenfilename(
            initialdir=self.directory,
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
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
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
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

        popup.mainloop()

    def new_file(self):
        pad = self.pad

        def create(file: str):
            file = file.lower()

            if not file.strip():
                return

            class_name = file.capitalize()
            new_file_path = f"{self.directory}/scripts/{file}.py"
            main_file_path = f"{self.directory}/main.py"

            # Create the new class file
            with open(new_file_path, "w") as f:
                f.write(
                    f"import pygame as pydot\n\nclass {class_name}:\n   def __init__(self):\n        # put stuff here\n      pass"
                )

            # Update main.py to import the new class
            if os.path.exists(main_file_path):
                with open(main_file_path, "r") as r:
                    content = r.read()

                # Add import line at the beginning
                import_line = f"from scripts.{file} import {class_name}\n"
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
            popup = Toplevel(self.win)
            popup.title("Create New File")

            name_lbl = Label(popup, text="File Name (without .py):")
            name_en = Entry(popup)
            name_en.focus_set()

            def on_create():
                file_name = name_en.get().strip()
                if file_name:
                    create(file_name)
                    popup.destroy()

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

    def start_game(self):
        """Start the game by running the project's main.py or game.py"""
        if not self.directory:
            print("❌ No project directory set")
            return

        # Save current file before running
        if self.current_file:
            self.save_file()
            print("💾 Saved current file")

        # Find the game file to run
        target_file = None
        for filename in ["game.py", "main.py"]:
            full_path = os.path.join(self.directory, filename)
            if os.path.exists(full_path):
                target_file = filename
                break
        
        if not target_file:
            print("❌ No game.py or main.py found in project directory")
            return

        try:
            print(f"🚀 Starting game: {target_file}")
            print(f"📁 Working directory: {self.directory}")
            
            # Create a simple command that works on Linux
            cmd = ["python3", target_file]
            
            # Start the process with proper environment
            self.game_process = subprocess.Popen(
                cmd,
                cwd=self.directory,
                stdout=None,  # Let output go to terminal
                stderr=None,  # Let errors go to terminal
                stdin=None    # No input needed
            )
            
            print(f"✅ Game process started with PID: {self.game_process.pid}")
            
            # Quick check if it started successfully
            import time
            time.sleep(0.2)
            
            if self.game_process.poll() is None:
                print("🎮 Game is running! Look for the game window.")
            else:
                exit_code = self.game_process.returncode
                print(f"❌ Game exited immediately with code: {exit_code}")
                self.game_process = None
                
        except FileNotFoundError:
            print("❌ Python3 not found. Trying 'python'...")
            try:
                cmd = ["python", target_file]
                self.game_process = subprocess.Popen(
                    cmd,
                    cwd=self.directory,
                    stdout=None,
                    stderr=None,
                    stdin=None
                )
                print(f"✅ Game started with PID: {self.game_process.pid}")
            except Exception as e2:
                print(f"❌ Failed to start with 'python': {e2}")
                
        except Exception as e:
            print(f"❌ Error starting game: {e}")
            import traceback
            traceback.print_exc()
            self.game_process = None

    def stop_game(self):
        """Stop the running game process"""
        if self.game_process:
            try:
                print(f"🛑 Stopping game process (PID: {self.game_process.pid})")
                self.game_process.terminate()
                
                # Wait a moment for graceful shutdown
                import time
                time.sleep(0.5)
                
                # Force kill if still running
                if self.game_process.poll() is None:
                    print("💀 Force killing game process")
                    self.game_process.kill()
                    
                self.game_process = None
                print("✅ Game stopped successfully")
                
            except Exception as e:
                print(f"❌ Error stopping game: {e}")
                self.game_process = None
        else:
            print("ℹ️  No game is currently running")
