import http.server
import socketserver
import requests
import urllib.parse
import cgi


referer = "http://fap.fpt.edu.vn/"
host = "fap.fpt.edu.vn"
origin = "http://fap.fpt.edu.vn"

class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def process_request_headers(self):
        request_headers = {}
        for h in self.headers:
            if h.lower() == "Host".lower():
                request_headers[h] = host
                continue
            if h.lower() == "Origin".lower():
                request_headers[h] = origin
                continue
            if h.lower() == "Referer".lower():
                request_headers[h] = referer
                continue
            request_headers[h] = self.headers.get(h)
        return request_headers

    def process_response(self, r):
        self.send_response(r.status_code)
        for key in r.headers.keys():
            if key.lower() == 'Content-Encoding'.lower():
                continue
            if key.lower() == 'Content-Length'.lower():
                continue
            self.send_header(key, r.headers.get(key))
        self.end_headers()
        self.wfile.write(r.content)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        r = requests.get(
            url="{origin}{uri.path}?{uri.params}".format(
                origin=origin, uri=parsed_path
            ),
            headers=self.process_request_headers()
        )
        self.process_response(r)

    def do_POST(self):
        global host
        global origin
        global referer
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/update-url":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            parsed_path = urllib.parse.urlparse(form.getvalue("url"))
            host = parsed_path.netloc
            origin = "{uri.scheme}://{host}".format(
                uri=parsed_path,
                host=host
            )
            referer = "{uri.scheme}://{host}/".format(
                uri=parsed_path,
                host=host
            )
            self.send_response(301)
            self.send_header(
                "Location", "{uri.path}?{uri.params}".format(uri=parsed_path)
            )
            self.end_headers()
        else:
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            r = requests.post(
                url="{origin}{uri.path}?{uri.params}".format(
                    origin=origin, uri=parsed_path
                ),
                headers=self.process_request_headers(),
                data=post_body
            )
            self.process_response(r)

    # def do_HEAD(self):
    #     parsed_path = urllib.parse.urlparse(self.path)
    #     r = requests.head(
    #         url="{host}{uri.path}?{uri.params}".format(
    #             host=referer, uri=parsed_path
    #         ),
    #         headers=self.process_request_headers()
    #     )
    #     self.process_response(r)

    # def do_PUT(self):
    #     parsed_path = urllib.parse.urlparse(self.path)
    #     r = requests.put(
    #         url="{host}{uri.path}?{uri.params}".format(
    #             host=referer, uri=parsed_path
    #         ),
    #         headers=self.process_request_headers()
    #     )
    #     self.process_response(r)

    # def do_DELETE(self):
    #     parsed_path = urllib.parse.urlparse(self.path)
    #     r = requests.delete(
    #         url="{host}{uri.path}?{uri.params}".format(
    #             host=referer, uri=parsed_path
    #         ),
    #         headers=self.process_request_headers()
    #     )
    #     self.process_response(r)

    # def do_OPTIONS(self):
    #     parsed_path = urllib.parse.urlparse(self.path)
    #     r = requests.options(
    #         url="{host}{uri.path}?{uri.params}".format(
    #             host=referer, uri=parsed_path
    #         ),
    #         headers=self.process_request_headers()
    #     )
    #     self.process_response(r)

    # def do_PATCH(self):
    #     parsed_path = urllib.parse.urlparse(self.path)
    #     r = requests.patch(
    #         url="{host}{uri.path}?{uri.params}".format(
    #             host=referer, uri=parsed_path
    #         ),
    #         headers=self.process_request_headers()
    #     )
    #     self.process_response(r)


def main():
    server_address = ('', 8080)
    http_server = http.server.HTTPServer(server_address, RedirectHandler)
    print('Starting http server...')
    http_server.serve_forever()


if __name__ == "__main__":
    main()
