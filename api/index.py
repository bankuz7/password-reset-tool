from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import parse_qs

HTML = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Password Reset • Vanraj College</title>
  <style>
    :root {
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --bg: #f1f5f9;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: var(--bg);
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 1.25rem;
      color: var(--text);
    }
    .card {
      background: var(--card);
      width: 100%;
      max-width: 420px;
      padding: 2rem;
      border-radius: 16px;
      box-shadow: 0 8px 30px rgba(0,0,0,.08);
    }
    h1 { font-size: 1.35rem; font-weight: 700; margin-bottom: .25rem; }
    .sub { color: var(--muted); font-size: .875rem; margin-bottom: 1.75rem; }
    label { display: block; font-size: .8125rem; font-weight: 500; margin: 1rem 0 .4rem; }
    input {
      width: 100%; padding: .7rem .9rem; border: 1px solid var(--border);
      border-radius: var(--radius); font-size: .95rem;
      transition: border-color .15s, box-shadow .15s;
    }
    input:focus {
      outline: none; border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37,99,235,.15);
    }
    button {
      width: 100%; margin-top: 1.75rem; padding: .8rem;
      background: var(--primary); color: #fff; border: none;
      border-radius: var(--radius); font-size: 1rem; font-weight: 600; cursor: pointer;
    }
    button:hover { background: var(--primary-hover); }
    button:disabled { opacity: .65; cursor: not-allowed; }
    #result {
      display: none; margin-top: 1.25rem; padding: .85rem 1rem;
      border-radius: var(--radius); font-size: .875rem; line-height: 1.45;
    }
    .ok  { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .err { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .note {
      margin-top: 1.5rem; padding: .85rem; background: #f8fafc;
      border-radius: 10px; font-size: .78rem; color: var(--muted); line-height: 1.5;
    }
    code { background: #e2e8f0; padding: .1rem .35rem; border-radius: 4px; font-size: .75rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Password Reset</h1>
    <p class="sub">Vanraj College Payment Portal</p>
    <label for="email">Email Address</label>
    <input id="email" type="email" placeholder="registered@email.com" autocomplete="email" required>
    <label for="token">Reset Token</label>
    <input id="token" type="text" placeholder="Email link se token" required>
    <label for="password">New Password</label>
    <input id="password" type="password" placeholder="Naya password (min 6)" autocomplete="new-password" required>
    <button id="btn" onclick="resetPassword()">Reset Password</button>
    <div id="result"></div>
    <div class="note">
      Token email ke reset link se aata hai:<br>
      <code>/password/reset/<b>yahan-wala-token</b></code>
    </div>
  </div>
  <script>
    const $ = id => document.getElementById(id);
    async function resetPassword() {
      const email = $('email').value.trim();
      const token = $('token').value.trim();
      const password = $('password').value.trim();
      const btn = $('btn');
      const result = $('result');
      if (!email || !token || !password) return show(result, 'Sab fields bharna zaroori hai', false);
      if (password.length < 6) return show(result, 'Password kam se kam 6 characters ka hona chahiye', false);
      btn.disabled = true; btn.textContent = 'Processing...'; result.style.display = 'none';
      try {
        const res = await fetch(window.location.pathname || '/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, token, password })
        });
        const data = await res.json();
        show(result, data.message, data.success);
      } catch (err) {
        show(result, 'Network error: ' + err.message, false);
      }
      btn.disabled = false; btn.textContent = 'Reset Password';
    }
    function show(el, msg, ok) {
      el.style.display = 'block';
      el.className = ok ? 'ok' : 'err';
      el.textContent = msg;
    }
    document.addEventListener('keydown', e => { if (e.key === 'Enter') resetPassword(); });
  </script>
</body>
</html>"""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body)
        except Exception:
            data = parse_qs(body)
            data = {k: v[0] for k, v in data.items()}

        email = data.get("email", "").strip()
        token = data.get("token", "").strip()
        password = data.get("password", "").strip()

        if not email or not token or not password:
            return self._json(400, {
                "success": False,
                "message": "Email, Token aur Password sab required hain"
            })

        try:
            BASE_URL = "https://payment.vaccdharampur.org"
            session = requests.Session()

            reset_url = f"{BASE_URL}/password/reset/{token}"
            resp = session.get(reset_url, timeout=15)

            if resp.status_code != 200:
                raise Exception(f"Reset page open nahi hua (Status: {resp.status_code}). Token expire ya invalid ho sakta hai.")

            csrf_token = None
            if 'name="_token"' in resp.text:
                start = resp.text.find('name="_token" value="') + len('name="_token" value="')
                end = resp.text.find('"', start)
                csrf_token = resp.text[start:end]

            if not csrf_token:
                raise Exception("CSRF token nahi mila. Page structure change ho sakta hai.")

            payload = {
                "_token": csrf_token,
                "token": token,
                "email": email,
                "password": password,
                "password_confirmation": password
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": reset_url,
                "Origin": BASE_URL
            }

            post_resp = session.post(
                f"{BASE_URL}/password/reset",
                data=payload,
                headers=headers,
                allow_redirects=True,
                timeout=15
            )

            text_lower = post_resp.text.lower()
            final_url = post_resp.url.lower()

            success = (
                "password has been reset" in text_lower or
                "your password has been reset" in text_lower or
                "password reset successfully" in text_lower or
                final_url.rstrip("/").endswith("/login") or
                "/login" in final_url
            )

            message = "✅ Password reset successful! Ab naye password se login karo." if success else "❌ Reset fail hua."

            if not success:
                if "we can't find a user with that e-mail address" in text_lower:
                    message = "❌ Is email se koi account nahi mila."
                elif "token" in text_lower and ("invalid" in text_lower or "expired" in text_lower):
                    message = "❌ Reset token invalid ya expire ho gaya hai. Naya link mangwao."
                elif "password" in text_lower and "confirmation" in text_lower:
                    message = "❌ Password confirmation match nahi kar raha."

            return self._json(200, {
                "success": success,
                "message": message,
                "status_code": post_resp.status_code,
                "final_url": post_resp.url
            })

        except Exception as e:
            return self._json(500, {
                "success": False,
                "message": f"Error: {str(e)}"
            })

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _json(self, status, data):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
