package main

import (
	"bytes"
	"context"
	"database/sql"
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"
	"unicode"

	"github.com/flosch/pongo2/v6"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/joho/godotenv"
	_ "modernc.org/sqlite"
)

//go:embed templates/*.html static/*
var embeddedAssets embed.FS

// ----------------------------------------------------------------------------
// Domain Models
// ----------------------------------------------------------------------------

type MonthTheme struct {
	Name   string `json:"name"`
	BG     string `json:"bg"`
	Accent string `json:"accent"`
	Emoji  string `json:"emoji"`
}

type MythologyStory struct {
	Title  string `json:"title"`
	Source string `json:"source"`
	Story  string `json:"story"`
	Lesson string `json:"lesson"`
}

type Mantra struct {
	Mantra        string `json:"mantra"`
	Pronunciation string `json:"pronunciation"`
	Meaning       string `json:"meaning"`
	Benefits      string `json:"benefits"`
	HowToUse      string `json:"how_to_use"`
}

type Ritual struct {
	Name        string   `json:"name"`
	Time        string   `json:"time"`
	Duration    string   `json:"duration"`
	Benefits    string   `json:"benefits"`
	Steps       []string `json:"steps"`
	PracticeTip string   `json:"practice_tip"`
}

type WellnessProgram struct {
	Title           string `json:"title"`
	Organizer       string `json:"organizer"`
	Category        string `json:"category"`
	Country         string `json:"country"`
	City            string `json:"city"`
	Format          string `json:"format"`
	Price           string `json:"price"`
	Language        string `json:"language"`
	StartUTC        string `json:"start_utc"`
	Duration        string `json:"duration"`
	Description     string `json:"description"`
	RegistrationURL string `json:"registration_url"`
	Audience        string `json:"audience,omitempty"`
	Verified        bool   `json:"verified"`
	SearchText      string `json:"search_text"`
}

type CalendarDay struct {
	Day     int
	Quote   string
	Action  string
	IsToday bool
}

type ChatRequest struct {
	Message string `json:"message"`
	Input   string `json:"input"`
}

type ChatResponse struct {
	Reply  string `json:"reply"`
	Source string `json:"source"`
}

type LLMStatusResponse struct {
	Available bool   `json:"available"`
	Model     string `json:"model"`
	Host      string `json:"host"`
	Message   string `json:"message"`
}

// ----------------------------------------------------------------------------
// Database (SQLite with WAL mode)
// ----------------------------------------------------------------------------

func initDB(dbPath string) (*sql.DB, error) {
	dsn := fmt.Sprintf("%s?_pragma=busy_timeout(5000)&_pragma=journal_mode(WAL)&_pragma=synchronous(NORMAL)", dbPath)
	database, err := sql.Open("sqlite", dsn)
	if err != nil {
		return nil, err
	}
	database.SetMaxOpenConns(1)

	schema := `
	CREATE TABLE IF NOT EXISTS moods (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		mood TEXT,
		ai_response TEXT,
		sentiment_score REAL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`
	if _, err := database.Exec(schema); err != nil {
		database.Close()
		return nil, err
	}
	return database, nil
}

func saveMood(database *sql.DB, mood, aiResponse string, sentimentScore float64) error {
	query := `INSERT INTO moods (mood, ai_response, sentiment_score) VALUES (?, ?, ?)`
	_, err := database.Exec(query, mood, aiResponse, sentimentScore)
	return err
}

func getWeeklyJoyIndex(database *sql.DB) float64 {
	var avg sql.NullFloat64
	err := database.QueryRow(`SELECT AVG(sentiment_score) FROM moods WHERE created_at >= datetime('now', '-7 days')`).Scan(&avg)
	if err != nil || !avg.Valid {
		return 0
	}
	return math.Round(avg.Float64*1000) / 1000
}

// ----------------------------------------------------------------------------
// Sentiment Analysis
// ----------------------------------------------------------------------------

var positiveWords = map[string]float64{
	"happy": 0.8, "joy": 0.9, "peace": 0.8, "peaceful": 0.8, "calm": 0.7,
	"good": 0.6, "great": 0.8, "grateful": 0.9, "love": 0.9, "kind": 0.7,
	"hope": 0.7, "gentle": 0.6, "relaxed": 0.7, "safe": 0.6, "radiant": 0.8,
}

var negativeWords = map[string]float64{
	"sad": 0.7, "angry": 0.8, "stress": 0.7, "stressed": 0.8, "anxious": 0.8,
	"anxiety": 0.8, "worried": 0.7, "overwhelmed": 0.8, "panic": 0.9, "hurt": 0.7,
}

