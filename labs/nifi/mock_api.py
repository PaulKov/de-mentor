from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Lock
from time import sleep
from urllib.parse import parse_qs, urlsplit

FIXTURES = Path(__file__).with_name("fixtures")
COUNTS = defaultdict(int)
LOCK = Lock()

SOAP_OK = b"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:o="urn:lab:orders"><soap:Body><o:GetOrderResponse><o:Id>o-101</o:Id>
 </o:GetOrderResponse></soap:Body></soap:Envelope>"""
SOAP_FAULT = b"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
 <soap:Body><soap:Fault><faultcode>soap:Client</faultcode><faultstring>Invalid order</faultstring>
 </soap:Fault></soap:Body></soap:Envelope>"""


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, content_type="application/json", **headers):
        if not isinstance(data, bytes):
            data = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for key, value in headers.items():
            self.send_header(key.replace("_", "-"), value)
        self.end_headers()
        if data:
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass  # The timeout exercise deliberately disconnects.

    def do_GET(self):
        url = urlsplit(self.path)
        params = parse_qs(url.query)
        case = params.get("case", ["default"])[0]
        run = params.get("run", ["demo"])[0][:80]
        if url.path == "/health":
            return self.reply(200, {"status": "ok"})
        if url.path == "/xml":
            return self.reply(200, (FIXTURES / "order.xml").read_bytes(), "application/xml")
        if url.path == "/idoc":
            return self.reply(200, (FIXTURES / "idoc.xml").read_bytes(), "application/xml")
        if url.path == "/orders":
            if case in {"429", "503"}:
                with LOCK:
                    COUNTS[(case, run)] += 1
                    attempts = COUNTS[(case, run)]
                if attempts == 1:
                    headers = {"Retry_After": "2"} if case == "429" else {}
                    return self.reply(int(case), {"error": "injected", "attempt": attempts}, **headers)
            if case == "400":
                return self.reply(400, {"error": "invalid query"})
            if case == "timeout":
                sleep(5)
            if case == "malformed":
                return self.reply(200, b'{"not":')
            if case == "empty":
                return self.reply(204, b"")
            return self.reply(200, (FIXTURES / "orders.json").read_bytes())
        return self.reply(404, {"error": "unknown mock endpoint"})

    def do_POST(self):
        url = urlsplit(self.path)
        if url.path != "/soap":
            return self.reply(404, {"error": "unknown mock endpoint"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.reply(400, {"error": "invalid Content-Length"})
        if not 0 < length <= 65536:
            return self.reply(400, {"error": "submit a SOAP envelope up to 64 KiB"})
        self.rfile.read(length)
        fault = parse_qs(url.query).get("case", [""])[0]
        if fault in {"fault", "fault200"}:
            return self.reply(200 if fault == "fault200" else 500, SOAP_FAULT, "text/xml")
        return self.reply(200, SOAP_OK, "text/xml")


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
