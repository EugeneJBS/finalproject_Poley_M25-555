from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional


class SettingsLoader:
    _instance: Optional["SettingsLoader"] = None
    _settings: dict[str, Any] = {}

    def __new__(cls) -> "SettingsLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_defaults()
        return cls._instance

    def _init_defaults(self) -> None:
        # Определяем корневую директорию проекта
        # Если запускаем из корня, то data будет в ./data
        base_dir = Path(os.getenv("VALUTA_BASE_DIR", ".")).resolve()
        data_dir = base_dir / "data"
        data_dir.mkdir(exist_ok=True, parents=True)

        logs_dir = base_dir / "logs"

        self._settings = {
            "DATA_DIR": str(data_dir),
            "USERS_FILE": str(data_dir / "users.json"),
            "PORTFOLIOS_FILE": str(data_dir / "portfolios.json"),
            "RATES_FILE": str(data_dir / "rates.json"),
            "EXCHANGE_HISTORY_FILE": str(
                data_dir / "exchange_rates.json"
            ),
            "RATES_TTL_SECONDS": 300,
            "DEFAULT_BASE_CURRENCY": "USD",
            "LOG_DIR": str(logs_dir),
        }

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value


def get_settings() -> SettingsLoader:
    return SettingsLoader()