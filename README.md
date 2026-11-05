# 🌿 JoyfulBeing — Go (Golang) Production Edition

This is the high-performance, external-purpose **Go (Golang)** edition of **JoyfulBeing**. It preserves 100% of the serene frontend styling, pastel color palettes, wisdom calendar, rituals, mantras, and AI chat bot, while packaging everything into a self-contained, production-ready binary with zero runtime dependencies.

---

## 🚀 Key Advantages of the Go Architecture

1. **Ultra-Low Resource Footprint**: Starts in under 20 milliseconds and consumes ~25 MB of RAM (versus 300+ MB in Python).
2. **Single Binary Deployment**: Compiles directly into a single executable (`joyfulbeing.exe` on Windows or `joyfulbeing` on Linux).
3. **High Concurrency & External Ready**:
   - Built on Go's lightweight goroutines and `chi` router.
   - Pure Go SQLite (`modernc.org/sqlite`) running in **WAL (Write-Ahead Logging)** mode for concurrent reads/writes without database locks.
   - Cross-Origin Resource Sharing (**CORS**) enabled for external web and mobile clients.
   - Built-in `/healthz` endpoint for cloud load balancers and orchestrators.
4. **Resilient AI & LLM Handling**:
   - Direct integration with local Ollama or remote cloud LLM endpoints.
   - Built-in graceful fallback to calm, thoughtful local responses if the LLM is offline or busy.

---

## 📦 Project Structure

```
Joyful Being/
├── cmd/
├── internal/
│   ├── agent/         # Program manager multi-agent system & feature routing
│   ├── data/          # 270+ quotes, Gita verses, rituals, mantras, month themes
│   ├── db/            # Pure Go SQLite driver with WAL mode
│   ├── models/        # Shared domain and API structs
│   ├── ollama/        # Ollama HTTP client and calm local fallback engine
│   └── sentiment/     # Native Go sentiment polarity analysis engine
├── static/            # CSS stylesheets, logos, manifests, images
├── templates/         # Pongo2 (Django/Jinja-compatible) HTML templates
├── joyfulbeing.exe    # Compiled single production binary (23 MB)
├── main.go            # Server entrypoint, chi router, route handlers
├── go.mod             # Go module definition
├── go.sum             # Dependency hashes
├── Dockerfile         # Multi-stage production container build
├── docker-compose.yml # Compose file with volume persistence
└── .env.example       # Sample environment configuration
```

---

## 🏃 Running Locally

### 1. Run the Pre-compiled Binary
```powershell
.\joyfulbeing.exe
```
The server will start immediately on **http://127.0.0.1:5000**.

### 2. Run with Go Source Code
```powershell
go run main.go
```

### 3. Rebuild the Executable
```powershell
go build -ldflags="-s -w" -o joyfulbeing.exe main.go
```

---

## 🌐 Routes & Endpoints

### Web Pages (Exact UI & Serene Aesthetics)
| Route | Description |
| :--- | :--- |
| `GET /` | Home sanctuary with daily quote, action, and Gita verse |
| `GET /calendar` | 365-day Wisdom Calendar with seasonal color themes |
| `GET /programs` | Global wellness events & curated workshops |
| `GET /mantras` | Sanskrit mantras with meanings & pronunciations |
| `GET /rituals` | Daily Vedic rituals and practice guides |
| `GET /stress` | Guided stress relief & breathing orb |
| `GET /emotions` | Emotional reflection & journaling tools |
| `GET /ideas` | Compassionate kindness micro-practices |
| `GET /about` | Philosophy & background |

### External APIs
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/chat` | `POST` | Namaskaram chatbot (`{"message": "I feel stressed"}`) |
| `/api/program-manager` | `POST` | Agent router for mood, sentiment, reports & reviews |
| `/api/mantra` | `GET` | Random Sanskrit mantra JSON |
| `/api/ritual` | `GET` | Random Vedic ritual JSON |
| `/api/llm-status` | `GET` | Ollama connection and model status |
| `/healthz` | `GET` | Production health check (`{"status": "healthy"}`) |

---

## 🐳 External Deployment (Docker)

To deploy to any cloud provider (AWS, Google Cloud, DigitalOcean, Fly.io, Railway, VPS):

```bash
# Build the Docker container
docker build -t joyfulbeing:latest .

# Run container with persistent data
docker run -d -p 8080:8080 -v jb-data:/app/data --name joyfulbeing-web joyfulbeing:latest
```

Or using Docker Compose:
```bash
docker-compose up -d
```

