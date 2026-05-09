import customtkinter as ctk
import tkinter.messagebox as messagebox
import config
from core.admin_credentials import get_admin_credentials

MAX_ATTEMPTS = 5


class AdminLoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        # FIX: read attempts from controller so recreating this frame does NOT reset
        # the counter.  Previously self.admin_attempts lived inside the frame, so
        # calling show_admin_login() (which destroys and recreates the frame) silently
        # reset it to 0 — letting an attacker try forever in groups of 5.
        if not hasattr(self.controller, "admin_attempts"):
            self.controller.admin_attempts = 0

        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.frame, text=config.ADMIN_APP_TITLE,
                     font=("Arial", 26, "bold"), text_color="#ff4444").pack(pady=(0, 30))

        self.user_entry = ctk.CTkEntry(self.frame, placeholder_text="Admin Username",
                                       height=40, font=("Arial", 13))
        self.user_entry.pack(pady=10, fill="x", padx=20)

        self.pass_entry = ctk.CTkEntry(self.frame, placeholder_text="Admin Password",
                                       show="*", height=40, font=("Arial", 13))
        self.pass_entry.pack(pady=10, fill="x", padx=20)

        ctk.CTkButton(self.frame, text="Login to Admin Console",
                      fg_color="#cc0000", hover_color="#990000",
                      command=self.login,
                      height=40, font=("Arial", 13, "bold")).pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(self.frame, text="Exit", fg_color="transparent",
                      font=("Arial", 12),
                      command=self.controller.destroy).pack(pady=5)

        # If already locked out when frame is (re)created, show it immediately
        if self.controller.admin_attempts >= MAX_ATTEMPTS:
            self._show_locked()

    def login(self):
        if self.controller.admin_attempts >= MAX_ATTEMPTS:
            self._show_locked()
            return

        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        admin_user, admin_pass = get_admin_credentials()
        if username == admin_user and password == admin_pass:
            self.controller.admin_attempts = 0   # reset on successful login
            self.controller.show_admin_dashboard()
        else:
            self._handle_failed_attempt()

    def _handle_failed_attempt(self):
        self.controller.admin_attempts += 1
        tries_left = MAX_ATTEMPTS - self.controller.admin_attempts
        if tries_left <= 0:
            self._show_locked()
        else:
            messagebox.showwarning(
                "Warning",
                f"Invalid admin credentials.\n\nYou have {tries_left} attempt(s) remaining.")

    def _show_locked(self):
        messagebox.showerror(
            "Locked Out",
            f"Maximum of {MAX_ATTEMPTS} attempts reached.\nThe application will now close.")
        self.controller.destroy()
