"""Vendor CoreUI free icons into src/django_coreui/icons.py.

Usage: python scripts/vendor_icons.py NAME [NAME ...]

NAME is a CoreUI free icon name, with or without the prefix: ``cil-people``, ``people`` or ``cilPeople``. Each one is
read from @coreui/icons on jsDelivr (``dist/esm/free/<name>.js``, a ``["512 512", "<path .../>"]`` pair) and merged
into ``ICONS``: names are added or refreshed, never dropped, and the dict stays sorted. Only the ICONS block of
icons.py is rewritten; its header (with the CC BY 4.0 attribution) and functions are kept.
"""

import ast
import json
import re
import sys
import urllib.request
from pathlib import Path

VERSION = "3.1.0"
URL = "https://cdn.jsdelivr.net/npm/@coreui/icons@{version}/dist/esm/free/{name}.js"
ICONS_PY = Path(__file__).resolve().parents[1] / "src" / "django_coreui" / "icons.py"

_BLOCK = re.compile(r"^ICONS: dict\[str, str\] = \{\n.*?^\}\n", re.MULTILINE | re.DOTALL)
_MODULE = re.compile(r"^var cil\w+ = (\[.*\]);$", re.MULTILINE)


def normalise(name: str) -> str:
    """``cilCheckCircle``, ``check-circle`` and ``cil-check-circle`` all become ``cil-check-circle``."""
    name = re.sub(r"(?<=[a-z0-9])([A-Z])", r"-\1", name).lower()
    return name if name.startswith("cil-") else f"cil-{name}"


def parse(source: str) -> str:
    """The inner SVG markup of an @coreui/icons ESM module; only 512x512 icons are accepted."""
    match = _MODULE.search(source)
    if not match:
        raise ValueError("not an @coreui/icons module")
    view_box, markup = json.loads(match.group(1))
    if view_box != "512 512":
        raise ValueError(f"unexpected viewBox {view_box!r}")
    return markup


def fetch(name: str) -> str:
    with urllib.request.urlopen(URL.format(version=VERSION, name=name), timeout=30) as response:
        return parse(response.read().decode())


def read_icons(source: str) -> dict[str, str]:
    match = _BLOCK.search(source)
    if not match:
        raise ValueError("no ICONS block in icons.py")
    return ast.literal_eval(match.group(0).split("=", 1)[1])


def merge(existing: dict[str, str], new: dict[str, str]) -> dict[str, str]:
    merged = {**existing, **new}
    return {name: merged[name] for name in sorted(merged)}


def rewrite(source: str, icons: dict[str, str]) -> str:
    lines = "".join(f"    {json.dumps(name)}: {json.dumps(markup)},\n" for name, markup in icons.items())
    block = "ICONS: dict[str, str] = {\n" + lines + "}\n"
    return _BLOCK.sub(lambda _: block, source, count=1)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    source = ICONS_PY.read_text()
    new = {}
    for name in map(normalise, argv):
        new[name] = fetch(name)
        print(f"vendored {name}")
    ICONS_PY.write_text(rewrite(source, merge(read_icons(source), new)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
