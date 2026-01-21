from http.server import BaseHTTPRequestHandler
import urllib.request
import json
from urllib.parse import urlparse, parse_qs

# Настройки твоего 3X-UI
PANEL_URL = "http://185.216.85.43:2053/VlMQP4XQzm7ABkdPlo"
LOGIN = "gdemrl"
PASSWORD = "20108888gg"

# Твой список "украденных" серверов
GIST_URL = "https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/26ab2ed6884ff4223cc0e1f1a3566525821269ac/serverv.txt"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        user_name = query.get('user', [None])[0]

        try:
            # 1. Логинимся в панель и получаем Cookie
            auth_url = f"{PANEL_URL}/login"
            auth_data = f"username={LOGIN}&password={PASSWORD}".encode()
            auth_req = urllib.request.Request(auth_url, data=auth_data)
            with urllib.request.urlopen(auth_req) as response:
                cookie = response.headers.get('Set-Cookie')

            # 2. Запрашиваем данные клиента из 3X-UI
            # (Ищем клиента по Email/Remark, который совпадает с ?user=)
            list_url = f"{PANEL_URL}/panel/api/inbounds/getClientTraffics/{user_name}"
            list_req = urllib.request.Request(list_url)
            list_req.add_header('Cookie', cookie)
            
            used, total, expire = 0, 0, 0
            with urllib.request.urlopen(list_req) as response:
                client_data = json.loads(response.read().decode())
                if client_data.get("success") and client_data.get("obj"):
                    obj = client_data["obj"]
                    used = obj.get("up", 0) + obj.get("down", 0)
                    total = obj.get("total", 0)
                    expire = obj.get("expiryTime", 0)

            # 3. Загружаем остальные сервера из Gist
            with urllib.request.urlopen(GIST_URL) as g_res:
                gist_servers = g_res.read().decode()

            # 4. Формируем ответ для Hiddify
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            # Передаем реальные данные в полоску сверху
            self.send_header('Subscription-Userinfo', f'upload=0; download={used}; total={total}; expire={expire // 1000}')
            self.end_headers()
            
            # В ответе будут все сервера: и те, что в Gist, и можно дописать свой
            self.wfile.write(gist_servers.encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

