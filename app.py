import os
import sys
import datetime
import calendar as pycalendar
import random
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATABASE = "joyfulbeing.db"

# -----------------------------------------------------------------------------
# Database Setup
# -----------------------------------------------------------------------------
def init_db():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mood TEXT NOT NULL,
                sentiment REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database init notice: {e}", flush=True)

# -----------------------------------------------------------------------------
# Data Constants
# -----------------------------------------------------------------------------
month_themes = {
    1: {"name": "New Beginning", "bg": "#E3F2FD", "accent": "#1565C0", "emoji": "❄️"},
    2: {"name": "Love & Compassion", "bg": "#FCE4EC", "accent": "#AD1457", "emoji": "💕"},
    3: {"name": "Growth & Renewal", "bg": "#E8F5E9", "accent": "#2E7D32", "emoji": "🌱"},
    4: {"name": "Awakening", "bg": "#FFF8E1", "accent": "#FF8F00", "emoji": "🌸"},
    5: {"name": "Joy & Creativity", "bg": "#F3E5F5", "accent": "#6A1B9A", "emoji": "🦋"},
    6: {"name": "Harmony", "bg": "#E0F2F1", "accent": "#00695C", "emoji": "🌊"},
    7: {"name": "Radiance", "bg": "#FFF3E0", "accent": "#EF6C00", "emoji": "☀️"},
    8: {"name": "Abundance", "bg": "#F1F8E9", "accent": "#558B2F", "emoji": "🌻"},
    9: {"name": "Wisdom & Balance", "bg": "#EDE7F6", "accent": "#4527A0", "emoji": "🍂"},
    10: {"name": "Gratitude", "bg": "#FFFDE7", "accent": "#F9A825", "emoji": "🎃"},
    11: {"name": "Reflection", "bg": "#ECEFF1", "accent": "#37474F", "emoji": "🍁"},
    12: {"name": "Peace & Hope", "bg": "#E0F7FA", "accent": "#00838F", "emoji": "❄️✨"},
}

