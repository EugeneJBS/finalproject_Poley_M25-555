from datetime import datetime
from typing import Dict, Optional, Union, Any
from valutatrade_hub.core.utils import generate_salt, hash_password


class User:
    def __init__(
            self,
            user_id: int,
            username: str,
            password: Optional[str] = None,
            hashed_password: Optional[str] = None,
            salt: Optional[str] = None,
            registration_date: Union[datetime, str, None] = None
    ):
        self._user_id = int(user_id)
        # Установка имени с валидацией
        self.username = username

        # Обработка даты регистрации
        if registration_date:
            if isinstance(registration_date, str):
                self._registration_date = datetime.fromisoformat(registration_date)
            else:
                self._registration_date = registration_date
        else:
            self._registration_date = datetime.now()

        # Установка пароля или хеша
        if hashed_password and salt:
            self._salt = salt
            self._hashed_password = hashed_password
        elif password:
            if len(password) < 4:
                raise ValueError("Пароль должен быть не короче 4 символов")
            self._salt = generate_salt()
            self._hashed_password = hash_password(password, self._salt)
        else:
            raise ValueError("Требуется пароль или хеш+соль")

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        # Проверка на пустое имя
        if not value:
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def get_user_info(self) -> str:
        # Вывод публичной информации
        return f"ID: {self._user_id}, Name: {self._username}, Registered: {self._registration_date.isoformat()}"

    def change_password(self, new_password: str) -> None:
        # Смена пароля с генерацией новой соли
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._salt = generate_salt()
        self._hashed_password = hash_password(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        # Проверка совпадения пароля
        return hash_password(password, self._salt) == self._hashed_password

    def to_dict(self) -> dict:
        # Подготовка данных для сохранения
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code.upper()
        self.balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        # Проверка типа и знака баланса
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)

    def deposit(self, amount: float):
        # Пополнение кошелька
        if amount <= 0:
            raise ValueError("'amount' должен быть положительным числом")
        self.balance += float(amount)

    def withdraw(self, amount: float):
        # Снятие средств с проверкой остатка
        if amount <= 0:
            raise ValueError("'amount' должен быть положительным числом")
        if amount > self.balance:
            raise ValueError(f"Недостаточно средств: доступно {self.balance}, требуется {amount}")
        self.balance -= float(amount)

    def get_balance_info(self) -> str:
        return f"{self.currency_code}: {self.balance:.4f}"

    def to_dict(self) -> dict:
        return {
            "currency_code": self.currency_code,
            "balance": self.balance,
        }


class Portfolio:
    def __init__(self, user_id: int, wallets: Optional[Dict[str, Any]] = None):
        self._user_id = user_id
        self._wallets: Dict[str, Wallet] = {}

        # Инициализация кошельков из словаря или объектов
        if wallets:
            for code, data in wallets.items():
                if isinstance(data, dict):
                    self._wallets[code] = Wallet(code, data.get('balance', 0.0))
                elif isinstance(data, Wallet):
                    self._wallets[code] = data

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        # Возврат копии словаря кошельков
        return self._wallets.copy()

    def add_currency(self, currency_code: str) -> Wallet:
        # Добавление новой валюты
        code = currency_code.upper()
        if code in self._wallets:
            return self._wallets[code]
        wallet = Wallet(currency_code=code, balance=0.0)
        self._wallets[code] = wallet
        return wallet

    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        return self._wallets.get(currency_code.upper())

    def get_total_value(self, exchange_rates: dict, base_currency: str = "USD") -> float:
        # Расчет общей стоимости портфеля
        total = 0.0
        base = base_currency.upper()
        for code, wallet in self._wallets.items():
            if code == base:
                total += wallet.balance
                continue

            pair = f"{code}_{base}"
            rate_info = exchange_rates.get(pair)

            rate = 0.0
            if rate_info:
                if isinstance(rate_info, dict) and "rate" in rate_info:
                    rate = float(rate_info["rate"])
                elif isinstance(rate_info, (int, float)):
                    rate = float(rate_info)

            total += wallet.balance * rate
        return total

    def to_dict(self) -> dict:
        # Сериализация портфеля
        wallets_data = {
            code: w.to_dict() for code, w in self._wallets.items()
        }
        return {
            "user_id": self._user_id,
            "wallets": wallets_data,
        }