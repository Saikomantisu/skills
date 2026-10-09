"""yeet deploy: pick or create the site, then upload the folder."""

import hashlib
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path

from errors import Fail, EXISTS, TAKEN
from names import check_name, random_name
from netlify import api, create_site, find_site, hide_badge, ok, show
from safety import safety_check

# One HTML page loading a bundle from Vite's /assets/ or CRA's /static/js/ means a single-page app.
SPA_BUNDLE = re.compile(r'<script[^>]+src="[^"]*(/assets/|/static/js/)')


def publishable(src):
    """{"/url/path": bytes}. Hidden files and folders are skipped, except .well-known/."""
    files = {}
    for root, dirs, names in os.walk(src):
        dirs[:] = [d for d in dirs if d != "node_modules" and (not d.startswith(".") or d == ".well-known")]
        for name in names:
            if name.startswith("."):
                continue
            path = Path(root, name)
            files["/" + path.relative_to(src).as_posix()] = path.read_bytes()
    return files


def is_spa(files):
    pages = [p for p in files if p.endswith(".html")]
    return pages == ["/index.html"] and bool(SPA_BUNDLE.search(files["/index.html"].decode(errors="replace")))


def pick_site(name, overwrite):
    """(name, site_id): the requested site, or a new one with a generated name."""
    if name:
        check_name(name)
        site_id = find_site(name)
        if site_id and not overwrite:
            raise Fail(f"{name}.netlify.app is already one of your sites; rerun with --overwrite to replace it", EXISTS)
        if not site_id:
            site_id = create_site(name)
            if not site_id:
                raise Fail(f"{name}.netlify.app is taken by someone else", TAKEN)
        return name, site_id

    for attempt in range(15):
        name = random_name(with_number=attempt >= 5)  # add a number once plain names keep colliding
        site_id = create_site(name)
        if site_id:
            return name, site_id
    raise Fail("could not find a free name after 15 tries")


def upload(site_id, files):
    """Digest deploy: send path -> sha1, then upload only what Netlify asks for.

    (Zip uploads make Netlify serve "/" as text/plain.)
    """
    digests = {path: hashlib.sha1(content).hexdigest() for path, content in files.items()}
    status, data = api("POST", f"/sites/{site_id}/deploys", {"files": digests})
    if not ok(status):
        raise Fail(f"creating deploy failed ({status}): {show(data)}")
    deploy_id, required = data["id"], set(data.get("required") or [])

    for path, content in files.items():
        if digests[path] in required:
            status, data = api("PUT", f"/deploys/{deploy_id}/files{urllib.parse.quote(path)}", raw=content)
            if not ok(status):
                raise Fail(f"uploading {path} failed ({status}): {show(data)}")
    return deploy_id


def wait_until_ready(deploy_id):
    state = None
    for _ in range(60):
        status, data = api("GET", f"/deploys/{deploy_id}")
        state = data.get("state") if isinstance(data, dict) else None
        if state == "ready":
            return
        if state == "error":
            raise Fail(f"deploy failed: {data.get('error_message') or 'unknown'}")
        time.sleep(2)
    raise Fail(f"deploy still '{state}' after 2 minutes; check https://app.netlify.com")


def deploy(args):
    src = Path(args.folder).expanduser().resolve()
    if not src.is_dir():
        raise Fail(f"folder not found: {src}")
    if not (src / "index.html").is_file():
        raise Fail(f"no index.html in {src} (point at the built output folder)")
    safety_check(src)

    name, site_id = pick_site(args.name, args.overwrite)

    if not hide_badge(site_id):
        print("warning: could not hide the Netlify badge; turn it off at "
              f"https://app.netlify.com/projects/{name}/configuration/general", file=sys.stderr)

    files = publishable(src)
    spa = is_spa(files) if args.spa is None else args.spa
    if spa and "/_redirects" not in files:
        files["/_redirects"] = b"/*  /index.html  200\n"
        print("single-page app: unknown paths will serve index.html", file=sys.stderr)

    wait_until_ready(upload(site_id, files))
    print(f"https://{name}.netlify.app")