sanskrit_mantras = [
    {
        "mantra": "Om (ॐ)",
        "pronunciation": "Aum",
        "meaning": "The primordial cosmic vibration, representing universal consciousness and the essence of all reality",
        "benefits": "Deep grounding, tranquil mind, spiritual connection, meditation foundation",
        "how_to_use": "Inhale deeply and chant slowly, feeling the resonant vibration rise from your heart to the crown of your head.",
    },
    {
        "mantra": "So Hum (सो ऽहम्)",
        "pronunciation": "So-Hum (Inhale: So, Exhale: Hum)",
        "meaning": '"I am That" — the eternal unity between individual breath and universal cosmos',
        "benefits": "Effortless breath awareness, nervous system relaxation, dissolves feelings of isolation",
        "how_to_use": 'Mentally inhale "So" and gently exhale "Hum". Synchronize with your natural breathing rhythm.',
    },
    {
        "mantra": "Aham Brahmasmi (अहं ब्रह्मास्मि)",
        "pronunciation": "Ah-hum Brah-mahs-mee",
        "meaning": '"I am the Divine Consciousness" — realizing the sacred infinite nature of one\'s true Self',
        "benefits": "Dissolves fear and inner limitation, awakens courage and unshakeable inner calm",
        "how_to_use": "Repeat 108 times with mala beads. Feel yourself gently expanding beyond mental boundaries.",
    },
    {
        "mantra": "Tat Tvam Asi (तत् त्वम् असि)",
        "pronunciation": "Tat Tvam Ah-see",
        "meaning": '"Thou art That" — you are one with the universal ground of all existence',
        "benefits": "Transcends dualistic thinking, promotes deep inner peace and empathy for all beings",
        "how_to_use": "Contemplate in silence during meditation. Acknowledge the shared divinity in everyone you meet.",
    },
    {
        "mantra": "Gayatri Mantra (गायत्री मंत्र)",
        "pronunciation": "Om Bhūr Bhuvaḥ Svaḥ, Tat-Savitur Vareṇyaṃ, Bhargo Devasya Dhīmahi, Dhiyo Yo Naḥ Pracodayāt",
        "meaning": '"We meditate on the radiant glory of the Divine Light that illumines the cosmos; may it awaken our intellect and guide our spiritual vision"',
        "benefits": "Mental clarity, spiritual illumination, energetic purification, protection",
        "how_to_use": "Chant facing the morning sun or at twilight. Repeat 108 times for deep mental focus.",
    },
    {
        "mantra": "Mahamantra (महामंत्र)",
        "pronunciation": "Hare Krishna, Hare Krishna, Krishna Krishna, Hare Hare, Hare Rama, Hare Rama, Rama Rama, Hare Hare",
        "meaning": "Calling upon the supreme source of divine love, pure bliss, and inner joy",
        "benefits": "Uplifts the heart, relieves deep emotional fatigue, awakens devotional sweetness and joy",
        "how_to_use": "Chant or sing softly with an open heart. Let the melodic vibration cleanse the mind of stress.",
    },
    {
        "mantra": "Maha Mrityunjaya Mantra (महामृत्युंजय मंत्र)",
        "pronunciation": "Om Tryambakaṃ Yajāmahe Sugandhiṃ Puṣṭi-vardhanam, Urvārukam-iva Bandhanān Mṛtyor Mukṣīya Māmṛtāt",
        "meaning": '"We worship the Three-Eyed One who is fragrant and nourishes all beings. May we be liberated from the bond of mortality as effortlessly as a ripe melon separates from its vine"',
        "benefits": "Cellular rejuvenation, deep emotional healing, protection, fearlessness",
        "how_to_use": "Chant 108 times during moments of physical recovery, stress, or when seeking renewal.",
    },
    {
        "mantra": "Asatoma Sadgamaya (असतो मा सद्गमय)",
        "pronunciation": "Om Asato Mā Sad-Gamaya, Tamaso Mā Jyotir-Gamaya, Mṛtyor Mā Amṛtaṃ Gamaya, Om Śāntiḥ Śāntiḥ Śāntiḥ",
        "meaning": '"Lead me from untruth to truth, from darkness to light, from mortality to immortality. Om Peace, Peace, Peace"',
        "benefits": "Disperses mental confusion, guides life decisions, restores serenity and higher purpose",
        "how_to_use": "Chant before studying, beginning important work, or closing an evening meditation.",
    },
]

