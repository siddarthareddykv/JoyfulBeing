import os
import subprocess
import sys

# 1. Compile the Go binary if not already present
binary_path = os.path.join(os.getcwd(), "bin", "joyfulbeing")
if not os.path.exists(binary_path):
    build_script = os.path.join(os.getcwd(), "build.sh")
    if os.path.exists(build_script):
        print("==> Building JoyfulBeing Go application...", flush=True)
        subprocess.run(["bash", build_script], check=True)

# 2. Start the compiled Go binary in the background
print("==> Starting JoyfulBeing Go web server...", flush=True)
go_proc = subprocess.Popen([binary_path])

# 3. WSGI proxy app for gunicorn so Render's health checks & routing work directly
import urllib.request
import urllib.error

def app(environ, start_response):
    port = os.environ.get("PORT", "5000")
    # Go server runs internally on port 5001 or fallback
    internal_port = "5001" if port != "5001" else "5002"
    path = environ.get("PATH_INFO", "/")
    query = environ.get("QUERY_STRING", "")
    url = f"http://127.0.0.1:{internal_port}{path}"
    if query:
        url += f"?{query}"
    
    headers = {}
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            h_name = key[5:].replace("_", "-").title()
            headers[h_name] = value

    method = environ.get("REQUEST_METHOD", "GET")
    data = None
    if method in ("POST", "PUT", "PATCH"):
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            data = environ["wsgi.input"].read(content_length)
        except (ValueError, KeyError):
            pass

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = f"{resp.status} OK"
            response_headers = [(k, v) for k, v in resp.getheaders()]
            start_response(status, response_headers)
            return [resp.read()]
    except urllib.error.HTTPError as e:
        status = f"{e.code} Error"
        response_headers = [(k, v) for k, v in e.headers.items()]
        start_response(status, response_headers)
        return [e.read()]
    except Exception as e:
        status = "500 Internal Server Error"
        start_response(status, [("Content-Type", "text/plain")])
        return [f"Server starting: {str(e)}".encode("utf-8")]

if __name__ == "__main__":
    if os.path.exists(binary_path):
        os.execv(binary_path, [binary_path])
