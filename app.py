import os
import sys
import subprocess
import time

print("==> JoyfulBeing startup script initialized.", flush=True)

port = os.environ.get("PORT", "10000")
print(f"==> Target port: {port}", flush=True)

# 1. Locate or compile the Go binary
binary_path = os.path.join(os.getcwd(), "bin", "joyfulbeing")
if not os.path.exists(binary_path):
    root_binary = os.path.join(os.getcwd(), "joyfulbeing")
    if os.path.exists(root_binary):
        binary_path = root_binary
    else:
        build_script = os.path.join(os.getcwd(), "build.sh")
        if os.path.exists(build_script):
            print("==> Compiling Go binary via build.sh...", flush=True)
            subprocess.run(["bash", build_script], check=True)

if not os.path.exists(binary_path):
    print("ERROR: joyfulbeing binary could not be found or built.", file=sys.stderr, flush=True)
    sys.exit(1)

# Ensure binary has execute permissions
try:
    os.chmod(binary_path, 0o755)
except Exception as e:
    print(f"==> Notice: chmod {binary_path}: {e}", flush=True)

# 2. Replace current Python process directly with the Go binary!
# This ensures joyfulbeing binds directly to 0.0.0.0:$PORT so Render's port scan succeeds immediately!
print(f"==> Executing {binary_path} directly on port {port}...", flush=True)
os.environ["PORT"] = port
sys.stdout.flush()
sys.stderr.flush()

os.execv(binary_path, [binary_path])
