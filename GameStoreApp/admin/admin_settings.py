import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.admin_credentials import get_admin_credentials, save_admin_credentials
from core.file_handler import sanitize


class AdminSettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=70, pady=35)

        ctk.CTkLabel(wrapper, text="Admin Settings",
                     font=("Arial", 24, "bold")).pack(anchor="w")
        ctk.CTkLabel(wrapper, text="Update the admin login used for this app.",
                     font=("Arial", 13), text_color="#9ca3af").pack(anchor="w", pady=(4, 22))

        card = ctk.CTkFrame(wrapper, fg_color="#23272f", corner_radius=8)
        card.pack(fill="x")

        current_user, _ = get_admin_credentials()
        self.username = ctk.StringVar(value=current_user)
        self.password = ctk.StringVar()
        self.confirm = ctk.StringVar()

        self._field(card, "Username", self.username)
        self._field(card, "New Password", self.password, show="*")
        self._field(card, "Confirm Password", self.confirm, show="*")

        self.show_var = ctk.IntVar(value=0)
        ctk.CTkCheckBox(card, text="Show passwords", variable=self.show_var,
                        command=self.toggle_passwords,
                        font=("Arial", 12)).pack(anchor="w", padx=22, pady=(2, 14))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=22, pady=(0, 22))
        ctk.CTkButton(actions, text="Save Admin Login",
                      height=40, font=("Arial", 13, "bold"),
                      command=self.save).pack(side="left")

    def _field(self, master, label, variable, show=""):
        ctk.CTkLabel(master, text=label, font=("Arial", 12, "bold"),
                     text_color="#d7dde8").pack(anchor="w", padx=22, pady=(18, 5))
        entry = ctk.CTkEntry(master, textvariable=variable, show=show,
                             height=40, font=("Arial", 13))
        entry.pack(fill="x", padx=22, pady=(0, 2))
        if show:
            if not hasattr(self, "password_entries"):
                self.password_entries = []
            self.password_entries.append(entry)
        return entry

    def toggle_passwords(self):
        show = "" if self.show_var.get() else "*"
        for entry in getattr(self, "password_entries", []):
            entry.configure(show=show)

    def save(self):
        username = sanitize(self.username.get().strip())
        password = sanitize(self.password.get().strip())
        confirm = sanitize(self.confirm.get().strip())

        if not username or not password or not confirm:
            messagebox.showerror("Error", "Username, password, and confirm password are required.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Confirm password does not match.")
            return

        save_admin_credentials(username, password)
        self.password.set("")
        self.confirm.set("")
        messagebox.showinfo("Saved", "Admin login updated successfully.")
