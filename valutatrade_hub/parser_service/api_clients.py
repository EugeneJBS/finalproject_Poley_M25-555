from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig

logger = logging.getLogger(__name__)


class BaseApiClient(ABC):
    def __init__(self, config: ParserConfig) -> None:
        self.config = config

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        raise NotImplementedError


class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self) -> Dict[str, float]:
        # Формируем строку ID для запроса: "bitcoin,ethereum,solana"
        ids = ",".join(
            self.config.CRYPTO_ID_MAP[code]
            for code in self.config.CRYPTO_CURRENCIES
        )
        params = {
            "ids": ids,
            "vs_currencies": self.config.BASE_CURRENCY.lower(),
        }

        try:
            resp = requests.get(
                self.config.COINGECKO_URL,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise ApiRequestError(f"CoinGecko error: {exc}")

        data = resp.json()
        result: Dict[str, float] = {}

        for code in self.config.CRYPTO_CURRENCIES:
            coin_id = self.config.CRYPTO_ID_MAP.get(code)
            if not coin_id:
                continue

            price_info = data.get(coin_id, {})
            value = price_info.get(self.config.BASE_CURRENCY.lower())

            if value is not None:
                pair = f"{code}_{self.config.BASE_CURRENCY}"
                result[pair] = float(value)

        logger.info(f"CoinGecko fetched {len(result)} rates")
        return result


class ExchangeRateApiClient(BaseApiClient):
    def fetch_rates(self) -> Dict[str, float]:
        if not self.config.EXCHANGERATE_API_KEY:
            # Если ключ не задан, то выводим ошибку
            raise ApiRequestError("EXCHANGERATE_API_KEY не задан.")

        # URL: https://v6.exchangerate-api.com/v6/KEY/latest/USD
        url = (
            f"{self.config.EXCHANGERATE_API_URL}/"
            f"{self.config.EXCHANGERATE_API_KEY}/latest/"
            f"{self.config.BASE_CURRENCY}"
        )

        try:
            resp = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise ApiRequestError(f"ExchangeRate-API error: {exc}")

        data = resp.json()
        if data.get("result") != "success":
            raise ApiRequestError(f"ExchangeRate-API error: {data.get('error-type')}")

        rates = data.get("rates", {})
        result: Dict[str, float] = {}

        for code in self.config.FIAT_CURRENCIES:
            if code == self.config.BASE_CURRENCY:
                continue

            # Инвертируем значение курса, ьак как API возвращает условно стоимость доллара за евро, а не наоборот
            rate_to_base = rates.get(code)

            if rate_to_base:
                pair = f"{code}_{self.config.BASE_CURRENCY}"
                try:
                    val = 1.0 / float(rate_to_base)
                    result[pair] = val
                except ZeroDivisionError:
                    logger.warning(f"Rate for {code} is 0, skipping.")
                    continue

        logger.info(f"ExchangeRate-API fetched {len(result)} rates")
        return result