func analyzeSentiment(text string) float64 {
	var total, count float64
	words := strings.FieldsFunc(strings.ToLower(text), func(r rune) bool {
		return !unicode.IsLetter(r) && !unicode.IsDigit(r)
	})

	for _, w := range words {
		if score, ok := positiveWords[w]; ok {
			total += score
			count++
		} else if score, ok := negativeWords[w]; ok {
			total -= score
			count++
		}
	}
	if count == 0 {
		return 0
	}
	res := total / count
	if res > 1 {
		res = 1
	} else if res < -1 {
		res = -1
	}
	return math.Round(res*1000) / 1000
}

// ----------------------------------------------------------------------------
// Ollama Client & Peaceful Fallbacks
// ----------------------------------------------------------------------------

const SystemPrompt = `
You are Namaskaram, a calm, compassionate guide inspired by Indian wisdom.
Your role is to gently reduce stress and emotional tension.
Rules: Speak softly and briefly (2-4 lines max). Encourage breathing and self-compassion.
`

type OllamaClient struct {
	BaseURL    string
	Model      string
	httpClient *http.Client
	mu         sync.RWMutex
	available  bool
	availMsg   string
	lastCheck  time.Time
}

func newOllamaClient(baseURL, model string) *OllamaClient {
	if baseURL == "" {
		baseURL = "http://localhost:11434"
	}
	if model == "" {
		model = "llama3.2:3b"
	}
	return &OllamaClient{
		BaseURL:    strings.TrimRight(baseURL, "/"),
		Model:      model,
		httpClient: &http.Client{Timeout: 15 * time.Second},
	}
}

func (c *OllamaClient) IsAvailable() (bool, string) {
	c.mu.RLock()
	if !c.lastCheck.IsZero() && time.Since(c.lastCheck) < 30*time.Second {
		defer c.mu.RUnlock()
		return c.available, c.availMsg
	}
	c.mu.RUnlock()

	c.mu.Lock()
	defer c.mu.Unlock()

	ctx, cancel := context.WithTimeout(context.Background(), 1500*time.Millisecond)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.BaseURL+"/api/tags", nil)
	if err != nil {
		c.available = false
		c.availMsg = err.Error()
		c.lastCheck = time.Now()
		return false, c.availMsg
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		c.available = false
		c.availMsg = err.Error()
		c.lastCheck = time.Now()
		return false, c.availMsg
	}
	defer resp.Body.Close()

	c.available = resp.StatusCode == http.StatusOK
	if c.available {
		c.availMsg = "Local Ollama available"
	} else {
		c.availMsg = fmt.Sprintf("HTTP status %d", resp.StatusCode)
	}
	c.lastCheck = time.Now()
	return c.available, c.availMsg
}

func (c *OllamaClient) Chat(ctx context.Context, userMsg string) (string, error) {
	payload := map[string]interface{}{
		"model": c.Model,
		"messages": []map[string]string{
			{"role": "system", "content": SystemPrompt},
			{"role": "user", "content": userMsg},
		},
		"stream": false,
		"options": map[string]interface{}{
			"num_predict": 120,
			"temperature": 0.4,
		},
	}

	body, _ := json.Marshal(payload)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.BaseURL+"/api/chat", bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var res struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return "", err
	}
	return strings.TrimSpace(res.Message.Content), nil
}

func generateLocalChatbotResponse(msg string) string {
	text := strings.ToLower(strings.TrimSpace(msg))
	if text == "" {
		return "I’m here to listen whenever you’re ready to share."
	}
	if strings.Contains(text, "hello") || strings.Contains(text, "namaste") || strings.Contains(text, "hi") {
		return "Hello. I’m Namaskaram 🌿. How are you feeling in your heart today?"
	}
	if strings.Contains(text, "stress") || strings.Contains(text, "anxious") || strings.Contains(text, "worried") || strings.Contains(text, "overwhelm") {
		return "I hear you. Take one gentle breath with me: inhale 4, hold 2, exhale 6. You are safe in this moment."
	}
	if strings.Contains(text, "sad") || strings.Contains(text, "lonely") || strings.Contains(text, "hurt") {
		return "It’s okay to feel this way. Your feeling is real and seen. Let’s stay with one soft breath."
	}
	if strings.Contains(text, "happy") || strings.Contains(text, "joy") || strings.Contains(text, "grateful") {
		return "That is beautiful. Stay with this gentle feeling for a moment. Keep this light with you today."
	}
	return "Thank you for sharing. I’m here with a calm presence. Take one soft breath."
}

func generateLocalGuidance(mood string) string {
	text := strings.ToLower(mood)
	if strings.Contains(text, "happy") || strings.Contains(text, "good") || strings.Contains(text, "grateful") {
		return "Stay with this light feeling. Breathing: inhale 4, hold 2, exhale 6. Joy action: share one kind thought today."
	}
	if strings.Contains(text, "stress") || strings.Contains(text, "anxious") || strings.Contains(text, "overwhelm") {
		return "You are safe right now. Breathing: inhale 4, hold 4, exhale 8 for 8 rounds. Joy action: step outside for 5 minutes."
	}
	return "Thank you for checking in with yourself. Breathing: inhale 4, hold 4, exhale 6. Joy action: drink water slowly."
}

