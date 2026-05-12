{% extends "base.html" %}
{% block content %}
<section class="card">
  <div class="hero">
    <div class="emoji">🏆</div>
    <h1>Αποτελέσματα</h1>
    <p>Σύνολο ψήφων: <strong>{{ total_votes }}</strong></p>
  </div>

  {% if leaderboard %}
    <div class="leaderboard">
      {% for r in leaderboard %}
        <div class="row">
          <div class="rank">#{{ loop.index }}</div>
          <div class="country">
            <strong>{{ r.country }}</strong>
            <span>{{ r.votes }} ψήφοι · Μ.Ο. {{ r.avg_score }}/40</span>
          </div>
          <div class="score">{{ r.total_score }}</div>
        </div>
      {% endfor %}
    </div>
  {% else %}
    <p class="empty">Δεν υπάρχουν ακόμα ψήφοι.</p>
  {% endif %}

  <a class="button-secondary" href="{{ url_for('vote') }}">Νέα ψήφος</a>

  <form method="post" action="{{ url_for('reset') }}" class="reset">
    <input name="password" placeholder="κωδικός reset">
    <button type="submit">Reset</button>
  </form>
</section>
{% endblock %}
