import http.server
import socketserver
import requests
import urllib.parse
import cgi


current_url = "https://github.com/"


class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/update-url":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open("index.html", "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode())
        else:
            r = requests.get(
                url="{host}{uri.path}?{uri.params}".format(
                    host=current_url, uri=parsed_path
                )
            )
            self.send_response(r.status_code)
            for attr, value in r.headers.__dict__.items():
                self.send_header(attr, value)
            self.end_headers()
            with open("index.html", "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode())
            self.wfile.write(r.content)

    def do_POST(self):
        global current_url
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/update-url":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            parsed_path = urllib.parse.urlparse(form.getvalue("url"))
            current_url = "{uri.scheme}://{uri.netloc}/".format(
                uri=parsed_path)
            self.send_response(301)
            self.send_header(
                "Location", "{uri.path}?{uri.params}".format(uri=parsed_path))
            self.end_headers()
        else:
            r = requests.post(
                url="{host}{uri.path}?{uri.params}".format(
                    host=current_url, uri=parsed_path
                )
            )
            self.send_response(r.status_code)
            for attr, value in r.headers.__dict__.items():
                self.send_header(attr, value)
            self.end_headers()
            self.wfile.write(r.content)


def main():
    server_address = ('', 8080)
    http_server = http.server.HTTPServer(server_address, RedirectHandler)
    print('Starting http server...')
    http_server.serve_forever()


if __name__ == "__main__":
    main()
