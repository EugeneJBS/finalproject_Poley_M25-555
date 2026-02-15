from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

from valutatrade_hub.core.models import User, Portfolio
from valutatrade_hub.core.utils import load_json, save_json
from valutatrade_hub.infra.settings import get_settings


class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_paths()
        return cls._instance

    def _init_paths(self) -> None:
        settings = get_settings()
        self.users_file = Path(settings.get("USERS_FILE"))
        self.portfolios_file = Path(settings.get("PORTFOLIOS_FILE"))
        self.rates_file = Path(settings.get("RATES_FILE"))
        self.exchange_history_file = Path(
            settings.get("EXCHANGE_HISTORY_FILE")
        )

    def load_users(self) -> List[User]:
        # Безопасная загрузка из utils
        raw_data = load_json(self.users_file, [])
        # Распаковываем словарь в конструктор __init__ для создания объектов
        return [User(**item) for item in raw_data]

    def save_users(self, users: List[User]) -> None:
        # Метод to_dict() моделей и безопасное сохранение
        data = [u.to_dict() for u in users]
        save_json(self.users_file, data)

    # Получение конкретного пользователя (в usecases)
    def get_user_by_username(self, username: str) -> Optional[User]:
        users = self.load_users()
        for user in users:
            if user.username == username:
                return user
        return None

    def save_user(self, user: User) -> None:
        users = self.load_users()
        for i, u in enumerate(users):
            if u.user_id == user.user_id:
                users[i] = user
                break
        else:
            users.append(user)
        self.save_users(users)

    def load_portfolios(self) -> List[Portfolio]:
        raw_data = load_json(self.portfolios_file, [])
        # Создаем объекты через конструктор
        return [Portfolio(**item) for item in raw_data]

    def save_portfolios(self, portfolios: List[Portfolio]) -> None:
        data = [p.to_dict() for p in portfolios]
        save_json(self.portfolios_file, data)

    def get_portfolio_by_user_id(self, user_id: int) -> Optional[Portfolio]:
        portfolios = self.load_portfolios()
        for p in portfolios:
            if p.user_id == user_id:
                return p
        return None

    def save_portfolio(self, portfolio: Portfolio) -> None:
        portfolios = self.load_portfolios()
        found = False
        for i, p in enumerate(portfolios):
            if p.user_id == portfolio.user_id:
                portfolios[i] = portfolio
                found = True
                break
        if not found:
            portfolios.append(portfolio)
        self.save_portfolios(portfolios)

    def load_rates_snapshot(self) -> dict:
        return load_json(self.rates_file, {"pairs": {}, "last_refresh": None})

    def save_rates_snapshot(self, data: dict) -> None:
        save_json(self.rates_file, data)

    # Алиас для совместимости с usecases
    def get_rates_snapshot(self) -> dict:
        return self.load_rates_snapshot()

    def append_exchange_record(self, record: dict) -> None:
        history = load_json(self.exchange_history_file, [])
        history.append(record)
        save_json(self.exchange_history_file, history)


def get_db() -> DatabaseManager:
    return DatabaseManager()