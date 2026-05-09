import re
from core.file_handler import read_table
from core.constants import FILES


def validate_registration(username, email, phone, password, name):
    # Full Name: only letters, spaces, dots, apostrophes
    if not name:
        return False, "Full Name is required."
    if not re.match(r"^[a-zA-Z\s.']+$", name):
        return False, "Full Name can only contain letters, spaces, ( . ) and ( ' )."

    # Username: FIX — was only checked for empty. Now enforces length and
    # allowed characters. Spaces in usernames caused display issues and
    # could confuse the pipe-separated file format.
    if not username:
        return False, "Username is required."
    if not (3 <= len(username) <= 20):
        return False, "Username must be between 3 and 20 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores ( _ )."

    # Email: must contain @ and a dot
    if not email:
        return False, "Email is required."
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return False, "Email must contain '@' and '.' (e.g. user@example.com)."

    # Phone: exactly 11 digits, starts with 01
    if not phone:
        return False, "Phone is required."
    if not re.match(r"^\d{11}$", phone):
        return False, "Phone must be exactly 11 digits."
    if not phone.startswith("01"):
        return False, "Phone number must start with 01."

    # Password: min 4, max 16, standard keyboard characters
    if not password:
        return False, "Password is required."
    if not (4 <= len(password) <= 16):
        return False, "Password must be between 4 and 16 characters."
    if not re.match(r"^[\x20-\x7E]+$", password):
        return False, "Password contains invalid characters."

    # Check duplicates
    users = read_table(FILES["users"])
    for u in users:
        if len(u) < 4:
            continue
        if u[0].lower() == username.lower():
            return False, "Username already taken."
        if u[2] == email:
            return False, "Email already registered."
        if u[3] == phone:
            return False, "Phone already registered."

    return True, "Valid"
