import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from typing import Tuple, List


class PhpMyAdminClient:
    """Клиент для взаимодействия с phpMyAdmin через веб-интерфейс."""
    
    def __init__(self, base_url: str, username: str, password: str):
        """Инициализация клиента.
        
        Args:
            base_url: Базовый URL phpMyAdmin (должен заканчиваться на /)
            username: Имя пользователя
            password: Пароль
        """
        
        if not base_url.endswith('/'):
            base_url += '/'
            
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
    
    def authenticate(self) -> bool:
        """Аутентификация в phpMyAdmin.
        
        Returns:
            True, если аутентификация прошла успешно.
            
        Raises:
            AuthenticationError: Если аутентификация не удалась.
            ConnectionError: Если не удалось подключиться к серверу.
        """
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            token = self._extract_csrf_token(soup)
            
            login_data = {
                'pma_username': self.username,
                'pma_password': self.password,
                'server': '1',
                'token': token
            }
            
            response = self.session.post(
                f"{self.base_url}index.php",
                data=login_data,
                timeout=10
            )
            response.raise_for_status()
            
            if 'name="login_form"' in response.text:
                raise AuthenticationError("Login failed. Check credentials.")
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Connection error: {e}") from e
    
    def _extract_csrf_token(self, soup: BeautifulSoup) -> str:
        """Извлекает CSRF-токен из HTML."""
        
        token_element = soup.find('input', {'name': 'token'})
        
        if not token_element or 'value' not in token_element.attrs:
            raise AuthenticationError("Could not find CSRF token on login page.")
        
        return token_element['value']
    
    def get_table_data(self, database: str, table: str) -> Tuple[List[str], List[List[str]]]:
        """Получает данные таблицы из phpMyAdmin.
        
        Args:
            database: Имя базы данных
            table: Имя таблицы
            
        Returns:
            Tuple (заголовки, данные таблицы).
            
        Raises:
            TableDataError: Если не удалось получить данные таблицы.
            ConnectionError: Если возникла сетевая ошибка.
        """
        try:
            params = {
                'route': '/sql',
                'db': database,
                'table': table,
                'pos': 0
            }
            
            response = self.session.get(
                f"{self.base_url}index.php",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            result_table = soup.find('table', {'class': 'table_results'})
            
            if not result_table:
                raise TableDataError(
                    f"Could not find table data for {database}.{table}. "
                    "Check database/table names or permissions."
                )
            
            headers = self._extract_headers(result_table)
            table_data = self._extract_table_data(result_table)
            
            return headers, table_data
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Connection error: {e}") from e
    
    
    def _extract_headers(self, table: BeautifulSoup) -> List[str]:
        """Извлекает заголовки таблицы.

        Args:
            table: BeautifulSoup объект с table тегом.

        Returns:
            List[str]: Список заголовков таблицы полученных из 'data-column' аттрибута 'th' элементов.
            Заголовок получает 'N/A' если 'data-column' аттрибут не найден.
        """
        
        return [
            th.get('data-column', 'N/A') 
            for th in table.find('thead').find_all('th', {'class': 'column_heading'})
        ]
    
    def _extract_table_data(self, table: BeautifulSoup) -> List[List[str]]:
        """Извлекает данные таблицы из BeautifulSoup объекта.
        
        Этот метод обрабатывает элемент таблицы BeautifulSoup, извлекая текстовые данные из каждой ячейки
        с классом 'data' в каждой строке. Извлеченные данные возвращаются в виде списка списков,
        где каждый внутренний список представляет строку данных таблицы.

        Args:
            table (BeautifulSoup): Объект BeautifulSoup, представляющий таблицу для извлечения данных.

        Returns:
            List[List[str]]: Список списков, содержащий извлеченные данные таблицы, где каждый внутренний список
        представляет строку, а каждый строковый элемент представляет значение ячейки.
        """
        
        table_data = []
        for tr in table.find('tbody').find_all('tr'):
            row = [td.get_text(strip=True) for td in tr.find_all('td', {'class': 'data'})]
            table_data.append(row)
        return table_data
    
    def close(self) -> None:
        """Закрывает сессию."""
        self.session.close()
    
    @staticmethod
    def display_table(headers: List[str], table_data: List[List[str]]) -> None:
        """Отображает данные таблицы в консоли."""
        print(tabulate(
            table_data,
            headers=headers,
            tablefmt='grid',
            stralign='left',
            showindex=True
        ))


class AuthenticationError(Exception):
    """Ошибка аутентификации."""


class TableDataError(Exception):
    """Ошибка получения данных таблицы."""


if __name__ == "__main__":
    phpmyadmin_url = "http://185.244.219.162/phpmyadmin/"
    username = "test"
    password = "JHFBdsyf2eg8*"
    database = "testDB"
    table = "users"
    
    client = None
    try:
        client = PhpMyAdminClient(phpmyadmin_url, username, password)
        client.authenticate()
        headers, table_data = client.get_table_data(database, table)
        PhpMyAdminClient.display_table(headers, table_data)
        
    except (AuthenticationError, TableDataError, ConnectionError) as e:
        print(f"Error: {e}")
    finally:
        if client:
            client.close()