import json, requests, base64, os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Берем токен из Environment Variables, которые ты настроил
        TOKEN = os.getenv('MY_GITHUB_TOKEN') 
        REPO = 'matvei-droid/zuubackvpn'
        FILE = 'api/users.json'
        GIST = 'https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/serverv.txt'

        # Извлекаем имя пользователя из запроса
        query = parse_qs(urlparse(self.path).query)
        user_name = query.get('user', [None])[0]

        try:
            # Запрашиваем файл с пользователями у GitHub
            r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{FILE}", 
                             headers={"Authorization": f"token {TOKEN}"})
            
            if r.status_code != 200:
                self.send_response(r.status_code)
                self.end_headers()
                self.wfile.write(f"GitHub Error: {r.status_code}".encode())
                return

            # Декодируем содержимое файла
            js = r.json()
            data = json.loads(base64.b64decode(js['content']).decode('utf-8'))
            user = data.get(user_name)

            # Проверяем статус пользователя
            if not user or user.get("status") != "active":
                self.send_error(403, "User not found or inactive")
                return

            # Читаем лимиты и дату из твоего JSON
            exp_str = user.get("expires", "2026-12-31")
            exp_ts = int(datetime.strptime(exp_str, "%Y-%m-%d").timestamp())
            limit_gb = int(user.get("limit_gb", 0))
            total_bytes = limit_gb * 1024 * 1024 * 1024

            # Загружаем сервера из Gist
            servers = requests.get(GIST).text

            # Отправляем заголовки для отображения в Hiddify
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Subscription-Userinfo', f"upload=0; download=0; total={total_bytes}; expire={exp_ts}")
            self.end_headers()
            self.wfile.write(servers.encode())

        except Exception as e:
            self.send_error(500, str(e))
