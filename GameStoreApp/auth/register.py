import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.file_handler import append_row, sanitize
from core.constants import FILES
from auth.validation import validate_registration


class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.frame, text="Create ScarZero Game Store Account",
                     font=("Arial", 28, "bold")).pack(pady=(0, 20))

        self.entries = {}
        fields = ["Full Name", "Username", "Email", "Phone", "Password", "Confirm Password"]
        for f in fields:
            is_pass = ("Password" in f)
            entry = ctk.CTkEntry(self.frame, placeholder_text=f, height=40,
                                 font=("Arial", 13), show="*" if is_pass else "")
            entry.pack(pady=6, fill="x", padx=20)
            self.entries[f] = entry

        self.show_pass_var = ctk.IntVar()
        self.show_checkbox = ctk.CTkCheckBox(self.frame, text="Show Passwords",
                                             font=("Arial", 12),
                                             variable=self.show_pass_var,
                                             command=self.toggle_password)
        self.show_checkbox.pack(pady=8, anchor="w", padx=20)

        ctk.CTkButton(self.frame, text="Register", command=self.handle_register,
                      height=40, font=("Arial", 13, "bold")).pack(pady=12, fill="x", padx=20)
        ctk.CTkButton(self.frame, text="Back to Login", fg_color="transparent",
                      font=("Arial", 12),
                      command=self.controller.show_login).pack(pady=5)

    def toggle_password(self):
        show_char = "" if self.show_pass_var.get() == 1 else "*"
        for field in ["Password", "Confirm Password"]:
            if field in self.entries:
                self.entries[field].configure(show=show_char)

    def handle_register(self):
        name = sanitize(self.entries["Full Name"].get().strip())
        username = sanitize(self.entries["Username"].get().strip())
        email = sanitize(self.entries["Email"].get().strip())
        phone = sanitize(self.entries["Phone"].get().strip())
        password = sanitize(self.entries["Password"].get().strip())
        confirm = sanitize(self.entries["Confirm Password"].get().strip())

        if not all([name, username, email, phone, password, confirm]):
            messagebox.showerror("Error", "All fields are required.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match. Please try again.")
            return

        is_valid, msg = validate_registration(username, email, phone, password, name)
        if not is_valid:
            messagebox.showerror("Error", msg)
            return

        # users.txt: username|password|email|phone|fullname|status|balance
        append_row(FILES["users"],
                   [username, password, email, phone, name, "ACTIVE", "0"])
        messagebox.showinfo("Success", "Signed up successfully. Click here to login.")
        self.controller.show_login()
