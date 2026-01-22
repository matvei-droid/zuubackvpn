import json
import requests
import base64
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ТВОИ НАСТРОЙКИ
GITHUB_TOKEN = 'ghp_Nm7fCQLO5aBiZM0o1u6qrgKMo3VC804IwXpu' # Твой токен
REPO = 'matvei-droid/zuubackvpn'
USERS_FILE = 'api/users.json'
GIST_URL = 'https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/26ab2ed6884ff4223cc0e1f1a3566525821269ac/serverv.txt' # ВСТАВЬ СВОЮ ССЫЛКУ НА GIST С СЕРВЕРАМИ

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        user_name = query.get('user', [None])[0]

        # 1. Загружаем базу пользователей с GitHub
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{USERS_FILE}", headers=headers)
        
        if r.status_code != 200:
            self.send_error(500, "Ошибка доступа к базе пользователей")
            return

        users_data = json.loads(base64.b64decode(r.json()['content']).decode('utf-8'))
        user_info = users_data.get(user_name)

        # 2. Проверка пользователя
        if not user_info or user_info.get("status") != "active":
            self.send_response(403)
            self.end_headers()
            self.wfile.write("❌ Доступ запрещен или подписка не найдена".encode())
            return

        # 3. Проверка даты истечения
        expire_date_str = user_info.get("expire")
        expire_timestamp = 0
        if expire_date_str:
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
            expire_timestamp = int(expire_date.timestamp())
            if datetime.now() > expire_date:
                self.send_response(403)
                self.end_headers()
                self.wfile.write("❌ Срок подписки истек!".encode())
                return

        # 4. Получаем сервера из Gist
        gist_r = requests.get(GIST_URL)
        servers = gist_r.text if gist_r.status_code == 200 else ""

        # 5. Отправляем ответ с заголовками для Hiddify
        # Формат: upload=...; download=...; total=...; expire=...
        user_info_header = f"upload=0; download=0; total={user_info.get('total', 0)}; expire={expire_timestamp}"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.send_header('Subscription-Userinfo', user_info_header)
        self.end_headers()
        self.wfile.write(servers.encode())
