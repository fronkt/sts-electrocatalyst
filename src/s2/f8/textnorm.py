"""Text normalisation for registrar metadata and citation labels."""
from __future__ import annotations

import html
import re
import unicodedata

_SUBSUP = re.compile(r"\s*<((?:jats:)?(?:sub|sup))>\s*(.*?)\s*</\1>\s*", re.S | re.I)
_MATH_OPEN = re.compile(r"(?<=\S)<(mml:)?math\b", re.I)
_MATH_CLOSE = re.compile(r"</(mml:)?math>(?=[A-Za-z0-9])", re.I)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def clean_markup(s: str | None) -> str:
    """Registrar title/container -> plain text.

    ``IrO\\n<sub>2</sub>\\nSurfaces`` -> ``IrO2 Surfaces``; MathML is flattened to
    its text with a space kept on either side of the formula; entities are
    unescaped; all whitespace (including em spaces) collapses to one space.
    """
    if not s:
        return ""
    t = s
    # keep the whitespace AFTER a sub/sup group, drop the whitespace before it
    t = _SUBSUP.sub(lambda m: m.group(2) + ("" if not m.group(0)[-1:].isspace() else " "), t)
    t = _MATH_OPEN.sub(lambda m: " " + m.group(0)[0:], t)
    t = _MATH_CLOSE.sub(lambda m: m.group(0) + " ", t)
    t = _TAG.sub("", t)
    t = html.unescape(t)
    t = unicodedata.normalize("NFC", t)
    t = t.replace("​", "")
    t = _WS.sub(" ", t).strip()
    return t


def fold(s: str | None) -> str:
    """Accent-stripped, case-folded, letters-and-digits-only form for name matching."""
    if not s:
        return ""
    t = unicodedata.normalize("NFKD", s)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("ø", "o").replace("Ø", "O").replace("ł", "l").replace("đ", "d").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]", "", t.casefold())


def norm_pages(s: str | None) -> str:
    if not s:
        return ""
    t = str(s).strip()
    t = re.sub(r"\s*[‐-―−-]+\s*", "-", t)
    return t


def title_key(s: str | None) -> str:
    """Comparison key for titles: markup removed, case-folded, punctuation-insensitive."""
    t = clean_markup(s)
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", t.casefold()).strip()
