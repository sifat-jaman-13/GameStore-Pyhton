import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.file_handler import read_table, write_table
from core.constants import FILES


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")

        self.title_colors = ["#e5f0ff", "#93c5fd", "#38bdf8", "#60a5fa", "#e5f0ff"]
        self.title_color_index = 0
        title_wrap = ctk.CTkFrame(self.center_container, fg_color="transparent",
                                  width=360, height=72)
        title_wrap.pack(pady=(0, 28))
        title_wrap.pack_propagate(False)

        self.title_shadow = ctk.CTkLabel(title_wrap, text="ScarZero Game Store",
                                         font=("Arial", 29, "bold"),
                                         text_color="#0f172a")
        self.title_shadow.place(relx=0.5, rely=0.35, anchor="center", x=2, y=2)

        self.title_label = ctk.CTkLabel(title_wrap, text="ScarZero Game Store",
                                        font=("Arial", 29, "bold"),
                                        text_color=self.title_colors[0])
        self.title_label.place(relx=0.5, rely=0.35, anchor="center")

        self.title_accent = ctk.CTkFrame(title_wrap, width=180, height=3,
                                         fg_color="#38bdf8", corner_radius=2)
        self.title_accent.place(relx=0.5, rely=0.82, anchor="center")
        self.animate_title()

        self.user_entry = ctk.CTkEntry(self.center_container, placeholder_text="Username",
                                       height=40, font=("Arial", 13))
        self.user_entry.pack(pady=10, fill="x", padx=20)

        self.pass_entry = ctk.CTkEntry(self.center_container, placeholder_text="Password",
                                       show="*", height=40, font=("Arial", 13))
        self.pass_entry.pack(pady=10, fill="x", padx=20)

        self.show_pass_var = ctk.IntVar()
        self.show_checkbox = ctk.CTkCheckBox(self.center_container, text="Show Password",
                                             font=("Arial", 12),
                                             variable=self.show_pass_var,
                                             command=self.toggle_password)
        self.show_checkbox.pack(pady=5, anchor="w", padx=20)

        ctk.CTkButton(self.center_container, text="Login", command=self.login,
                      height=40, font=("Arial", 13, "bold")).pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(self.center_container, text="New User? Register Now",
                      fg_color="transparent", hover_color="#333333",
                      font=("Arial", 12),
                      command=self.controller.show_register).pack(pady=5)

    def toggle_password(self):
        self.pass_entry.configure(show="" if self.show_pass_var.get() == 1 else "*")

    def animate_title(self):
        if not self.winfo_exists():
            return
        color = self.title_colors[self.title_color_index]
        self.title_label.configure(text_color=color)
        self.title_accent.configure(fg_color=color)
        self.title_color_index = (self.title_color_index + 1) % len(self.title_colors)
        self.after(550, self.animate_title) # noqa

    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return

        users = read_table(FILES["users"])
        changed = False

        for user in users:
            if len(user) < 7:
                continue
            if user[0] == username and user[1] == password:
                status = user[5]
                if status == "TIMEOUT":
                    user[5] = "ACTIVE"
                    if len(user) > 7:
                        user[7] = ""
                    changed = True
                    status = "ACTIVE"
                if changed:
                    write_table(FILES["users"], users)
                if status in ("BANNED", "DISABLED"):
                    messagebox.showerror("Access Denied", f"Account is {status}.")
                    return
                self.controller.show_user_dashboard(username)
                return

        messagebox.showerror("Error", "Invalid credentials.")
