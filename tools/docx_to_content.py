#!/usr/bin/env python3
"""
Chuyen "Interview Question.docx" thanh cac partial HTML trong content/generated/.

Quy trinh:
  docx -> DocxReader (tools/docx_extract.py)
       -> dinh tuyen theo tools/topic_routes.py
       -> gom block (doan van / danh sach / code / anh)
       -> content/generated/<topic>.html

Anh trong docx duoc trich ra assets/img/. Chay:
    python tools/docx_to_content.py
"""

import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx_extract import DocxReader  # noqa: E402
from topic_routes import (  # noqa: E402
    HEADING_FIXES,
    ROUTES,
    SKIP,
    SKIP_TABS,
    SYNTHETIC_SECTIONS,
    TAB_LABELS,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(ROOT, "Interview Question.docx")
OUT_DIR = os.path.join(ROOT, "content", "generated")
IMG_DIR = os.path.join(ROOT, "assets", "img")

BULLET_PREFIXES = ("- ", "+ ", "• ", "* ", "– ", "✅ ", "❌ ", "👉 ", "📌 ")


# ------------------------------------------------------------------ helpers
def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def slugify(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "D")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "muc"


CODE_STARTERS = ("const ", "let ", "var ", "function ", "class ", "import ",
                 "export ", "return ", "async ", "await ", "public ", "private ",
                 "select ", "from ", "where ", "join ", "with ", "insert ",
                 "update ", "delete ", "create ", "npm ", "yarn ", "git ", "$ ",
                 "@", "}", ")", "{")


def is_ascii_only(text):
    """Code trong tai lieu nay hau het thuan ASCII; van xuoi tieng Viet thi khong."""
    return all(ord(c) < 128 for c in text)


def looks_like_code(text):
    """Dong nhin giong code: mo dau bang tu khoa hoac nhieu ky tu cu phap."""
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.lower().startswith(CODE_STARTERS):
        return True
    symbols = sum(stripped.count(c) for c in "{}();=><[]")
    return symbols >= 2 and len(stripped) < 200


# ------------------------------------------------------------------- inline
def inline_html(nodes):
    """Chuyen cac run cua mot doan thanh HTML inline (bold, code, link)."""
    out = []
    for node in nodes:
        if node[0] == "link":
            _, text, href = node
            out.append('<a href="{}" target="_blank" rel="noopener">{}</a>'.format(
                esc(href), esc(text.strip()) or esc(href)))
        elif node[0] == "text":
            _, text, bold, mono = node
            if not text:
                continue
            piece = esc(text)
            if mono and text.strip():
                # giu khoang trang hai ben ra ngoai the <code>
                lead = len(text) - len(text.lstrip())
                tail = len(text) - len(text.rstrip())
                piece = (text[:lead] + "<code>" + esc(text.strip()) + "</code>"
                         + text[len(text) - tail:] if tail else
                         text[:lead] + "<code>" + esc(text.strip()) + "</code>")
            elif bold:
                piece = "<b>" + piece + "</b>"
            out.append(piece)
    return "".join(out).strip()


def strip_bullet(nodes, bullet):
    """Bo dau gach dau dong ngay tren run text dau tien, giu nguyen dinh dang."""
    out = list(nodes)
    for idx, node in enumerate(out):
        if node[0] == "text" and node[1].strip():
            text = node[1].lstrip()
            if text.startswith(bullet):
                text = text[len(bullet):]
            out[idx] = ("text", text.lstrip(), node[2], node[3])
            break
    return out


def mono_ratio(nodes):
    """Ty le ky tu nam trong run dung font mono cua mot doan."""
    total = mono = 0
    for node in nodes:
        if node[0] != "text":
            continue
        length = len(node[1].strip())
        total += length
        if node[3]:
            mono += length
    return (mono / total) if total else 0.0


# ------------------------------------------------------------------ builder
class SectionBuilder:
    """Gom cac doan lien tiep thanh block HTML cua mot muc."""

    def __init__(self, reader, img_prefix):
        self.reader = reader
        self.img_prefix = img_prefix
        self.html = []
        self.list_buf = []
        self.code_buf = []
        self.img_count = 0

    # ---- flush
    def flush_list(self):
        if not self.list_buf:
            return
        # Danh sach chi co dung mot y thi de nguyen dang doan van cho do vun
        if len(self.list_buf) == 1:
            self.html.append("      <p>{}</p>".format(self.list_buf[0]))
        else:
            items = "\n".join("        <li>{}</li>".format(i) for i in self.list_buf)
            self.html.append("      <ul>\n{}\n      </ul>".format(items))
        self.list_buf = []

    def flush_code(self):
        if self.code_buf:
            body = "\n".join(self.code_buf).strip("\n")
            self.html.append("      <pre><code>{}</code></pre>".format(esc(body)))
            self.code_buf = []

    def flush(self):
        self.flush_list()
        self.flush_code()

    # ---- add
    def add_paragraph(self, nodes, is_list, plain):
        images = [n[1] for n in nodes if n[0] == "img"]
        text = plain.strip()
        if images and not text:
            self.flush()
            for name in images:
                self.add_image(name)
            return
        if not text:
            return
        if images:
            # Doan vua co chu vua co anh: giu chu truoc, anh xuong duoi
            self.add_paragraph([n for n in nodes if n[0] != "img"], is_list, plain)
            self.flush()
            for name in images:
                self.add_image(name)
            return

        mono = mono_ratio(nodes) >= 0.4
        # Dong noi tiep cua khoi code dang mo: thuan ASCII va nhin giong code
        # (hoac chi la dong ngan kieu "FROM orders", ")" ...)
        continues_code = (
            bool(self.code_buf)
            and is_ascii_only(text)
            and (looks_like_code(text) or len(text) < 70)
        )
        # Nhieu doan code trong docx khong duoc dat font mono; nhan dien bang
        # dac diem "thuan ASCII + cu phap code" de mo khoi <pre> moi.
        starts_code = (
            is_ascii_only(text)
            and looks_like_code(text)
            and not text.startswith(BULLET_PREFIXES)
        )
        if not is_list and (mono or continues_code or starts_code):
            self.flush_list()
            self.code_buf.append(plain.rstrip())
            return

        self.flush_code()

        bullet = next((b for b in BULLET_PREFIXES if text.startswith(b)), None)
        if is_list or bullet:
            html = inline_html(strip_bullet(nodes, bullet) if bullet else nodes)
            if html:
                self.list_buf.append(html)
            return

        self.flush_list()
        html = inline_html(nodes)
        if html:
            self.html.append("      <p>{}</p>".format(html))

    def add_image(self, name):
        self.img_count += 1
        ext = os.path.splitext(name)[1] or ".png"
        filename = "{}-{:02d}{}".format(self.img_prefix, self.img_count, ext)
        with open(os.path.join(IMG_DIR, filename), "wb") as f:
            f.write(self.reader.media_bytes(name))
        self.html.append(
            '      <figure class="doc-figure">'
            '<img src="../assets/img/{}" alt="Minh hoạ" loading="lazy"></figure>'.format(filename)
        )

    def result(self):
        self.flush()
        return "\n".join(self.html)


# ------------------------------------------------------------------- routing
def route_for(tab, heading):
    """Tim slug chu de cho heading; tra ve None neu khong co route."""
    key_head = heading.strip().lower()
    best, best_len = None, -1
    for key, topic in ROUTES.items():
        route_tab, route_head = key.split("::", 1)
        if route_tab != tab:
            continue
        rh = route_head.strip().lower()
        if key_head.startswith(rh) and len(rh) > best_len:
            best, best_len = topic, len(rh)
    return best


def clean_heading(heading):
    for bad, good in HEADING_FIXES.items():
        if heading.strip().lower().startswith(bad.strip().lower()):
            return good
    # cat phan URL bi dinh vao cuoi tieu de
    heading = re.split(r"https?://", heading)[0].strip()
    return esc(heading.rstrip(" :-"))


def nav_label(title_html):
    text = re.sub(r"<[^>]+>", "", title_html)
    return text if len(text) <= 46 else text[:44].rstrip() + "…"


# ---------------------------------------------------------------------- main
def main():
    for d in (OUT_DIR, IMG_DIR):
        if not os.path.isdir(d):
            os.makedirs(d)

    reader = DocxReader(DOCX)
    paragraphs = list(reader.paragraphs())

    synthetic_by_start = {s["start"]: s for s in SYNTHETIC_SECTIONS}
    synthetic_ranges = [(s["start"], s["end"]) for s in SYNTHETIC_SECTIONS]

    topics = {}          # slug -> [(id, nav, html), ...]
    unrouted = []
    tab = None
    current = None       # dict dang mo

    def close_current():
        if not current:
            return
        body = current["builder"].result()
        if not body.strip():
            return
        section = (
            '    <section class="qa" id="{id}" data-nav="{nav}">\n'
            '      <div class="q-tag"><span class="n">1</span> {tab}</div>\n'
            '      <h2 class="q-title">{title}</h2>\n'
            "{body}\n"
            "    </section>"
        ).format(id=current["id"], nav=current["nav"],
                 tab=esc(TAB_LABELS.get(current["tab"], current["tab"])),
                 title=current["title"], body=body)
        topics.setdefault(current["topic"], []).append(section)

    used_ids = set()

    def make_id(topic, base):
        sid = base
        n = 2
        while (topic, sid) in used_ids:
            sid = "{}-{}".format(base, n)
            n += 1
        used_ids.add((topic, sid))
        return sid

    for i, (style, is_list, nodes, plain) in enumerate(paragraphs):
        if style == "Title":
            close_current()
            current = None
            tab = plain.strip()
            continue

        # muc tong hop cho cac tab khong co heading
        if i in synthetic_by_start:
            close_current()
            spec = synthetic_by_start[i]
            current = {
                "topic": spec["topic"],
                "id": make_id(spec["topic"], spec["id"]),
                "nav": esc(spec["nav"]),
                "tab": spec["tab"],
                "title": esc(spec["title"]),
                "builder": SectionBuilder(reader, "{}-{}".format(spec["topic"], spec["id"])),
            }

        in_synthetic = any(s <= i < e for s, e in synthetic_ranges)

        if style.startswith("Heading"):
            heading = plain.strip()
            # Vai dong noi dung trong docx bi to nham style Heading (bat dau bang
            # gach dau dong) -> giu lai nhu mot doan cua muc dang mo
            # Heading rong (chi chua anh) hoac dong noi dung bi to nham style
            # Heading -> giu lai trong muc dang mo thay vi lam mat noi dung
            if current and (not heading or heading.startswith(BULLET_PREFIXES)):
                current["builder"].add_paragraph(nodes, is_list, plain)
                continue
            close_current()
            current = None
            if not heading or tab in SKIP_TABS:
                continue
            topic = route_for(tab, heading)
            if topic is None:
                unrouted.append((tab, heading))
                continue
            if topic == SKIP:
                continue
            title = clean_heading(heading)
            sid = make_id(topic, slugify(re.sub(r"<[^>]+>", "", title)))
            current = {
                "topic": topic,
                "id": sid,
                "nav": nav_label(title),
                "tab": tab,
                "title": title,
                "builder": SectionBuilder(reader, "{}-{}".format(topic, sid)),
            }
            # Vai tieu de trong docx bi dinh lien link tham khao -> giu lai link
            url = re.search(r"https?://\S+", heading)
            if url:
                current["builder"].html.append(
                    '      <p><a href="{0}" target="_blank" rel="noopener">'
                    "Bài tham khảo ↗</a></p>".format(esc(url.group(0)))
                )
            continue

        if current and (in_synthetic or not synthetic_by_start or True):
            # bo qua phan nam ngoai khoang cua muc tong hop
            if current["id"] in {s["id"] for s in SYNTHETIC_SECTIONS} and not in_synthetic:
                close_current()
                current = None
                continue
            current["builder"].add_paragraph(nodes, is_list, plain)

    close_current()

    for slug, sections in sorted(topics.items()):
        path = os.path.join(OUT_DIR, slug + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(sections) + "\n")

    print("Sinh {} chu de:".format(len(topics)))
    for slug, sections in sorted(topics.items()):
        print("  {:26s} {:3d} mục".format(slug, len(sections)))
    if unrouted:
        print("\nCHUA DINH TUYEN ({}):".format(len(unrouted)))
        for tab_name, head in unrouted:
            print("  [{}] {}".format(tab_name, head[:70]))


if __name__ == "__main__":
    main()
