"""
URL Shortener
-------------
Shorten long URLs, generate unique short links, and redirect users to the
original URL. Uses only the Python standard library (no installs needed).

Features:
  - Validates URLs before shortening
  - Generates unique short codes (and reuses the code if a URL was already shortened)
  - Stores URL mappings in a JSON file (urls.json) next to this script
  - Built-in redirect server: open http://localhost:8000/<code> in a browser
  - Tracks click counts

Run:  python url_shortener.py
"""

import json
import random
import string
import threading
from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DATA_FILE = Path(__file__).with_name("urls.json")
HOST, PORT = "localhost", 8000
BASE_URL = f"http://{HOST}:{PORT}"
CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits

_lock = threading.Lock()


# ---------- Storage ----------

def load_urls():
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read urls file. Starting empty.")
        return {}


def save_urls(urls):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(urls, f, indent=2)
    except OSError as err:
        print(f"Error: could not save URLs ({err}).")


# ---------- Core logic ----------

def validate_url(url):
    """Return (is_valid, cleaned_url_or_error_message)."""
    url = url.strip()
    if not url:
        return False, "URL cannot be empty."
    if " " in url:
        return False, "URL cannot contain spaces."
    if "://" not in url:
        url = "https://" + url  # be forgiving: 'example.com' -> 'https://example.com'
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, "Only http and https URLs are supported."
    host = parsed.hostname
    if not host:
        return False, "URL is missing a domain name."
    if host != "localhost" and "." not in host:
        return False, f"'{host}' does not look like a valid domain."
    if host.startswith(".") or host.endswith(".") or ".." in host:
        return False, f"'{host}' is not a valid domain."
    return True, url


def generate_code(urls):
    """Generate a short code that is not already in use."""
    while True:
        code = "".join(random.choices(ALPHABET, k=CODE_LENGTH))
        if code not in urls:
            return code


def shorten(url):
    """Validate and shorten a URL. Returns (code, error)."""
    ok, result = validate_url(url)
    if not ok:
        return None, result
    with _lock:
        urls = load_urls()
        for code, entry in urls.items():  # reuse existing code for same URL
            if entry["url"] == result:
                return code, None
        code = generate_code(urls)
        urls[code] = {
            "url": result,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "clicks": 0,
        }
        save_urls(urls)
    return code, None


def resolve(code, count_click=False):
    """Return the original URL for a code, or None."""
    with _lock:
        urls = load_urls()
        entry = urls.get(code)
        if entry is None:
            return None
        if count_click:
            entry["clicks"] += 1
            save_urls(urls)
        return entry["url"]


# ---------- Redirect server ----------

PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>URL Shortener</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:560px;margin:60px auto;padding:0 16px}}
input[type=text]{{width:100%;padding:10px;font-size:16px;box-sizing:border-box}}
button{{margin-top:10px;padding:10px 18px;font-size:16px;cursor:pointer}}
.msg{{margin-top:20px;padding:12px;background:#eef6ff;border-radius:6px}}
.err{{background:#ffecec}}
</style></head><body>
<h1>URL Shortener</h1>
<form method="POST" action="/shorten">
<input type="text" name="url" placeholder="Paste a long URL here" required>
<button type="submit">Shorten</button>
</form>
{message}
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send_html(self, body, status=200):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        code = urlparse(self.path).path.strip("/")
        if not code:
            self._send_html(PAGE.format(message=""))
            return
        target = resolve(code, count_click=True)
        if target is None:
            msg = '<div class="msg err">Short link not found.</div>'
            self._send_html(PAGE.format(message=msg), status=404)
            return
        self.send_response(302)
        self.send_header("Location", target)
        self.end_headers()

    def do_POST(self):
        if self.path != "/shorten":
            self._send_html(PAGE.format(message=""), status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        url = form.get("url", [""])[0]
        code, error = shorten(url)
        if error:
            msg = f'<div class="msg err">{escape(error)}</div>'
        else:
            short = f"{BASE_URL}/{code}"
            msg = (f'<div class="msg">Short link: '
                   f'<a href="{escape(short)}">{escape(short)}</a></div>')
        self._send_html(PAGE.format(message=msg))

    def log_message(self, format, *args):  # keep the console clean
        pass


def run_server():
    try:
        server = HTTPServer((HOST, PORT), Handler)
    except OSError as err:
        print(f"Could not start server on port {PORT}: {err}")
        return
    print(f"\nServer running at {BASE_URL}")
    print("Open that address in your browser, or visit a short link like "
          f"{BASE_URL}/<code>")
    print("Press Ctrl+C to stop the server and return to the menu.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


# ---------- Menu actions ----------

def menu_shorten():
    url = input("Enter the long URL: ")
    code, error = shorten(url)
    if error:
        print(f"Invalid URL: {error}")
    else:
        print(f"Short link: {BASE_URL}/{code}")
        print("(Start the server from the menu so this link redirects.)")


def menu_expand():
    raw = input("Enter a short code or short link: ").strip()
    code = urlparse(raw).path.strip("/") if "://" in raw else raw.strip("/")
    target = resolve(code)
    print(f"Original URL: {target}" if target else "Short link not found.")


def menu_list():
    urls = load_urls()
    if not urls:
        print("No URLs shortened yet.")
        return
    print(f"\n{'Code':<8}{'Clicks':<8}{'Created':<18}Original URL")
    print("-" * 70)
    for code, e in urls.items():
        print(f"{code:<8}{e['clicks']:<8}{e['created']:<18}{e['url'][:40]}")


MENU = """
========== URL SHORTENER ==========
1. Shorten a URL
2. Look up a short link
3. List all links
4. Start redirect server
5. Exit
"""


def main():
    actions = {"1": menu_shorten, "2": menu_expand, "3": menu_list, "4": run_server}
    while True:
        print(MENU)
        try:
            choice = input("Choose an option (1-5): ").strip()
            if choice == "5":
                print("Goodbye!")
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Please enter a number from 1 to 5.")
            else:
                action()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
