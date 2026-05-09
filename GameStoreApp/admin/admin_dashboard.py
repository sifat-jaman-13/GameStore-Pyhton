import customtkinter as ctk
import config
from admin.manage_games import ManageGamesFrame
from admin.manage_users import ManageUsersFrame
from admin.wallet_requests import WalletRequestsFrame
from admin.profile_requests import ProfileRequestsFrame
from admin.admin_messages import ManageMessagesFrame
from admin.admin_settings import AdminSettingsFrame
from core.constants import FILES
from core.file_handler import read_table
from core.message_utils import count_unread


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)
        self._last_unread_notice = 0

        header = ctk.CTkFrame(self, fg_color="#1f232b", corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=config.ADMIN_APP_TITLE,
                     font=("Arial", 20, "bold")).pack(side="left", padx=24)
        ctk.CTkButton(header, text="Logout", width=100, height=34,
                      font=("Arial", 12, "bold"),
                      fg_color="#b42318", hover_color="#8f1d14",
                      command=self.controller.show_admin_login).pack(side="right", padx=22)

        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change,
                                      fg_color="#181b21",
                                      segmented_button_fg_color="#2b313b",
                                      segmented_button_selected_color="#2563eb",
                                      segmented_button_selected_hover_color="#1d4ed8")
        self.tabview.pack(fill="both", expand=True, padx=24, pady=20)
        # noinspection PyProtectedMember
        self.tabview._segmented_button.configure(font=("Arial", 12, "bold"))

        # Spec tabs: Dashboard, Games, Users, Wallet Requests, Profile Requests, Messages, Logout
        self.tabs = ["Dashboard", "Games", "Users", "Wallet Requests", "Profile Requests", "Messages", "Settings"]
        for t in self.tabs:
            self.tabview.add(t)

        self.build_dashboard()
        self.games_tab    = ManageGamesFrame(self.tabview.tab("Games"), self.controller)
        self.users_tab    = ManageUsersFrame(self.tabview.tab("Users"), self.controller)
        self.wallet_tab   = WalletRequestsFrame(self.tabview.tab("Wallet Requests"), self.controller)
        self.profile_requests_tab = ProfileRequestsFrame(self.tabview.tab("Profile Requests"), self.controller)
        self.messages_tab = ManageMessagesFrame(self.tabview.tab("Messages"), self.controller)
        self.settings_tab = AdminSettingsFrame(self.tabview.tab("Settings"), self.controller)
        self.after(300, self.poll_unread_messages) # noqa ignore warning

    def build_dashboard(self):
        tab = self.tabview.tab("Dashboard")
        wrap = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=70, pady=45)
        ctk.CTkLabel(wrap, text="ScarZero Game Store Admin Control Center",
                     font=("Arial", 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(wrap, text="Manage games, users, wallets, profile requests, and support messages.",
                     font=("Arial", 14), text_color="#9ca3af").pack(anchor="w", pady=(6, 24))

        stats = ctk.CTkFrame(wrap, fg_color="transparent")
        stats.pack(fill="x")
        self.games_count_label = None
        self.users_count_label = None
        self.support_status_label = None

        for title, color in [
            ("Games", "#22c55e"),
            ("Users", "#38bdf8"),
            ("Support", "#f59e0b"),
        ]:
            card = ctk.CTkFrame(stats, fg_color="#23272f", corner_radius=8)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            ctk.CTkLabel(card, text=title, font=("Arial", 13, "bold"),
                         text_color="#d7dde8").pack(anchor="w", padx=18, pady=(16, 4))
            value_label = ctk.CTkLabel(card, text="0", font=("Arial", 22, "bold"),
                                       text_color=color)
            value_label.pack(anchor="w", padx=18, pady=(0, 18))

            if title == "Games":
                self.games_count_label = value_label
            elif title == "Users":
                self.users_count_label = value_label
            else:
                self.support_status_label = value_label

        self.refresh_dashboard_stats()

    def refresh_dashboard_stats(self):
        games_count = sum(1 for g in read_table(FILES["games"]) if len(g) >= 4)
        users_count = sum(1 for u in read_table(FILES["users"]) if len(u) >= 7)

        if self.games_count_label is not None:
            self.games_count_label.configure(text=str(games_count))
        if self.users_count_label is not None:
            self.users_count_label.configure(text=str(users_count))
        if self.support_status_label is not None:
            self.support_status_label.configure(text="Live")

    def on_tab_change(self):
        current = self.tabview.get()
        if current == "Dashboard":        self.refresh_dashboard_stats()
        elif current == "Games":          self.games_tab.refresh_games()
        elif current == "Users":          self.users_tab.refresh_users()
        elif current == "Wallet Requests": self.wallet_tab.refresh_requests()
        elif current == "Profile Requests": self.profile_requests_tab.refresh_requests()
        elif current == "Messages":
            self.messages_tab.refresh_users()
            self._last_unread_notice = 0
        if current != "Messages":
            self.notify_unread_messages()

    def notify_unread_messages(self):
        unread = count_unread("ADMIN")
        if unread:
            self._last_unread_notice = unread

    def poll_unread_messages(self):
        if not self.winfo_exists():
            return
        if self.tabview.get() != "Messages":
            self.notify_unread_messages()
        self.after(1000, self.poll_unread_messages) # noqa ignore warning
