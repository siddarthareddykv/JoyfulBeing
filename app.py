import os
import subprocess
import sys
import shutil

print("==> JoyfulBeing deployment bridge running...")

# Check if binary already built
binary_path = os.path.join(os.getcwd(), "bin", "joyfulbeing")
if not os.path.exists(binary_path):
    print("==> Compiling Go binary via build.sh...")
    subprocess.run(["bash", "build.sh"], check=True)

if os.path.exists(binary_path):
    print("==> Launching JoyfulBeing Go application...")
    os.execv(binary_path, [binary_path])
else:
    # Try looking in root directory
    root_binary = os.path.join(os.getcwd(), "joyfulbeing")
    if os.path.exists(root_binary):
        print("==> Launching JoyfulBeing Go application from root...")
        os.execv(root_binary, [root_binary])
    else:
        print("ERROR: joyfulbeing binary not found after build.", file=sys.stderr)
        sys.exit(1)
