import customtkinter as ctk

from user.profile import ProfileFrame
from user.store import StoreFrame
from user.wallet import WalletFrame
from user.cart import CartFrame
from user.library import LibraryFrame
from user.messages import MessagesFrame
from core.catalog import game_meta_text, game_price_text
from core.constants import FILES
from core.file_handler import read_table
from core.message_utils import count_unread
from core.utils import fmt_price


POPULAR_GAMES = [
    ("GME-0001", "9.6", "Massive open-world RPG"),
    ("GME-0011", "9.7", "Choice-rich fantasy adventure"),
    ("GME-0003", "9.5", "Cinematic western open world"),
    ("GME-0036", "9.4", "Award-winning story RPG"),
    ("GME-0012", "9.3", "Fast roguelike action"),
    ("GME-0044", "9.1", "Festival racing favorite"),
    ("GME-0033", "9.4", "Classic co-op puzzle game"),
    ("GME-0016", "9.2", "Relaxed farming simulation"),
]


class UserDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.controller.dashboard = self
        self.pack(fill="both", expand=True)
        self._last_unread_notice = 0

        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        # noinspection PyProtectedMember
        self.tabview._segmented_button.configure(font=("Arial", 12, "bold"))

        self.tabs = ["Home", "Store", "Library", "Cart", "Wallet", "Profile", "Messages"]
        for t in self.tabs:
            self.tabview.add(t)

        ctk.CTkButton(self, text="Logout", width=100, height=35,
                      font=("Arial", 12, "bold"),
                      fg_color="#b30000", hover_color="#800000",
                      command=self.controller.show_login).place(relx=0.98, rely=0.02, anchor="ne")

        self.build_home()
        self.store_tab    = StoreFrame(self.tabview.tab("Store"), self.controller)
        self.wallet_tab   = WalletFrame(self.tabview.tab("Wallet"), self.controller)
        self.profile_tab  = ProfileFrame(self.tabview.tab("Profile"), self.controller)
        self.cart_tab     = CartFrame(self.tabview.tab("Cart"), self.controller)
        self.library_tab  = LibraryFrame(self.tabview.tab("Library"), self.controller)
        self.messages_tab = MessagesFrame(self.tabview.tab("Messages"), self.controller)
        self.after(300, self.poll_unread_messages) # noqa #ignore ide warning

    def build_home(self):
        tab = self.tabview.tab("Home")
        username = self.controller.session.current_user
        home = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        home.pack(fill="both", expand=True)

        ctk.CTkLabel(home, text=f"Welcome back, {username}!",
                     font=("Arial", 24, "bold")).pack(anchor="w", padx=50, pady=(28, 6))
        ctk.CTkLabel(home, text="Popular and top-rated games from the ScarZero catalog.",
                     font=("Arial", 13), text_color="#9ca3af").pack(anchor="w", padx=50, pady=(0, 18))

        featured = ctk.CTkFrame(home, fg_color="#23272f", corner_radius=8)
        featured.pack(fill="x", padx=50, pady=(0, 16))
        ctk.CTkLabel(featured, text="Featured Popular Pick",
                     font=("Arial", 13, "bold"), text_color="#38bdf8").pack(anchor="w", padx=18, pady=(16, 2))

        games = {g[0]: g for g in read_table(FILES["games"]) if len(g) >= 4}
        featured_game = games.get("GME-0001")
        if featured_game:
            ctk.CTkLabel(featured, text=featured_game[1],
                         font=("Arial", 22, "bold")).pack(anchor="w", padx=18, pady=(4, 4))
            ctk.CTkLabel(
                featured,
                text=f"{featured_game[2]}  |  Rating: 9.6/10  |  {game_price_text(featured_game, fmt_price)}",
                font=("Arial", 13),
                text_color="#d1d5db",
            ).pack(anchor="w", padx=18)
            meta = game_meta_text(featured_game)
            if meta:
                ctk.CTkLabel(featured, text=meta,
                             font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", padx=18, pady=(5, 16))

        ctk.CTkLabel(home, text="Popular Rated Games",
                     font=("Arial", 18, "bold")).pack(anchor="w", padx=50, pady=(8, 10))

        grid = ctk.CTkFrame(home, fg_color="transparent")
        grid.pack(fill="x", padx=50, pady=(0, 24))
        for col in range(2):
            grid.grid_columnconfigure(col, weight=1, uniform="popular")

        for index, (game_id, rating, tagline) in enumerate(POPULAR_GAMES):
            game = games.get(game_id)
            if not game:
                continue

            card = ctk.CTkFrame(grid, fg_color="#2b2b2b", corner_radius=8)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=6, pady=6)

            ctk.CTkLabel(card, text=game[1],
                         font=("Arial", 14, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
            ctk.CTkLabel(card, text=tagline,
                         font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", padx=14, pady=(0, 6))
            ctk.CTkLabel(
                card,
                text=f"{game[2]}  |  Rating: {rating}/10  |  {game_price_text(game, fmt_price)}",
                font=("Arial", 11, "bold"),
                text_color="#22c55e",
            ).pack(anchor="w", padx=14, pady=(0, 12))

    def on_tab_change(self):
        current = self.tabview.get()
        if current == "Cart":     self.cart_tab.refresh_cart()
        elif current == "Library": self.library_tab.refresh_library()
        elif current == "Wallet":
            self.wallet_tab.refresh_balance()
            self.wallet_tab.refresh_pending_requests()
        elif current == "Messages":
            self.messages_tab.refresh_messages()
            self._last_unread_notice = 0
        elif current == "Store":   self.store_tab.refresh_store()
        elif current == "Profile": self.profile_tab.refresh()
        if current != "Messages":
            self.notify_unread_messages()

    def notify_unread_messages(self):
        unread = count_unread(self.controller.session.current_user)
        if unread:
            self._last_unread_notice = unread

    def poll_unread_messages(self):
        if not self.winfo_exists():
            return
        if self.tabview.get() != "Messages":
            self.notify_unread_messages()
        self.after(1000, self.poll_unread_messages) # noqa #ignore ide warning