vedic_rituals = [
    {
        "name": "Surya Namaskara (Sun Salutation)",
        "time": "Early morning (sunrise preferred)",
        "duration": "10-15 minutes",
        "benefits": "Energizes body, connects with life force, improves flexibility",
        "steps": [
            "Stand facing the sunrise with hands in prayer",
            "Perform 12 salutations, synchronizing with breath",
            "Each round connects you with the sun's healing energy",
            "Feel gratitude for the light and warmth",
        ],
        "practice_tip": "Do 12 rounds for optimal benefit. Build gradually if new to practice.",
    },
    {
        "name": "Sandhya Vandana (Prayer at Twilight)",
        "time": "Sunrise and sunset",
        "duration": "20-30 minutes",
        "benefits": "Connects you with cosmic rhythms, purifies mind, builds discipline",
        "steps": [
            "Face east at sunrise, west at sunset",
            "Perform water rituals symbolizing purification",
            "Recite mantras with focused intention",
            "Meditate on the transition between day and night",
        ],
        "practice_tip": "This ancient ritual aligns you with nature's rhythms.",
    },
    {
        "name": "Pranayama (Breath Regulation)",
        "time": "Early morning or evening",
        "duration": "15-20 minutes",
        "benefits": "Purifies nadis (energy channels), calms mind, increases prana (life force)",
        "steps": [
            "Sit comfortably with spine straight",
            "Practice Nadi Shodhana (alternate nostril breathing)",
            "Follow with Ujjayi or Sama Vritti breathing",
            "End with natural breathing meditation",
        ],
        "practice_tip": "Empty your lungs fully. Quality over quantity matters.",
    },
    {
        "name": "Abhyanga (Self-Oil Massage)",
        "time": "Early morning before bath",
        "duration": "15-20 minutes",
        "benefits": "Nourishes skin, calms nervous system, improves circulation",
        "steps": [
            "Warm sesame or coconut oil slightly",
            "Apply warm oil to entire body in circular motions",
            "Massage each body part with love and intention",
            "Let oil sit for 5-10 minutes before bathing",
        ],
        "practice_tip": "This is a form of self-love and healing. Feel the nurturing energy.",
    },
    {
        "name": "Sattvic Eating (Mindful Eating)",
        "time": "All meals",
        "duration": "Varies",
        "benefits": "Purifies mind, increases clarity, improves digestion, raises consciousness",
        "steps": [
            "Eat foods in their natural form (fresh fruits, vegetables, grains)",
            "Eat mindfully, tasting each bite",
            "Avoid overeating—eat until 75% full",
            "Eat with gratitude and positive thoughts",
        ],
        "practice_tip": "Sattvic foods include: fruits, vegetables, whole grains, milk, honey, ghee, nuts.",
    },
    {
        "name": "Meditation (Dhyana)",
        "time": "Early morning or evening",
        "duration": "20-45 minutes",
        "benefits": "Connects with inner self, reduces stress, brings clarity and peace",
        "steps": [
            "Sit in quiet space with spine straight",
            "Close eyes and focus on your breath or a mantra",
            "Let thoughts pass without judgment",
            "Rest in the silence and stillness",
        ],
        "practice_tip": "Consistency matters more than duration. Even 10 minutes daily transforms.",
    },
    {
        "name": "Gratitude Ritual (Kriti Vidya)",
        "time": "Morning or before bed",
        "duration": "5-10 minutes",
        "benefits": "Shifts consciousness, attracts abundance, increases happiness",
        "steps": [
            "Sit quietly with closed eyes",
            "Recall 5 things you're grateful for today",
            "Feel the gratitude deeply in your heart",
            "Say a prayer of thanks to the universe",
        ],
        "practice_tip": "Gratitude is the fastest way to raise your vibration.",
    },
    {
        "name": "Mudra Practice (Hand Gestures)",
        "time": "Anytime",
        "duration": "5-15 minutes",
        "benefits": "Balances energy, enhances meditation, heals emotional patterns",
        "steps": [
            "Learn specific hand positions (Gyan Mudra for knowledge, etc.)",
            "Hold mudra while meditating or breathing",
            "Feel the energy shift in your body",
            "Different mudras for different intentions",
        ],
        "practice_tip": "Gyan Mudra (thumb + index finger) is easiest for beginners.",
    },
]

wisdom_quotes = [
    "In a gentle way, you can shake the world. — Mahatma Gandhi",
    "Compassion is the fragrance of the soul. — Swami Vivekananda",
    "The only true wisdom is in knowing you know nothing. — Socrates",
    "Peace comes from within. Do not seek it without. — Buddha",
    "Be the change you wish to see in the world. — Mahatma Gandhi",
    "The mind is everything. What you think you become. — Buddha",
    "Yesterday I was clever, so I wanted to change the world. Today I am wise, so I am changing myself. — Rumi",
    "Silence is the language of peace; stillness is its sanctuary. — Rumi",
]

daily_actions = [
    "Drink a glass of warm water with full, quiet attention",
    "Take 5 deep breaths, lengthening each exhale",
    "Write down 3 simple things you are grateful for right now",
    "Stretch your spine and shoulders gently for 2 minutes",
    "Spend 10 minutes in natural sunlight or near greenery",
    "Pause for one conscious breath before opening your next screen",
]

