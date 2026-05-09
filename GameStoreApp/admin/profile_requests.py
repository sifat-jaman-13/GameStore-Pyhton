import re
import time
import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.constants import FILES
from core.file_handler import append_row, read_table, write_table
from core.message_utils import UNREAD


class ProfileRequestsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(20, 8))
        ctk.CTkLabel(header, text="Profile Requests",
                     font=("Arial", 22, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Review user requests for name and username changes.",
                     font=("Arial", 12), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=50, pady=20)

        self.refresh_requests()

    def refresh_requests(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        found = False
        for req in read_table(FILES["profile_requests"]):
            if len(req) < 5:
                continue
            req_id, username, new_fullname, new_username, status = req[:5]
            if status != "PENDING":
                continue

            found = True
            row = ctk.CTkFrame(self.scroll, fg_color="#23272f", corner_radius=8)
            row.pack(fill="x", pady=8, padx=5)

            info = (
                f"User: {username} | "
                f"Full Name -> {new_fullname or '(no change)'} | "
                f"Username -> {new_username or '(no change)'}"
            )
            ctk.CTkLabel(row, text=info, font=("Arial", 13),
                         anchor="w").pack(side="left", padx=15, pady=10,
                                          expand=True, fill="x")

            ctk.CTkButton(row, text="Reject",
                          fg_color="#b30000", hover_color="#800000",
                          width=80, height=35, font=("Arial", 12, "bold"),
                          command=lambda r=req_id, u=username:
                          self.update_request(r, "REJECTED", u)).pack(side="right", padx=5)

            ctk.CTkButton(row, text="Approve",
                          fg_color="#00cc66", hover_color="#00994d",
                          width=80, height=35, font=("Arial", 12, "bold"),
                          command=lambda r=req_id:
                          self.update_request(r, "APPROVED", None)).pack(side="right", padx=5)

        if not found:
            ctk.CTkLabel(self.scroll, text="No pending profile requests.",
                         font=("Arial", 22)).pack(pady=20)

    def update_request(self, req_id, new_status, fallback_user):
        requests = read_table(FILES["profile_requests"])
        target = None
        for req in requests:
            if len(req) >= 5 and req[0] == req_id:
                req[4] = new_status
                target = req
                break

        if not target:
            messagebox.showerror("Error", "Request not found.")
            return

        username, new_fullname, new_username = target[1], target[2], target[3]

        if new_status == "APPROVED":
            ok, msg, final_username = self.apply_profile_change(username, new_fullname, new_username)
            if not ok:
                target[4] = "PENDING"
                messagebox.showerror("Error", msg)
                return
            target[1] = final_username
            username = final_username
            self._notify_user(username, "Your profile change request was approved.")
        else:
            self._notify_user(fallback_user or username, "Your profile change request was rejected.")

        write_table(FILES["profile_requests"], requests)
        messagebox.showinfo("Done", f"Request {new_status}.")
        self.refresh_requests()

    def apply_profile_change(self, old_username, new_fullname, new_username):
        users = read_table(FILES["users"])
        target = None
        for user in users:
            if len(user) >= 7 and user[0] == old_username:
                target = user
                break

        if not target:
            return False, "User not found.", old_username

        final_username = new_username or old_username
        if final_username != old_username:
            if not (3 <= len(final_username) <= 20):
                return False, "Requested username must be between 3 and 20 characters.", old_username
            if not re.match(r"^[a-zA-Z0-9_]+$", final_username):
                return False, "Requested username can only contain letters, numbers, and underscores.", old_username
            for user in users:
                if len(user) >= 1 and user[0].lower() == final_username.lower():
                    return False, "Requested username is already taken.", old_username

        if new_fullname:
            target[4] = new_fullname
        target[0] = final_username
        write_table(FILES["users"], users)

        if final_username != old_username:
            self.rename_user_references(old_username, final_username)

        return True, "Updated.", final_username

    @staticmethod
    def rename_user_references(old_username, new_username):
        replacements = {
            "cart": [0],
            "purchases": [0],
            "wallet_requests": [1],
            "profile_requests": [1],
            "message_status": [0],
            "message_sessions": [1],
        }
        for file_key, indexes in replacements.items():
            rows = read_table(FILES[file_key])
            changed = False
            for row in rows:
                for index in indexes:
                    if len(row) > index and row[index] == old_username:
                        row[index] = new_username
                        changed = True
            if changed:
                write_table(FILES[file_key], rows)

        messages = read_table(FILES["messages"])
        changed = False
        for row in messages:
            if len(row) >= 6:
                sender_idx, receiver_idx = 2, 3
            else:
                sender_idx, receiver_idx = 1, 2
            if len(row) > sender_idx and row[sender_idx] == old_username:
                row[sender_idx] = new_username
                changed = True
            if len(row) > receiver_idx and row[receiver_idx] == old_username:
                row[receiver_idx] = new_username
                changed = True
        if changed:
            write_table(FILES["messages"], messages)

        sessions = read_table(FILES["message_sessions"])
        changed = False
        for row in sessions:
            if len(row) >= 2 and row[1] == old_username:
                row[1] = new_username
                changed = True
        if changed:
            write_table(FILES["message_sessions"], sessions)

    @staticmethod
    def _notify_user(username, text):
        """
        FIX: Use legacy 4-column format so message_utils auto-creates a legacy
        session for it. Previously used 6-column 'admin-notification-...' session_id
        which was never in message_sessions.txt — users got the unread badge
        but could never open the message.
        """
        msg_id = str(int(time.time() * 1000))
        append_row(FILES["messages"], [msg_id, "ADMIN", username, text, UNREAD])
