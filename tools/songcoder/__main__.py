import sys

from .render import render, retag

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--tags"] and len(args) == 2:
        retag(args[1])
    elif len(args) == 1:
        render(args[0])
    else:
        raise SystemExit("Användning: python -m songcoder [--tags] songs/<slug>")
