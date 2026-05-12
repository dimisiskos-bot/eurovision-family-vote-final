from flask import Flask, request, redirect, url_for, flash, jsonify, render_template_string
import sqlite3
from pathlib import Path
from datetime import datetime

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "votes.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

COUNTRIES = [
    "Albania", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Belgium", "Croatia", "Cyprus", "Czechia", "Denmark",
    "Estonia", "Finland", "France", "Georgia", "Germany",
    "Greece", "Iceland", "Ireland", "Israel", "Italy",
    "Latvia", "Lithuania", "Luxembourg", "Malta", "Moldova",
    "Netherlands", "Norway", "Poland", "Portugal", "San Marino",
    "Serbia", "Slovenia", "Spain", "Sweden", "Switzerland",
    "Ukraine", "United Kingdom"
]

CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #111827; color: #f9fafb; }
.app { min-height: 100vh; padding: 18px; display: flex; justify-content: center; align-items: flex-start; }
.card { width: 100%; max-width: 520px; background: #1f2937; border: 1px solid #374151; border-radius: 26px; padding: 22px; box-shadow: 0 20px 50px rgba(0,0,0,.35); }
.hero { text-align: center; margin-bottom: 22px; }
.emoji { font-size: 46px; }
h1 { margin: 8px 0; font-size: 28px; }
p { color: #d1d5db; }
.form { display: grid; gap: 12px; }
label { font-weight: 700; margin-top: 6px; }
input, select, textarea { width: 100%; border: 1px solid #4b5563; background: #111827; color: #f9fafb; border-radius: 16px; padding: 14px; font-size: 17px; }
textarea { min-height: 90px; resize: vertical; }
input[type="range"] { padding: 0; accent-color: #facc15; }
output { justify-self: end; background: #facc15; color: #111827; font-weight: 900; padding: 6px 12px; border-radius: 999px; }
button, .button-secondary { width: 100%; border: 0; background: #facc15; color: #111827; font-size: 18px; font-weight: 900; padding: 16px; border-radius: 18px; margin-top: 12px; text-decoration: none; display: block; text-align: center; }
.link { display: block; color: #facc15; text-align: center; margin-top: 18px; font-weight: 700; }
.toast { position: fixed; top: 12px; left: 16px; right: 16px; max-width: 520px; margin: auto; background: #facc15; color: #111827; padding: 12px 16px; border-radius: 16px; font-weight: 800; z-index: 10; }
.leaderboard { display: grid; gap: 10px; }
.row { display: grid; grid-template-columns: 48px 1fr auto; gap: 12px; align-items: center; background: #111827; border: 1px solid #374151; border-radius: 18px; padding: 14px; }
.rank { background: #374151; border-radius: 14px; padding: 10px; text-align: center; font-weight: 900; }
.country span { display: block; color: #9ca3af; font-size: 14px; margin-top: 4px; }
.score { font-size: 24px; font-weight: 900; color: #facc15; }
.reset { display: grid; grid-template-columns: 1fr auto; gap: 8px; margin-top: 20px; }
.reset button { width: auto; margin-top: 0; padding-inline: 18px; background: #ef4444; color: white; }
.empty { text-align: center; }
@media (max-width: 420px) { .card { padding: 18px; border-radius: 22px; } h1 { font-size: 24px; } .row { grid-template-columns: 42px 1fr; } .score { grid-column: 2; } }
"""

BASE = """
<!doctype html>
<html lang="el">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#111827">
  <title>Eurovision Family Vote</title>
  <style>{{ css }}</style>
</head>
<body>
  <main class="app">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="toast">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}
    {{ body|safe }}
  </main>
</body>
</html>
"""

def page(body):
    return render_template_string(BASE, css=CSS, body=body)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_name TEXT NOT NULL,
                country TEXT NOT NULL,
                song_score INTEGER NOT NULL,
                stage_score INTEGER NOT NULL,
                voice_score INTEGER NOT NULL,
                impression_score INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

@app.before_request
def before_request():
    init_db()

@app.route("/", methods=["GET", "POST"])
def vote():
    if request.method == "POST":
        voter_name = request.form.get("voter_name", "").strip()
        country = request.form.get("country", "").strip()
        comment = request.form.get("comment", "").strip()

        try:
            song_score = int(request.form.get("song_score", "0"))
            stage_score = int(request.form.get("stage_score", "0"))
            voice_score = int(request.form.get("voice_score", "0"))
            impression_score = int(request.form.get("impression_score", "0"))
        except ValueError:
            flash("Λάθος βαθμολογία.")
            return redirect(url_for("vote"))

        if not voter_name or country not in COUNTRIES:
            flash("Συμπλήρωσε όνομα και χώρα.")
            return redirect(url_for("vote"))

        if any(s < 1 or s > 10 for s in [song_score, stage_score, voice_score, impression_score]):
            flash("Οι βαθμολογίες πρέπει να είναι από 1 έως 10.")
            return redirect(url_for("vote"))

        with get_conn() as conn:
            conn.execute("""
                INSERT INTO votes
                (voter_name, country, song_score, stage_score, voice_score, impression_score, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (voter_name, country, song_score, stage_score, voice_score, impression_score, comment,
                  datetime.now().isoformat(timespec="seconds")))
            conn.commit()

        flash("Η ψήφος καταχωρήθηκε!")
        return redirect(url_for("results"))

    options = "".join([f'<option value="{c}">{c}</option>' for c in COUNTRIES])
    body = f"""
    <section class="card">
      <div class="hero">
        <div class="emoji">🎤</div>
        <h1>Eurovision Family Vote</h1>
        <p>Ψήφισε από το κινητό σου. Βαθμολογία 1–10 σε κάθε κατηγορία.</p>
      </div>
      <form method="post" class="form">
        <label>Το όνομά σου</label>
        <input name="voter_name" placeholder="π.χ. Δημήτρης" required>
        <label>Χώρα</label>
        <select name="country" required>
          <option value="">Επίλεξε χώρα</option>
          {options}
        </select>
        <label>Τραγούδι</label>
        <input type="range" name="song_score" min="1" max="10" value="7" oninput="this.nextElementSibling.value=this.value"><output>7</output>
        <label>Σκηνική παρουσία</label>
        <input type="range" name="stage_score" min="1" max="10" value="7" oninput="this.nextElementSibling.value=this.value"><output>7</output>
        <label>Φωνή</label>
        <input type="range" name="voice_score" min="1" max="10" value="7" oninput="this.nextElementSibling.value=this.value"><output>7</output>
        <label>Τελική εντύπωση</label>
        <input type="range" name="impression_score" min="1" max="10" value="7" oninput="this.nextElementSibling.value=this.value"><output>7</output>
        <label>Σχόλιο προαιρετικό</label>
        <textarea name="comment" placeholder="π.χ. Καλό ρεφρέν, αδύναμη σκηνή"></textarea>
        <button type="submit">Καταχώρηση ψήφου</button>
      </form>
      <a class="link" href="/results">Δες αποτελέσματα</a>
    </section>
    """
    return page(body)

@app.route("/results")
def results():
    with get_conn() as conn:
        leaderboard = conn.execute("""
            SELECT
                country,
                COUNT(*) AS votes,
                SUM(song_score + stage_score + voice_score + impression_score) AS total_score,
                ROUND(AVG(song_score + stage_score + voice_score + impression_score), 2) AS avg_score
            FROM votes
            GROUP BY country
            ORDER BY total_score DESC, avg_score DESC, votes DESC
        """).fetchall()
        total_votes = conn.execute("SELECT COUNT(*) AS c FROM votes").fetchone()["c"]

    if leaderboard:
        rows = ""
        for i, r in enumerate(leaderboard, start=1):
            rows += f"""
            <div class="row">
              <div class="rank">#{i}</div>
              <div class="country">
                <strong>{r['country']}</strong>
                <span>{r['votes']} ψήφοι · Μ.Ο. {r['avg_score']}/40</span>
              </div>
              <div class="score">{r['total_score']}</div>
            </div>
            """
    else:
        rows = '<p class="empty">Δεν υπάρχουν ακόμα ψήφοι.</p>'

    body = f"""
    <section class="card">
      <div class="hero">
        <div class="emoji">🏆</div>
        <h1>Αποτελέσματα</h1>
        <p>Σύνολο ψήφων: <strong>{total_votes}</strong></p>
      </div>
      <div class="leaderboard">{rows}</div>
      <a class="button-secondary" href="/">Νέα ψήφος</a>
      <form method="post" action="/reset" class="reset">
        <input name="password" placeholder="κωδικός reset">
        <button type="submit">Reset</button>
      </form>
    </section>
    """
    return page(body)

@app.route("/api/results")
def api_results():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT country,
                   COUNT(*) AS votes,
                   SUM(song_score + stage_score + voice_score + impression_score) AS total_score,
                   ROUND(AVG(song_score + stage_score + voice_score + impression_score), 2) AS avg_score
            FROM votes
            GROUP BY country
            ORDER BY total_score DESC
        """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/reset", methods=["POST"])
def reset():
    if request.form.get("password", "") != "family2026":
        flash("Λάθος κωδικός reset.")
        return redirect(url_for("results"))

    with get_conn() as conn:
        conn.execute("DELETE FROM votes")
        conn.commit()

    flash("Τα αποτελέσματα μηδενίστηκαν.")
    return redirect(url_for("results"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
