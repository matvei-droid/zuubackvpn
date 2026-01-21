from http.server import BaseHTTPRequestHandler
import requests

# Твоя рабочая ссылка, которую ты прислал
GIST_URL = "https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/26ab2ed6884ff4223cc0e1f1a3566525821269ac/serverv.txt"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Проверяем, что запрос идет именно на /api/sub
        if '/api/sub' in self.path:
            try:
                res = requests.get(GIST_URL)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(res.text.encode('utf-8'))
            except:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
