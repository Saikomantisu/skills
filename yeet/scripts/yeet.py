#!/usr/bin/env python3
"""Put static sites live at <name>.netlify.app. Standard library only.

    yeet.py deploy <folder> [name] [--overwrite] [--spa | --no-spa]
    yeet.py list
    yeet.py delete <name> [name...]

Exit codes: 0 ok, 1 error, 3 name is already one of YOUR sites (deploy again with --overwrite),
4 name isn't available (deploy: someone else has it; delete: not one of your sites),
5 folder looks unsafe to publish (nothing was uploaded).
"""

import sys

sys.dont_write_bytecode = True  # keep __pycache__ out of the skill folder

import argparse  # noqa: E402

from deploy import deploy  # noqa: E402
from errors import Fail  # noqa: E402
from manage import delete, list_sites  # noqa: E402


def main():
    parser = argparse.ArgumentParser(prog="yeet", description="Put static sites live at <name>.netlify.app.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("deploy", help="deploy a folder")
    p.add_argument("folder")
    p.add_argument("name", nargs="?", help="subdomain; a random adjective-animal if omitted")
    p.add_argument("--overwrite", action="store_true", help="replace one of your existing sites")
    spa = p.add_mutually_exclusive_group()
    spa.add_argument("--spa", dest="spa", action="store_true", default=None, help="force single-page-app fallback")
    spa.add_argument("--no-spa", dest="spa", action="store_false", default=None, help="turn single-page-app fallback off")
    p.set_defaults(run=deploy)

    sub.add_parser("list", help="list your sites").set_defaults(run=list_sites)

    p = sub.add_parser("delete", help="permanently delete sites")
    p.add_argument("names", nargs="+")
    p.set_defaults(run=delete)

    args = parser.parse_args()
    try:
        args.run(args)
    except Fail as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(e.code)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
