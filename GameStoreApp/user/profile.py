import re
import time
import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.file_handler import append_row, read_table, write_table, sanitize
from core.constants import FILES


class ProfileFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.entries = {}
        self.user_index = -1
        self.user_data = None
        self.show_pass_var = None
        self.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self.entries = {}

        username = self.controller.session.current_user
        users = read_table(FILES["users"])
        self.user_index, self.user_data = next(
            ((i, u) for i, u in enumerate(users) if u and u[0] == username),
            (-1, None)
        )

        if not self.user_data:
            ctk.CTkLabel(self, text="User not found.", font=("Arial", 20)).pack(pady=30)
            return

        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=45, pady=(24, 20))

        ctk.CTkLabel(content, text="My Profile",
                     font=("Arial", 24, "bold")).pack(pady=(0, 18))

        card = ctk.CTkFrame(content, fg_color="#24282b",
                            border_width=1, border_color="#3b4650",
                            corner_radius=8, width=620)
        card.pack()

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=34, pady=(24, 12))

        self._info_row(info, "Full Name", self._field(4))
        self._info_row(info, "Username", self._field(0))
        self._info_row(info, "Status", self._field(5))

        ctk.CTkLabel(card, text="Request Admin Approval",
                     font=("Arial", 16, "bold"),
                     text_color="#ffaa00").pack(anchor="w", padx=34, pady=(6, 8))

        request_form = ctk.CTkFrame(card, fg_color="transparent")
        request_form.pack(fill="x", padx=34)

        self._entry(request_form, "New Full Name", "requested_fullname", "")
        self._entry(request_form, "New Username", "requested_username", "")

        ctk.CTkButton(card, text="Send Change Request",
                      width=190, height=34,
                      font=("Arial", 12, "bold"),
                      fg_color="#3b4650", hover_color="#4a5661",
                      command=self.submit_profile_request).pack(anchor="e", padx=34, pady=(8, 12))

        ctk.CTkLabel(card, text="Account Details",
                     font=("Arial", 16, "bold"),
                     text_color="#ffaa00").pack(anchor="w", padx=34, pady=(0, 8))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=34)

        self._entry(form, "Email Address", "email", self._field(2))
        self._entry(form, "Phone Number", "phone", self._field(3))
        self._entry(form, "Current Password", "current_password", "", show="*")
        ctk.CTkLabel(form, text="Required before saving any profile change.",
                     font=("Arial", 11),
                     text_color="#8f9aa3").pack(anchor="e", pady=(0, 2))

        ctk.CTkLabel(card, text="Change Password",
                     font=("Arial", 16, "bold"),
                     text_color="#ffaa00").pack(anchor="w", padx=34, pady=(16, 8))

        pass_form = ctk.CTkFrame(card, fg_color="transparent")
        pass_form.pack(fill="x", padx=34)

        self._entry(pass_form, "New Password", "new_password", "", show="*")
        self._entry(pass_form, "Confirm New Password", "confirm_password", "", show="*")

        bottom = ctk.CTkFrame(card, fg_color="transparent")
        bottom.pack(fill="x", padx=34, pady=(22, 26))

        self.show_pass_var = ctk.IntVar(value=0)
        ctk.CTkCheckBox(bottom, text="Show passwords",
                        variable=self.show_pass_var,
                        command=self.toggle_passwords,
                        font=("Arial", 12)).pack(side="left")

        ctk.CTkButton(bottom, text="Save Changes",
                      width=160, height=38,
                      font=("Arial", 13, "bold"),
                      fg_color="#1f6aa5", hover_color="#18547f",
                      command=self.save_changes).pack(side="right")

    def _field(self, index):
        return self.user_data[index] if index < len(self.user_data) else ""

    # noinspection PyMethodMayBeStatic
    def _info_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=f"{label}:",
                     width=115, anchor="w",
                     font=("Arial", 13, "bold"),
                     text_color="#b8c0c8").pack(side="left")
        ctk.CTkLabel(row, text=value or "N/A",
                     anchor="w", font=("Arial", 13)).pack(side="left")

    def _entry(self, parent, label, key, value, show=""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=label,
                     width=150, anchor="w",
                     font=("Arial", 12, "bold"),
                     text_color="#b8c0c8").pack(side="left", padx=(0, 10))
        entry = ctk.CTkEntry(row, width=360, height=34,
                             font=("Arial", 13),
                             border_width=1,
                             show=show)
        entry.pack(side="left", fill="x", expand=True)
        if value:
            entry.insert(0, value)
        self.entries[key] = entry

    def toggle_passwords(self):
        show_char = "" if self.show_pass_var.get() == 1 else "*"
        for key in ("current_password", "new_password", "confirm_password"):
            self.entries[key].configure(show=show_char)

    def save_changes(self):
        users = read_table(FILES["users"])
        if self.user_index < 0 or self.user_index >= len(users):
            messagebox.showerror("Error", "User not found.")
            return

        current_user = users[self.user_index]
        email = sanitize(self.entries["email"].get().strip())
        phone = sanitize(self.entries["phone"].get().strip())
        current_password = sanitize(self.entries["current_password"].get().strip())
        new_password = sanitize(self.entries["new_password"].get().strip())
        confirm_password = sanitize(self.entries["confirm_password"].get().strip())

        old_email = current_user[2] if len(current_user) > 2 else ""
        old_phone = current_user[3] if len(current_user) > 3 else ""
        old_password = current_user[1] if len(current_user) > 1 else ""

        email_changed = email != old_email
        phone_changed = phone != old_phone
        password_changed = bool(new_password or confirm_password)

        if not (email_changed or phone_changed or password_changed):
            messagebox.showinfo("Profile", "No changes to save.")
            return

        if not current_password:
            messagebox.showerror("Error", "Enter your current password before saving changes.")
            return

        if current_password != old_password:
            messagebox.showerror("Error", "Current password is incorrect.")
            return

        if not email:
            messagebox.showerror("Error", "Email is required.")
            return
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            messagebox.showerror("Error", "Enter a valid email address.")
            return
        if not phone:
            messagebox.showerror("Error", "Phone is required.")
            return
        if not re.match(r"^\d{11}$", phone):
            messagebox.showerror("Error", "Phone must be exactly 11 digits.")
            return

        for i, user in enumerate(users):
            if i == self.user_index or len(user) < 4:
                continue
            if user[2] == email:
                messagebox.showerror("Error", "Email already registered.")
                return
            if user[3] == phone:
                messagebox.showerror("Error", "Phone already registered.")
                return

        if password_changed:
            if not new_password or not confirm_password:
                messagebox.showerror("Error", "Enter and confirm the new password.")
                return
            if new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match.")
                return
            current_user[1] = new_password

        current_user[2] = email
        current_user[3] = phone
        users[self.user_index] = current_user
        write_table(FILES["users"], users)

        messagebox.showinfo("Success", "Profile updated successfully.")
        self.refresh()

    def submit_profile_request(self):
        new_fullname = sanitize(self.entries["requested_fullname"].get().strip())
        new_username = sanitize(self.entries["requested_username"].get().strip())
        current_fullname = self._field(4)
        current_username = self._field(0)

        if not new_fullname and not new_username:
            messagebox.showerror("Error", "Enter a new full name or username to request.")
            return

        if new_fullname == current_fullname:
            new_fullname = ""
        if new_username == current_username:
            new_username = ""

        if not new_fullname and not new_username:
            messagebox.showinfo("Profile", "Requested values match your current profile.")
            return

        if new_username:
            if not (3 <= len(new_username) <= 20):
                messagebox.showerror("Error", "Username must be between 3 and 20 characters.")
                return
            if not re.match(r"^[a-zA-Z0-9_]+$", new_username):
                messagebox.showerror("Error", "Username can only contain letters, numbers, and underscores ( _ ).")
                return
            for user in read_table(FILES["users"]):
                if len(user) >= 1 and user[0].lower() == new_username.lower():
                    messagebox.showerror("Error", "Username already taken.")
                    return

        for req in read_table(FILES["profile_requests"]):
            if len(req) >= 5 and req[1] == current_username and req[4] == "PENDING":
                messagebox.showerror("Error", "You already have a pending profile change request.")
                return

        req_id = str(int(time.time() * 1000))
        append_row(FILES["profile_requests"],
                   [req_id, current_username, new_fullname, new_username, "PENDING"])
        messagebox.showinfo("Success", "Profile change request sent to admin.")
        self.refresh()
