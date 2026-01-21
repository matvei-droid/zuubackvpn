from http.server import BaseHTTPRequestHandler
import urllib.request
import json
from urllib.parse import urlparse, parse_qs

GIST_URL = "https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/26ab2ed6884ff4223cc0e1f1a3566525821269ac/serverv.txt"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Парсим параметры из ссылки (например, ?user=matvei)
        query = parse_qs(urlparse(self.path).query)
        user_name = query.get('user', [None])[0]

        # 2. Имитация базы данных (потом заменим на чтение из файла)
        users = {
            "matvei": {"status": "active"},
            "test": {"status": "banned"}
        }

        # 3. Логика проверки
        if user_name in users and users[user_name]["status"] == "active":
            try:
                with urllib.request.urlopen(GIST_URL) as response:
                    data = response.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(data)
            except:
                self.send_response(500)
                self.end_headers()
        else:
            # Если юзер забанен или его нет - выдаем ошибку 403 (Доступ запрещен)
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Access Denied: User banned or not found in ZuuVPN")
