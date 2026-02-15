from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

from prettytable import PrettyTable

from ..decorators import log_action
from ..infra.database import DatabaseManager
from ..infra.settings import SettingsLoader
from .exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from .models import User, Portfolio
from ..core.currencies import get_currency

_current_username: Optional[str] = None


def get_current_username() -> Optional[str]:
    return _current_username


def set_current_username(username: Optional[str]) -> None:
    global _current_username
    _current_username = username


def _get_db() -> DatabaseManager:
    return DatabaseManager()


def _require_login() -> User:
    username = get_current_username()
    if not username:
        raise PermissionError("Сначала выполните login")

    db = _get_db()
    user = db.get_user_by_username(username)
    if not user:
        set_current_username(None)
        raise PermissionError("Пользователь не найден, выполните login заново")
    return user


@log_action("REGISTER")
def register_user(username: str, password: str) -> str:
    db = _get_db()

    if db.get_user_by_username(username):
        return f"Имя пользователя '{username}' уже занято"

    # Генерация ID
    users = db.load_users()
    new_id = max((u.user_id for u in users), default=0) + 1

    try:
        # Создание пользователя (пароль хешируется внутри __init__)
        user = User(user_id=new_id, username=username, password=password)
    except ValueError as exc:
        return str(exc)

    # Сохранение пользователя
    db.save_user(user)

    # Создание пустого портфеля
    portfolio = Portfolio(user_id=user.user_id)
    db.save_portfolio(portfolio)

    return (
        f"Пользователь '{username}' зарегистрирован (id={user.user_id}). "
        "Войдите: login --username <name> --password ****"
    )


@log_action("LOGIN")
def login_user(username: str, password: str) -> str:
    db = _get_db()
    user = db.get_user_by_username(username)

    if not user:
        return f"Пользователь '{username}' не найден"

    if not user.verify_password(password):
        return "Неверный пароль"

    set_current_username(username)
    return f"Вы вошли как '{username}'"


def show_portfolio(base_currency: str = "USD") -> str:
    user = _require_login()
    db = _get_db()

    portfolio = db.get_portfolio_by_user_id(user.user_id)
    if not portfolio:
        return "Портфель не найден"

    # Получаем словарь курсов
    rates_data = db.get_rates_snapshot().get("pairs", {})
    base = base_currency.upper()

    if not portfolio.wallets:
        return "У вас пока нет ни одного кошелька"

    table = PrettyTable()
    table.field_names = ["Валюта", "Баланс", f"Стоимость в {base}"]
    table.align = "l"

    total = portfolio.get_total_value(rates_data, base)

    # Формирование строк таблицы
    for code, wallet in portfolio.wallets.items():
        # Расчет стоимости конкретного кошелька для отображения
        val_in_base = 0.0
        if code == base:
            val_in_base = wallet.balance
        else:
            pair = f"{code}_{base}"
            info = rates_data.get(pair)
            if info:
                rate = float(info["rate"])
                val_in_base = wallet.balance * rate

        table.add_row([
            code,
            f"{wallet.balance:.4f}",
            f"{val_in_base:.2f} {base}"
        ])

    header = f"Портфель пользователя '{user.username}' (база: {base}):\n"
    footer = f"ИТОГО: {total:,.2f} {base}"
    return header + str(table) + "\n---------------------------------\n" + footer


@log_action("BUY", verbose=True)
def buy_currency(currency_code: str, amount: float) -> str:
    # Валидация
    if amount <= 0:
        return "'amount' должен быть положительным числом"

    # Провеяем существует ли валюта
    currency = get_currency(currency_code)
    code = currency.code

    user = _require_login()
    db = _get_db()

    # Получение портфеля
    portfolio = db.get_portfolio_by_user_id(user.user_id)
    if not portfolio:
        portfolio = Portfolio(user_id=user.user_id)

    # Пополнение
    wallet = portfolio.get_wallet(code)
    if not wallet:
        wallet = portfolio.add_currency(code)

    before = wallet.balance
    wallet.deposit(amount)
    after = wallet.balance

    # Сохраняем изменения
    db.save_portfolio(portfolio)

    # Оценочная стоимость
    rates_data = db.get_rates_snapshot().get("pairs", {})
    pair = f"{code}_USD"
    info = rates_data.get(pair)

    est_msg = ""
    if info:
        rate = float(info["rate"])
        estimated = amount * rate
        est_msg = f"\nОценочная стоимость покупки: {estimated:,.2f} USD"

    return (
        f"Покупка выполнена: {amount:.4f} {code}\n"
        f"Изменения в портфеле:\n"
        f"- {code}: было {before:.4f} → стало {after:.4f}"
        f"{est_msg}"
    )