bhagavad_gita_verses = [
    "You have the right to work, but never to the fruit of work. — Bhagavad Gita 2.47",
    "Yoga is the journey of the self, through the self, to the self. — Bhagavad Gita 6.20",
    "The soul is never born, and nor does it die. — Bhagavad Gita 2.20",
    "When meditation is mastered, the mind is unwavering like the flame of a lamp in a windless place. — Bhagavad Gita 6.19",
    "A person is said to have achieved yoga when the perfectly disciplined mind gets absorbed in the infinite. — Bhagavad Gita 6.23",
]

program_seeds = [
    {
        "title": "Sunrise Breath Circle",
        "organizer": "Joyful Being Community",
        "category": "Breathwork",
        "country": "India",
        "city": "Bengaluru",
        "format": "Online",
        "price": "Free",
        "language": "English",
        "days_offset": 0,
        "hour_utc": 17,
        "minute_utc": 30,
        "duration": "30 min",
        "description": "Begin your evening with gentle breath awareness, calming pranayama, and quiet grounding.",
        "verified": True,
    },
    {
        "title": "Community Meditation for Rest",
        "organizer": "Stillpoint Collective",
        "category": "Meditation",
        "country": "United States",
        "city": "New York",
        "format": "Online",
        "price": "Donation",
        "language": "English",
        "days_offset": 0,
        "hour_utc": 20,
        "minute_utc": 0,
        "duration": "45 min",
        "description": "A guided practice for softening the nervous system, clearing mental fatigue, and entering restorative stillness.",
        "verified": True,
    },
    {
        "title": "Mindful Movement in the Park",
        "organizer": "Open Ground Wellness",
        "category": "Movement",
        "country": "United Kingdom",
        "city": "London",
        "format": "In person",
        "price": "Free",
        "language": "English",
        "days_offset": 1,
        "hour_utc": 9,
        "minute_utc": 30,
        "duration": "60 min",
        "description": "A low-pressure morning park walk, gentle mobility stretches, and somatic grounding for all levels.",
        "verified": True,
    },
    {
        "title": "Workday Reset for Teams",
        "organizer": "Joyful Being Workplace Wellness",
        "category": "Employee Wellness",
        "country": "India",
        "city": "Bengaluru",
        "format": "Online",
        "price": "Paid",
        "language": "English",
        "days_offset": 2,
        "hour_utc": 8,
        "minute_utc": 30,
        "duration": "30 min",
        "description": "A guided mid-day reset with desk posture alignment, box breathing, and focus recovery for distributed teams.",
        "audience": "For teams",
        "verified": True,
    },
    {
        "title": "Quiet Evening Yin Yoga",
        "organizer": "Casa Serena",
        "category": "Yoga",
        "country": "Brazil",
        "city": "Sao Paulo",
        "format": "Online",
        "price": "Free",
        "language": "Portuguese / English",
        "days_offset": 3,
        "hour_utc": 21,
        "minute_utc": 0,
        "duration": "50 min",
        "description": "Slow, accessible movement and restorative floor postures to close the week with ease and gratitude.",
        "verified": True,
    },
    {
        "title": "Ayurvedic Seasonal Self-Care Workshop",
        "organizer": "Prana House",
        "category": "Ayurveda",
        "country": "Sri Lanka",
        "city": "Colombo",
        "format": "In person",
        "price": "Paid",
        "language": "English",
        "days_offset": 4,
        "hour_utc": 10,
        "minute_utc": 0,
        "duration": "90 min",
        "description": "Learn simple, non-clinical daily rituals (dinacharya), herbal teas, and seasonal nourishment for vitality.",
        "verified": True,
    },
    {
        "title": "Digital Sabbath Gathering",
        "organizer": "The Gentle Hour",
        "category": "Mindfulness",
        "country": "Australia",
        "city": "Melbourne",
        "format": "Online",
        "price": "Free",
        "language": "English",
        "days_offset": 5,
        "hour_utc": 7,
        "minute_utc": 30,
        "duration": "45 min",
        "description": "Reflective prompts and practical ideas for creating a kinder, more intentional relationship with screens.",
        "verified": True,
    },
]

