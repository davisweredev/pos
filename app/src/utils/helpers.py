from datetime import datetime


def format_money(amount, currency: str = "UGX") -> str:
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0.0
    negative = amount < 0
    value = f"{abs(amount):,.2f}".rstrip("0").rstrip(".")
    return f"{'-' if negative else ''}{value} {currency}"


def format_short_number(amount, currency: str = "UGX") -> str:
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0.0
    if abs(amount) >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M {currency}"
    if abs(amount) >= 1_000:
        return f"{amount / 1_000:.1f}K {currency}"
    return f"{amount:.0f} {currency}"


def format_datetime(dt, fallback: str = "—") -> str:
    if not dt:
        return fallback
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except (AttributeError, ValueError):
        return fallback


def format_date(dt, fallback: str = "—") -> str:
    if not dt:
        return fallback
    try:
        return dt.strftime("%d %b %Y")
    except (AttributeError, ValueError):
        return fallback


def initials(name: str | None) -> str:
    if not name:
        return "?"
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def today_label() -> str:
    return datetime.now().strftime("%A, %d %B %Y")


def validate_number(raw: str, label: str, minimum: float = 0.0):
    """Validate a numeric input. Returns (ok, error|None)."""
    raw = (raw or "").strip()
    if not raw:
        return False, f"{label} is required."
    try:
        value = float(raw)
    except ValueError:
        return False, f"{label} must be a number."
    if value < minimum:
        return False, f"{label} cannot be negative." if minimum == 0 else f"{label} is too small."
    return True, None