import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.file_handler import read_table, write_table
from core.constants import FILES, STATUSES
from core.catalog import game_meta_text, game_price_text, get_game_price
from core.message_utils import parse_message
from core.utils import fmt_price, normalize_balance


# Canonical schema for users.txt:
# [0] username, [1] password, [2] email, [3] phone, [4] name,
# [5] status, [6] balance
USER_COLS = 7

class ManageUsersFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(20, 8))
        ctk.CTkLabel(header, text="Manage Users",
                     font=("Arial", 22, "bold")).pack(anchor="w")
        ctk.CTkLabel(header,
                     text="Edit account details, status, wallet balance, and user libraries.",
                     font=("Arial", 12), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=50, pady=20)

        self.refresh_users()

    # ------------------------------------------------------------------ list --

    def refresh_users(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        users = read_table(FILES["users"]) or []
        if not users:
            ctk.CTkLabel(self.scroll, text="No users registered.",
                         font=("Arial", 20), text_color="gray").pack(pady=20)
            return

        for u in users:
            if not u or len(u) < 7:
                continue
            # Schema: [username, password, email, phone, name, status, balance]
            username = u[0]
            email = u[2]
            phone = u[3]
            name = u[4]
            status = "ACTIVE" if u[5] == "TIMEOUT" else u[5]
            balance = u[6]

            row = ctk.CTkFrame(self.scroll, fg_color="#23272f", corner_radius=8)
            row.pack(fill="x", pady=10, padx=10)

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=10)

            ctk.CTkLabel(info_frame, text=f"{username}  |  {name}",
                         font=("Arial", 15, "bold")).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"{email}  |  {phone}",
                         font=("Arial", 12), text_color="#aeb7c5").pack(anchor="w", pady=(4, 0))
            ctk.CTkLabel(info_frame, text=f"Wallet Balance: ৳{fmt_price(balance)}",
                         font=("Arial", 12, "bold"), text_color="#22c55e").pack(anchor="w", pady=(5, 0))

            games_count = self.get_user_games_count(username)

            ctk.CTkLabel(info_frame,
                         text=f"Games Purchased: {games_count}  |  Status: {status}",
                         font=("Arial", 12), text_color="#f59e0b").pack(anchor="w")

            controls_frame = ctk.CTkFrame(row, fg_color="transparent")
            controls_frame.pack(fill="x", padx=15, pady=10)

            ctk.CTkButton(controls_frame, text="Full Control", width=100, height=35,
                          font=("Arial", 12, "bold"),
                          command=lambda un=username: self.open_full_control(un)).pack(side="left", padx=5)
            ctk.CTkButton(controls_frame, text="View Games", width=100, height=35,
                          font=("Arial", 12, "bold"), fg_color="#0066cc",
                          command=lambda un=username: self.view_user_games(un)).pack(side="left", padx=5)
            ctk.CTkButton(controls_frame, text="Delete",
                          fg_color="#b30000", hover_color="#800000",
                          width=80, height=35, font=("Arial", 12, "bold"),
                          command=lambda un=username: self.delete_user(un)).pack(side="right", padx=5)

    # ---------------------------------------------------------- helpers -------

    @staticmethod
    def get_user_games_count(username):
        # FIX #12: guard row length before indexing.
        return sum(
            1 for p in read_table(FILES["purchases"])
            if p and len(p) >= 2 and p[0] == username
        )

    @staticmethod
    def _pad(user, length=USER_COLS):
        """Return a length-`length` view of user without mutating disk state."""
        if len(user) >= length:
            return user
        return list(user) + [""] * (length - len(user))

    # -------------------------------------------------------- full control ----

    def open_full_control(self, username):
        users = read_table(FILES["users"]) or []
        found = next((u for u in users if u and u[0] == username), None)
        if found is None:
            messagebox.showerror("Error", "User not found")
            return

        # Snapshot at open time — re-read on save to avoid clobbering concurrent edits (FIX #8).
        original_snapshot: list = self._pad(list(found))

        popup = ctk.CTkToplevel(self)
        popup.title(f"Full Control - {username}")
        popup.geometry("520x700")
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()  # FIX #15: keep messageboxes attached to popup

        ctk.CTkLabel(popup, text=f"Edit User: {username}",
                     font=("Arial", 18, "bold")).pack(pady=10)

        scroll = ctk.CTkScrollableFrame(popup)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Username (read-only)
        ctk.CTkLabel(scroll, text="Username:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        username_var = ctk.StringVar(value=original_snapshot[0])
        ctk.CTkEntry(scroll, textvariable=username_var, state="disabled").pack(fill="x", pady=(0, 10))

        # Password
        ctk.CTkLabel(scroll, text="Password:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        password_var = ctk.StringVar(value=original_snapshot[1])
        ctk.CTkEntry(scroll, textvariable=password_var).pack(fill="x", pady=(0, 10))

        # Email
        ctk.CTkLabel(scroll, text="Email:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        email_var = ctk.StringVar(value=original_snapshot[2])
        ctk.CTkEntry(scroll, textvariable=email_var).pack(fill="x", pady=(0, 10))

        # Phone
        ctk.CTkLabel(scroll, text="Phone:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        phone_var = ctk.StringVar(value=original_snapshot[3])
        ctk.CTkEntry(scroll, textvariable=phone_var).pack(fill="x", pady=(0, 10))

        # Full Name
        ctk.CTkLabel(scroll, text="Full Name:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        name_var = ctk.StringVar(value=original_snapshot[4])
        ctk.CTkEntry(scroll, textvariable=name_var).pack(fill="x", pady=(0, 10))

        # Status
        ctk.CTkLabel(scroll, text="Status:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        status_var = ctk.StringVar(value=original_snapshot[5] if original_snapshot[5] in STATUSES else "ACTIVE")
        ctk.CTkOptionMenu(scroll, variable=status_var, values=STATUSES).pack(fill="x", pady=(0, 10))

        # ---- Set vs. Adjust balance (mutually exclusive) ----
        ctk.CTkLabel(scroll, text="Set Balance (replaces current):",
                     font=("Arial", 12, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(10, 0))
        balance_var = ctk.StringVar(value=original_snapshot[6])
        ctk.CTkEntry(scroll, textvariable=balance_var,
                     placeholder_text="Enter exact new balance").pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(scroll, text="OR  Adjust Balance (+/- from current):",
                     font=("Arial", 12, "bold"), text_color="#f59e0b").pack(anchor="w", pady=(10, 0))
        adjustment_var = ctk.StringVar(value="")
        ctk.CTkEntry(scroll, textvariable=adjustment_var,
                     placeholder_text="e.g. +500 or -200  (leave blank to use Set Balance)").pack(
            fill="x", pady=(0, 4))
        ctk.CTkLabel(scroll, text="Leave 'Adjust' blank to use 'Set Balance' instead.",
                     font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", pady=(0, 10))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        def save_changes():
            # FIX #8: re-read users now to detect concurrent modifications.
            users_all = read_table(FILES["users"]) or []
            current_idx = next(
                (i for i, u in enumerate(users_all) if u and u[0] == username), None)
            if current_idx is None:
                messagebox.showerror("Error", "User no longer exists.")
                popup.destroy()
                self.refresh_users()
                return
            current_row = self._pad(list(users_all[current_idx]))

            # Drift check: if stored balance changed under us, confirm overwrite.
            try:
                snapshot_bal = float(original_snapshot[6] or 0)
                current_bal = float(current_row[6] or 0)
            except (ValueError, TypeError):
                snapshot_bal = current_bal = 0.0
            drift = abs(snapshot_bal - current_bal) > 1e-9

            # ---- Validate basic fields ----
            email_val = email_var.get().strip()
            phone_val = phone_var.get().strip()
            name_val = name_var.get().strip()
            password_val = password_var.get()

            if not name_val:
                messagebox.showerror("Error", "Full Name cannot be empty.")
                return
            if not password_val:
                messagebox.showerror("Error", "Password cannot be empty.")
                return
            if "@" not in email_val or "." not in email_val:
                messagebox.showerror("Error", "Email looks invalid.")
                return
            if not phone_val.replace("+", "").replace("-", "").replace(" ", "").isdigit():
                messagebox.showerror("Error", "Phone must contain digits only (with optional + - spaces).")
                return

            # ---- Balance: Adjust takes precedence over Set ----
            adj_text = adjustment_var.get().strip().replace(" ", "")  # FIX #10
            if adj_text:
                try:
                    adj = float(adj_text)
                except ValueError:
                    messagebox.showerror("Error", "Adjust amount must be a valid number (e.g. 500 or -200).")
                    return
                # FIX #8: adjust against the CURRENT stored balance, not the stale snapshot.
                final_balance = current_bal + adj
            else:
                try:
                    final_balance = float(balance_var.get())
                except ValueError:
                    messagebox.showerror("Error", "Balance must be a valid number.")
                    return
                if drift and not messagebox.askyesno(
                        "Balance changed",
                        f"Stored balance changed from ৳{snapshot_bal} to ৳{current_bal} "
                        f"since you opened this dialog.\n\nOverwrite with ৳{final_balance}?"):
                    return

            if final_balance < 0:
                messagebox.showerror("Error", "Balance cannot be negative.")
                return

            # FIX #9: single source of truth for username (it is read-only).
            new_data = [
                username,
                password_val,
                email_val,
                phone_val,
                name_val,
                status_var.get(),
                normalize_balance(final_balance),
            ]

            users_all[current_idx] = new_data
            write_table(FILES["users"], users_all)
            popup.destroy()
            self.refresh_users()
            messagebox.showinfo("Success", "User updated successfully!")

        ctk.CTkButton(btn_frame, text="Save Changes", command=save_changes,
                      width=150, height=40).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=popup.destroy,
                      width=150, height=40, fg_color="#666").pack(side="left", padx=5)

    # -------------------------------------------------------- view games ------

    def view_user_games(self, username):
        purchases = read_table(FILES["purchases"])
        games = read_table(FILES["games"])
        user_games = [p for p in purchases if p and len(p) >= 2 and p[0] == username]

        popup = ctk.CTkToplevel(self)
        popup.title(f"Games - {username}")
        popup.geometry("500x400")
        popup.minsize(500, 400)
        popup.resizable(True, True)

        ctk.CTkLabel(popup, text=f"Games Owned by {username}",
                     font=("Arial", 18, "bold")).pack(pady=10)

        if not user_games:
            ctk.CTkLabel(popup, text="No games purchased",
                         font=("Arial", 14), text_color="gray").pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(popup)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        total_value = 0.0  # FIX (minor): floats from the start
        for purchase in user_games:
            game_id = purchase[1]
            found = next((g for g in games if g and len(g) >= 4 and g[0] == game_id), None)
            if found is None:
                continue
            game_info = found  # already a list; cast was unnecessary
            name = game_info[1]
            price = get_game_price(game_info)

            try:
                total_value += float(price)
            except (TypeError, ValueError):
                pass

            game_frame = ctk.CTkFrame(scroll, fg_color="#23272f", corner_radius=8)
            game_frame.pack(fill="x", pady=5, padx=5)

            details = ctk.CTkFrame(game_frame, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            ctk.CTkLabel(details, text=name, font=("Arial", 12, "bold")).pack(anchor="w")
            ctk.CTkLabel(details, text=f"Price: {game_price_text(game_info, fmt_price)}",
                         font=("Arial", 11), text_color="#22c55e").pack(anchor="w", pady=(2, 0))
            meta = game_meta_text(game_info)
            if meta:
                ctk.CTkLabel(details, text=meta,
                             font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", pady=(2, 0))
            ctk.CTkButton(game_frame, text="Remove",
                          fg_color="#b30000", hover_color="#800000",
                          width=80, height=32, font=("Arial", 11, "bold"),
                          command=lambda gid=game_id, pop=popup:
                          self.delete_game_from_user(username, gid, pop)).pack(
                side="right", padx=10, pady=8)

        ctk.CTkLabel(scroll,
                     text=f"\nTotal Value (current catalog prices): ৳{fmt_price(total_value)}",
                     font=("Arial", 12, "bold"), text_color="#ffaa00").pack(anchor="w", pady=10)

    def delete_game_from_user(self, username, game_id, popup):
        if not messagebox.askyesno("Confirm", "Remove this game from the user's library?"):
            return
        # FIX #2 + #3: guard None/short rows AND remove only ONE matching copy.
        purchases = read_table(FILES["purchases"])
        new_purchases = []
        removed = False
        for p in purchases:
            if (not removed and p and len(p) >= 2
                    and p[0] == username and p[1] == game_id):
                removed = True  # skip exactly one occurrence
                continue
            new_purchases.append(p)
        write_table(FILES["purchases"], new_purchases)
        popup.destroy()
        self.refresh_users()
        self.view_user_games(username)

    # -------------------------------------------------------- delete user -----

    def delete_user(self, username):
        if not messagebox.askyesno(
                "Confirm",
                f"Delete user '{username}'?\n\nThis will permanently remove all their data."):
            return

        # Helper to filter rows safely.
        def _filter(file_key, predicate_keep):
            rows = [r for r in read_table(FILES[file_key]) if r and predicate_keep(r)]
            write_table(FILES[file_key], rows)

        _filter("users",            lambda u: u[0] != username)
        _filter("purchases",        lambda p: len(p) >= 2 and p[0] != username)
        _filter("cart",             lambda c: len(c) >= 2 and c[0] != username)
        _filter("wallet_requests",  lambda r: len(r) >= 2 and r[1] != username)
        _filter("profile_requests", lambda r: len(r) >= 2 and r[1] != username)
        _filter("message_sessions", lambda s: len(s) >= 2 and s[1] != username)
        _filter("message_status",   lambda s: len(s) >= 1 and s[0] != username)

        messages = []
        for row in read_table(FILES["messages"]):
            if not row:
                continue
            msg = parse_message(row)
            if msg and (msg["sender"] == username or msg["receiver"] == username):
                continue
            messages.append(row)
        write_table(FILES["messages"], messages)

        self.refresh_users()
        messagebox.showinfo("Success", f"User '{username}' and all related data deleted.")