// ----------------------------------------------------------------------------
// Application Server
// ----------------------------------------------------------------------------

type App struct {
	db           *sql.DB
	ollama       *OllamaClient
	tplSet       *pongo2.TemplateSet
	isProduction bool
}

func main() {
	_ = godotenv.Load()

	port := os.Getenv("PORT")
	if port == "" {
		port = "5000"
	}
	ollamaHost := os.Getenv("OLLAMA_HOST")
	ollamaModel := os.Getenv("OLLAMA_MODEL")
	dbPath := os.Getenv("DATABASE")
	if dbPath == "" {
		dbPath = "joyfulbeing.db"
	}

	database, err := initDB(dbPath)
	if err != nil {
		log.Fatalf("Database error: %v", err)
	}
	defer database.Close()

	app := &App{
		db:           database,
		ollama:       newOllamaClient(ollamaHost, ollamaModel),
		tplSet:       pongo2.NewSet("app_templates", pongo2.DefaultLoader),
		isProduction: os.Getenv("ENV") == "production",
	}

	// Router setup
	r := chi.NewRouter()
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	r.Use(cors.Handler(cors.Options{
		AllowedOrigins: []string{"*"},
		AllowedMethods: []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders: []string{"*"},
	}))

	// Static assets
	var staticFS http.FileSystem
	if app.isProduction {
		sub, _ := fs.Sub(embeddedAssets, "static")
		staticFS = http.FS(sub)
	} else {
		staticFS = http.Dir("static")
	}
	r.Handle("/static/*", http.StripPrefix("/static/", http.FileServer(staticFS)))

	// Web Routes
	r.Get("/", app.handleHome)
	r.Get("/calendar", app.handleCalendar)
	r.Get("/mantras", app.handleMantras)
	r.Get("/rituals", app.handleRituals)
	r.Get("/programs", app.handlePrograms)
	r.Get("/emotions", app.handleEmotions)
	r.Get("/ideas", app.handleIdeas)
	r.Get("/stress", app.handleStress)
	r.Get("/about", app.handleAbout)

	// API Routes
	r.Post("/chat", app.handleChat)
	r.Get("/api/mantra", app.handleAPIMantra)
	r.Get("/api/ritual", app.handleAPIRitual)
	r.Get("/api/llm-status", app.handleAPILLMStatus)
	r.Post("/api/program-manager", app.handleAPIProgramManager)
	r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "healthy", "version": "simple-go-1.0"})
	})

	srv := &http.Server{
		Addr:         ":" + port,
		Handler:      r,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
	}

	go func() {
		log.Printf("🌿 JoyfulBeing running on http://127.0.0.1:%s", port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down cleanly...")
	_ = srv.Shutdown(context.Background())
}

func (app *App) render(w http.ResponseWriter, r *http.Request, name string, ctx pongo2.Context) {
	if ctx == nil {
		ctx = pongo2.Context{}
	}
	ctx["request"] = map[string]interface{}{"path": r.URL.Path}

	tpl, err := app.tplSet.FromFile("templates/" + name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_ = tpl.ExecuteWriter(ctx, w)
}

// Page Handlers

func (app *App) handleHome(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "home.html", pongo2.Context{
		"month_themes": MonthThemes,
		"daily_content": map[string]string{
			"quote":         randomChoice(WisdomQuotes),
			"action":        randomChoice(DailyActions),
			"bhagavad_gita": randomChoice(BhagavadGitaVerses),
			"tip":           "Start your day with gratitude. It shifts your vibration instantly.",
		},
	})
}

func (app *App) handleCalendar(w http.ResponseWriter, r *http.Request) {
	now := time.Now()
	year := now.Year()
	month := int(now.Month())

	if mParam := r.URL.Query().Get("month"); mParam != "" {
		if mVal, err := strconv.Atoi(mParam); err == nil && mVal >= 1 && mVal <= 12 {
			month = mVal
		}
	}

	themeName := "Mindfulness"
	if theme, ok := MonthThemes[month]; ok {
		themeName = theme.Name
	}

	firstOfMonth := time.Date(year, time.Month(month), 1, 0, 0, 0, 0, time.UTC)
	lastOfMonth := firstOfMonth.AddDate(0, 1, -1)
	startWeekday := (int(firstOfMonth.Weekday()) + 6) % 7
	totalDays := lastOfMonth.Day()

	var weeks [][]CalendarDay
	var currentWeek []CalendarDay

	for i := 0; i < startWeekday; i++ {
		currentWeek = append(currentWeek, CalendarDay{Day: 0})
	}

	todayDay := 0
	var todayQuote, todayAction string
	if month == int(now.Month()) && year == now.Year() {
		todayDay = now.Day()
	}

	dayOfYearStart := firstOfMonth.YearDay()
	for day := 1; day <= totalDays; day++ {
		quoteIdx := (dayOfYearStart + day - 2) % len(WisdomQuotes)
		quote := WisdomQuotes[quoteIdx]
		action := DailyActions[quoteIdx%len(DailyActions)]
		isToday := day == todayDay

		if isToday {
			todayQuote = quote
			todayAction = action
		}

		currentWeek = append(currentWeek, CalendarDay{
			Day:     day,
			Quote:   quote,
			Action:  action,
			IsToday: isToday,
		})

		if len(currentWeek) == 7 {
			weeks = append(weeks, currentWeek)
			currentWeek = []CalendarDay{}
		}
	}

	if len(currentWeek) > 0 {
		for len(currentWeek) < 7 {
			currentWeek = append(currentWeek, CalendarDay{Day: 0})
		}
		weeks = append(weeks, currentWeek)
	}

	app.render(w, r, "calendar.html", pongo2.Context{
		"weeks":        weeks,
		"month":        month,
		"month_name":   time.Month(month).String(),
		"year":         year,
		"theme":        themeName,
		"month_themes": MonthThemes,
		"today_day":    todayDay,
		"today_date":   now.Format("2006-01-02"),
		"today_quote":  todayQuote,
		"today_action": todayAction,
		"months":       []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12},
	})
}

