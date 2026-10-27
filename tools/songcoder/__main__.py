import sys

from .render import render

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Användning: python -m songcoder songs/<slug>")
    render(sys.argv[1])
