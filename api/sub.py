from http.server import BaseHTTPRequestHandler
import requests

GIST_URL = "https://gist.githubusercontent.com/matvei-droid/8f4b0f87c5b18011a55490fcac60f57f/raw/26ab2ed6884ff4223cc0e1f1a3566525821269ac/serverv.txt"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Скрипт просто берет данные из твоего Gist и отдает их
            res = requests.get(GIST_URL)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(res.text.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
