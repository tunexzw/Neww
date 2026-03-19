# ---------------------------------------------------
# File Name: App.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# Created: 2025-11-21
# Last Modified: 2025-11-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

from flask import Flask, render_template_string
from config import PORT
from MyselfNeon.web_verify import decode_verify_slug

app = Flask(__name__)

LANDING_PAGE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>SaveRestriction Bot</title>
  <style>
    :root {
      --bg: #060816;
      --card: rgba(14, 18, 38, 0.84);
      --card-border: rgba(139, 92, 246, 0.28);
      --blue: #3b82f6;
      --purple: #a855f7;
      --text: #f8fbff;
      --muted: #a7b0d0;
      --glow: 0 0 30px rgba(91, 141, 255, 0.28), 0 0 60px rgba(168, 85, 247, 0.18);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(59,130,246,.22), transparent 26%),
        radial-gradient(circle at top right, rgba(168,85,247,.24), transparent 28%),
        radial-gradient(circle at bottom center, rgba(59,130,246,.18), transparent 30%),
        linear-gradient(180deg, #040612 0%, #080b1d 45%, #04050d 100%);
      overflow-x: hidden;
    }
    body::before, body::after {
      content: '';
      position: fixed;
      width: 340px;
      height: 340px;
      border-radius: 50%;
      filter: blur(70px);
      z-index: 0;
      opacity: .55;
      pointer-events: none;
    }
    body::before { background: rgba(59,130,246,.28); top: -80px; left: -60px; }
    body::after { background: rgba(168,85,247,.28); top: 20px; right: -70px; }
    .container { position: relative; z-index: 1; width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 60px; }
    .hero, .section-card, .footer-card {
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 28px;
      box-shadow: var(--glow);
      backdrop-filter: blur(18px);
    }
    .hero {
      display: grid;
      grid-template-columns: 1.25fr .75fr;
      gap: 24px;
      align-items: center;
      padding: 34px;
    }
    .kicker {
      display: inline-block;
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(59,130,246,.14);
      border: 1px solid rgba(96,165,250,.28);
      color: #bfe1ff;
      font-size: 14px;
      margin-bottom: 16px;
    }
    h1 { font-size: clamp(2.6rem, 7vw, 5.5rem); margin: 0 0 12px; line-height: 1.02; }
    .accent { background: linear-gradient(90deg, #ffffff 10%, #a5b4fc 45%, #c084fc 100%); -webkit-background-clip: text; color: transparent; }
    .hero p { color: var(--muted); font-size: clamp(1rem, 2vw, 1.24rem); line-height: 1.7; max-width: 680px; }
    .cta-row { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 26px; }
    .btn {
      text-decoration: none;
      color: white;
      padding: 14px 22px;
      border-radius: 14px;
      font-weight: 700;
      min-width: 180px;
      text-align: center;
      transition: .25s ease;
      border: 1px solid rgba(255,255,255,.14);
    }
    .btn.primary { background: linear-gradient(135deg, #1d4ed8, #2563eb 55%, #3b82f6); box-shadow: 0 14px 30px rgba(37,99,235,.28); }
    .btn.secondary { background: linear-gradient(135deg, #7c3aed, #9333ea 55%, #c026d3); box-shadow: 0 14px 30px rgba(147,51,234,.26); }
    .btn:hover { transform: translateY(-2px) scale(1.01); }
    .bot-visual {
      position: relative;
      min-height: 340px;
      border-radius: 24px;
      background: radial-gradient(circle at 50% 10%, rgba(99,102,241,.38), transparent 34%), rgba(6,10,24,.72);
      border: 1px solid rgba(129,140,248,.18);
      display: grid;
      place-items: center;
      overflow: hidden;
    }
    .orb, .orb2 {
      position: absolute; border-radius: 50%; filter: blur(18px); opacity: .85;
    }
    .orb { width: 110px; height: 110px; background: rgba(59,130,246,.65); left: 14%; top: 18%; }
    .orb2 { width: 130px; height: 130px; background: rgba(168,85,247,.6); right: 10%; top: 14%; }
    .bot {
      width: min(260px, 64%);
      aspect-ratio: 1/1.08;
      border-radius: 34px;
      background: linear-gradient(180deg, rgba(191,219,254,.95), rgba(129,140,248,.92));
      box-shadow: 0 24px 55px rgba(33, 79, 196, .45);
      position: relative;
    }
    .bot::before {
      content: '';
      position: absolute;
      inset: 18% 18% 39% 18%;
      border-radius: 28px;
      background: linear-gradient(180deg, #051123, #0d1535);
      box-shadow: inset 0 0 0 2px rgba(255,255,255,.1);
    }
    .eye, .eye2, .mouth {
      position: absolute;
      z-index: 2;
      background: #53e8ff;
      box-shadow: 0 0 18px rgba(83,232,255,.95);
    }
    .eye, .eye2 { width: 18px; height: 18px; border-radius: 50%; top: 34%; }
    .eye { left: 36%; } .eye2 { right: 36%; }
    .mouth { width: 48px; height: 6px; border-radius: 999px; top: 46%; left: 50%; transform: translateX(-50%); background: white; box-shadow: none; }
    .section-title {
      display: flex; align-items: center; gap: 16px; justify-content: center;
      margin: 36px 0 20px; font-size: clamp(1.8rem, 4vw, 3rem); font-weight: 800;
    }
    .section-title::before, .section-title::after {
      content: ''; height: 4px; width: min(20vw, 160px); border-radius: 999px;
    }
    .section-title::before { background: linear-gradient(90deg, transparent, #49b7ff); }
    .section-title::after { background: linear-gradient(90deg, #c77dff, transparent); }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
    .card {
      padding: 22px;
      border-radius: 22px;
      background: rgba(12,16,34,.84);
      border: 1px solid rgba(99,102,241,.16);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.03), 0 18px 30px rgba(0,0,0,.18);
    }
    .icon {
      width: 66px; height: 66px; border-radius: 18px; display: grid; place-items: center;
      font-size: 30px; margin-bottom: 16px;
      background: linear-gradient(135deg, rgba(59,130,246,.24), rgba(168,85,247,.24));
      border: 1px solid rgba(255,255,255,.08);
      box-shadow: 0 10px 24px rgba(59,130,246,.12);
    }
    .card h3 { margin: 0 0 10px; font-size: 1.5rem; }
    .card p { margin: 0; color: var(--muted); line-height: 1.6; }
    .steps { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 18px; }
    .step { text-align: center; }
    .step-number { font-size: .92rem; color: #c4b5fd; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 8px; }
    .footer-card { margin-top: 34px; padding: 26px; text-align: center; }
    .footer-card p { color: var(--muted); margin: 10px auto 22px; max-width: 700px; }
    @media (max-width: 980px) {
      .hero { grid-template-columns: 1fr; }
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .steps { grid-template-columns: 1fr; }
    }
    @media (max-width: 640px) {
      .container { width: min(100% - 20px, 1180px); }
      .hero { padding: 22px; }
      .grid { grid-template-columns: 1fr; }
      .btn { width: 100%; }
      .bot-visual { min-height: 280px; }
    }
  </style>
</head>
<body>
  <div class=\"container\">
    <section class=\"hero\">
      <div>
        <span class=\"kicker\">⚡ Secure Telegram Access Flow</span>
        <h1><span class=\"accent\">SaveRestriction Bot</span></h1>
        <p>Unlock and save restricted Telegram content with a premium-style neon interface, fast verification flow, and smooth redirection experience inspired by the theme you shared.</p>
        <div class=\"cta-row\">
          <a class=\"btn primary\" href=\"https://t.me/SaveRestriction_oBot\" target=\"_blank\" rel=\"noreferrer\">Open Bot</a>
          <a class=\"btn secondary\" href=\"https://t.me/TuneBots\" target=\"_blank\" rel=\"noreferrer\">Join Channel</a>
        </div>
      </div>
      <div class=\"bot-visual\">
        <div class=\"orb\"></div>
        <div class=\"orb2\"></div>
        <div class=\"bot\">
          <div class=\"eye\"></div>
          <div class=\"eye2\"></div>
          <div class=\"mouth\"></div>
        </div>
      </div>
    </section>

    <h2 class=\"section-title\">Why Use This Bot?</h2>
    <section class=\"grid\">
      <article class=\"card\"><div class=\"icon\">🤖</div><h3>Easy to Use</h3><p>Simple flow for login, verification, and direct Telegram processing without confusing steps.</p></article>
      <article class=\"card\"><div class=\"icon\">🛡️</div><h3>Secure & Reliable</h3><p>Verification tokens are checked before granting access, helping protect the bot flow.</p></article>
      <article class=\"card\"><div class=\"icon\">⚡</div><h3>Fast Performance</h3><p>The verification page now auto-updates statuses and redirects in a smooth 5-second sequence.</p></article>
      <article class=\"card\"><div class=\"icon\">🔗</div><h3>Short Verify Links</h3><p>Users now receive your keep-alive domain based links in the <strong>/verify/random-code</strong> style.</p></article>
    </section>

    <h2 class=\"section-title\">How It Works</h2>
    <section class=\"steps\">
      <article class=\"card step\"><div class=\"icon\">1</div><div class=\"step-number\">Step 1</div><h3>Get Verify Link</h3><p>The bot generates a short verification URL on your keep-alive domain.</p></article>
      <article class=\"card step\"><div class=\"icon\">2</div><div class=\"step-number\">Step 2</div><h3>Security Check Screen</h3><p>The page shows your requested verification statuses with the same dark neon theme.</p></article>
      <article class=\"card step\"><div class=\"icon\">3</div><div class=\"step-number\">Step 3</div><h3>Auto Redirect</h3><p>After the 5-second staged flow, the user is redirected back to the Telegram verification deep link.</p></article>
    </section>

    <section class=\"footer-card\">
      <h2 style=\"margin:0;font-size:clamp(1.9rem,4vw,3rem);\">Stay Updated</h2>
      <p>Join the Telegram channel for bot updates, new features, and support announcements.</p>
      <a class=\"btn secondary\" href=\"https://t.me/TuneBots\" target=\"_blank\" rel=\"noreferrer\">Join @TuneBots</a>
    </section>
  </div>
</body>
</html>"""

VERIFY_PAGE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Verification Check</title>
  <style>
    :root {
      --bg: #050814;
      --card: rgba(10, 14, 32, .88);
      --border: rgba(127, 92, 255, .24);
      --text: #eef4ff;
      --muted: #adb7d5;
      --blue: #3b82f6;
      --purple: #a855f7;
      --success: #4ade80;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 22px;
      color: var(--text);
      font-family: Inter, Arial, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(59,130,246,.22), transparent 24%),
        radial-gradient(circle at top right, rgba(168,85,247,.22), transparent 24%),
        linear-gradient(180deg, #03050d 0%, #060918 50%, #03050d 100%);
    }
    .panel {
      width: min(100%, 720px);
      padding: 34px 30px;
      border-radius: 28px;
      background: var(--card);
      border: 1px solid var(--border);
      box-shadow: 0 24px 80px rgba(17, 24, 39, .45), 0 0 40px rgba(99,102,241,.15);
      text-align: center;
      position: relative;
      overflow: hidden;
    }
    .panel::before, .panel::after {
      content: '';
      position: absolute;
      width: 180px; height: 180px;
      border-radius: 50%;
      filter: blur(50px);
      opacity: .5;
      pointer-events: none;
    }
    .panel::before { background: rgba(59,130,246,.32); top: -60px; left: -60px; }
    .panel::after { background: rgba(168,85,247,.32); right: -60px; top: -40px; }
    .badge {
      display: inline-flex; align-items: center; gap: 10px;
      padding: 10px 16px; border-radius: 999px;
      background: rgba(59,130,246,.12); border: 1px solid rgba(96,165,250,.26);
      color: #c7ddff; font-weight: 600; margin-bottom: 18px;
    }
    h1 { font-size: clamp(2rem, 5vw, 3.4rem); margin: 0 0 12px; }
    p.lead { color: var(--muted); font-size: 1.05rem; line-height: 1.7; margin: 0 auto 26px; max-width: 560px; }
    .progress-shell {
      height: 12px; border-radius: 999px; background: rgba(148,163,184,.15); overflow: hidden;
      border: 1px solid rgba(148,163,184,.12); margin-bottom: 28px;
    }
    .progress-bar {
      width: 0%; height: 100%;
      background: linear-gradient(90deg, var(--blue), var(--purple));
      box-shadow: 0 0 22px rgba(96,165,250,.55);
      transition: width .8s ease;
    }
    .status-list { display: grid; gap: 14px; text-align: left; }
    .status {
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
      padding: 16px 18px; border-radius: 18px;
      background: rgba(15, 23, 42, .78); border: 1px solid rgba(99,102,241,.16);
    }
    .status strong { display: block; font-size: 1rem; }
    .status span { display: block; color: var(--muted); margin-top: 4px; font-size: .95rem; }
    .pill {
      min-width: 108px; text-align: center; padding: 10px 14px; border-radius: 999px; font-weight: 700;
      background: rgba(148,163,184,.14); color: #dbe4ff; border: 1px solid rgba(148,163,184,.16);
    }
    .pill.active { background: rgba(59,130,246,.18); color: #d9ebff; border-color: rgba(96,165,250,.28); }
    .pill.done { background: rgba(74,222,128,.14); color: #c8ffd9; border-color: rgba(74,222,128,.24); }
    .redirect-note { margin-top: 22px; color: #c4b5fd; font-weight: 600; }
    .error-box {
      padding: 16px 18px; border-radius: 18px; background: rgba(127,29,29,.28); border: 1px solid rgba(248,113,113,.28); color: #fee2e2;
    }
  </style>
</head>
<body>
  <div class=\"panel\">
    {% if valid %}
      <div class=\"badge\">🔐 Secure Verification Gateway</div>
      <h1>Verifying Your Access</h1>
      <p class=\"lead\">Please wait while we complete the security checks and redirect you to the verification confirmation link.</p>
      <div class=\"progress-shell\"><div class=\"progress-bar\" id=\"bar\"></div></div>
      <div class=\"status-list\">
        <div class=\"status\"><div><strong>Verifying your access</strong><span id=\"desc-1\">Please wait to complete security checks.</span></div><div class=\"pill active\" id=\"pill-1\">Running</div></div>
        <div class=\"status\"><div><strong>Validating your request</strong><span id=\"desc-2\">Queued for next stage.</span></div><div class=\"pill\" id=\"pill-2\">Pending</div></div>
        <div class=\"status\"><div><strong>Redirecting please wait...</strong><span id=\"desc-3\">We will open your final verification link automatically.</span></div><div class=\"pill\" id=\"pill-3\">Pending</div></div>
      </div>
      <div class=\"redirect-note\" id=\"countdown\">Redirecting in 5 seconds...</div>
    {% else %}
      <div class=\"badge\">⚠️ Verification Error</div>
      <h1>Invalid Verification Link</h1>
      <div class=\"error-box\">This verification URL is invalid or has expired. Please go back to Telegram and generate a fresh link using <strong>/verify</strong>.</div>
    {% endif %}
  </div>
  {% if valid %}
  <script>
    const stages = [
      { time: 0, bar: 22, active: 1, done: [] },
      { time: 1800, bar: 66, active: 2, done: [1] },
      { time: 3400, bar: 100, active: 3, done: [1, 2] },
      { time: 5000, redirect: true, done: [1, 2, 3] }
    ];

    const setPill = (id, state, label) => {
      const el = document.getElementById(`pill-${id}`);
      el.className = `pill ${state}`.trim();
      el.textContent = label;
    };

    stages.forEach((stage) => {
      setTimeout(() => {
        if (stage.bar !== undefined) {
          document.getElementById('bar').style.width = `${stage.bar}%`;
        }
        [1, 2, 3].forEach((id) => setPill(id, '', 'Pending'));
        (stage.done || []).forEach((id) => setPill(id, 'done', 'Done'));
        if (stage.active) {
          setPill(stage.active, 'active', stage.active === 3 ? 'Starting' : 'Running');
        }
        if (stage.redirect) {
          window.location.href = {{ redirect_url|tojson }};
        }
      }, stage.time);
    });

    let remaining = 5;
    const countdown = document.getElementById('countdown');
    const interval = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        countdown.textContent = 'Redirecting now...';
        clearInterval(interval);
      } else {
        countdown.textContent = `Redirecting in ${remaining} seconds...`;
      }
    }, 1000);
  </script>
  {% endif %}
</body>
</html>"""


@app.route('/')
def hello_world():
    return render_template_string(LANDING_PAGE)


@app.route('/verify/<slug>')
def verify_redirect(slug):
    redirect_url = decode_verify_slug(slug)
    if not redirect_url or not redirect_url.startswith(("http://", "https://")):
        return render_template_string(VERIFY_PAGE, valid=False)

    return render_template_string(VERIFY_PAGE, valid=True, redirect_url=redirect_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)


# MyselfNeon
# Don't Remove Credit 🥺
# Telegram Channel @NeonFiles
