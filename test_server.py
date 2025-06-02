from http.server import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello World")

    def log_message(self, format, *args):
        return

server = HTTPServer(("127.0.0.1", 5000), TestHandler)
print("Listening on http://127.0.0.1:5000/")
server.serve_forever()