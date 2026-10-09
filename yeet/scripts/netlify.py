"""Thin wrapper over the Netlify API."""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from errors import Fail

API = "https://api.netlify.com/api/v1"
TOKEN_FILE = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "yeet" / "token"


def token():
    tok = os.environ.get("NETLIFY_AUTH_TOKEN", "").strip()
    if not tok and TOKEN_FILE.is_file():
        tok = TOKEN_FILE.read_text().strip()
    if not tok:
        raise Fail(f"no token: put a Netlify personal access token in {TOKEN_FILE}")
    return tok


def api(method, path, body=None, raw=None):
    """Call the API; returns (status, parsed JSON or None). Never raises on HTTP errors."""
    headers = {"Authorization": f"Bearer {token()}", "User-Agent": "yeet"}
    if body is not None:
        raw = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    elif raw is not None:
        headers["Content-Type"] = "application/octet-stream"
    req = urllib.request.Request(API + path, data=raw, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as res:
            status, text = res.status, res.read()
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read()
    except urllib.error.URLError as e:
        raise Fail(f"can't reach Netlify: {e.reason}")
    try:
        return status, json.loads(text) if text else None
    except ValueError:
        return status, text.decode(errors="replace")


def ok(status):
    return 200 <= status < 300


def show(data):
    return json.dumps(data) if isinstance(data, (dict, list)) else str(data)


def find_site(name):
    """Site ID if <name> is one of your sites, else None."""
    status, data = api("GET", f"/sites/{name}.netlify.app")
    return data["id"] if status == 200 else None


def create_site(name):
    """Site ID, or None if the name is taken."""
    status, data = api("POST", "/sites", {"name": name})
    if ok(status):
        return data["id"]
    if status == 422:
        return None
    raise Fail(f"creating site failed ({status}): {show(data)}")


def hide_badge(site_id):
    """Turn off the "Powered by Netlify" badge. Returns False if it didn't take.

    Undocumented field (the docs say the badge is UI-only), so callers should only warn on failure.
    """
    status, data = api("PATCH", f"/sites/{site_id}", {"built_with_badge_enabled": False})
    return ok(status) and isinstance(data, dict) and data.get("built_with_badge_enabled") is False
