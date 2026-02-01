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

1.  **Установить зависимости:**
    ```bash
    make install
    ```

2.  **Указать API-ключ для ExchangeRate-API:**
    Для работы парсера курсов валют необходимо установить переменную окружения:
    ```bash
    export EXCHANGERATE_API_KEY="ваш_ключ"
    ```

## Запуск

Запуск основного консольного приложения:
```bash
make project
```

## Основные команды

### Управление аккаунтом
* **Регистрация:**
    ```bash
    register --username alice --password 1234
    ```
* **Вход:**
    ```bash
    login --username alice --password 1234
    ```

### Торговля и портфель
* **Показать портфель:**
    ```bash
    show-portfolio
    ```
* **Покупка:**
    ```bash
    buy --currency BTC --amount 0.05
    ```
* **Продажа:**
    ```bash
    sell --currency BTC --amount 0.01
    ```

### Курсы валют
* **Получить конкретный курс:**
    ```bash
    get-rate --from USD --to BTC
    ```
* **Обновить курсы (Parser Service):**
    ```bash
    update-rates
    ```
* **Показать список всех курсов:**
    ```bash
    show-rates
    ```

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
```bash
https://asciinema.org/a/cObWNjBIHtcfUC6o
```
## Автор
ФИО: Полей Евгений

Группа: M25-555