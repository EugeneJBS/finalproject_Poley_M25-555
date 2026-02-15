import functools
import logging
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

# Настройка логгера
logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def log_action(action: str, verbose: bool = False) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Используем timezone-aware datetime
            timestamp = datetime.now(timezone.utc).isoformat()

            # Пытаемся найти пользователя в аргументах (для register/login)
            username = kwargs.get("username") or kwargs.get("current_username")

            msg_prefix = (
                f"{action} ts={timestamp} user={username if username else '-'}"
            )

            logger.info(f"{msg_prefix} started")
            try:
                result = func(*args, **kwargs)

                if verbose and isinstance(result, str):
                    # Если результат строка, то убираем переносы
                    clean_res = result.replace('\n', ' | ')
                    logger.info(f"{msg_prefix} OK details='{clean_res}'")
                elif verbose and isinstance(result, dict):
                    logger.info(f"{msg_prefix} OK details={result}")
                else:
                    logger.info(f"{msg_prefix} OK")

                return result
            except Exception as exc:
                logger.error(
                    f"{msg_prefix} ERROR type={type(exc).__name__} msg='{str(exc)}'"
                )
                raise

        return wrapper

    return decorator