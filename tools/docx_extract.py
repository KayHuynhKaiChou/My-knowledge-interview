#!/usr/bin/env python3
"""
Doc "Interview Question.docx" va tra ve cau truc da phan tich:

    [{tab, heading, blocks: [(kind, payload), ...]}, ...]

kind co the la: para | list | pre | img
Module nay chi lo phan DOC docx; viec sap xep chu de va sinh HTML nam o
tools/docx_to_content.py.
"""

import re
import zipfile

MONO_FONTS = {"Courier New", "Roboto Mono", "Cousine", "Consolas"}
P_RE = re.compile(r"<w:p[ >].*?</w:p>|<w:p/>", re.S)
STYLE_RE = re.compile(r'<w:pStyle w:val="([^"]+)"')
# Run hoac hyperlink, giu nguyen thu tu xuat hien trong doan
NODE_RE = re.compile(r"<w:hyperlink[^>]*>.*?</w:hyperlink>|<w:r[ >].*?</w:r>", re.S)
TEXT_RE = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
FONT_RE = re.compile(r'w:ascii="([^"]+)"')
EMBED_RE = re.compile(r'r:embed="([^"]+)"')
RID_RE = re.compile(r'r:id="([^"]+)"')


def unescape(text):
    for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                 ("&apos;", "'"), ("&amp;", "&")):
        text = text.replace(a, b)
    return text


def run_text(run_xml):
    """Text cua mot run, giu tab va line-break."""
    body = run_xml
    body = body.replace("<w:tab/>", "\t").replace("<w:br/>", "\n")
    parts = TEXT_RE.findall(body)
    return unescape("".join(parts))


class DocxReader:
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path)
        self.xml = self.zip.read("word/document.xml").decode("utf-8")
        rels = self.zip.read("word/_rels/document.xml.rels").decode("utf-8")
        self.media = dict(
            re.findall(r'Id="([^"]+)"[^>]*Target="media/([^"]+)"', rels)
        )
        self.links = dict(
            re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"[^>]*TargetMode="External"', rels)
        )

    def media_bytes(self, name):
        return self.zip.read("word/media/" + name)

    # ---------------------------------------------------------------- runs
    def parse_runs(self, para_xml):
        """Tra ve list cac inline node: ('text', txt, bold, mono) | ('link', txt, href) | ('img', filename)"""
        nodes = []
        for m in NODE_RE.finditer(para_xml):
            chunk = m.group(0)
            if chunk.startswith("<w:hyperlink"):
                rid = RID_RE.search(chunk)
                href = self.links.get(rid.group(1), "") if rid else ""
                text = "".join(run_text(r) for r in re.findall(r"<w:r[ >].*?</w:r>", chunk, re.S))
                if text.strip():
                    nodes.append(("link", text, href))
                continue

            embed = EMBED_RE.search(chunk)
            if embed:
                name = self.media.get(embed.group(1))
                if name:
                    nodes.append(("img", name))
                continue

            rpr = chunk.split("</w:rPr>")[0] if "<w:rPr>" in chunk else ""
            bold = "<w:b/>" in rpr or "<w:b " in rpr
            font = FONT_RE.search(rpr)
            mono = bool(font and font.group(1) in MONO_FONTS)
            text = run_text(chunk)
            if text:
                nodes.append(("text", text, bold, mono))
        return nodes

    # ------------------------------------------------------------ document
    def paragraphs(self):
        """Sinh ra (style, is_list, nodes, plain_text) theo dung thu tu tai lieu."""
        for m in P_RE.finditer(self.xml):
            para = m.group(0)
            style = STYLE_RE.search(para)
            style = style.group(1) if style else ""
            nodes = self.parse_runs(para)
            plain = "".join(n[1] for n in nodes if n[0] in ("text", "link"))
            yield style, "<w:numPr>" in para, nodes, plain
