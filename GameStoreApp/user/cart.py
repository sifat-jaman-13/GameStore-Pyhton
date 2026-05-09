import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.file_handler import read_table, write_table, append_row
from core.constants import FILES
from core.catalog import game_meta_text, game_price_text, get_game_price
from core.utils import fmt_price, normalize_balance


class CartFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.username = self.controller.session.current_user
        self.cart_total = 0.0

        self.cart_scroll = ctk.CTkScrollableFrame(self)
        self.cart_scroll.pack(fill="both", expand=True, padx=50, pady=(20, 10))

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", side="bottom", pady=20, padx=50)

        self.total_label = ctk.CTkLabel(bottom, text="Total: ৳0",
                                        font=("Arial", 18, "bold"))
        self.total_label.pack(side="left", padx=20)

        ctk.CTkButton(bottom, text="Checkout", width=150, height=45,
                      font=("Arial", 14, "bold"),
                      fg_color="#00cc66", hover_color="#00994c",
                      command=self.checkout).pack(side="right", padx=20)

        self.refresh_cart()

    def refresh_cart(self):
        for w in self.cart_scroll.winfo_children():
            w.destroy()

        cart = read_table(FILES["cart"])
        games_db = {g[0]: g for g in read_table(FILES["games"]) if len(g) >= 4}

        self.cart_total = 0.0
        has_items = False

        for c in cart:
            if len(c) < 2 or c[0] != self.username or c[1] not in games_db:
                continue
            has_items = True
            g = games_db[c[1]]
            price = get_game_price(g)
            self.cart_total += price

            frame = ctk.CTkFrame(self.cart_scroll, fg_color="#2b2b2b", corner_radius=8)
            frame.pack(fill="x", pady=8, padx=5)

            info = f"{g[1]}  |  {game_price_text(g, fmt_price)}"
            details = ctk.CTkFrame(frame, fg_color="transparent")
            details.pack(side="left", padx=15, pady=10, expand=True, fill="x")
            ctk.CTkLabel(details, text=info,
                         font=("Arial", 13, "bold")).pack(anchor="w")
            meta = game_meta_text(g)
            if meta:
                ctk.CTkLabel(details, text=meta,
                             font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

            ctk.CTkButton(frame, text="Remove", width=90, height=35,
                          font=("Arial", 12),
                          fg_color="#cc0000", hover_color="#990000",
                          command=lambda gid=c[1]: self.remove_from_cart(gid)).pack(
                side="right", padx=5, pady=5)

        if not has_items:
            ctk.CTkLabel(self.cart_scroll, text="Your cart is empty.",
                         font=("Arial", 24), text_color="gray").pack(pady=50)

        self.total_label.configure(text=f"Total: ৳{fmt_price(self.cart_total)}")

    def remove_from_cart(self, game_id):
        cart = read_table(FILES["cart"])
        new_cart = [c for c in cart
                    if not (len(c) >= 2 and c[0] == self.username and c[1] == game_id)]
        write_table(FILES["cart"], new_cart)
        self.refresh_cart()

    def checkout(self):
        cart = read_table(FILES["cart"])
        user_cart = [c for c in cart if len(c) >= 2 and c[0] == self.username]
        if not user_cart:
            messagebox.showwarning("Warning", "Your cart is empty.")
            return

        # FIX: build games_db NOW so we can detect deleted games at checkout time.
        # Previously every cart item was blindly added to purchases even if the game
        # had been deleted by the admin after it was added to the cart.
        games_db = {g[0]: g for g in read_table(FILES["games"]) if len(g) >= 4}

        # Separate valid items from stale (deleted) ones
        valid_cart = [c for c in user_cart if c[1] in games_db]
        stale_cart = [c for c in user_cart if c[1] not in games_db]

        if stale_cart:
            # Silently remove stale entries and warn the user
            all_cart = read_table(FILES["cart"])
            stale_ids = {c[1] for c in stale_cart}
            cleaned = [c for c in all_cart
                       if not (len(c) >= 2 and c[0] == self.username and c[1] in stale_ids)]
            write_table(FILES["cart"], cleaned)
            messagebox.showwarning(
                "Cart Updated",
                f"{len(stale_cart)} item(s) in your cart were removed by the store and "
                "have been taken out of your cart.")
            self.refresh_cart()
            if not valid_cart:
                return

        # Recalculate total using only valid items (prices may have changed)
        total = sum(get_game_price(games_db[c[1]]) for c in valid_cart)

        users = read_table(FILES["users"])
        user_idx = -1
        user_bal = 0.0
        for i, u in enumerate(users):
            if len(u) >= 7 and u[0] == self.username:
                try:
                    user_bal = float(u[6])
                except ValueError:
                    user_bal = 0.0
                user_idx = i
                break

        if user_idx == -1:
            messagebox.showerror("Error", "User not found.")
            return

        if user_bal < total:
            messagebox.showerror(
                "Error",
                f"Insufficient funds. You need ৳{fmt_price(total)} but have ৳{fmt_price(user_bal)}.")
            return

        # Deduct balance (FIX: use normalize_balance for consistent storage format)
        users[user_idx][6] = normalize_balance(user_bal - total)
        write_table(FILES["users"], users)

        # Move valid cart items to purchases
        all_cart = read_table(FILES["cart"])
        valid_ids = {c[1] for c in valid_cart}
        new_cart = []
        for c in all_cart:
            if len(c) >= 2 and c[0] == self.username and c[1] in valid_ids:
                append_row(FILES["purchases"], [self.username, c[1]])
            else:
                new_cart.append(c)
        write_table(FILES["cart"], new_cart)

        messagebox.showinfo("Success", "Checkout successful! Games added to your Library.")
        self.refresh_cart()
