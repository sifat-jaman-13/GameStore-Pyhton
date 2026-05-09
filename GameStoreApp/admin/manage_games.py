import customtkinter as ctk
import tkinter.messagebox as messagebox
import time
from core.file_handler import read_table, write_table, append_row, sanitize
from core.constants import FILES
from core.catalog import add_category, game_meta_text, game_price_text, get_categories
from core.utils import fmt_price


class ManageGamesFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        page = ctk.CTkScrollableFrame(self, fg_color="transparent")
        page.pack(fill="both", expand=True)

        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(20, 8))
        ctk.CTkLabel(header, text="Games Catalog",
                     font=("Arial", 22, "bold")).pack(anchor="w")
        ctk.CTkLabel(header,
                     text="Add categories, update prices, set discounts, and manage the catalog.",
                     font=("Arial", 12), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

        # -- Category card --
        category_card = ctk.CTkFrame(page, fg_color="#23272f", corner_radius=8)
        category_card.pack(fill="x", padx=50, pady=(8, 10))
        ctk.CTkLabel(category_card, text="Create Category",
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=18, pady=(14, 4))
        category_row = ctk.CTkFrame(category_card, fg_color="transparent")
        category_row.pack(fill="x", padx=18, pady=(0, 16))
        self.new_category_entry = ctk.CTkEntry(
            category_row, placeholder_text="Category name", height=38, font=("Arial", 13))
        self.new_category_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(category_row, text="Add Category", width=130, height=38,
                      font=("Arial", 12, "bold"),
                      command=self.create_category).pack(side="right", padx=(10, 0))

        # -- Add game form --
        form = ctk.CTkFrame(page, fg_color="#23272f", corner_radius=8)
        form.pack(fill="x", padx=50, pady=(0, 18))
        ctk.CTkLabel(form, text="Add New Game",
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=18, pady=(14, 0))

        self.name_entry = ctk.CTkEntry(form, placeholder_text="Game Name",
                                       height=40, font=("Arial", 13))
        self.name_entry.pack(pady=(18, 8), fill="x", padx=18)

        self.category_var = ctk.StringVar(value="Action")
        self.category_menu = ctk.CTkOptionMenu(
            form, variable=self.category_var, values=get_categories(),
            height=40, font=("Arial", 12))
        self.category_menu.pack(pady=8, fill="x", padx=18)

        self.price_entry = ctk.CTkEntry(form, placeholder_text="Price in Taka (e.g. 599)",
                                        height=40, font=("Arial", 13))
        self.price_entry.pack(pady=8, fill="x", padx=18)

        self.discount_entry = ctk.CTkEntry(
            form, placeholder_text="Discount % (0-100, optional)",
            height=40, font=("Arial", 13))
        self.discount_entry.pack(pady=8, fill="x", padx=18)

        self.developer_entry = ctk.CTkEntry(
            form, placeholder_text="Developer (e.g. FromSoftware)",
            height=40, font=("Arial", 13))
        self.developer_entry.pack(pady=8, fill="x", padx=18)

        self.publisher_entry = ctk.CTkEntry(
            form, placeholder_text="Publisher (e.g. Bandai Namco Entertainment)",
            height=40, font=("Arial", 13))
        self.publisher_entry.pack(pady=8, fill="x", padx=18)

        self.company_entry = ctk.CTkEntry(
            form, placeholder_text="Company / Studio Group (optional)",
            height=40, font=("Arial", 13))
        self.company_entry.pack(pady=8, fill="x", padx=18)

        self.release_year_entry = ctk.CTkEntry(
            form, placeholder_text="Release Year (e.g. 2022)",
            height=40, font=("Arial", 13))
        self.release_year_entry.pack(pady=8, fill="x", padx=18)

        self.free_var = ctk.IntVar(value=0)
        ctk.CTkCheckBox(form, text="Make this game free", variable=self.free_var,
                        command=self.toggle_free,
                        font=("Arial", 12)).pack(anchor="w", padx=18, pady=(2, 8))

        ctk.CTkButton(form, text="Add Game", height=40,
                      font=("Arial", 13, "bold"),
                      command=self.add_game).pack(pady=(8, 18), fill="x", padx=18)

        ctk.CTkLabel(page, text="Current Games",
                     font=("Arial", 18, "bold")).pack(pady=(15, 10))

        self.scroll = ctk.CTkFrame(page, fg_color="transparent")
        self.scroll.pack(fill="x", padx=50, pady=(0, 20))

        self.refresh_games()

    def create_category(self):
        ok, msg = add_category(self.new_category_entry.get())
        if not ok:
            messagebox.showerror("Error", msg)
            return
        self.new_category_entry.delete(0, "end")
        self.refresh_category_menu()
        messagebox.showinfo("Done", msg)

    def refresh_category_menu(self):
        categories = get_categories()
        self.category_menu.configure(values=categories)
        if self.category_var.get() not in categories:
            self.category_var.set(categories[0] if categories else "Action")

    def toggle_free(self):
        # FIX: when "free" is toggled, set price=0 and discount=0 (not 100).
        # The effective price 0*(1-0/100)=0 is still correctly shown as "Free"
        # by game_price_text(). Using discount=100 was inconsistent because
        # add_game() then silently overrode it back to 0 anyway.
        if self.free_var.get():
            self.price_entry.delete(0, "end")
            self.price_entry.insert(0, "0")
            self.discount_entry.delete(0, "end")
            self.discount_entry.insert(0, "0")

    def add_game(self):
        name     = sanitize(self.name_entry.get().strip())
        cat      = self.category_var.get()
        price    = sanitize(self.price_entry.get().strip())
        discount = sanitize(self.discount_entry.get().strip() or "0")
        developer = sanitize(self.developer_entry.get().strip())
        publisher = sanitize(self.publisher_entry.get().strip())
        company = sanitize(self.company_entry.get().strip())
        release_year = sanitize(self.release_year_entry.get().strip())

        # Free checkbox always wins — clear both fields
        if self.free_var.get():
            price    = "0"
            discount = "0"

        if not name or not price:
            messagebox.showerror("Error", "Name and price are required.")
            return
        try:
            if float(price) < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Price must be a positive number.")
            return
        try:
            discount_value = float(discount)
            if discount_value < 0 or discount_value > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Discount must be between 0 and 100.")
            return
        if release_year:
            try:
                year_value = int(release_year)
                if year_value < 1970 or year_value > 2100:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Release year must be a valid year.")
                return

        game_id = str(int(time.time() * 1000))
        append_row(FILES["games"], [
            game_id, name, cat, price, discount,
            developer, publisher, company, release_year,
        ])
        self.name_entry.delete(0, "end")
        self.price_entry.delete(0, "end")
        self.discount_entry.delete(0, "end")
        self.developer_entry.delete(0, "end")
        self.publisher_entry.delete(0, "end")
        self.company_entry.delete(0, "end")
        self.release_year_entry.delete(0, "end")
        self.free_var.set(0)
        self.refresh_games()

    def refresh_games(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        games = read_table(FILES["games"])
        if not games:
            ctk.CTkLabel(self.scroll, text="No games yet.",
                         font=("Arial", 20), text_color="gray").pack(pady=20)
            return

        for g in games:
            if len(g) < 4:
                continue
            row = ctk.CTkFrame(self.scroll, fg_color="#23272f", corner_radius=8)
            row.pack(fill="x", pady=5, padx=5)

            details = ctk.CTkFrame(row, fg_color="transparent")
            details.pack(side="left", padx=15, pady=10, expand=True, fill="x")
            price_text = game_price_text(g, fmt_price)
            ctk.CTkLabel(details, text=f"{g[1]} ({g[2]}) - {price_text}",
                         font=("Arial", 13, "bold")).pack(anchor="w")
            meta = game_meta_text(g)
            if meta:
                ctk.CTkLabel(details, text=meta,
                             font=("Arial", 11), text_color="#9ca3af").pack(anchor="w", pady=(3, 0))

            ctk.CTkButton(row, text="Edit",
                          fg_color="#2563eb", hover_color="#1d4ed8",
                          width=70, height=35, font=("Arial", 12, "bold"),
                          command=lambda game=g: self.open_edit_game(game)).pack(
                side="right", padx=5, pady=5)
            ctk.CTkButton(row, text="Delete",
                          fg_color="#b30000", hover_color="#800000",
                          width=80, height=35, font=("Arial", 12, "bold"),
                          command=lambda i=g[0]: self.delete_game(i)).pack(
                side="right", padx=5, pady=5)

    def open_edit_game(self, game):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Edit Game - {game[1]}")
        popup.geometry("520x650")
        popup.resizable(False, False)

        ctk.CTkLabel(popup, text="Edit Game",
                     font=("Arial", 20, "bold")).pack(pady=(18, 8))
        body = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=8)

        name_var     = ctk.StringVar(value=game[1])
        category_var = ctk.StringVar(value=game[2])
        price_var    = ctk.StringVar(value=game[3])
        discount_var = ctk.StringVar(value=game[4] if len(game) >= 5 else "0")
        developer_var = ctk.StringVar(value=game[5] if len(game) >= 6 else "")
        publisher_var = ctk.StringVar(value=game[6] if len(game) >= 7 else "")
        company_var = ctk.StringVar(value=game[7] if len(game) >= 8 else "")
        release_year_var = ctk.StringVar(value=game[8] if len(game) >= 9 else "")
        # FIX: free if price is 0 (discount is irrelevant — price=0 is always free)
        free_var = ctk.IntVar(value=1 if price_var.get() in ("0", "0.0") else 0)

        ctk.CTkEntry(body, textvariable=name_var, height=40,
                     font=("Arial", 13)).pack(fill="x", pady=8)
        ctk.CTkOptionMenu(body, variable=category_var, values=get_categories(),
                          height=40, font=("Arial", 12)).pack(fill="x", pady=8)
        ctk.CTkEntry(body, textvariable=price_var, placeholder_text="Price in Taka",
                     height=40, font=("Arial", 13)).pack(fill="x", pady=8)
        ctk.CTkEntry(body, textvariable=discount_var, placeholder_text="Discount %",
                     height=40, font=("Arial", 13)).pack(fill="x", pady=8)
        ctk.CTkEntry(body, textvariable=developer_var, placeholder_text="Developer",
                     height=40, font=("Arial", 13)).pack(fill="x", pady=8)
        ctk.CTkEntry(body, textvariable=publisher_var, placeholder_text="Publisher",
                     height=40, font=("Arial", 13)).pack(fill="x", pady=8)
        ctk.CTkEntry(body, textvariable=company_var, placeholder_text="Company / Studio Group",
                     height=40, font=("Arial", 13)).pack(fill="x", pady=8)
        ctk.CTkEntry(body, textvariable=release_year_var, placeholder_text="Release Year",
                     height=40, font=("Arial", 13)).pack(fill="x", pady=8)

        def apply_free():
            # FIX: consistent with add_game — free means price=0, discount=0
            if free_var.get():
                price_var.set("0")
                discount_var.set("0")

        ctk.CTkCheckBox(body, text="Make this game free", variable=free_var,
                        command=apply_free, font=("Arial", 12)).pack(anchor="w", pady=8)

        def save():
            name     = sanitize(name_var.get().strip())
            price    = sanitize(price_var.get().strip())
            discount = sanitize(discount_var.get().strip() or "0")
            developer = sanitize(developer_var.get().strip())
            publisher = sanitize(publisher_var.get().strip())
            company = sanitize(company_var.get().strip())
            release_year = sanitize(release_year_var.get().strip())
            if free_var.get():
                price    = "0"
                discount = "0"
            if not name or not price:
                messagebox.showerror("Error", "Name and price are required.")
                return
            try:
                if float(price) < 0:
                    raise ValueError
                discount_num = float(discount)
                if discount_num < 0 or discount_num > 100:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Price must be positive and discount 0-100.")
                return
            if release_year:
                try:
                    year_value = int(release_year)
                    if year_value < 1970 or year_value > 2100:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Release year must be a valid year.")
                    return

            rows = read_table(FILES["games"])
            for index, row in enumerate(rows):
                if row and row[0] == game[0]:
                    rows[index] = [
                        game[0], name, category_var.get(), price, discount,
                        developer, publisher, company, release_year,
                    ]
                    break
            write_table(FILES["games"], rows)
            popup.destroy()
            self.refresh_games()

        ctk.CTkButton(body, text="Save Changes", height=40,
                      font=("Arial", 13, "bold"),
                      command=save).pack(fill="x", pady=(14, 8))

    def delete_game(self, game_id):
        if not messagebox.askyesno("Confirm", "Delete this game?"):
            return
        games = [g for g in read_table(FILES["games"]) if g and g[0] != game_id]
        write_table(FILES["games"], games)
        purchases = [p for p in read_table(FILES["purchases"]) if len(p) < 2 or p[1] != game_id]
        write_table(FILES["purchases"], purchases)
        cart = [c for c in read_table(FILES["cart"]) if len(c) < 2 or c[1] != game_id]
        write_table(FILES["cart"], cart)
        self.refresh_games()
