#!/usr/bin/env python3
"""
A.B.E.L - Launcher
Compile with: pyinstaller --onefile --noconsole --icon=abel.ico launcher.py
"""

import subprocess
import sys
import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time


class AbelLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("A.B.E.L - Launcher")
        self.root.geometry("500x400")
        self.root.configure(bg="#050505")
        self.root.resizable(False, False)

        # Center window
        self.center_window()

        # Status
        self.is_running = False

        self.create_ui()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def create_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#050505")
        title_frame.pack(pady=20)

        title = tk.Label(
            title_frame,
            text="A.B.E.L",
            font=("Consolas", 36, "bold"),
            fg="#00F0FF",
            bg="#050505"
        )
        title.pack()

        subtitle = tk.Label(
            title_frame,
            text="Autonomous Backend Entity for Living",
            font=("Consolas", 12),
            fg="#888888",
            bg="#050505"
        )
        subtitle.pack()

        version = tk.Label(
            title_frame,
            text="v2.0",
            font=("Consolas", 10),
            fg="#00F0FF",
            bg="#050505"
        )
        version.pack()

        # Status indicator
        self.status_frame = tk.Frame(self.root, bg="#050505")
        self.status_frame.pack(pady=10)

        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=20,
            height=20,
            bg="#050505",
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.status_circle = self.status_indicator.create_oval(
            2, 2, 18, 18, fill="#FF0000", outline=""
        )

        self.status_label = tk.Label(
            self.status_frame,
            text="Arrete",
            font=("Consolas", 12),
            fg="#FF0000",
            bg="#050505"
        )
        self.status_label.pack(side=tk.LEFT)

        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="#050505")
        btn_frame.pack(pady=20)

        # Style buttons
        btn_style = {
            "font": ("Consolas", 11),
            "width": 25,
            "height": 2,
            "cursor": "hand2"
        }

        self.start_btn = tk.Button(
            btn_frame,
            text="Demarrer A.B.E.L",
            bg="#00F0FF",
            fg="#050505",
            activebackground="#00C0CC",
            command=self.start_abel,
            **btn_style
        )
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(
            btn_frame,
            text="Arreter A.B.E.L",
            bg="#FF006E",
            fg="#FFFFFF",
            activebackground="#CC0058",
            command=self.stop_abel,
            state=tk.DISABLED,
            **btn_style
        )
        self.stop_btn.pack(pady=5)

        # Links frame
        links_frame = tk.Frame(self.root, bg="#050505")
        links_frame.pack(pady=10)

        link_style = {
            "font": ("Consolas", 10),
            "fg": "#00F0FF",
            "bg": "#050505",
            "cursor": "hand2"
        }

        api_link = tk.Label(links_frame, text="API Documentation", **link_style)
        api_link.pack(side=tk.LEFT, padx=20)
        api_link.bind("<Button-1>", lambda e: self.open_url("http://localhost:8000/docs"))

        dash_link = tk.Label(links_frame, text="Dashboard", **link_style)
        dash_link.pack(side=tk.LEFT, padx=20)
        dash_link.bind("<Button-1>", lambda e: self.open_url("http://localhost:3000"))

        # Log area
        log_frame = tk.Frame(self.root, bg="#050505")
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_frame,
            height=6,
            bg="#111111",
            fg="#00FF00",
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_status(self, running):
        self.is_running = running
        if running:
            self.status_indicator.itemconfig(self.status_circle, fill="#00FF00")
            self.status_label.config(text="En cours", fg="#00FF00")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_indicator.itemconfig(self.status_circle, fill="#FF0000")
            self.status_label.config(text="Arrete", fg="#FF0000")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def check_docker(self):
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def start_abel(self):
        def run():
            if not self.check_docker():
                messagebox.showerror(
                    "Erreur",
                    "Docker n'est pas installe ou n'est pas en cours d'execution.\n"
                    "Veuillez demarrer Docker Desktop."
                )
                return

            self.log("Demarrage de A.B.E.L...")

            try:
                process = subprocess.Popen(
                    ["docker-compose", "up", "-d"],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    self.log("A.B.E.L demarre avec succes!")
                    self.root.after(0, lambda: self.update_status(True))
                else:
                    self.log(f"Erreur: {stderr.decode()}")
            except Exception as e:
                self.log(f"Erreur: {str(e)}")

        threading.Thread(target=run, daemon=True).start()

    def stop_abel(self):
        def run():
            self.log("Arret de A.B.E.L...")

            try:
                process = subprocess.Popen(
                    ["docker-compose", "down"],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    self.log("A.B.E.L arrete.")
                    self.root.after(0, lambda: self.update_status(False))
                else:
                    self.log(f"Erreur: {stderr.decode()}")
            except Exception as e:
                self.log(f"Erreur: {str(e)}")

        threading.Thread(target=run, daemon=True).start()

    def open_url(self, url):
        webbrowser.open(url)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AbelLauncher()
    app.run()
