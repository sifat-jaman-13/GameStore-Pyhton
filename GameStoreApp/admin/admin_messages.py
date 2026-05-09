import time
import customtkinter as ctk
from core.file_handler import append_row, read_table, sanitize
from core.constants import FILES
from core.message_utils import (
    ADMIN,
    DONE,
    OPEN,
    UNREAD,
    get_session_messages,
    get_session_status,
    get_sessions,
    mark_all_read,
    mark_conversation_read,
    parse_message,
    set_session_status,
    ticket_session_title,
)


class ManageMessagesFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.session_map = {}
        self.current_session_id = None
        self.pack(fill="both", expand=True)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(20, 10), padx=50)
        ctk.CTkLabel(top, text="Admin Support",
                     font=("Arial", 22, "bold")).pack(side="left")

        self.status_lbl = ctk.CTkLabel(top, text="", font=("Arial", 12, "bold"))
        self.status_lbl.pack(side="left", padx=18)

        self.status_btn = ctk.CTkButton(top, text="Mark as Done",
                                        width=120, height=35,
                                        font=("Arial", 12, "bold"),
                                        command=self.toggle_status)
        self.status_btn.pack(side="right", padx=(10, 0))
        self.status_btn.configure(state="disabled")

        ctk.CTkButton(top, text="Mark All Read",
                      width=120, height=35,
                      font=("Arial", 12, "bold"),
                      fg_color="#4b5563", hover_color="#374151",
                      command=self.mark_all_messages_read).pack(side="right", padx=(10, 0))

        self.session_var = ctk.StringVar(value="Select Session")
        self.session_menu = ctk.CTkOptionMenu(top, variable=self.session_var,
                                              values=["Select Session"],
                                              width=210, height=35,
                                              command=self.load_session_by_title)
        self.session_menu.pack(side="right", padx=10)

        self.usr = ctk.StringVar(value="Select User")
        self.menu = ctk.CTkOptionMenu(top, variable=self.usr,
                                      values=["Select User"],
                                      width=170, height=35, font=("Arial", 12),
                                      command=lambda user: self.refresh_sessions(user))
        self.menu.pack(side="right")

        self.scr = ctk.CTkScrollableFrame(self)
        self.scr.pack(fill="both", expand=True, padx=50, pady=10)

        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", side="bottom", pady=20, padx=50)
        self.ent = ctk.CTkEntry(bot, placeholder_text="Reply...",
                                width=500, height=40, font=("Arial", 12))
        self.ent.pack(side="left", padx=10, expand=True, fill="x")
        self.ent.bind("<Return>", lambda _event: self.send_message())
        self.send_btn = ctk.CTkButton(bot, text="Send", width=100, height=40,
                                      font=("Arial", 12, "bold"),
                                      command=self.send_message)
        self.send_btn.pack(side="right")

        self.refresh_users(mark_read=False)

    def refresh_users(self, mark_read=True):
        users = set()
        for row in read_table(FILES["messages"]):
            msg = parse_message(row)
            if not msg:
                continue
            if msg["sender"] == ADMIN and msg["receiver"] != ADMIN:
                users.add(msg["receiver"])
            elif msg["receiver"] == ADMIN and msg["sender"] != ADMIN:
                users.add(msg["sender"])

        usr_list = sorted(users) if users else ["Select User"]
        self.menu.configure(values=usr_list)

        if self.usr.get() not in usr_list:
            self.usr.set(usr_list[0])
        self.refresh_sessions(self.usr.get(), mark_read=mark_read)

    def refresh_sessions(self, username, mark_read=True):
        self.session_map = {}
        self.current_session_id = None

        if username == "Select User":
            self.session_menu.configure(values=["Select Session"])
            self.session_var.set("Select Session")
            self.load_session(None)
            return

        sessions = get_sessions(username)
        if not sessions:
            self.session_menu.configure(values=["Select Session"])
            self.session_var.set("Select Session")
            self.load_session(None)
            return

        self.session_map = {
            self.session_title(i, row): row[0]
            for i, row in enumerate(sessions, start=1)
        }
        values = list(self.session_map.keys())
        self.session_menu.configure(values=values)
        self.current_session_id = sessions[-1][0]
        self.session_var.set(values[-1])
        self.load_session(self.current_session_id, mark_read=mark_read)

    def session_title(self, index, row):
        status = row[3] if len(row) >= 4 else OPEN
        username = row[1] if len(row) >= 2 else self.usr.get()
        return f"{ticket_session_title(username, index)} ({status.title()})"

    def load_session_by_title(self, title):
        self.current_session_id = self.session_map.get(title)
        self.load_session(self.current_session_id)

    def load_session(self, session_id, mark_read=True):
        for w in self.scr.winfo_children():
            w.destroy()
        self.scr.grid_columnconfigure(0, weight=1)

        username = self.usr.get()
        if not session_id or username == "Select User":
            self.status_lbl.configure(text="")
            self.status_btn.configure(text="Mark as Done", state="disabled")
            self.send_btn.configure(state="disabled")
            ctk.CTkLabel(self.scr, text="No conversations yet.",
                         font=("Arial", 20), text_color="gray").pack(pady=50)
            return

        self.send_btn.configure(state="normal")
        self.refresh_status_controls(username, session_id)
        messages = get_session_messages(session_id, username)

        for index, msg in enumerate(messages):
            adm = msg["sender"] == ADMIN
            is_unread = msg["receiver"] == ADMIN and msg["read_status"] == UNREAD
            f = ctk.CTkFrame(self.scr, fg_color="transparent")
            f.grid(row=index, column=0, sticky="ew", pady=5, padx=10)
            bubble = ctk.CTkFrame(
                f,
                fg_color="#2563eb" if adm else ("#3a3320" if is_unread else "#23272f"),
                corner_radius=8,
            )
            bubble.pack(anchor="e" if adm else "w", padx=12)
            ctk.CTkLabel(bubble, text=f"{'You' if adm else username}:\n{msg['text']}",
                         font=("Arial", 12), justify="left",
                         anchor="w", wraplength=520,
                         padx=15, pady=10).pack(fill="both")

        if mark_read:
            mark_conversation_read(ADMIN, username, session_id)

    def send_message(self):
        txt = sanitize(self.ent.get().strip())
        trg = self.usr.get()
        if not txt or trg == "Select User" or not self.current_session_id:
            return
        msg_id = str(time.time_ns())
        set_session_status(self.current_session_id, trg, OPEN)
        append_row(FILES["messages"], [msg_id, self.current_session_id, ADMIN, trg, txt, UNREAD])
        self.ent.delete(0, 'end')
        self.load_session(self.current_session_id)
        self.ent.focus()

    def refresh_status_controls(self, username, session_id):
        status = get_session_status(session_id, username)
        if status == DONE:
            self.status_lbl.configure(text="Status: Done", text_color="#00cc66")
            self.status_btn.configure(text="Reopen", state="normal")
        else:
            self.status_lbl.configure(text="Status: Open", text_color="#ffaa00")
            self.status_btn.configure(text="Mark as Done", state="normal")

    def toggle_status(self):
        username = self.usr.get()
        if username == "Select User" or not self.current_session_id:
            return
        current = get_session_status(self.current_session_id, username)
        set_session_status(self.current_session_id, username, OPEN if current == DONE else DONE)
        self.refresh_sessions(username)

    def mark_all_messages_read(self):
        mark_all_read(ADMIN)
        self.refresh_users(mark_read=False)
