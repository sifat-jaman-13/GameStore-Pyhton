import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.file_handler import read_table
from core.constants import FILES
from core.catalog import game_meta_text


class LibraryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.username = self.controller.session.current_user

        ctk.CTkLabel(self, text="My Game Library",
                     font=("Arial", 18, "bold")).pack(pady=(20, 10))

        self.lib_scroll = ctk.CTkScrollableFrame(self)
        self.lib_scroll.pack(fill="both", expand=True, padx=50, pady=20)

        self.refresh_library()

    def refresh_library(self):
        for w in self.lib_scroll.winfo_children():
            w.destroy()

        purchases = read_table(FILES["purchases"])
        games_db = {g[0]: g for g in read_table(FILES["games"]) if len(g) >= 4}

        has_games = False
        for p in purchases:
            if len(p) < 2 or p[0] != self.username or p[1] not in games_db:
                continue
            has_games = True
            g = games_db[p[1]]

            frame = ctk.CTkFrame(self.lib_scroll, fg_color="#2b2b2b", corner_radius=8)
            frame.pack(fill="x", pady=8, padx=5)

            details = ctk.CTkFrame(frame, fg_color="transparent")
            details.pack(side="left", padx=15, pady=10, expand=True, fill="x")
            ctk.CTkLabel(details, text=g[1],
                         font=("Arial", 13, "bold")).pack(anchor="w")
            meta = game_meta_text(g)
            if meta:
                ctk.CTkLabel(details, text=meta,
                             font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

            ctk.CTkButton(frame, text="Play", width=80, height=35,
                          font=("Arial", 12, "bold"),
                          fg_color="#00cc66", hover_color="#00994c",
                          command=lambda n=g[1]: self.simulate(f"Playing {n}...\nEnjoy your game!")).pack(
                side="right", padx=3, pady=5)

            ctk.CTkButton(frame, text="Install", width=80, height=35,
                          font=("Arial", 12),
                          fg_color="#4d4d4d", hover_color="#333333",
                          command=lambda n=g[1]: self.simulate(f"Installing {n}...\nPlease wait.")).pack(
                side="right", padx=3, pady=5)

        if not has_games:
            ctk.CTkLabel(self.lib_scroll,
                         text="You don't own any games yet. Head to the Store!",
                         font=("Arial", 14), text_color="gray").pack(pady=50)

    # noinspection PyMethodMayBeStatic
    def simulate(self, message):
        messagebox.showinfo("Simulation", message)
