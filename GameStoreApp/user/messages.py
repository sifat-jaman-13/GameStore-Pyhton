import os
import time
import customtkinter as ctk
from core.file_handler import append_row, sanitize
from core.constants import FILES
from core.message_utils import (
    ADMIN,
    DONE,
    OPEN,
    UNREAD,
    create_session,
    get_session_messages,
    get_session_status,
    get_sessions,
    mark_all_read,
    mark_conversation_read,
    set_session_status,
    ticket_session_title,
)


class MessagesFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.username = self.controller.session.current_user
        self.session_map = {}
        self.current_session_id = None
        self._message_count = 0
        self._last_messages_mtime = 0.0
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=50, pady=(18, 8))

        ctk.CTkLabel(top, text="Support Messages",
                     font=("Arial", 18, "bold")).pack(side="left")

        ctk.CTkButton(top, text="New Message", width=120, height=34,
                      font=("Arial", 12, "bold"),
                      command=self.start_new_session).pack(side="right")

        ctk.CTkButton(top, text="Mark All Read", width=120, height=34,
                      font=("Arial", 12, "bold"),
                      fg_color="#4b5563", hover_color="#374151",
                      command=self.mark_all_messages_read).pack(side="right", padx=(0, 10))

        self.session_var = ctk.StringVar(value="No sessions")
        self.session_menu = ctk.CTkOptionMenu(top, variable=self.session_var,
                                              values=["No sessions"],
                                              width=220, height=34,
                                              command=self.load_session_by_title)
        self.session_menu.pack(side="right", padx=10)

        self.status_lbl = ctk.CTkLabel(self, text="", font=("Arial", 12, "bold"))
        self.status_lbl.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        self.msg_scroll = ctk.CTkScrollableFrame(self)
        self.msg_scroll.grid(row=2, column=0, sticky="nsew", padx=50, pady=(10, 10))

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="ew", padx=50, pady=(0, 18))
        bottom.grid_columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(bottom,
                                      placeholder_text="",
                                      height=40, font=("Arial", 12))
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.msg_entry.bind("<Return>", lambda _event: self.send_message())

        self.send_btn = ctk.CTkButton(bottom, text="Send", width=120, height=40,
                                      font=("Arial", 12, "bold"),
                                      command=self.send_message)
        self.send_btn.grid(row=0, column=1, sticky="e")

        self.refresh_messages(mark_read=False)
        self.after(500, self.poll_live_messages)

    def refresh_messages(self, mark_read=True):
        self.refresh_sessions()
        self.load_session(self.current_session_id, mark_read=mark_read)
        self._last_messages_mtime = self.messages_file_mtime()

    def refresh_sessions(self):
        sessions = get_sessions(self.username)
        if not sessions:
            self.session_map = {}
            self.current_session_id = None
            self.session_menu.configure(values=["No sessions"])
            self.session_var.set("No sessions")
            return

        self.session_map = {
            self.session_title(i, row): row[0]
            for i, row in enumerate(sessions, start=1)
        }
        values = list(self.session_map.keys())
        self.session_menu.configure(values=values)

        if self.current_session_id not in [row[0] for row in sessions]:
            self.current_session_id = sessions[-1][0]

        for title, session_id in self.session_map.items():
            if session_id == self.current_session_id:
                self.session_var.set(title)
                break

    def session_title(self, index, row):
        status = row[3] if len(row) >= 4 else OPEN
        return f"{ticket_session_title(self.username, index)} ({status.title()})"

    def load_session_by_title(self, title):
        self.current_session_id = self.session_map.get(title)
        self.load_session(self.current_session_id)

    def load_session(self, session_id, mark_read=True):
        for w in self.msg_scroll.winfo_children():
            w.destroy()
        self.msg_scroll.grid_columnconfigure(0, weight=1)
        self._message_count = 0

        if not session_id:
            self.status_lbl.configure(text="Click New Message to contact admin.", text_color="#8f9aa3")
            self.send_btn.configure(text="Send", state="normal")
            ctk.CTkLabel(self.msg_scroll,
                         text="No messages yet. Start a new support message.",
                         font=("Arial", 20), text_color="gray").pack(pady=50)
            return

        self.send_btn.configure(state="normal")
        status = get_session_status(session_id, self.username)
        if status == DONE:
            self.status_lbl.configure(
                text="This support session is done. Click New Message to start another session.",
                text_color="#00cc66",
            )
            self.msg_entry.configure(placeholder_text="")
            self.send_btn.configure(state="disabled")
        else:
            self.status_lbl.configure(text="Support session is open", text_color="#ffaa00")
            self.msg_entry.configure(placeholder_text="")

        messages = get_session_messages(session_id, self.username)
        for index, msg in enumerate(messages):
            self.add_message_bubble(index, msg)
        self._message_count = len(messages)

        if mark_read:
            mark_conversation_read(self.username, ADMIN, session_id)

        if not messages:
            ctk.CTkLabel(self.msg_scroll,
                         text="No messages in this session yet.",
                         font=("Arial", 20), text_color="gray").pack(pady=50)

    def start_new_session(self):
        self.current_session_id = create_session(self.username)
        self.refresh_messages()
        self.msg_entry.focus()

    def add_message_bubble(self, index, msg):
        is_from_user = msg["sender"] == self.username
        sender = "You" if is_from_user else "Admin"
        color = "#2b2b2b" if is_from_user else "#1f538d"
        align = "e" if is_from_user else "w"

        wrap = ctk.CTkFrame(self.msg_scroll, fg_color="transparent")
        wrap.grid(row=index, column=0, sticky="ew", pady=5, padx=10)
        bubble = ctk.CTkFrame(wrap, fg_color=color, corner_radius=10)
        bubble.pack(anchor=align, padx=12)
        ctk.CTkLabel(bubble, text=f"{sender}:\n{msg['text']}",
                     font=("Arial", 12), justify="left",
                     anchor="w", wraplength=520,
                     padx=15, pady=10).pack(fill="both")

    def messages_file_mtime(self):
        try:
            return os.path.getmtime(FILES["messages"])
        except OSError:
            return 0.0

    def poll_live_messages(self):
        if not self.winfo_exists():
            return
        dashboard = getattr(self.controller, "dashboard", None)
        is_messages_tab = bool(dashboard and dashboard.tabview.get() == "Messages")
        current_mtime = self.messages_file_mtime()
        if is_messages_tab and current_mtime != self._last_messages_mtime:
            self.refresh_messages()
        self.after(500, self.poll_live_messages)

    def send_message(self):
        text = sanitize(self.msg_entry.get().strip())
        if not text:
            return
        is_new_session = not self.current_session_id
        if not self.current_session_id:
            self.current_session_id = create_session(self.username)

        msg_id = str(time.time_ns())
        set_session_status(self.current_session_id, self.username, OPEN)
        append_row(FILES["messages"],
                   [msg_id, self.current_session_id, self.username, ADMIN, text, UNREAD])
        self.msg_entry.delete(0, 'end')
        self._last_messages_mtime = self.messages_file_mtime()
        if is_new_session:
            self.refresh_messages(mark_read=False)
        else:
            self.add_message_bubble(self._message_count, {
                "id": msg_id,
                "session_id": self.current_session_id,
                "sender": self.username,
                "receiver": ADMIN,
                "text": text,
                "read_status": UNREAD,
            })
            self._message_count += 1
        self.msg_entry.focus()

    def mark_all_messages_read(self):
        mark_all_read(self.username)
        self.refresh_messages(mark_read=False)
