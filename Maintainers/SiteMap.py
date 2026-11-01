import glob
import gzip
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path
import unicodedata
from urllib.parse import quote
from xml.sax.saxutils import escape

#settings
SITE = "https://civie.ie"

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR.parent
DATABASE_DIR = APP_DIR / "Database"
DB_PATH = Path(os.environ.get("CIVIE_DB_PATH", str(DATABASE_DIR / "civie.db")))
SITE_ROOT = Path(os.environ.get("CIVIE_SITE_ROOT", "/var/www/civie"))
OUT_DIR = SITE_ROOT / "SiteMap"
INDEX_PATH = SITE_ROOT / "sitemap.xml"
SITEMAP_FILES_BASE_URL = SITE + "/SiteMap/"
TMP_DIR = SITE_ROOT / "SiteMap_building"

MAX_URLS = 45_000                # protocol limit is 50,000
MAX_BYTES = 40 * 1024 * 1024      # protocol limit is 50 MB uncompressed
MAX_LOC_LEN = 2048              # protocol limit for a URL
WRITE_GZ = True                   # also write .gz copies of each file
FETCH_BATCH = 10_000

# Static pages (relative to SITE)
STATIC_PAGES = [
    "index.html",
    "contact.html",
    "license.html",
    "parties.html",
    "recordsearcher.html?type=votes",
    "recordsearcher.html?type=bills",
    "recordsearcher.html?type=lobbying",
    "recordsearcher.html?type=questions",
    "recordsearcher.html?type=debates",
    "recordsearcher.html?type=househistory",
    "recordsearcher.html?type=lobbyists",
    "recordsearcher.html?type=tds",
]

# (sitemap name, table, key column, URL directory, record kind)
SOURCES = [
    ("houses",    "Composition", "CompositionPrimaryKey", "houses",    "house"),
    ("tds",       "Members",     "MemberID",              "members",   "member"),
    ("bills",     "Legislation", "BillPrimaryKey",        "bills",     "bill"),
    ("votes",     "Votes",       "VotePrimaryKey",        "votes",     "vote"),
    ("lobbying",  "Lobbying",    "LobbyingPrimaryKey",    "lobbying",  "lobby"),
    ("questions", "Questions",   "QuestionPrimaryKey",    "questions", "question"),
    ("debates",   "Debates",     "DebateID",              "debates",   "debate"),
    ("lobbyists", "Lobbyist",    "LobbyistPrimaryKey",    "lobbyists", "lobbyist"),
]

# Optional <lastmod>: map sitemap name -> a REAL "last changed / date" column.
# Leave as None unless the date is accurate. Google ignores inaccurate lastmod.
# Example: "bills": "LastUpdated", "votes": "VoteDate", "debates": "DebateDate"
LASTMOD_COLUMNS = {name: None for name, *_ in SOURCES}
# ---------------------------------------------------------------------------

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


class SitemapWriter:
    HEADER = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
              b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    FOOTER = b"</urlset>\n"

    def __init__(self, name, directory):
        self.name, self.dir = name, directory
        self.files = []
        self.total = 0
        self.skipped = 0
        self._f = None
        self._cur = None
        self._count = 0
        self._bytes = 0
        self._part = 0

    def _open(self):
        self._part += 1
        self._cur = f"sitemap-{self.name}-{self._part}.xml"
        self._f = open(os.path.join(self.dir, self._cur), "wb")
        self._f.write(self.HEADER)
        self._bytes = len(self.HEADER)
        self._count = 0

    def _close(self):
        if self._f is None:
            return
        self._f.write(self.FOOTER)
        self._f.close()
        self._f = None
        self.files.append(self._cur)
        path = os.path.join(self.dir, self._cur)
        if WRITE_GZ:
            with open(path, "rb") as src, gzip.open(path + ".gz", "wb", 9) as dst:
                shutil.copyfileobj(src, dst)

    def add(self, loc, lastmod=None):
        if len(loc) > MAX_LOC_LEN:
            self.skipped += 1
            return
        lm = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        entry = f"  <url><loc>{escape(loc)}</loc>{lm}</url>\n".encode("utf-8")
        if (self._f is None or self._count >= MAX_URLS
                or self._bytes + len(entry) + len(self.FOOTER) > MAX_BYTES):
            self._close()
            self._open()
        self._f.write(entry)
        self._bytes += len(entry)
        self._count += 1
        self.total += 1

    def finish(self):
        self._close()
        return self.files