def get_upcoming_programs():
    now = datetime.datetime.now(datetime.timezone.utc)
    today = datetime.datetime(now.year, now.month, now.day, tzinfo=datetime.timezone.utc)
    programs = []
    for seed in program_seeds:
        dt = today + datetime.timedelta(
            days=seed["days_offset"],
            hours=seed["hour_utc"],
            minutes=seed["minute_utc"]
        )
        prog = dict(seed)
        prog["start_utc"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        prog["search_text"] = f"{seed['title']} {seed['organizer']} {seed['category']} {seed['city']} {seed['country']} {seed['format']} {seed['price']}".lower()
        prog["registration_url"] = f"mailto:contact@joyfulbeing.in?subject=Register%20for%20{seed['title'].replace(' ', '%20')}"
        programs.append(prog)
    return programs

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    daily_content = {
        "quote": random.choice(wisdom_quotes),
        "action": random.choice(daily_actions),
        "bhagavad_gita": random.choice(bhagavad_gita_verses),
        "tip": "Start your day with gratitude. It shifts your vibration instantly.",
        "affirmation": "I am peaceful and calm. My mind is clear and centered.",
    }
    return render_template("home.html", daily_content=daily_content, month_themes=month_themes)

@app.route("/calendar")
def calendar_view():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    try:
        m_param = int(request.args.get("month", month))
        if 1 <= m_param <= 12:
            month = m_param
    except Exception:
        pass

    theme_info = month_themes.get(month, {"name": "Mindfulness"})
    theme_name = theme_info["name"]

    cal = pycalendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    weeks = []
    for week in month_days:
        current_week = []
        for d in week:
            if d == 0:
                current_week.append({"Day": 0})
            else:
                is_today = (d == now.day and month == now.month and year == now.year)
                quote = wisdom_quotes[(d - 1) % len(wisdom_quotes)]
                action = daily_actions[(d - 1) % len(daily_actions)]
                current_week.append({
                    "Day": d,
                    "Quote": quote,
                    "Action": action,
                    "IsToday": is_today
                })
        weeks.append(current_week)

    return render_template(
        "calendar.html",
        weeks=weeks,
        month=month,
        month_name=pycalendar.month_name[month],
        year=year,
        theme=theme_name,
        month_themes=month_themes,
        today_day=now.day if (month == now.month and year == now.year) else 0,
        today_date=now.strftime("%Y-%m-%d"),
        today_quote=wisdom_quotes[0],
        today_action=daily_actions[0],
        months=list(range(1, 13))
    )

@app.route("/mantras")
def mantras():
    featured = random.choice(sanskrit_mantras)
    return render_template("mantras.html", mantras=sanskrit_mantras, featured_mantra=featured)

@app.route("/rituals")
def rituals():
    featured = random.choice(vedic_rituals)
    return render_template("rituals.html", rituals=vedic_rituals, featured_ritual=featured)

@app.route("/programs")
def programs():
    return render_template("programs.html", programs=get_upcoming_programs())

@app.route("/stress")
def stress():
    return render_template("stress.html")

@app.route("/emotions")
def emotions():
    return render_template("emotions.html")

@app.route("/ideas")
def ideas():
    return render_template("ideas.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/healthz")
def healthz():
    return jsonify({"status": "healthy", "service": "JoyfulBeing"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or data.get("input") or "").strip().lower()
    if not msg:
        return jsonify({"reply": "I am here to listen whenever you're ready to share."})
    
    replies = [
        "Take one gentle breath with me: inhale peace, exhale tension. You are safe in this moment.",
        "Allow your thoughts to pass like clouds. Stillness is always present beneath the noise.",
        "In a gentle way, you can meet whatever comes today with calm awareness and grace.",
    ]
    return jsonify({"reply": random.choice(replies), "source": "joyfulbeing-core"})

# -----------------------------------------------------------------------------
# App Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"🌿 JoyfulBeing starting on port {port}...", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
