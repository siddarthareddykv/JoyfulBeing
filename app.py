import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

# Internal port where Go runs (avoiding PORT which gunicorn binds to)
INTERNAL_PORT = "5005"

# 1. Compile the Go binary if not present
binary_path = os.path.join(os.getcwd(), "bin", "joyfulbeing")
if not os.path.exists(binary_path):
    root_binary = os.path.join(os.getcwd(), "joyfulbeing")
    if os.path.exists(root_binary):
        binary_path = root_binary
    else:
        build_script = os.path.join(os.getcwd(), "build.sh")
        if os.path.exists(build_script):
            print("==> Building JoyfulBeing Go application...", flush=True)
            subprocess.run(["bash", build_script], check=True)

# 2. Launch the Go application in the background on INTERNAL_PORT
go_env = os.environ.copy()
go_env["PORT"] = INTERNAL_PORT
print(f"==> Launching JoyfulBeing Go binary on 127.0.0.1:{INTERNAL_PORT}...", flush=True)
go_proc = subprocess.Popen([binary_path], env=go_env)

# 3. WSGI proxy application for Gunicorn
def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    query = environ.get("QUERY_STRING", "")
    url = f"http://127.0.0.1:{INTERNAL_PORT}{path}"
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
    
    # Retry loop while Go starts up
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = f"{resp.status} OK"
                response_headers = [(k, v) for k, v in resp.getheaders()]
                start_response(status, response_headers)
                return [resp.read()]
        except urllib.error.HTTPError as e:
            status = f"{e.code} Error"
            response_headers = [(k, v) for k, v in e.headers.items()]
            start_response(status, response_headers)
            return [e.read()]
        except Exception:
            if attempt < 4:
                time.sleep(0.5)
                continue
            status = "503 Service Unavailable"
            start_response(status, [("Content-Type", "text/plain")])
            return [b"JoyfulBeing Go server is starting up. Please refresh in a moment."]

if __name__ == "__main__":
    if os.path.exists(binary_path):
        os.execv(binary_path, [binary_path])
