from abc import ABC, abstractmethod
from typing import Dict

from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str) -> None:
        # Валидация общая для всех валют
        code_upper = code.upper()
        if not (2 <= len(code_upper) <= 5) or " " in code_upper:
            raise ValueError(f"Некорректный код валюты: {code}")
        if not name:
            raise ValueError("Имя валюты не может быть пустым")

        self.name = name
        self.code = code_upper

    @abstractmethod
    def get_display_info(self) -> str:
        raise NotImplementedError


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str = "Unknown") -> None:
        super().__init__(name=name, code=code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return (
            f"[FIAT] {self.code} — {self.name} "
            f"(Issuing: {self.issuing_country})"
        )


class CryptoCurrency(Currency):
    def __init__(
            self,
            name: str,
            code: str,
            algorithm: str = "Unknown",
            market_cap: float = 0.0,
    ) -> None:
        super().__init__(name=name, code=code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"
        )


# Реестр валют
_CURRENCY_REGISTRY: Dict[str, Currency] = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 4.5e11),
    "SOL": CryptoCurrency("Solana", "SOL", "Proof-of-History", 8.0e10),
}


def get_currency(code: str) -> Currency:
    normalized = code.upper()
    currency = _CURRENCY_REGISTRY.get(normalized)
    if not currency:
        raise CurrencyNotFoundError(code=normalized)
    return currency