def resolve(conn, table, column):
    """Case-insensitive lookup of the real table/column names. None if missing."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view')").fetchall()
    real_table = next((r[0] for r in rows if r[0].lower() == table.lower()), None)
    if not real_table:
        return None, None
    cols = [c[1] for c in conn.execute(f'PRAGMA table_info("{real_table}")')]
    real_col = next((c for c in cols if c.lower() == column.lower()), None)
    return real_table, real_col


def resolve_col(conn, table, column):
    cols = [c[1] for c in conn.execute(f'PRAGMA table_info("{table}")')]
    return next((c for c in cols if c.lower() == column.lower()), None)


def iter_keys(conn, table, key_col, lastmod_col):
    if lastmod_col:
        json_col = resolve_col(conn, table, "JSON")
        if not json_col:
            raise RuntimeError(f"JSON column not found in {table}")
        sql = (f'SELECT "{key_col}", "{json_col}", MAX("{lastmod_col}") FROM "{table}" '
               f'WHERE "{key_col}" IS NOT NULL GROUP BY "{key_col}" '
               f'ORDER BY "{key_col}"')
    else:
        json_col = resolve_col(conn, table, "JSON")
        if not json_col:
            raise RuntimeError(f"JSON column not found in {table}")
        sql = (f'SELECT DISTINCT "{key_col}", "{json_col}", NULL FROM "{table}" '
               f'WHERE "{key_col}" IS NOT NULL ORDER BY "{key_col}"')
    cur = conn.execute(sql)
    while True:
        batch = cur.fetchmany(FETCH_BATCH)
        if not batch:
            break
        yield from batch


def record_title(kind, record):
    """Mirror the title selection in js/urls.js."""
    if kind == "bill":
        bill = record.get("bill") or {}
        title = str(bill.get("shortTitleEn") or "")
        year = bill.get("billYear")
        return f"{title} {year}" if year and str(year) not in title else title
    if kind == "vote":
        return ((record.get("division") or {}).get("debate") or {}).get("showAs", "")
    if kind == "question":
        return (record.get("question") or {}).get("showAs", "")
    if kind == "debate":
        return (record.get("debatestuff") or {}).get("title", "")
    if kind == "lobby":
        return record.get("Specific Details", "")
    if kind == "member":
        return record.get("showAs") or (record.get("member") or {}).get("showAs", "")
    if kind == "house":
        houses = [record.get("dail") or {}] + (record.get("seanad") or [])
        return " & ".join(house.get("house", "") for house in houses if house.get("house"))
    if kind == "lobbyist":
        return record.get("name", "")
    raise ValueError(f"Unsupported sitemap record kind: {kind}")


def slugify(value, max_length=70):
    """Keep slugs in sync with CivieURL.slugify() in js/urls.js."""
    text = re.sub(r"<[^>]*>", " ", str(value or ""))
    text = re.sub(r"&amp;", " and ", text, flags=re.IGNORECASE)
    text = re.sub(r"&[a-z#0-9]+;", " ", text, flags=re.IGNORECASE)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("&", " and ")
    text = re.sub(r"['’‘`]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) <= max_length:
        return text
    cut = text[:max_length]
    if text[max_length] == "-":
        return cut
    last_hyphen = cut.rfind("-")
    return cut[:last_hyphen].rstrip("-") if last_hyphen > 20 else cut.rstrip("-")


def record_url(directory, key, kind, record):
    slug = slugify(record_title(kind, record))
    path = f"/{directory}/{quote(str(key), safe='')}"
    return f"{SITE}{path}-{slug}" if slug else f"{SITE}{path}"


def main():
    if not DB_PATH.is_file():
        sys.exit(f"Database not found: {DB_PATH}")

    if os.path.isdir(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    conn = sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True)
    summary = []
    all_files = []

    # Static pages
    w = SitemapWriter("static", TMP_DIR)
    for page in STATIC_PAGES:
        w.add(f"{SITE}/{page}")
    all_files += w.finish()
    summary.append(("static", w.total, 0, "-"))

    # Database-driven pages
    for name, table, key_col, directory, kind in SOURCES:
        real_table, real_col = resolve(conn, table, key_col)
        if not real_table or not real_col:
            print(f"WARNING: {table}.{key_col} not found, skipping '{name}'")
            summary.append((name, 0, 0, "MISSING"))
            continue

        json_col = resolve_col(conn, real_table, "JSON")
        if not json_col:
            print(f"WARNING: {table}.JSON not found, skipping '{name}'")
            summary.append((name, 0, 0, "MISSING JSON"))
            continue

        lm_col = None
        if LASTMOD_COLUMNS.get(name):
            lm_col = resolve_col(conn, real_table, LASTMOD_COLUMNS[name])
            if not lm_col:
                print(f"WARNING: lastmod column {LASTMOD_COLUMNS[name]} not found "
                      f"in {real_table}, continuing without lastmod")

        w = SitemapWriter(name, TMP_DIR)
        for key, record_json, lm in iter_keys(conn, real_table, real_col, lm_col):
            key_str = str(key).strip()
            if not key_str:
                w.skipped += 1
                continue
            record = json.loads(record_json)
            url = record_url(directory, key_str, kind, record)
            m = DATE_RE.match(str(lm)) if lm else None
            w.add(url, m.group(1) if m else None)
        all_files += w.finish()
        summary.append((name, w.total, w.skipped, f"{len(w.files)} file(s)"))

    conn.close()

    grand_total = sum(s[1] for s in summary)
    if grand_total == 0:
        shutil.rmtree(TMP_DIR)
        sys.exit("No URLs generated, old sitemap left untouched.")

    # Sitemap index
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for fname in all_files:
        lines.append(
            f"  <sitemap><loc>{escape(SITEMAP_FILES_BASE_URL + fname)}</loc></sitemap>"
        )
    lines.append("</sitemapindex>")
    staged_index = os.path.join(TMP_DIR, "sitemap.xml")
    with open(staged_index, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # Replace the sitemap files first, then publish the root index.
    os.makedirs(OUT_DIR, exist_ok=True)
    removed = 0
    for pattern in ("sitemap*.xml", "sitemap*.xml.gz"):
        for old in glob.glob(os.path.join(OUT_DIR, pattern)):
            os.remove(old)
            removed += 1
    for fname in all_files:
        shutil.move(os.path.join(TMP_DIR, fname), os.path.join(OUT_DIR, fname))
    os.replace(staged_index, INDEX_PATH)
    shutil.rmtree(TMP_DIR)

    # Report
    print(f"\nDeleted {removed} old sitemap file(s).\n")
    print(f"{'Sitemap':<12}{'URLs':>10}{'Skipped':>9}  Files")
    for name, total, skipped, files in summary:
        print(f"{name:<12}{total:>10,}{skipped:>9}  {files}")
    print(f"{'TOTAL':<12}{grand_total:>10,}\n")
    print("Largest files:")
    sizes = sorted(((os.path.getsize(os.path.join(OUT_DIR, f)), f)
                    for f in os.listdir(OUT_DIR) if f.endswith(".xml")), reverse=True)
    for size, f in sizes[:5]:
        print(f"  {f:<35}{size / 1024 / 1024:6.2f} MB")
    print(f"\nIndex: {INDEX_PATH}")
    print(f"Sitemap files: {OUT_DIR}")
    print("Upload sitemap.xml and the SiteMap folder to the website root.")
    print("Add this to robots.txt:")
    print(f"  Sitemap: {SITE}/sitemap.xml")


if __name__ == "__main__":
    main()