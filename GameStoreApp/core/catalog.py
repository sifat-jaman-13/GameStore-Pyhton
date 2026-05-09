from core.constants import CATEGORIES, FILES
from core.file_handler import read_table, sanitize, write_table


def get_categories(include_all=False):
    categories = [c for c in CATEGORIES if include_all or c != "All"]
    for row in read_table(FILES["categories"]):
        if not row:
            continue
        category = row[0].strip()
        if category and category not in categories and category != "All":
            categories.append(category)
    return (["All"] + [c for c in categories if c != "All"]) if include_all else categories


def add_category(category):
    category = sanitize(category.strip())
    if not category or category == "All":
        return False, "Enter a valid category name."

    categories = get_categories()
    if category.lower() in [c.lower() for c in categories]:
        return False, "Category already exists."

    write_table(FILES["categories"], [[c] for c in categories + [category]])
    return True, "Category added."


def get_game_price(game):
    try:
        price = float(game[3])
    except (IndexError, TypeError, ValueError):
        price = 0.0
    discount = get_game_discount(game)
    return max(0.0, price * (1 - discount / 100))


def get_game_discount(game):
    try:
        discount = float(game[4])
    except (IndexError, TypeError, ValueError):
        discount = 0.0
    return min(100.0, max(0.0, discount))


def game_price_text(game, fmt_price):
    original = get_raw_price(game)
    effective = get_game_price(game)
    discount = get_game_discount(game)

    if effective <= 0:
        return "Free"
    if discount > 0:
        return f"৳{fmt_price(effective)} ({discount}% off, was ৳{fmt_price(original)})"
    return f"৳{fmt_price(original)}"


def get_raw_price(game):
    try:
        return max(0.0, float(game[3]))
    except (IndexError, TypeError, ValueError):
        return 0.0


def get_game_field(game, index, default=""):
    try:
        value = game[index].strip()
    except (IndexError, AttributeError, TypeError):
        return default
    return value or default


def get_game_developer(game):
    return get_game_field(game, 5)


def get_game_publisher(game):
    return get_game_field(game, 6)


def get_game_company(game):
    return get_game_field(game, 7)


def get_game_release_year(game):
    return get_game_field(game, 8)


def game_meta_text(game):
    parts = []
    developer = get_game_developer(game)
    publisher = get_game_publisher(game)
    company = get_game_company(game)
    release_year = get_game_release_year(game)

    if developer:
        parts.append(f"Developer: {developer}")
    if publisher:
        parts.append(f"Publisher: {publisher}")
    if company:
        parts.append(f"Company: {company}")
    if release_year:
        parts.append(f"Release: {release_year}")

    return "  |  ".join(parts)
