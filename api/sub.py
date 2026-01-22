import json, requests, base64, os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # TOKEN БЕРЕТСЯ ИЗ НАСТРОЕК VERCEL
        TOKEN = os.getenv('MY_GITHUB_TOKEN') 
        REPO = 'matvei-droid/zuubackvpn'
        FILE = 'api/users.json'
        GIST = 'https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/serverv.txt'

        user_name = parse_qs(urlparse(self.path).query).get('user', [None])[0]

        try:
            r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{FILE}", 
                             headers={"Authorization": f"token {TOKEN}"})
            
            if r.status_code != 200:
                self.send_response(r.status_code)
                self.end_headers()
                self.wfile.write(f"Error: {r.status_code}".encode())
                return

            js = r.json()
            data = json.loads(base64.b64decode(js['content']).decode('utf-8'))
            user = data.get(user_name)

            if not user or user.get("status") != "active":
                self.send_error(403, "Forbidden")
                return

            exp_ts = int(datetime.strptime(user.get("expires", "2026-12-31"), "%Y-%m-%d").timestamp())
            total_bytes = int(user.get("limit_gb", 100)) * 1024 * 1024 * 1024

            # Получаем список серверов
            servers = requests.get(GIST).text
            
            # ФОРМИРУЕМ КОНФИГ СО СКРЫТИЕМ
            # Эти строки заставят Hiddify спрятать стрелочки настроек
            config_lines = (
                "#profile-title: VPN\n"
                "#profile-update-interval: 1\n"
                "#profile-config: {\"hide_settings\":true}\n\n"
            )
            final_content = config_lines + servers

            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Profile-Config', '{"hide_settings":true}')
            self.send_header('Subscription-Userinfo', f"upload=0; download=0; total={total_bytes}; expire={exp_ts}")
            self.end_headers()
            
            # Отправляем обновленный контент
            self.wfile.write(final_content.encode('utf-8'))
        except:
            self.send_error(500)
