import customtkinter as ctk

class TitleLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        super().__init__(master, font=("Arial", 40, "bold"), **kwargs)

class LargeEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=500, height=50, font=("Arial", 22), **kwargs)

class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=500, height=50, font=("Arial", 22, "bold"), **kwargs)

class DangerButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=150, height=50, font=("Arial", 18, "bold"),
                         fg_color="#b30000", hover_color="#800000", **kwargs)
