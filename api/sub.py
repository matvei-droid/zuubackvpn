import json, requests, base64
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # НАСТРОЙКИ
        TOKEN = 'ghp_Nm7fCQLO5aBiZM0o1u6qrgKMo3VC804IwXpu'
        REPO = 'matvei-droid/zuubackvpn'
        FILE = 'api/users.json'
        GIST = 'https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/serverv.txt'

        user_name = parse_qs(urlparse(self.path).query).get('user', [None])[0]

        try:
            # Загрузка базы
            r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{FILE}", 
                             headers={"Authorization": f"token {TOKEN}"})
            
            if r.status_code == 401:
                self.send_error(401, "GitHub Token is invalid")
                return

            data = json.loads(base64.b64decode(r.json()['content']).decode('utf-8'))
            user = data.get(user_name)

            if not user or user.get("status") != "active":
                self.send_error(403, "User not found or inactive")
                return

            # Срок и лимиты
            exp_str = user.get("expires", "2099-01-01")
            exp_ts = int(datetime.strptime(exp_str, "%Y-%m-%d").timestamp())
            total_bytes = int(user.get("limit_gb", 0)) * 1024 * 1024 * 1024

            # Ответ для Hiddify
            servers = requests.get(GIST).text
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Subscription-Userinfo', f"upload=0; download=0; total={total_bytes}; expire={exp_ts}")
            self.end_headers()
            self.wfile.write(servers.encode())

        except Exception as e:
            self.send_error(500, str(e))

