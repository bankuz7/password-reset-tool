from http.server import BaseHTTPRequestHandler
import json, os, re, requests
from urllib.parse import parse_qs

ACCESS_PIN = os.environ.get("ACCESS_PIN", "9712")
APP_VERSION = os.environ.get("APP_VERSION", "2.4.0")
APP_CHANGELOG = "Local history: last 5 attempts (browser only, no passwords)"

PORTALS = {
    "vanraj": {
        "name": "Vanraj College",
        "base": "https://payment.vaccdharampur.org",
        "login": "https://payment.vaccdharampur.org/login",
        "fee": "https://payment.vaccdharampur.org/",
    },
    "jppacc": {
        "name": "JPPACC Student",
        "base": "https://student.jppacc.org",
        "login": "https://student.jppacc.org/login",
        "fee": "https://student.jppacc.org/",
    },
}

HTML = open.__doc__  # placeholder replaced below
