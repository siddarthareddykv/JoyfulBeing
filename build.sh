# JoyfulBeing — Deploy Script
# Supports deployment when Render is set to Python, Shell, or Go.

set -e

# If Go is available, compile binary
if command -v go >/dev/null 2>&1; then
    echo "==> Go detected. Building Go binary..."
    go build -ldflags="-s -w" -o bin/joyfulbeing .
else
    echo "==> Go not found in current environment. Installing Go..."
    export GOLANG_VERSION=1.23.2
    curl -fsSL "https://go.dev/dl/go${GOLANG_VERSION}.linux-amd64.tar.gz" -o go.tar.gz
    tar -C /tmp -xzf go.tar.gz
    export PATH="/tmp/go/bin:${PATH}"
    mkdir -p bin
    go build -ldflags="-s -w" -o bin/joyfulbeing .
fi

echo "==> Build complete: bin/joyfulbeing"
