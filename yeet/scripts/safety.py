"""Refuse to publish folders that look like a project root or hold secrets."""

import fnmatch
import os
import re
from pathlib import Path

from errors import Fail, UNSAFE

# Never published: anything that looks like a secret or private data.
RISKY = [".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "id_ed25519*", "id_ecdsa*",
         ".npmrc", ".netrc", ".pypirc", "*.kdbx", "credentials*.json", "service-account*.json",
         "*.sqlite", "*.db"]
PRIVATE_KEY = re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")


def walk(src):
    """Yield every file under src except node_modules/."""
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d != "node_modules"]
        for f in files:
            yield Path(root, f)


def safety_check(src):
    if (src / "package.json").exists():
        raise Fail(f"{src} has a package.json, so it looks like a project root, not build output; "
                   "build it and deploy dist/ (or similar)", UNSAFE)
    flagged = []
    for path in walk(src):
        rel = path.relative_to(src).as_posix()
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in RISKY):
            flagged.append(rel)
            continue
        try:
            with open(path, "rb") as fh:
                head = fh.read(5_000_000)
        except OSError:
            continue
        if b"\0" not in head[:8000] and PRIVATE_KEY.search(head):
            flagged.append(rel)
    if flagged:
        listing = "\n".join(f"  {f}" for f in sorted(flagged))
        raise Fail(f"refusing to publish; these look like secrets or private data:\n{listing}", UNSAFE)
