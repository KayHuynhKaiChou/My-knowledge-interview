"""Doc theo audio (read-along): to sang tung tu tieng Anh khi audio dang phat.

Quy trinh:
  1. --transcribe: chay faster-whisper tren assets/audio/<ten>.wav, luu timestamp
     tung tu ra assets/audio/<ten>.words.json (can `pip install faster-whisper`
     va ffmpeg trong PATH; chi chay lai khi file audio thay doi).
  2. Mac dinh: voi moi <section class="qa"> co <audio>, khop cac tu Whisper nghe
     duoc voi chu trong cac <p class="en"> (so khop chuoi kieu difflib, vi chu
     hien thi va chu doc co the lech nhau: tieu de, "C sharp", ...), roi boc tung
     tu vao <span class="w" data-s data-e>. Audio duoc boc vao .audio-dock de
     sticky trong pham vi muc cua no.

Chay lai nhieu lan van cho cung ket qua (go span/dock cu truoc khi sinh lai).

  python tools/audio_read_along.py [--transcribe] [trang.html ...]
"""
import difflib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, "assets", "audio")
DEFAULT_PAGES = [os.path.join(ROOT, "interview-intro", "index.html")]

# Khoang tu khong khop dai hon nguong nay thi coi nhu audio khong doc doan do
# (vd phan phap ly cuoi JD) va de nguyen, khong noi suy thoi gian.
MAX_INTERPOLATE_GAP = 12

AUDIO_RE = re.compile(
    r'(?:<div class="audio-dock">\s*)?<audio[^>]*>\s*<source src="\.\./assets/audio/([^"]+)\.wav"[^>]*>.*?</audio>(?:\s*</div>)?',
    re.S,
)
SECTION_RE = re.compile(r'(<section class="qa"[^>]*>)(.*?)(</section>)', re.S)
EN_PARA_RE = re.compile(r'(<p class="en">)(.*?)(</p>)', re.S)
WORD_SPAN_RE = re.compile(r'<span class="w"[^>]*>(.*?)</span>', re.S)


def norm(token):
    """Chuan hoa de so khop: bo dau cau, viet thuong ("AI-first," -> "aifirst")."""
    return re.sub(r"[^0-9a-z]", "", token.lower())


def transcribe(name):
    from faster_whisper import WhisperModel  # import tre: chi can khi --transcribe
    import numpy as np

    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    # Doc audio qua ffmpeg (16kHz mono float32) de khong phu thuoc phien ban PyAV
    raw = subprocess.run(
        ["ffmpeg", "-v", "quiet", "-i", os.path.join(AUDIO_DIR, name + ".wav"),
         "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    segments, _ = model.transcribe(np.frombuffer(raw, np.float32), language="en",
                                   word_timestamps=True, beam_size=5)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
             for seg in segments for w in seg.words]
    with open(os.path.join(AUDIO_DIR, name + ".words.json"), "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)
    print("transcribed", name, len(words), "words")


def align(display_tokens, spoken):
    """Tra ve [(start, end) | None] cho tung tu hien thi."""
    a = [norm(t) for t in display_tokens]
    b = [norm(w["w"]) for w in spoken]
    times = [None] * len(a)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            w = spoken[blk.b + k]
            times[blk.a + k] = (w["s"], w["e"])

    # Noi suy cho cac tu le khong khop nam giua 2 tu da khop (sai chinh ta nhe,
    # so, ky hieu...). Khoang dai thi de None: audio khong doc doan do.
    i = 0
    while i < len(times):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(times) and times[j] is None:
            j += 1
        if 0 < i and j < len(times) and j - i <= MAX_INTERPOLATE_GAP:
            t0, t1 = times[i - 1][1], times[j][0]
            step = max(t1 - t0, 0) / (j - i)
            for k in range(i, j):
                s = t0 + step * (k - i)
                times[k] = (s, s + step)
        i = j
    return times


def wrap_words(fragment, next_time):
    """Boc tung tu trong cac text node cua fragment HTML (giu nguyen the con nhu <code>)."""
    out = []
    for part in re.split(r"(<[^>]+>)", fragment):
        if not part or part.startswith("<"):
            out.append(part)
            continue
        for tok in re.split(r"(\s+)", part):
            if not tok or tok.isspace():
                out.append(tok)
                continue
            t = next_time()
            if t is None:
                out.append(tok)
            else:
                out.append('<span class="w" data-s="{:.2f}" data-e="{:.2f}">{}</span>'.format(t[0], t[1], tok))
    return "".join(out)


def process_section(sec_html):
    m = AUDIO_RE.search(sec_html)
    if not m:
        return sec_html
    name = m.group(1)
    words_path = os.path.join(AUDIO_DIR, name + ".words.json")
    if not os.path.isfile(words_path):
        print("skip (chua co timestamp):", name)
        return sec_html
    with open(words_path, encoding="utf-8") as f:
        spoken = json.load(f)

    # Dock audio: bo style inline cu, boc vao khung sticky
    dock = ('<div class="audio-dock">\n        <audio controls preload="none">\n'
            '          <source src="../assets/audio/{}.wav" type="audio/wav">\n'
            '          Trình duyệt của bạn không hỗ trợ phát audio.\n'
            '        </audio>\n      </div>').format(name)
    sec_html = sec_html[:m.start()] + dock + sec_html[m.end():]

    paras = [WORD_SPAN_RE.sub(r"\1", p.group(2)) for p in EN_PARA_RE.finditer(sec_html)]
    tokens = []
    for p in paras:
        for part in re.split(r"<[^>]+>", p):
            tokens.extend(part.split())
    times = iter(align(tokens, spoken))

    def repl(pm):
        inner = WORD_SPAN_RE.sub(r"\1", pm.group(2))
        return pm.group(1) + wrap_words(inner, lambda: next(times)) + pm.group(3)

    sec_html = EN_PARA_RE.sub(repl, sec_html)
    print("aligned", name, sum(1 for t in align(tokens, spoken) if t), "/", len(tokens), "words")
    return sec_html


def process_page(path):
    with open(path, encoding="utf-8-sig") as f:
        page = f.read()
    page = SECTION_RE.sub(lambda m: m.group(1) + process_section(m.group(2)) + m.group(3), page)
    # Gan CSS/JS rieng cua tinh nang (khong sua main.css/main.js vi build_pages.py sinh lai)
    # Thu tu: player dung thanh dieu khien truoc, read-along gan su kien sau
    css_anchor = '<link rel="stylesheet" href="../assets/css/main.css">'
    js_anchor = '<script src="../assets/js/main.js" defer></script>'
    for name in ("audio-read-along", "audio-dock-player"):
        css = '<link rel="stylesheet" href="../assets/css/{}.css">'.format(name)
        js = '<script src="../assets/js/{}.js" defer></script>'.format(name)
        if css not in page:
            page = page.replace(css_anchor, css_anchor + "\n" + css, 1)
        if js not in page:
            page = page.replace(js_anchor, js_anchor + "\n" + js, 1)
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(page)


def main():
    args = sys.argv[1:]
    pages = [a for a in args if not a.startswith("--")] or DEFAULT_PAGES
    if "--transcribe" in args:
        names = set()
        for p in pages:
            with open(p, encoding="utf-8-sig") as f:
                names.update(AUDIO_RE.findall(f.read()))
        for name in sorted(names):
            transcribe(name)
    for p in pages:
        process_page(p)


if __name__ == "__main__":
    main()
