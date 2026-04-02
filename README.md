# ozon-seller-mcp

MCP-сервер для [Ozon Seller API](https://docs.ozon.ru/api/seller/) — позволяет AI-ассистентам (Claude, etc.) работать с вашим магазином на Ozon.

## Возможности

- **Товары** — просмотр, создание, обновление, архивация, удаление, загрузка изображений
- **Цены** — получение и обновление цен
- **Остатки** — просмотр и обновление остатков (FBS/FBO)
- **Заказы FBS** — список, детали, подтверждение отправки, отмена, этикетки, трекинг
- **Заказы FBO** — список и детали
- **Склады** — список складов продавца и FBO
- **Категории** — дерево категорий, атрибуты, значения справочников
- **Аналитика** — продажи, просмотры, конверсии, остатки на складах
- **Финансы** — транзакции, итоги, реализация
- **Чаты** — переписка с покупателями
- **Отзывы** — просмотр и ответы на отзывы
- **Рейтинг** — текущий рейтинг и история
- **Акции** — список акций, добавление/удаление товаров

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/your-username/ozon-seller-mcp.git
cd ozon-seller-mcp

# Установить зависимости
uv sync
```

## Настройка

Получите Client ID и API Key в личном кабинете Ozon Seller → Настройки → Seller API.

```bash
cp .env.example .env
# Заполните OZON_CLIENT_ID и OZON_API_KEY
```

## Использование с Claude Desktop

Добавьте в `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ozon-seller": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ozon-seller-mcp", "python", "server.py"],
      "env": {
        "OZON_CLIENT_ID": "your_client_id",
        "OZON_API_KEY": "your_api_key"
      }
    }
  }
}
```

## Использование с Claude Code

Добавьте в `.claude/settings.json`:

```json
{
  "mcpServers": {
    "ozon-seller": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ozon-seller-mcp", "python", "server.py"],
      "env": {
        "OZON_CLIENT_ID": "your_client_id",
        "OZON_API_KEY": "your_api_key"
      }
    }
  }
}
```

## Лицензия

MIT