@log_action("SELL", verbose=True)
def sell_currency(currency_code: str, amount: float) -> str:
    # Валидация
    if amount <= 0:
        return "'amount' должен быть положительным числом"

    currency = get_currency(currency_code)
    code = currency.code

    user = _require_login()
    db = _get_db()

    portfolio = db.get_portfolio_by_user_id(user.user_id)
    if not portfolio:
        return f"У вас нет кошелька '{code}'."

    wallet = portfolio.get_wallet(code)
    if not wallet:
        return f"У вас нет кошелька '{code}'. Сначала купите валюту."

    before = wallet.balance

    # Снятие
    wallet.withdraw(amount)
    after = wallet.balance

    db.save_portfolio(portfolio)

    # Оценочная выручка
    rates_data = db.get_rates_snapshot().get("pairs", {})
    pair = f"{code}_USD"
    info = rates_data.get(pair)

    est_msg = ""
    if info:
        rate = float(info["rate"])
        revenue = amount * rate
        est_msg = f"\nОценочная выручка: {revenue:,.2f} USD"

    return (
        f"Продажа выполнена: {amount:.4f} {code}\n"
        f"Изменения в портфеле:\n"
        f"- {code}: было {before:.4f} → стало {after:.4f}"
        f"{est_msg}"
    )


def get_rate(from_code: str, to_code: str) -> str:
    # Валидация кодов через get_currency
    base_curr = get_currency(from_code)
    quote_curr = get_currency(to_code)
    base = base_curr.code
    quote = quote_curr.code

    # Загрузка настроек для проверки TTL
    settings = SettingsLoader()
    ttl = int(settings.get("RATES_TTL_SECONDS", 300))

    db = _get_db()
    snapshot = db.get_rates_snapshot()
    pairs = snapshot.get("pairs", {})
    last_refresh_raw = snapshot.get("last_refresh")

    # Проверка актуальности кэша
    is_outdated = False
    if last_refresh_raw:
        last_refresh = datetime.fromisoformat(last_refresh_raw)
        if datetime.now(timezone.utc) - last_refresh > timedelta(seconds=ttl):
            is_outdated = True
    else:
        is_outdated = True

    pair = f"{base}_{quote}"
    info = pairs.get(pair)

    warning = " (Данные устарели, пожалуйста, выполните update-rates)" if is_outdated else ""

    if info:
        rate = float(info["rate"])
        updated = info.get("updated_at", "N/A")
        return (
            f"Курс {base}→{quote}: {rate:.8f} (обновлено: {updated}){warning}\n"
            f"Обратный курс {quote}→{base}: {(1 / rate):.8f}"
        )

    # Обратный курс
    rev_pair = f"{quote}_{base}"
    rev_info = pairs.get(rev_pair)
    if rev_info:
        rev_rate = float(rev_info["rate"])
        rate = 1 / rev_rate if rev_rate else 0.0
        updated = rev_info.get("updated_at", "N/A")
        return (
            f"Курс {base}→{quote}: {rate:.8f} (вычислено через обратный, обновлено: {updated}){warning}"
        )

    raise CurrencyNotFoundError(f"Пара {base}/{quote}")


def show_rates(currency: str | None = None, top: int | None = None) -> str:
    db = _get_db()
    snapshot = db.get_rates_snapshot()
    pairs = snapshot.get("pairs", {})
    last_refresh = snapshot.get("last_refresh", "Never")

    if not pairs:
        return "Локальный кеш курсов пуст. Выполните 'update-rates'."

    # Фильтрация и сортировка
    items = []
    for pair, data in pairs.items():
        if currency:
            target = currency.upper()
            if target not in pair:
                continue
        items.append((pair, data))

    items.sort(key=lambda x: float(x[1].get('rate', 0)), reverse=True)

    if top:
        items = items[:top]

    if not items:
        return "Курсы не найдены по заданным критериям."

    table = PrettyTable()
    table.field_names = ["Пара", "Курс", "Обновлено", "Источник"]
    table.align = "l"

    for pair, data in items:
        table.add_row([
            pair,
            f"{float(data.get('rate', 0)):.6f}",
            data.get('updated_at', '-'),
            data.get('source', '-')
        ])

    return f"Rates from cache (updated at {last_refresh}):\n" + str(table)