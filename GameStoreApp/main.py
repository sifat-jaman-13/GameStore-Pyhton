import customtkinter as ctk
import config
from core.file_handler import init_db
from core.session import Session

from auth.login import LoginFrame
from auth.register import RegisterFrame
from user.dashboard import UserDashboard


class GameStoreApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(config.APP_TITLE)
        self.geometry(config.WINDOW_SIZE)
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)

        init_db()
        self.session = Session()

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_container()
        self.session.clear()
        LoginFrame(self.container, self)

    def show_register(self):
        self.clear_container()
        RegisterFrame(self.container, self)

    def show_user_dashboard(self, username):
        self.session.set_user(username)
        self.clear_container()
        UserDashboard(self.container, self)


if __name__ == "__main__":
    app = GameStoreApp()
    app.mainloop()
