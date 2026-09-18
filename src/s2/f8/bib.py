"""Minimal BibTeX reader/writer for the brace-delimited form of docs/references.bib."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_HEAD = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.S)


@dataclass
class Entry:
    kind: str
    key: str
    fields: dict = field(default_factory=dict)   # lower-case name -> raw value
    order: list = field(default_factory=list)
    line: int = 0                                 # 1-based line of the '@'


def _read_braced(text: str, i: int) -> tuple[str, int]:
    """text[i] == '{'; return (inner, index after the matching '}')."""
    assert text[i] == "{"
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    raise ValueError(f"unbalanced braces starting at offset {i}")


def parse(text: str) -> list[Entry]:
    entries = []
    pos = 0
    while True:
        m = _HEAD.search(text, pos)
        if not m:
            break
        e = Entry(kind=m.group(1).lower(), key=m.group(2), line=text.count("\n", 0, m.start()) + 1)
        j = m.end()
        while True:
            fm = re.compile(r"\s*(\w+)\s*=\s*").match(text, j)
            if not fm:
                break
            name = fm.group(1).lower()
            j = fm.end()
            if text[j] == "{":
                val, j = _read_braced(text, j)
            elif text[j] == '"':
                k = text.index('"', j + 1)
                val, j = text[j + 1:k], k + 1
            else:
                vm = re.compile(r"[^,}\s]+").match(text, j)
                val, j = vm.group(0), vm.end()
            e.fields[name] = val
            e.order.append(name)
            cm = re.compile(r"\s*,").match(text, j)
            if cm:
                j = cm.end()
        end = re.compile(r"\s*\}").match(text, j)
        if not end:
            raise ValueError(f"entry {e.key} not closed near offset {j}")
        pos = end.end()
        entries.append(e)
    return entries


_ESC = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "$": r"\$"}


def escape(value: str) -> str:
    """Escape LaTeX specials outside of already-escaped sequences."""
    out = []
    prev = ""
    for ch in value:
        if ch in _ESC and prev != "\\":
            out.append(_ESC[ch])
        else:
            out.append(ch)
        prev = ch
    s = "".join(out)
    depth = 0
    for ch in s:
        depth += (ch == "{") - (ch == "}")
        if depth < 0:
            break
    if depth != 0:
        s = s.replace("{", "(").replace("}", ")")
    return s


VERBATIM_FIELDS = {"doi", "url", "eprint"}


def format_entry(kind: str, key: str, fields: list[tuple[str, str]]) -> str:
    body = []
    for name, value in fields:
        if value is None or value == "":
            continue
        v = value if name in VERBATIM_FIELDS else escape(str(value))
        body.append(f"  {name} = {{{v}}}")
    return f"@{kind}{{{key},\n" + ",\n".join(body) + "\n}\n"
