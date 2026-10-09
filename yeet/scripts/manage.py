"""yeet list / yeet delete."""

from datetime import datetime

from errors import Fail, TAKEN
from names import check_name
from netlify import api, find_site, ok, show


def list_sites(_args):
    sites = []
    for page in range(1, 21):
        status, data = api("GET", f"/sites?filter=all&per_page=100&page={page}")
        if status != 200:
            raise Fail(f"listing sites failed ({status}): {show(data)}")
        if not data:
            break
        sites += data
    if not sites:
        print("no sites yet")
        return

    def local(ts):
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")

    rows = [(s["name"], s.get("ssl_url") or s["url"], local(s["updated_at"]))
            for s in sorted(sites, key=lambda s: s["updated_at"], reverse=True)]
    rows.insert(0, ("NAME", "URL", "UPDATED"))
    widths = [max(len(r[i]) for r in rows) for i in range(3)]
    for row in rows:
        print("  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip())


def delete(args):
    # check every name first so a typo doesn't leave a half-done delete
    targets = []
    for name in args.names:
        check_name(name)
        site_id = find_site(name)
        if not site_id:
            raise Fail(f"{name}.netlify.app is not one of your sites", TAKEN)
        targets.append((name, site_id))
    for name, site_id in targets:
        status, data = api("DELETE", f"/sites/{site_id}")
        if not ok(status):
            raise Fail(f"deleting {name} failed ({status}): {show(data)}")
        print(f"deleted {name}.netlify.app")
