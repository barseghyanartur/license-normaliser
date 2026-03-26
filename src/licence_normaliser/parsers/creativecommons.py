"""Creative Commons parser - scrapes creativecommons.org for multilingual deed URLs."""

from __future__ import annotations

import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from licence_normaliser.plugins import BasePlugin, RegistryPlugin, URLPlugin

CC_LICENCE_RE = re.compile(
    r"^(by|by-nc|by-nc-nd|by-nc-sa|by-nd|by-sa|"
    r"zero|pdmark|devnations|"
    r"nc|nd|sa|sampling|nc-sa|sampling\+|nc-sampling\+|nd-nc)"
    r"/([\d.]+)"
    r"(/igo)?"
    r"(/deed\.\w+)?$",
)
VERSION_RE = re.compile(r"^[\d.]+$")


def _path_to_licence_key(path: str) -> str | None:
    m = CC_LICENCE_RE.match(path)
    if not m:
        return None
    lic_type, version, igo = m.group(1), m.group(2), m.group(3)

    prefix_map = {
        "by": "cc-by",
        "by-nc": "cc-by-nc",
        "by-nc-nd": "cc-by-nc-nd",
        "by-nc-sa": "cc-by-nc-sa",
        "by-nd": "cc-by-nd",
        "by-sa": "cc-by-sa",
        "zero": "cc0",
        "pdmark": "cc-pdm",
        "devnations": "cc-devnations",
        "nc": "cc-nc",
        "nd": "cc-nd",
        "sa": "cc-sa",
        "sampling": "cc-sampling",
        "nc-sa": "cc-nc-sa",
        "sampling+": "cc-sampling-plus",
        "nc-sampling+": "cc-nc-sampling-plus",
        "nd-nc": "cc-nd-nc",
    }
    prefix = prefix_map.get(lic_type)
    if not prefix:
        return None
    suffix = "igo" if igo else ""
    key = f"{prefix}-{version}" if VERSION_RE.match(version) else prefix
    if suffix:
        key = f"{key}-{suffix}"
    return key.lower()


class CCLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_td = False
        self.current_cell = ""
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "td":
            self.in_td = True
            self.current_cell = ""
        elif tag == "a" and self.in_td:
            href = dict(attrs).get("href") or ""
            if href:
                self.current_cell += " AHREF:" + href

    def handle_endtag(self, tag: str) -> None:
        if tag == "td":
            self.in_td = False
            self.current_row.append(self.current_cell.strip())
        elif tag == "tr":
            if self.current_row:
                self.rows.append(self.current_row)
            self.current_row = []

    def handle_data(self, data: str) -> None:
        if self.in_td:
            self.current_cell += data


def _fetch_html(url: str) -> str:
    """Fetch HTML from a hardcoded URL.

    Security note: This function uses urlopen with S310 suppression.
    It is safe because it is only called from _scrape() with hardcoded
    URL constants, never with user-supplied input.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310
        return response.read().decode("utf-8")


JURISDICTION_CODES = {
    "au",
    "at",
    "be",
    "br",
    "ca",
    "ch",
    "cl",
    "cn",
    "co",
    "cz",
    "de",
    "dk",
    "ee",
    "eg",
    "es",
    "fi",
    "fr",
    "gb",
    "gr",
    "hr",
    "hu",
    "id",
    "ie",
    "il",
    "in",
    "ir",
    "is",
    "it",
    "jp",
    "kr",
    "lt",
    "lu",
    "lv",
    "ma",
    "mt",
    "mx",
    "my",
    "nl",
    "no",
    "nz",
    "pe",
    "ph",
    "pl",
    "pt",
    "ro",
    "rs",
    "ru",
    "se",
    "si",
    "sk",
    "th",
    "tr",
    "tw",
    "ua",
    "ug",
    "us",
    "za",
    "vn",
}


def _is_international(href: str) -> bool:
    parts = href.split("/")
    return not any(p in JURISDICTION_CODES for p in parts[1:])


def _extract_deeds(html: str) -> set[str]:
    parser = CCLinkParser()
    parser.feed(html)
    deeds: set[str] = set()
    for row in parser.rows:
        if not row:
            continue
        jurisdiction = row[0]
        if jurisdiction != "English":
            continue
        for cell in row[1:]:
            for part in cell.split():
                if part.startswith("AHREF:"):
                    href = part[6:]
                    if href and _is_international(href):
                        deeds.add(href)
    return deeds


def _scrape() -> list[dict[str, str]]:
    """Scrape Creative Commons license data from hardcoded URLs.

    Security note: All URLs in this function are hardcoded constants,
    ensuring safe use of urlopen in _fetch_html().
    """
    pages = [
        "https://creativecommons.org/licenses/list.en",
        "https://creativecommons.org/publicdomain/list.en",
    ]
    all_deeds: set[str] = set()
    try:
        for page_url in pages:
            html = _fetch_html(page_url)
            all_deeds |= _extract_deeds(html)
    except Exception:
        pass

    entries: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    for href in sorted(all_deeds):
        lic_key = _path_to_licence_key(href)
        if not lic_key:
            continue
        url_path = href.rsplit("/deed.", 1)[0]
        url = f"https://creativecommons.org/licenses/{url_path}/"
        if lic_key in seen_keys:
            continue
        seen_keys.add(lic_key)
        entries.append({"license_key": lic_key, "url": url, "path": url_path})

    return entries


class CreativeCommonsParser(BasePlugin, RegistryPlugin, URLPlugin):
    id = "creativecommons"
    url = "https://creativecommons.org/licenses/list.en"
    local_path = "data/creativecommons/creativecommons.json"

    def load_registry(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        if not path.exists():
            return {}
        data: list[dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for entry in data:
            key = entry.get("license_key", "")
            if key:
                result[key.lower().strip()] = key.lower().strip()
        return result

    def load_urls(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        if not path.exists():
            return {}
        data: list[dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for entry in data:
            key = entry.get("license_key", "")
            if not key:
                continue
            canonical = key.lower().strip()
            raw_url = entry.get("url", "")
            if not raw_url:
                continue
            clean = raw_url.strip().lower().rstrip("/")
            if clean.startswith("http://"):
                clean = "https://" + clean[7:]
            result[clean] = canonical
        return result

    @classmethod
    def refresh(cls, force: bool = False) -> bool:
        target = Path(__file__).parent.parent / cls.local_path
        if target.exists() and not force:
            return True
        try:
            data = _scrape()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            return True
        except Exception:
            return False
