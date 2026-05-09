import os
from typing import List, Any
from core.constants import FILES, DATA_DIR, SEPARATOR, APP_DIR


def init_db() -> None:
    """Create the data folder and all required .txt files if missing."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for path in FILES.values():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("")

    migrate_legacy_data()


def migrate_legacy_data() -> None:
    """Merge rows from the old project-root data folder into the app data folder."""
    legacy_dir = os.path.join(os.path.dirname(APP_DIR), "data")
    if not os.path.isdir(legacy_dir) or os.path.abspath(legacy_dir) == os.path.abspath(DATA_DIR):
        return

    for key, target_path in FILES.items():
        legacy_path = os.path.join(legacy_dir, f"{key}.txt")
        if not os.path.exists(legacy_path):
            continue
        existing = read_table(target_path)
        existing_keys = {SEPARATOR.join(row) for row in existing}
        incoming = [
            row for row in read_table(legacy_path)
            if row and SEPARATOR.join(row) not in existing_keys
        ]
        if incoming:
            write_table(target_path, existing + incoming)


def read_table(path: str) -> List[List[str]]:
    """Read a pipe-separated file and return list[list[str]]. Skips blank lines."""

    if not os.path.exists(path):
        return []

    rows: List[List[str]] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")

            if not line.strip():
                continue

            rows.append(line.split(SEPARATOR))

    return rows


def write_table(path: str, rows: List[List[Any]]) -> None:
    """Write list[list[str]] back to file."""
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(SEPARATOR.join(str(c) for c in row) + "\n")


def append_row(path: str, row: List[Any]) -> None:
    """Append a single row."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(SEPARATOR.join(str(c) for c in row) + "\n")


def sanitize(value: Any) -> str:
    """Strip pipe character and newlines so they cannot corrupt the file format."""
    return str(value).replace(SEPARATOR, "").replace("\n", "").replace("\r", "")
