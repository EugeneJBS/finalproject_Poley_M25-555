# ValutaTrade Hub

Консольное приложение для симуляции торговли валютами и управления портфелем с интеграцией внешнего API курсов валют.

## Структура проекта

```text
finalproject_<фамилия>_<группа>/
├── data/                       # Хранилище JSON-файлов
│   ├── users.json
│   ├── portfolios.json
│   ├── rates.json
│   └── exchange_rates.json
├── valutatrade_hub/            # Основной пакет приложения
│   ├── core/                   # Бизнес-логика
│   ├── infra/                  # Работа с данными и API
│   ├── parser_service/         # Сервис обновления курсов
│   ├── cli/                    # Интерфейс командной строки
│   ├── logging_config.py       # Настройки логирования
│   └── decorators.py           # Декораторы (логирование, валидация)
├── main.py                     # Точка входа
├── Makefile                    # Команды автоматизации
├── pyproject.toml              # Конфигурация Poetry и Ruff
└── README.md                   # Документация проекта
```

## Установка

Для работы требуется Python 3.11+ и Poetry

1.  **Установить зависимости:**
    ```bash
    make install
    ```

2.  **Указать API-ключ для ExchangeRate-API:**

    Настройте переменные окружения:
    ```bash
    export EXCHANGERATE_API_KEY="ваш_ключ"
    ```

## Запуск

Запуск основного консольного приложения:
```bash
make project
```

## Основные команды

### Внутри приложения доступны следующие команды:

- ```register --username <name> --password <pass>``` — Регистрация нового пользователя.

- ```login --username <name> --password <pass>``` — Вход в систему.

- ```update-rates``` — Загрузка актуальных курсов валют из интернета.

- ```buy --currency <CODE> --amount <N>``` — Покупка валюты (например, BTC).

- ```sell --currency <CODE> --amount <N>``` — Продажа валюты.

- ```show-portfolio``` — Просмотр балансов и общей стоимости.

- ```show-rates``` — Просмотр текущих курсов.

- ```help``` — Список всех команд.

## Линтер и сборка

Проверка стиля кода (Ruff/PEP8):
```bash
make lint
```

Сборка пакета:
```bash
make build
```

## Запись консоли (asciinema)
Демонстрация работы старой версии
```bash
https://asciinema.org/a/cObWNjBIHtcfUC6o
```
## Автор
### Полей Евгений

### Группа: M25-555