import customtkinter as ctk
import time
import tkinter.messagebox as msg
from core.file_handler import read_table, append_row, sanitize
from core.constants import FILES
from core.utils import fmt_price


class WalletFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.user = self.controller.session.current_user

        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=44, pady=(22, 18))

        self.bal_lbl = ctk.CTkLabel(content, text="Balance: ৳0",
                                    font=("Arial", 30, "bold"), text_color="#00cc66")
        self.bal_lbl.pack(pady=(0, 18))
        self.refresh_balance()

        # Pending requests section
        pending_frame = ctk.CTkFrame(content, fg_color="#24282b",
                                     border_width=1, border_color="#3b4650",
                                     corner_radius=8, width=720, height=230)
        pending_frame.pack(pady=(0, 22), fill="x")
        pending_frame.pack_propagate(False)

        pending_header = ctk.CTkFrame(pending_frame, fg_color="transparent")
        pending_header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(pending_header, text="Pending Requests",
                     font=("Arial", 17, "bold"),
                     text_color="#ffaa00").pack(side="left")

        self.pending_count_lbl = ctk.CTkLabel(
            pending_header, text="", font=("Arial", 12, "bold"),
            text_color="#d7dde8")
        self.pending_count_lbl.pack(side="right")

        self.pending_scroll = ctk.CTkScrollableFrame(pending_frame, fg_color="transparent",
                                                     width=660, height=156)
        self.pending_scroll.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        self.refresh_pending_requests()

        form = ctk.CTkFrame(content, fg_color="#24282b",
                            border_width=1, border_color="#3b4650",
                            corner_radius=8, width=620, height=285)
        form.pack(pady=(0, 0), fill="x")
        form.pack_propagate(False)

        ctk.CTkLabel(form, text="Add Funds (bKash)",
                     font=("Arial", 18, "bold")).pack(pady=(20, 14))

        self.amt = ctk.CTkEntry(form, placeholder_text="Amount (৳)",
                                width=520, height=38, font=("Arial", 13),
                                border_width=1)
        self.amt.pack(pady=5)
        self.bkash = ctk.CTkEntry(form, placeholder_text="bKash (11 digits)",
                                  width=520, height=38, font=("Arial", 13),
                                  border_width=1)
        self.bkash.pack(pady=5)
        self.trx = ctk.CTkEntry(form, placeholder_text="Trx ID",
                                width=520, height=38, font=("Arial", 13),
                                border_width=1)
        self.trx.pack(pady=5)

        ctk.CTkButton(form, text="Submit Request", width=520, height=40,
                      font=("Arial", 13, "bold"),
                      fg_color="#1f6aa5", hover_color="#18547f",
                      command=self.submit).pack(pady=(16, 18))

    def refresh_pending_requests(self):
        """Display all pending wallet requests for the user"""
        for widget in self.pending_scroll.winfo_children():
            widget.destroy()

        requests = read_table(FILES["wallet_requests"])
        pending = [r for r in requests if r and len(r) >= 6 and r[1] == self.user and r[5] == "PENDING"]
        self.pending_count_lbl.configure(
            text=f"{len(pending)} pending" if pending else "No pending requests")

        if not pending:
            ctk.CTkLabel(self.pending_scroll, text="No pending requests",
                         font=("Arial", 14), text_color="#8f9aa3").pack(pady=48)
            return

        total_pending = 0.0
        for req in pending:
            req_id, username, amount, bkash, trx_id, status = req[0], req[1], req[2], req[3], req[4], req[5]
            try:
                total_pending += float(amount)
            except (ValueError, TypeError):
                pass

            req_frame = ctk.CTkFrame(self.pending_scroll, fg_color="#171a1d",
                                     border_width=1, border_color="#303945",
                                     corner_radius=8)
            req_frame.pack(fill="x", pady=7, padx=4)

            # Request details
            ctk.CTkLabel(req_frame, text=f"Amount Requested: ৳{fmt_price(amount)}",
                         font=("Arial", 13, "bold"), text_color="#ffaa00").pack(anchor="w", padx=14, pady=(10, 2))

            ctk.CTkLabel(req_frame, text=f"bKash: {bkash} | TRX: {trx_id}",
                         font=("Arial", 12), text_color="#d1d5db").pack(anchor="w", padx=14, pady=(2, 0))

            status_color = "#ffaa00" if status == "PENDING" else "#00ff00"
            ctk.CTkLabel(req_frame, text=f"Status: {status}",
                         font=("Arial", 12, "bold"), text_color=status_color).pack(anchor="w", padx=14, pady=(2, 10))

        # Total pending amount
        ctk.CTkLabel(self.pending_scroll, text=f"Total Pending: ৳{fmt_price(total_pending)}",
                     font=("Arial", 13, "bold"), text_color="#ff6b6b").pack(anchor="w", padx=6, pady=(10, 0))

    def refresh_balance(self):
        for u in read_table(FILES["users"]):
            if len(u) >= 7 and u[0] == self.user:
                self.bal_lbl.configure(text=f"Balance: ৳{fmt_price(u[6])}")
                return
        self.bal_lbl.configure(text="Balance: ৳0")

    def submit(self):
        a = sanitize(self.amt.get().strip())
        b = sanitize(self.bkash.get().strip())
        t = sanitize(self.trx.get().strip())

        if not (a and b and t):
            msg.showerror("Error", "All fields required.")
            return
        if not a.isdigit() or int(a) <= 0:
            msg.showerror("Error", "Amount must be a positive whole number.")
            return
        if len(b) != 11 or not b.isdigit():
            msg.showerror("Error", "bKash must be 11 digits.")
            return

        append_row(FILES["wallet_requests"],
                   [str(int(time.time())), self.user, a, b, t, "PENDING"])
        msg.showinfo("Success", "Request submitted! Waiting for admin approval.")
        for e in (self.amt, self.bkash, self.trx):
            e.delete(0, 'end')
        self.refresh_pending_requests()
