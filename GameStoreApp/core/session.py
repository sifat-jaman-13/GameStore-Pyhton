class Session:
    """Tracks who is currently logged in (single-window app)."""

    def __init__(self):
        self.current_user = None
        self.is_admin = False

    def set_user(self, username):
        self.current_user = username
        self.is_admin = False

    def set_admin(self):
        self.current_user = "ADMIN"
        self.is_admin = True

    def clear(self):
        self.current_user = None
        self.is_admin = False
