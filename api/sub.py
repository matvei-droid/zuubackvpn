from http.server import BaseHTTPRequestHandler
import urllib.request
import json
from urllib.parse import urlparse, parse_qs

GIST_URL = "https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/26ab2ed6884ff4223cc0e1f1a3566525821269ac/serverv.txt"
USERS_URL = "https://raw.githubusercontent.com/matvei-droid/zuubackvpn/main/api/users.json"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        user_name = query.get('user', [None])[0]

        try:
            with urllib.request.urlopen(USERS_URL) as u_res:
                users = json.loads(u_res.read().decode())
            
            if user_name in users and users[user_name].get("status") == "active":
                user_data = users[user_name]
                used = user_data.get("used", 0)
                total = user_data.get("total", 0)
                
                # Загружаем сервера
                with urllib.request.urlopen(GIST_URL) as g_res:
                    data = g_res.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                
                # ЭТА СТРОКА РИСУЕТ ПОЛОСКУ В ПРИЛОЖЕНИИ
                # Формат: upload=0; download=использовано; total=лимит; expire=время
                self.send_header('Subscription-Userinfo', f'upload=0; download={used}; total={total}; expire=0')
                
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

