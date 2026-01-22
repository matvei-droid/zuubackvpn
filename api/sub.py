import requests
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Прямая ссылка на твои сервера (Gist не требует токена для чтения)
        GIST = 'https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/serverv.txt'

        try:
            # Просто качаем сервера и отдаем их
            servers = requests.get(GIST).text
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            # Прописываем лимит вручную (100 ГБ), чтобы Hiddify не ругался
            self.send_header('Subscription-Userinfo', 'upload=0; download=0; total=107374182400; expire=1798713600')
            self.end_headers()
            self.wfile.write(servers.encode())
        except Exception as e:
            self.send_error(500, str(e))
