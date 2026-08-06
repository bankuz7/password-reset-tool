from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except:
            data = parse_qs(body)
            data = {k: v[0] for k, v in data.items()}

        email = data.get("email", "").strip()
        token = data.get("token", "").strip()
        password = data.get("password", "").strip()

        if not email or not token or not password:
            return self._json_response(400, {
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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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

            return self._json_response(200, {
                "success": success,
                "message": message,
                "status_code": post_resp.status_code,
                "final_url": post_resp.url
            })

        except Exception as e:
            return self._json_response(500, {
                "success": False,
                "message": f"Error: {str(e)}"
            })

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
