import json

from sqlmodel import select

from app.src.database.db import db
from app.src.models.payment import PaymentMethod
from app.src.models.setting import Setting

DEFAULT_SETTINGS = {
    "business_name": "SwiftPOS",
    "business_tagline": "Retail & Point of Sale",
    "currency": "UGX",
    "receipt_footer": "Thank you for shopping with us.",
    "low_stock_default": "5",
    "vat_rate": "0",
}


class SettingsService:
    @staticmethod
    def get_setting(key: str, default: str = "") -> str:
        with next(db.get_session()) as session:
            setting = session.get(Setting, key)
            return setting.value if setting else default

    @staticmethod
    def set_setting(key: str, value: str) -> None:
        with next(db.get_session()) as session:
            setting = session.get(Setting, key)
            if setting:
                setting.value = value
            else:
                setting = Setting(key=key, value=value)
            session.add(setting)
            session.commit()

    @staticmethod
    def all_settings() -> dict[str, str]:
        with next(db.get_session()) as session:
            return {s.key: s.value for s in session.exec(select(Setting)).all()}

    @staticmethod
    def save_batch(values: dict[str, str]) -> None:
        with next(db.get_session()) as session:
            for key, value in values.items():
                setting = session.get(Setting, key)
                if setting:
                    setting.value = value
                else:
                    session.add(Setting(key=key, value=value))
            session.commit()


class PaymentMethodService:
    @staticmethod
    def list_methods() -> list[PaymentMethod]:
        with next(db.get_session()) as session:
            return session.exec(
                select(PaymentMethod).order_by(PaymentMethod.name)
            ).all()

    @staticmethod
    def create_method(name: str, code: str, is_cash: bool) -> tuple[bool, str]:
        name = name.strip()
        code = code.strip().upper()
        if not name or not code:
            return False, "Name and code are required."
        with next(db.get_session()) as session:
            existing = session.exec(
                select(PaymentMethod).where(
                    (PaymentMethod.code == code) | (PaymentMethod.name == name)
                )
            ).first()
            if existing:
                return False, "A payment method with this name or code already exists."
            session.add(PaymentMethod(name=name, code=code, is_cash=is_cash))
            session.commit()
        return True, "Payment method added."

    @staticmethod
    def update_method(method_id: int, name: str, is_active: bool, is_cash: bool) -> tuple[bool, str]:
        name = name.strip()
        if not name:
            return False, "Name is required."
        with next(db.get_session()) as session:
            method = session.get(PaymentMethod, method_id)
            if not method:
                return False, "Payment method not found."
            method.name = name
            method.is_active = is_active
            method.is_cash = is_cash
            session.add(method)
            session.commit()
        return True, "Payment method updated."

    @staticmethod
    def toggle_active(method_id: int) -> tuple[bool, str]:
        with next(db.get_session()) as session:
            method = session.get(PaymentMethod, method_id)
            if not method:
                return False, "Payment method not found."
            method.is_active = not method.is_active
            session.add(method)
            session.commit()
            return True, f"Payment method {'activated' if method.is_active else 'deactivated'}."

    @staticmethod
    def delete_method(method_id: int) -> tuple[bool, str]:
        with next(db.get_session()) as session:
            method = session.get(PaymentMethod, method_id)
            if not method:
                return False, "Payment method not found."
            session.delete(method)
            session.commit()
        return True, "Payment method deleted."

    @staticmethod
    def external_providers_configured() -> int:
        """Number of methods carrying a provider config (non-secret, e.g. 'momo').

        Live providers are a Phase 2 concern; this simply reports how many
        methods have a runtime provider hint attached.
        """
        count = 0
        for method in PaymentMethodService.list_methods():
            if method.configuration:
                try:
                    config = json.loads(method.configuration)
                except (TypeError, ValueError):
                    config = {}
                if config.get("provider"):
                    count += 1
        return count