import customtkinter as ctk
import tkinter.messagebox as messagebox
import time
from core.file_handler import read_table, write_table, append_row
from core.constants import FILES
from core.utils import normalize_balance
from core.message_utils import UNREAD


class WalletRequestsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(20, 8))
        ctk.CTkLabel(header, text="Wallet Requests",
                     font=("Arial", 22, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Approve or reject pending balance top-ups.",
                     font=("Arial", 12), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=50, pady=20)

        self.refresh_requests()

    def refresh_requests(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        requests = read_table(FILES["wallet_requests"])
        pending_found = False

        for req in requests:
            if len(req) < 6:
                continue
            req_id, username, amount, bkash, trx_id, status = req[:6]
            if status != "PENDING":
                continue

            pending_found = True
            row = ctk.CTkFrame(self.scroll, fg_color="#23272f", corner_radius=8)
            row.pack(fill="x", pady=8, padx=5)

            info = f"User: {username} | Amount: ৳{amount} | bKash: {bkash} | Trx: {trx_id}"
            ctk.CTkLabel(row, text=info, font=("Arial", 13)).pack(
                side="left", padx=15, pady=10, expand=True, fill="x")

            ctk.CTkButton(row, text="Reject",
                          fg_color="#b30000", hover_color="#800000",
                          width=80, height=35, font=("Arial", 12, "bold"),
                          command=lambda r=req_id, u=username:
                                self.update_request(r, "REJECTED", u, None)).pack(side="right", padx=5)

            ctk.CTkButton(row, text="Approve",
                          fg_color="#00cc66", hover_color="#00994d",
                          width=80, height=35, font=("Arial", 12, "bold"),
                          command=lambda r=req_id, u=username, a=amount:
                                self.update_request(r, "APPROVED", u, a)).pack(side="right", padx=5)

        if not pending_found:
            ctk.CTkLabel(self.scroll, text="No pending requests.",
                         font=("Arial", 22)).pack(pady=20)

    def update_request(self, req_id, new_status, username, amount):
        requests = read_table(FILES["wallet_requests"])
        target = None
        for r in requests:
            if len(r) >= 6 and r[0] == req_id:
                target = r
                break

        if target is None:
            messagebox.showerror("Error", "Request not found.")
            self.refresh_requests()
            return

        if new_status == "APPROVED" and amount is not None:
            try:
                amt = float(amount)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Request amount is invalid.")
                return

            users = read_table(FILES["users"])
            user_found = False
            for u in users:
                if len(u) >= 7 and u[0] == username:
                    user_found = True
                    try:
                        cur = float(u[6])
                    except ValueError:
                        cur = 0.0
                    # FIX: use normalize_balance for consistent storage
                    u[6] = normalize_balance(cur + amt)
                    break
            if not user_found:
                messagebox.showerror("Error", "User not found. Request was left pending.")
                self.refresh_requests()
                return

            target[5] = new_status
            write_table(FILES["wallet_requests"], requests)
            write_table(FILES["users"], users)
            self._notify_user(username, "Funds added successfully.")
        elif new_status == "REJECTED":
            target[5] = new_status
            write_table(FILES["wallet_requests"], requests)
            self._notify_user(username, "Transaction rejected. Please try again.")
        else:
            target[5] = new_status
            write_table(FILES["wallet_requests"], requests)

        messagebox.showinfo("Done", f"Request {new_status}.")
        self.refresh_requests()

    @staticmethod
    def _notify_user(username, text):
        """
        FIX: Use legacy 4-column format (no session_id column) so message_utils
        automatically creates a synthetic legacy session for it. Previously the
        6-column format with 'admin-notification-...' session_id was never added
        to message_sessions.txt, so users could see the unread badge but could
        never actually open or read the message.
        """
        msg_id = str(int(time.time() * 1000))
        append_row(FILES["messages"], [msg_id, "ADMIN", username, text, UNREAD])
