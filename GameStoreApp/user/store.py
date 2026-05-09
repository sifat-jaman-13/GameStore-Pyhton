import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.file_handler import read_table, append_row
from core.constants import FILES
from core.catalog import game_meta_text, game_price_text, get_categories
from core.utils import fmt_price


class StoreFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=15, padx=50)

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(top_bar, textvariable=self.search_var,
                     placeholder_text="Search games...",
                     height=35, font=("Arial", 12)).pack(side="left", padx=5, fill="x", expand=True)

        ctk.CTkButton(top_bar, text="Search", command=self.refresh_store,
                      width=90, height=35, font=("Arial", 12, "bold")).pack(side="left", padx=5)

        self.cat_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(top_bar, variable=self.cat_var, values=get_categories(include_all=True),
                          command=lambda _: self.refresh_store(),
                          width=120, height=35, font=("Arial", 12)).pack(side="right", padx=5)

        self.store_scroll = ctk.CTkScrollableFrame(self)
        self.store_scroll.pack(fill="both", expand=True, padx=50, pady=10)

        self.refresh_store()

    def refresh_store(self):
        for w in self.store_scroll.winfo_children():
            w.destroy()

        username = self.controller.session.current_user
        games = read_table(FILES["games"])
        owned_ids = {
            p[1] for p in read_table(FILES["purchases"])
            if len(p) >= 2 and p[0] == username
        }
        cart_ids = {
            c[1] for c in read_table(FILES["cart"])
            if len(c) >= 2 and c[0] == username
        }
        search_q = self.search_var.get().lower()
        cat_q = self.cat_var.get()

        any_shown = False
        for g in games:
            if len(g) < 4:
                continue
            searchable = " ".join(g).lower()
            if search_q in searchable and (cat_q == "All" or cat_q == g[2]):
                any_shown = True
                frame = ctk.CTkFrame(self.store_scroll, fg_color="#2b2b2b", corner_radius=8)
                frame.pack(fill="x", pady=8, padx=5, ipady=0)

                info = f"{g[1]}  |  Genre: {g[2]}  |  Price: {game_price_text(g, fmt_price)}"
                details = ctk.CTkFrame(frame, fg_color="transparent")
                details.pack(side="left", padx=15, pady=10, expand=True, fill="x")
                ctk.CTkLabel(details, text=info,
                             font=("Arial", 13, "bold")).pack(anchor="w")
                meta = game_meta_text(g)
                if meta:
                    ctk.CTkLabel(details, text=meta,
                                 font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

                button_text = "Owned" if g[0] in owned_ids else "Added to Cart" if g[0] in cart_ids else "Add to Cart"
                button_state = "disabled" if g[0] in owned_ids or g[0] in cart_ids else "normal"
                add_button = ctk.CTkButton(frame, text=button_text, width=120, height=35,
                                           font=("Arial", 12), state=button_state)
                add_button.configure(command=lambda gid=g[0], btn=add_button: self.add_to_cart(gid, btn))
                add_button.pack(side="right", padx=5, pady=5)

        if not any_shown:
            ctk.CTkLabel(self.store_scroll, text="No games match your search.",
                         font=("Arial", 22), text_color="gray").pack(pady=50)

    def add_to_cart(self, game_id, button=None):
        username = self.controller.session.current_user

        for p in read_table(FILES["purchases"]):
            if len(p) >= 2 and p[0] == username and p[1] == game_id:
                if button is not None:
                    button.configure(text="Owned", state="disabled")
                messagebox.showinfo("Library", "You already own this game!")
                return

        for c in read_table(FILES["cart"]):
            if len(c) >= 2 and c[0] == username and c[1] == game_id:
                if button is not None:
                    button.configure(text="Added to Cart", state="disabled")
                messagebox.showinfo("Cart", "This game is already in your cart!")
                return

        append_row(FILES["cart"], [username, game_id])
        if button is not None:
            button.configure(text="Added to Cart", state="disabled")
        if hasattr(self.controller, "dashboard") and hasattr(self.controller.dashboard, "cart_tab"):
            self.controller.dashboard.cart_tab.refresh_cart()
        messagebox.showinfo("Success", "Game added to Cart!")
