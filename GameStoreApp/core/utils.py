def fmt_price(value):
    """Format a price for display in Taka."""
    try:
        f = float(value)
        if f.is_integer():
            return str(int(f))
        return f"{f:.2f}"
    except (TypeError, ValueError):
        return "0"


def normalize_balance(value):
    """
    Store balance as a clean string — integer string when whole, 2dp otherwise.
    FIX: prevents '50000.0' vs '50000' inconsistency across files.
    """
    try:
        f = float(value)
        return str(int(f)) if f.is_integer() else f"{f:.2f}"
    except (TypeError, ValueError):
        return "0"
