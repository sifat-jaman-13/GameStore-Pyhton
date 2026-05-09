import os

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(APP_DIR, "data")

FILES = {
    "users":           os.path.join(DATA_DIR, "users.txt"),
    "games":           os.path.join(DATA_DIR, "games.txt"),
    "categories":      os.path.join(DATA_DIR, "categories.txt"),
    "cart":            os.path.join(DATA_DIR, "cart.txt"),
    "purchases":       os.path.join(DATA_DIR, "purchases.txt"),
    "wallet_requests": os.path.join(DATA_DIR, "wallet_requests.txt"),
    "profile_requests": os.path.join(DATA_DIR, "profile_requests.txt"),
    "messages":        os.path.join(DATA_DIR, "messages.txt"),
    "message_sessions": os.path.join(DATA_DIR, "message_sessions.txt"),
    "message_status":  os.path.join(DATA_DIR, "message_status.txt"),
    "admin":           os.path.join(DATA_DIR, "admin.txt"),
}

# users.txt row layout: username|password|email|phone|fullname|status|balance
# categories.txt row layout: category_name
# games.txt row layout:
# game_id|name|category|price|discount_percent|developer|publisher|company|release_year
# cart.txt row layout: username|game_id
# purchases.txt row layout: username|game_id
# wallet_requests.txt row layout: req_id|username|amount|bkash|trx_id|status
# profile_requests.txt row layout: req_id|username|new_fullname|new_username|status
# messages.txt row layout: msg_id|session_id|sender|receiver|text|read_status
# old messages.txt rows are still supported as: msg_id|sender|receiver|text|read_status
# message_sessions.txt row layout: session_id|username|title|status
# message_status.txt row layout: username|status
# admin.txt row layout: username|password

CATEGORIES = [
    "All",
    "Action",
    "Action RPG",
    "Adventure",
    "Arcade",
    "Atmospheric",
    "Battle Royale",
    "Casual",
    "Co-op",
    "Competitive",
    "Early Access",
    "Educational",
    "Family Friendly",
    "Fantasy",
    "Fighting",
    "Free to Play",
    "Hack and Slash",
    "Horror",
    "Indie",
    "MMO",
    "Multiplayer",
    "Mystery",
    "Open World",
    "Party",
    "Platformer",
    "Puzzle",
    "Racing",
    "Retro",
    "Roguelike",
    "RPG",
    "Sandbox",
    "Sci-Fi",
    "Shooter",
    "Simulation",
    "Single Player",
    "Sports",
    "Stealth",
    "Story Rich",
    "Strategy",
    "Survival",
    "Tactical",
    "VR",
]
STATUSES = ["ACTIVE", "DISABLED", "BANNED"]
SEPARATOR = "|"
