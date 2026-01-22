from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ZuuVPN Connect</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: sans-serif; text-align: center; padding: 50px; background: #121212; color: white; }
                .btn { background: #6200ee; color: white; padding: 20px 40px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block; }
            </style>
        </head>
        <body>
            <h1>ZuuVPN</h1>
            <p>Нажми на кнопку ниже, чтобы добавить подписку</p>
            <a href="hiddify://install-config?url=https://zuubackvpn.vercel.app/api/sub?user=gay&name=ZuuVPN" class="btn">ПОДКЛЮЧИТЬ В ПРИЛОЖЕНИЕ</a>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
