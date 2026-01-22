import json
import requests
import base64
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Настройки
        TOKEN = 'ghp_Nm7fCQLO5aBiZM0o1u6qrgKMo3VC804IwXpu'
        REPO = 'matvei-droid/zuubackvpn'
        FILE = 'api/users.json'
        GIST = 'https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/serverv.txt'

        # 2. Получаем имя юзера из ссылки
        query = parse_qs(urlparse(self.path).query)
        user_name = query.get('user', [None])[0]

        try:
            # 3. Загружаем базу из GitHub
            url = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
            r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
            data = json.loads(base64.b64decode(r.json()['content']).decode('utf-8'))
            
            user = data.get(user_name)
            
            if not user or user.get("status") != "active":
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden: User not active")
                return

            # 4. Считаем время и лимиты под твой JSON
            exp_str = user.get("expires", "2099-01-01")
            exp_ts = int(datetime.strptime(exp_str, "%Y-%m-%d").timestamp())
            limit_gb = int(user.get("limit_gb", 0))
            total_bytes = limit_gb * 1024 * 1024 * 1024

            # 5. Получаем сервера
            servers = requests.get(GIST).text

            # 6. Отправляем ответ для Hiddify
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Subscription-Userinfo', f"upload=0; download=0; total={total_bytes}; expire={exp_ts}")
            self.end_headers()
            self.wfile.write(servers.encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
