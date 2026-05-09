from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent / "GameStoreApp"
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR.parent))

import customtkinter as ctk
import config
from admin.admin_dashboard import AdminDashboard
from auth.admin_login import AdminLoginFrame
from core.file_handler import init_db
from core.session import Session


class AdminStoreApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(config.ADMIN_APP_TITLE)
        self.geometry(config.WINDOW_SIZE)
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)

        init_db()
        self.session = Session()

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_admin_login()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_admin_login(self):
        self.clear_container()
        self.session.clear()
        AdminLoginFrame(self.container, self)

    def show_admin_dashboard(self):
        self.session.set_admin()
        self.clear_container()
        AdminDashboard(self.container, self)


if __name__ == "__main__":
    app = AdminStoreApp()
    app.mainloop()
