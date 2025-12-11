from flask import Flask, render_template, request
from datetime import datetime
import calendar as pycalendar

app = Flask(__name__)

# -----------------------------
# MONTH THEMES (colors per month)
# -----------------------------
month_themes = {
    1:  {"bg": "#E3F2FD", "accent": "#1565C0"},
    2:  {"bg": "#FCE4EC", "accent": "#AD1457"},
    3:  {"bg": "#E8F5E9", "accent": "#2E7D32"},
    4:  {"bg": "#FFF8E1", "accent": "#FF8F00"},
    5:  {"bg": "#F3E5F5", "accent": "#6A1B9A"},
    6:  {"bg": "#E0F2F1", "accent": "#00695C"},
    7:  {"bg": "#FFF3E0", "accent": "#EF6C00"},
    8:  {"bg": "#F1F8E9", "accent": "#558B2F"},
    9:  {"bg": "#EDE7F6", "accent": "#4527A0"},
    10: {"bg": "#FFFDE7", "accent": "#F9A825"},
    11: {"bg": "#ECEFF1", "accent": "#37474F"},
    12: {"bg": "#E0F7FA", "accent": "#00838F"}
}

# -----------------------------
# Quotes for each month (Indian themed)
# -----------------------------
quotes_by_month = {
    m: [
        "“In a gentle way, you can shake the world.” — Gandhi",
        "“Compassion is the fragrance of the soul.” — Vivekananda",
        "“Be kind whenever possible. It is always possible.” — Dalai Lama",
        "“The best way to find yourself is to lose yourself in service.” — Gandhi",
        "“What you give is what you receive.” — Indian proverb"
    ] for m in range(1, 13)
}

# -----------------------------
# Actions for each month
# -----------------------------
actions_by_month = {
    m: [
        "Send a message of gratitude to someone.",
        "Help someone without expecting anything.",
        "Offer a compliment today.",
        "Listen to someone with full attention.",
        "Do something kind for yourself."
    ] for m in range(1, 13)
}

# -----------------------------
# Build Calendar Function
# -----------------------------
def build_month_calendar(year, month, quotes, actions):
    cal = pycalendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    mapping = {}
    q_list = quotes.get(month, [])
    a_list = actions.get(month, [])

    q_i, a_i = 0, 0

    for week in month_days:
        for day in week:
            if day != 0:
                mapping[day] = {
                    "quote": q_list[q_i % len(q_list)],
                    "action": a_list[a_i % len(a_list)]
                }
                q_i += 1
                a_i += 1

    return month_days, mapping, len(mapping)

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/stress")
def stress():
    return render_template("stress.html")

@app.route("/emotions")
def emotions():
    return render_template("emotions.html")

@app.route("/ideas")
def ideas():
    return render_template("ideas.html")

# -----------------------------
# CALENDAR (fixed 2026)
# -----------------------------
@app.route("/calendar")
def calendar_view():
    year = 2026
    now = datetime.now()

    month = request.args.get("month", default=now.month, type=int)
    if month < 1 or month > 12:
        month = now.month

    weeks, mapping, num_days = build_month_calendar(
        year, month, quotes_by_month, actions_by_month
    )

    month_name = pycalendar.month_name[month]
    theme = month_themes.get(month, month_themes[1])

    return render_template(
        "calendar.html",
        title=f"{month_name} 2026",
        year=year,
        month=month,
        month_name=month_name,
        weeks=weeks,
        mapping=mapping,
        theme=theme
    )


if __name__ == "__main__":
    app.run(debug=True)
