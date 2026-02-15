import time
import logging
from typing import List, Optional

from .config import ParserConfig
from .api_clients import CoinGeckoClient, ExchangeRateApiClient, BaseApiClient
from .updater import RatesUpdater

logger = logging.getLogger(__name__)


def run_scheduler(interval: int = 300) -> None:
    """
    Бесконечный цикл обновления курсов.
    interval: частота обновления в секундах (по умолчанию 5 минут).
    """
    # Настраиваем базовый логгер
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s"
        )

    config = ParserConfig()

    # Инициализация клиентов внутри шедулера
    clients: List[BaseApiClient] = []

    try:
        clients.append(CoinGeckoClient(config))
    except Exception as e:
        logger.error(f"Failed to initialize CoinGeckoClient: {e}")

    if config.EXCHANGERATE_API_KEY:
        try:
            clients.append(ExchangeRateApiClient(config))
        except Exception as e:
            logger.error(f"Failed to initialize ExchangeRateApiClient: {e}")
    else:
        logger.warning("ExchangeRate API key not found. Fiat rates will be skipped.")

    if not clients:
        logger.error("No API clients configured. Exiting scheduler.")
        return

    updater = RatesUpdater(clients)

    logger.info(f"Starting Scheduler. Update interval: {interval} seconds.")
    print(f"Scheduler started. Updating every {interval}s. Press Ctrl+C to stop.")

    try:
        while True:
            logger.info("Scheduler: Initiating update...")
            try:
                updater.run_update()
            except Exception as e:
                logger.error(f"Unexpected error in scheduler loop: {e}")

            logger.info(f"Scheduler: Sleeping for {interval} seconds...")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
        print("\nScheduler stopped.")


if __name__ == "__main__":
    # Реализовал запуск напрямую для проверки
    run_scheduler()