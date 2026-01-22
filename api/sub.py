import json, requests, base64, os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Берем токен из настроек Vercel, а не из текста!
        TOKEN = os.getenv('MY_GITHUB_TOKEN') 
        REPO = 'matvei-droid/zuubackvpn'
        FILE = 'api/users.json'
        GIST = 'https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/serverv.txt'

        user_name = parse_qs(urlparse(self.path).query).get('user', [None])[0]

        try:
            r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{FILE}", 
                             headers={"Authorization": f"token {TOKEN}"})
            
            if r.status_code != 200:
                self.send_error(r.status_code, f"GitHub Error: {r.text}")
                return

            js = r.json()
            data = json.loads(base64.b64decode(js['content']).decode('utf-8'))
            user = data.get(user_name)

            if not user or user.get("status") != "active":
                self.send_error(403, "User not found")
                return

            exp_ts = int(datetime.strptime(user.get("expires", "2026-01-01"), "%Y-%m-%d").timestamp())
            limit = int(user.get("limit_gb", 0)) * 1024 * 1024 * 1024

            servers = requests.get(GIST).text
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Subscription-Userinfo', f"upload=0; download=0; total={limit}; expire={exp_ts}")
            self.end_headers()
            self.wfile.write(servers.encode())
        except Exception as e:
            self.send_error(500, str(e))
