import config
from core.constants import FILES
from core.file_handler import read_table, sanitize, write_table


def get_admin_credentials():
    rows = read_table(FILES["admin"])
    if rows and len(rows[0]) >= 2:
        return rows[0][0], rows[0][1]
    return config.ADMIN_USER, config.ADMIN_PASS


def save_admin_credentials(username, password):
    write_table(FILES["admin"], [[sanitize(username), sanitize(password)]])