func toMap(v interface{}) interface{} {
	b, err := json.Marshal(v)
	if err != nil {
		return v
	}
	var out interface{}
	_ = json.Unmarshal(b, &out)
	return out
}

func (app *App) handleMantras(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "mantras.html", pongo2.Context{
		"mantras":         toMap(SanskritMantras),
		"featured_mantra": toMap(SanskritMantras[rand.Intn(len(SanskritMantras))]),
	})
}

func (app *App) handleRituals(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "rituals.html", pongo2.Context{
		"rituals":         toMap(VedicRituals),
		"featured_ritual": toMap(VedicRituals[rand.Intn(len(VedicRituals))]),
	})
}

func (app *App) handlePrograms(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "programs.html", pongo2.Context{"programs": toMap(GetUpcomingPrograms())})
}

func (app *App) handleEmotions(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "emotions.html", pongo2.Context{})
}

func (app *App) handleIdeas(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "ideas.html", pongo2.Context{})
}

func (app *App) handleStress(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "stress.html", pongo2.Context{})
}

func (app *App) handleAbout(w http.ResponseWriter, r *http.Request) {
	app.render(w, r, "about.html", pongo2.Context{})
}

// API Handlers

func (app *App) handleChat(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var req ChatRequest
	_ = json.NewDecoder(r.Body).Decode(&req)
	msg := strings.TrimSpace(req.Message)
	if msg == "" {
		msg = strings.TrimSpace(req.Input)
	}

	avail, _ := app.ollama.IsAvailable()
	if avail {
		if reply, err := app.ollama.Chat(r.Context(), msg); err == nil && reply != "" {
			_ = json.NewEncoder(w).Encode(ChatResponse{Reply: reply, Source: "ollama"})
			return
		}
	}
	_ = json.NewEncoder(w).Encode(ChatResponse{Reply: generateLocalChatbotResponse(msg), Source: "local-fallback"})
}

func (app *App) handleAPIMantra(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(SanskritMantras[rand.Intn(len(SanskritMantras))])
}

func (app *App) handleAPIRitual(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(VedicRituals[rand.Intn(len(VedicRituals))])
}

func (app *App) handleAPILLMStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	avail, msg := app.ollama.IsAvailable()
	_ = json.NewEncoder(w).Encode(LLMStatusResponse{
		Available: avail,
		Model:     app.ollama.Model,
		Host:      app.ollama.BaseURL,
		Message:   msg,
	})
}

func (app *App) handleAPIProgramManager(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var req struct {
		Input string `json:"input"`
	}
	_ = json.NewDecoder(r.Body).Decode(&req)

	score := analyzeSentiment(req.Input)
	guidance := generateLocalGuidance(req.Input)
	_ = saveMood(app.db, req.Input, guidance, score)

	_ = json.NewEncoder(w).Encode(map[string]interface{}{
		"result": map[string]interface{}{
			"guidance":        guidance,
			"sentiment_score": score,
		},
	})
}

func randomChoice(slice []string) string {
	if len(slice) == 0 {
		return ""
	}
	return slice[rand.Intn(len(slice))]
}
