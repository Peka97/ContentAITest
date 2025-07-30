# PHPMyAdmin Web Client

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Requests](https://img.shields.io/badge/Requests-2.32+-green)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.0+-orange)

Клиент для взаимодействия с phpMyAdmin через веб-интерфейс. Позволяет аутентифицироваться и получать данные таблиц без прямого доступа к БД.

## 📌 Особенности

- Аутентификация в phpMyAdmin через веб-интерфейс
- Получение данных таблиц в структурированном виде
- Красивое отображение таблиц в консоли
- Обработка ошибок аутентификации и соединения

## ⚙️ Установка

1. Убедитесь, что у вас установлен Python 3.12+
2. Установите зависимости:

```bash
pip install requests beautifulsoup4 tabulate
```

## 🚀 Использование
```python
from main import PhpMyAdminClient

# Настройки подключения
phpmyadmin_url = "http://your-server/phpmyadmin/"
username = "your_username"
password = "your_password"
database = "your_db"
table = "your_table"

# Создание клиента
client = PhpMyAdminClient(phpmyadmin_url, username, password)

try:
    # Аутентификация
    client.authenticate()
    
    # Получение данных таблицы
    headers, table_data = client.get_table_data(database, table)
    
    # Отображение данных
    PhpMyAdminClient.display_table(headers, table_data)
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
```

## Demo:

<a href="https://gyazo.com/ece8f7074b3267b4e08de879bd1ea7f0"><img src="https://i.gyazo.com/ece8f7074b3267b4e08de879bd1ea7f0.gif" alt="Image from Gyazo" width="638"/></a>
