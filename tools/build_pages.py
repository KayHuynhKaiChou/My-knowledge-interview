#!/usr/bin/env python3
"""
Build site tinh "MyInterviewKnowledge".

Hai nguon noi dung:
  1. "backend-interview-qa (1).html"  -> 12 cau hoi chuyen sau (moi cau 1 page)
  2. content/<topic-slug>.html        -> partial cua cac chu de con lai
                                        (moi muc = 1 <section class="qa">)

Ket qua:
  index.html                     trang chu, liet ke tat ca chu de
  <topic>/index.html             trang muc luc cua chu de
  advanced-backend/NN-slug.html  trang chi tiet tung cau hoi
  assets/css/main.css, assets/js/main.js

Chay lai sau khi sua noi dung:
    python tools/build_pages.py
"""

import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_QA = os.path.join(ROOT, "backend-interview-qa (1).html")
CONTENT_DIR = os.path.join(ROOT, "content")

BRAND_SVG = """<svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true">
      <defs><linearGradient id="ikBadge" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#f0b355"/><stop offset="1" stop-color="#b9752a"/>
      </linearGradient></defs>
      <rect x="2" y="2" width="60" height="60" rx="15" fill="url(#ikBadge)"/>
      <path d="M21 21 L33 32 L21 43" fill="none" stroke="#0b0e13" stroke-width="7"
            stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M37 43 H46" stroke="#0b0e13" stroke-width="7" stroke-linecap="round"/>
    </svg>"""

SITE_NAME = "Interview Knowledge"
SITE_TAGLINE = "Sổ tay ôn phỏng vấn — Backend, Frontend, Hạ tầng, Nền tảng"

# --------------------------------------------------------------------------
# Chu de: thu tu o day chinh la thu tu tren header menu
# kind = "qa"      -> sinh tu file HTML goc, moi cau hoi mot page rieng
# kind = "partial" -> sinh tu content/<slug>.html, gop cac muc vao mot page
# --------------------------------------------------------------------------
from site_topics import GROUPS, TOPIC_BY_SLUG, TOPICS  # noqa: E402

QA_DIR = "advanced-backend"

# (so thu tu, slug file, nhan ngan tren menu, mo ta ngan cho card)
QA_PAGES = [
    (1, "race-condition-lock-deadlock", "Race Condition, Lock &amp; Deadlock",
     "Hai request cùng trừ tiền một tài khoản: khoảng hở đọc&ndash;ghi, pessimistic vs optimistic lock, và cách tránh deadlock."),
    (2, "idempotency", "Idempotency",
     "User bấm thanh toán 2 lần do mạng chậm &mdash; idempotency key, unique constraint và retry an toàn."),
    (3, "distributed-transaction-saga", "Transaction xuyên service",
     "Order &ndash; payment &ndash; inventory: saga, outbox pattern, compensation thay cho distributed transaction."),
    (4, "queue-async-processing", "Queue &amp; Async Processing",
     "1000 request thanh toán cùng lúc: tách xử lý đồng bộ sang hàng đợi, worker, backpressure và retry."),
    (5, "rate-limiting", "Rate Limiting",
     "Chặn spam rút tiền / đặt hàng: fixed window, sliding window, token bucket và nơi đặt rate limit."),
    (6, "database-query-optimization", "Tối ưu Database &amp; Query",
     "Bảng transaction log hàng chục triệu row: index, partition, archive và cách đọc EXPLAIN."),
    (7, "redis-caching", "Redis &mdash; khái niệm &amp; case study",
     "Redis dùng ở đâu trong dự án thật: cache, lock phân tán, rate limit, session và hàng đợi nhẹ."),
    (8, "scalability-pagination", "Scalability &amp; Pagination",
     "API trả về 10.000 record: offset vs cursor-based pagination, chi phí thực tế của mỗi cách."),
    (9, "database-index", "Index &mdash; cơ chế &amp; đánh đổi",
     "B-Tree hoạt động ra sao, composite index, và cái giá phải trả khi index quá nhiều."),
    (10, "background-job", "Background Job",
     "Khi nào tách tác vụ ra chạy nền thay vì xử lý ngay trong request, và cách đảm bảo job không mất."),
    (11, "multi-tenant", "Multi-tenant",
     "Shared schema, schema riêng hay database riêng &mdash; chọn theo quy mô và yêu cầu cách ly dữ liệu."),
    (12, "api-design", "API Design",
     "REST vs GraphQL vs gRPC, versioning, idempotent method và chuẩn hoá format response / error."),
]

EXTRA_CSS = """
  /* ================================================================
     Chan tran ngang tren mobile: grid item mac dinh co min-width:auto,
     nen mot khoi <pre>/<table> dai se keo rong ca layout thay vi tu cuon.
     ================================================================ */
  .shell > *{min-width:0;}
  main{min-width:0;}
  pre, .flow{max-width:100%;}

  /* URL dai / ten bien dai phai tu xuong dong, neu khong se lam vo layout
     tren man hinh nho. Rieng trong <pre> van giu nguyen de cuon ngang. */
  p, li, td, th, a, code{overflow-wrap:anywhere;}
  pre, pre code{overflow-wrap:normal;}

  /* ================================================================
     Header menu tong: dieu huong giua cac chu de
     ================================================================ */
  :root{ --topbar-h:56px; }

  .topbar{
    position:sticky;
    top:0;
    z-index:40;
    display:flex;
    align-items:center;
    gap:18px;
    height:var(--topbar-h);
    padding:0 24px;
    background:rgba(11,14,19,0.92);
    backdrop-filter:blur(8px);
    border-bottom:1px solid var(--border);
  }
  /* Logo: badge chu nhat mang mau nhan hieu + wordmark mot mau,
     ngan cach voi menu bang mot duong ke doc */
  .topbar-brand{
    display:flex;
    align-items:center;
    gap:10px;
    text-decoration:none;
    padding-right:16px;
    margin-right:2px;
    border-right:1px solid var(--border);
    white-space:nowrap;
  }
  /* Icon la SVG inline (cung hinh voi assets/favicon.svg) */
  .brand-mark{
    width:27px;
    height:27px;
    flex:none;
    display:block;
  }
  .brand-text{
    font-family:var(--display);
    font-weight:600;
    font-size:14px;
    color:var(--ink);
    letter-spacing:0.01em;
    transition:color .15s ease;
  }
  .topbar-brand:hover .brand-text{color:#fff;}

  .topbar-nav{
    display:flex;
    align-items:center;
    gap:2px;
    flex:1;
    /* flex item mac dinh min-width:auto -> phai dat 0 thi thanh menu moi
       chiu co lai va tu cuon ngang thay vi tran ra ngoai header */
    min-width:0;
    /* Tren desktop phai de overflow visible, neu khong menu tha xuong
       (position:absolute) se bi vung cuon cua thanh nhom cat mat */
    overflow:visible;
    scrollbar-width:none;
    -webkit-overflow-scrolling:touch;
  }
  .topbar-nav::-webkit-scrollbar{display:none;}
  @media (max-width: 900px){
    .topbar-nav{overflow-x:auto;}
  }
  /* Nhom chu de: dung <details> nen mo/dong duoc ca tren mobile khong can JS */
  .nav-group{position:relative; flex:none;}
  .nav-group > summary{
    list-style:none;
    cursor:pointer;
    padding:7px 12px;
    border-radius:6px;
    font-family:var(--display);
    font-size:13px;
    font-weight:500;
    color:var(--ink-dim);
    white-space:nowrap;
    border:1px solid transparent;
    user-select:none;
    transition:color .15s ease, background .15s ease, border-color .15s ease;
  }
  .nav-group > summary::-webkit-details-marker{display:none;}
  .nav-group > summary::after{content:"▾"; margin-left:6px; font-size:10px; opacity:.65;}
  .nav-group > summary:hover{color:var(--ink); background:var(--bg-card);}
  .nav-group.has-active > summary{
    color:var(--amber);
    background:var(--bg-card);
    border-color:var(--amber-dim);
  }
  .nav-group[open] > summary{background:var(--bg-card); color:var(--ink);}

  .nav-dropdown{
    position:absolute;
    top:calc(100% + 6px);
    left:0;
    z-index:60;
    min-width:230px;
    display:flex;
    flex-direction:column;
    gap:2px;
    padding:8px;
    background:var(--bg-raised);
    border:1px solid var(--border);
    border-radius:10px;
    box-shadow:0 14px 34px rgba(0,0,0,0.5);
  }
  .nav-dropdown a{
    padding:8px 10px;
    border-radius:6px;
    font-family:var(--display);
    font-size:13px;
    color:var(--ink-dim);
    text-decoration:none;
    white-space:nowrap;
  }
  .nav-dropdown a:hover{background:var(--bg-card); color:var(--ink);}
  .nav-dropdown a.active{color:var(--amber); background:var(--bg-card);}
  @media (max-width: 900px){
    /* Tren mobile menu tha xuong chiem het be ngang, dung position:fixed de
       khong bi thanh nhom (cuon ngang) cat mat */
    .nav-dropdown{
      position:fixed;
      left:8px;
      right:8px;
      top:calc(var(--topbar-h) + 6px);
      min-width:0;
      max-height:70vh;
      overflow-y:auto;
    }
  }

  /* ================================================================
     Tim kiem: nut tren header + lop phu ket qua
     ================================================================ */
  .search-trigger{
    display:flex;
    align-items:center;
    gap:8px;
    flex:none;
    margin-left:auto;
    padding:6px 10px 6px 12px;
    background:var(--bg-card);
    border:1px solid var(--border);
    border-radius:8px;
    color:var(--ink-faint);
    font-family:var(--display);
    font-size:12.5px;
    cursor:pointer;
    transition:border-color .15s ease, color .15s ease;
  }
  .search-trigger:hover{border-color:var(--amber-dim); color:var(--ink-dim);}
  .search-trigger .search-icon{font-size:16px; line-height:1; color:var(--amber);}
  .search-trigger kbd{
    font-family:var(--mono);
    font-size:10.5px;
    padding:1px 6px;
    border:1px solid var(--border);
    border-radius:4px;
    color:var(--ink-faint);
    background:var(--ledger);
  }
  @media (max-width: 900px){
    .search-trigger{padding:6px 10px;}
    .search-trigger .search-label, .search-trigger kbd{display:none;}
  }

  .search-overlay{
    position:fixed;
    inset:0;
    z-index:80;
    background:rgba(4,6,10,0.72);
    backdrop-filter:blur(3px);
    display:flex;
    justify-content:center;
    padding:12vh 16px 24px;
  }
  .search-overlay[hidden]{display:none;}
  .search-box{
    width:min(720px, 100%);
    max-height:70vh;
    display:flex;
    flex-direction:column;
    background:var(--bg-raised);
    border:1px solid var(--border);
    border-radius:12px;
    box-shadow:0 24px 60px rgba(0,0,0,0.6);
    overflow:hidden;
  }
  #searchInput{
    width:100%;
    padding:16px 18px;
    border:none;
    border-bottom:1px solid var(--border);
    background:transparent;
    color:var(--ink);
    font-family:var(--display);
    font-size:15px;
    outline:none;
  }
  #searchInput::placeholder{color:var(--ink-faint);}

  .search-results{overflow-y:auto; padding:6px;}
  .search-empty{padding:18px; color:var(--ink-faint); font-family:var(--mono); font-size:12.5px;}
  .search-hit{
    display:block;
    padding:10px 12px;
    border-radius:8px;
    text-decoration:none;
    border:1px solid transparent;
  }
  .search-hit:hover, .search-hit.is-active{background:var(--bg-card); border-color:var(--border);}
  .search-hit .hit-topic{
    font-family:var(--mono);
    font-size:10.5px;
    letter-spacing:.08em;
    text-transform:uppercase;
    color:var(--amber);
    display:block;
    margin-bottom:3px;
  }
  .search-hit .hit-title{
    font-family:var(--display);
    font-size:14px;
    font-weight:600;
    color:var(--ink);
    display:block;
    margin-bottom:3px;
  }
  .search-hit .hit-snippet{
    font-size:13px;
    color:var(--ink-dim);
    line-height:1.5;
    display:block;
  }
  .search-hit mark{background:rgba(232,163,61,0.22); color:var(--amber); padding:0 2px; border-radius:3px;}
  .search-hint{
    padding:8px 14px;
    border-top:1px solid var(--border);
    font-family:var(--mono);
    font-size:11px;
    color:var(--ink-faint);
  }
  @media (max-width: 600px){
    .search-overlay{padding:8vh 10px 16px;}
    .search-hint{display:none;}
  }

  /* Anh minh hoa lay tu tai lieu goc */
  .doc-figure{margin:0 0 20px;}
  .doc-figure img{
    display:block;
    width:100%;
    border:1px solid var(--border);
    border-radius:8px;
    background:var(--ledger);
  }
  @media (max-width: 900px){
    .topbar{padding:0 12px; gap:10px;}
    /* Man hinh hep chi giu badge, bo wordmark de danh cho cho menu */
    .topbar-brand{padding-right:12px; gap:0;}
    .brand-text{display:none;}
    .nav-group > summary{font-size:12.5px; padding:6px 10px;}
  }

  /* Sidebar & nut mo menu mobile phai nam duoi header sticky */
  .sidebar{top:var(--topbar-h); height:calc(100vh - var(--topbar-h));}
  @media (max-width:900px){
    .mobile-toggle{top:var(--topbar-h);}
    .sidebar{height:auto;}
  }
  .shell{min-height:calc(100vh - var(--topbar-h));}

  /* Trang chu khong co sidebar */
  .shell.no-sidebar{grid-template-columns:1fr;}
  .shell.no-sidebar main{margin:0 auto;}

  /* ================================================================
     Sidebar: link ve trang chu, muc luc trong trang
     ================================================================ */
  .brand-link{text-decoration:none; display:block; margin-bottom:4px;}
  .brand-link:hover .brand{color:#fff;}

  .nav-block{margin-bottom:26px;}
  .nav-list a .nav-text{flex:1; min-width:0;}

  /* Muc luc trong trang (sinh boi JS tu cac h3.sub) */
  .toc-list{list-style:none; margin:0; padding:0; border-left:1px solid var(--border-soft);}
  .toc-list li{margin:0;}
  .toc-list a{
    display:block;
    padding:6px 12px;
    font-family:var(--display);
    font-size:12.5px;
    color:var(--ink-faint);
    text-decoration:none;
    border-left:2px solid transparent;
    margin-left:-1px;
    transition:color .15s ease, border-color .15s ease;
  }
  .toc-list a:hover{color:var(--ink-dim);}
  .toc-list a.active{color:var(--teal); border-left-color:var(--teal);}

  /* Breadcrumb dau trang */
  .crumb{
    font-family:var(--mono);
    font-size:11.5px;
    letter-spacing:.06em;
    text-transform:uppercase;
    color:var(--ink-faint);
    margin-bottom:26px;
    display:flex;
    align-items:center;
    gap:8px;
    flex-wrap:wrap;
  }
  .crumb a{color:var(--ink-dim); text-decoration:none;}
  .crumb a:hover{color:var(--amber);}
  .crumb .sep{color:var(--border);}

  /* ================================================================
     The chu de / the cau hoi
     ================================================================ */
  .topic-grid{
    display:grid;
    grid-template-columns:repeat(auto-fill, minmax(300px, 1fr));
    gap:16px;
    margin-bottom:40px;
  }
  @media (max-width: 520px){ .topic-grid{grid-template-columns:1fr;} }
  .topic-card{
    display:block;
    background:var(--bg-card);
    border:1px solid var(--border);
    border-radius:10px;
    padding:18px 20px;
    text-decoration:none;
    color:inherit;
    transition:border-color .15s ease, transform .15s ease, background .15s ease;
  }
  .topic-card:hover{
    border-color:var(--amber-dim);
    background:var(--bg-raised);
    transform:translateY(-2px);
  }
  .topic-card .card-num{
    font-family:var(--mono);
    font-size:11px;
    color:var(--amber);
    letter-spacing:.1em;
    display:block;
    margin-bottom:8px;
  }
  .topic-card h3{
    font-family:var(--display);
    font-size:16px;
    font-weight:600;
    color:#fff;
    margin:0 0 8px;
    line-height:1.35;
  }
  .topic-card p{
    color:var(--ink-dim);
    font-size:14px;
    margin:0;
    line-height:1.55;
  }
  .topic-card .card-meta{
    display:block;
    margin-top:12px;
    font-family:var(--mono);
    font-size:11px;
    color:var(--ink-faint);
  }

  /* ================================================================
     Pager: cau truoc / cau sau
     ================================================================ */
  .pager{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:14px;
    margin-top:8px;
    padding-top:28px;
    border-top:1px solid var(--border-soft);
  }
  @media (max-width: 560px){ .pager{grid-template-columns:1fr;} }
  .pager a{
    display:block;
    padding:14px 16px;
    border:1px solid var(--border);
    border-radius:10px;
    text-decoration:none;
    background:var(--bg-card);
    transition:border-color .15s ease, background .15s ease;
  }
  .pager a:hover{border-color:var(--teal-dim); background:var(--bg-raised);}
  .pager .pager-dir{
    display:block;
    font-family:var(--mono);
    font-size:10.5px;
    letter-spacing:.1em;
    text-transform:uppercase;
    color:var(--ink-faint);
    margin-bottom:6px;
  }
  .pager .pager-title{
    font-family:var(--display);
    font-size:14px;
    font-weight:600;
    color:var(--ink);
    line-height:1.4;
  }
  .pager a:hover .pager-title{color:var(--teal);}
  .pager .next{text-align:right;}
  @media (max-width: 560px){ .pager .next{text-align:left;} }

  /* Trang chi tiet chi co 1 section nen bo khoang cach thua duoi cung */
  main > section.qa:last-of-type{margin-bottom:40px;}

  /* Anchor offset khi nhay toi section (header sticky che mat tieu de) */
  section.qa{scroll-margin-top:calc(var(--topbar-h) + 16px);}
"""

JS = r"""// Dieu khien chung cho toan bo site tinh.
// 1) Bat/tat sidebar tren mobile
// 2) Scroll-spy cho sidebar dang anchor (trang chu de gop nhieu muc)
// 3) Sinh muc luc "Trong trang nay" tu cac h3.sub (trang chi tiet cau hoi)

(function () {
  'use strict';

  // ================= Tim kiem toan bo noi dung =================
  // Chi muc duoc sinh luc build (assets/search-index.js) nen khong can server.
  var searchTrigger = document.getElementById('searchTrigger');
  var overlay = document.getElementById('searchOverlay');
  var input = document.getElementById('searchInput');
  var results = document.getElementById('searchResults');
  var root = document.body.getAttribute('data-root') || '';
  var index = [];
  var hits = [];
  var cursor = 0;

  // Bo dau tieng Viet de go khong dau van tim duoc ("tu khoa" = "từ khoá").
  // Fold theo tung ky tu de chuoi ket qua dai bang chuoi goc -> vi tri khop
  // van dung khi to sang doan trich.
  function foldChar(ch) {
    // NFD tach "ố" thanh "o" + dau; lay ky tu dau la duoc chu cai goc.
    // Rieng "đ" khong tach nen phai doi tay.
    var c = ch.toLowerCase().normalize('NFD').charAt(0) || ' ';
    return c === 'đ' ? 'd' : c;
  }

  function fold(text) {
    var out = '';
    for (var i = 0; i < text.length; i++) out += foldChar(text[i]);
    return out;
  }

  function buildIndex() {
    if (index.length || !window.SEARCH_INDEX) return;
    index = window.SEARCH_INDEX.map(function (entry) {
      return {
        title: entry.t,
        topic: entry.g,
        url: entry.u,
        body: entry.b,
        fTitle: fold(entry.t),
        fTopic: fold(entry.g),
        fBody: fold(entry.b)
      };
    });
  }

  function countOf(haystack, token) {
    var n = 0;
    var at = haystack.indexOf(token);
    while (at >= 0 && n < 6) {          // dem toi da 6 lan cho khoi ton cong
      n++;
      at = haystack.indexOf(token, at + token.length);
    }
    return n;
  }

  function scoreOf(entry, tokens, phrase) {
    var score = 0;
    for (var i = 0; i < tokens.length; i++) {
      var token = tokens[i];
      var inTitle = entry.fTitle.indexOf(token);
      var inTopic = entry.fTopic.indexOf(token);
      var bodyHits = countOf(entry.fBody, token);
      if (inTitle < 0 && inTopic < 0 && bodyHits === 0) return 0;  // thieu tu -> loai
      if (inTitle === 0) score += 14;
      else if (inTitle > 0) score += 9;
      if (inTopic >= 0) score += 2;
      score += bodyHits;               // xuat hien cang nhieu lan cang sat chu de
    }
    // Khop nguyen cum ("khoang ho", "virtual dom") dang tin hon khop roi rac
    if (tokens.length > 1) {
      if (entry.fTitle.indexOf(phrase) >= 0) score += 30;
      else if (entry.fBody.indexOf(phrase) >= 0) score += 12;
    }
    return score;
  }

  function escapeHtml(text) {
    return text.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // Cat doan van quanh tu khoa dau tien va to sang cac tu khop
  function snippetOf(entry, tokens) {
    var pos = entry.fBody.indexOf(tokens[0]);
    var start = pos < 0 ? 0 : Math.max(0, pos - 60);
    var raw = entry.body.slice(start, start + 190);
    var folded = fold(raw);

    // Danh dau vi tri khop trước, roi moi escape tung ky tu -> khong the
    // chen the <mark> vao giua mot HTML entity
    var marked = [];
    tokens.forEach(function (token) {
      var at = folded.indexOf(token);
      while (at >= 0) {
        for (var j = at; j < at + token.length; j++) marked[j] = true;
        at = folded.indexOf(token, at + token.length);
      }
    });

    var out = '';
    var open = false;
    for (var i = 0; i < raw.length; i++) {
      if (marked[i] && !open) { out += '<mark>'; open = true; }
      if (!marked[i] && open) { out += '</mark>'; open = false; }
      out += escapeHtml(raw[i]);
    }
    if (open) out += '</mark>';

    return (start > 0 ? '…' : '') + out +
      (entry.body.length > start + 190 ? '…' : '');
  }

  function render(query) {
    var phrase = fold(query).trim();
    var tokens = phrase.split(/\s+/).filter(Boolean);
    if (!tokens.length) {
      hits = [];
      results.innerHTML =
        '<div class="search-empty">Gõ từ khoá để tìm trong ' + index.length + ' mục nội dung.</div>';
      return;
    }
    hits = index
      .map(function (entry) { return { entry: entry, score: scoreOf(entry, tokens, phrase) }; })
      .filter(function (h) { return h.score > 0; })
      .sort(function (a, b) { return b.score - a.score; })
      .slice(0, 25);

    if (!hits.length) {
      results.innerHTML = '<div class="search-empty">Không tìm thấy mục nào khớp.</div>';
      return;
    }
    cursor = 0;
    results.innerHTML = hits.map(function (h, i) {
      return '<a class="search-hit' + (i === 0 ? ' is-active' : '') + '" href="' +
        root + h.entry.url + '">' +
        '<span class="hit-topic">' + escapeHtml(h.entry.topic) + '</span>' +
        '<span class="hit-title">' + escapeHtml(h.entry.title) + '</span>' +
        '<span class="hit-snippet">' + snippetOf(h.entry, tokens) + '</span></a>';
    }).join('');
  }

  function moveCursor(step) {
    var nodes = results.querySelectorAll('.search-hit');
    if (!nodes.length) return;
    nodes[cursor].classList.remove('is-active');
    cursor = (cursor + step + nodes.length) % nodes.length;
    nodes[cursor].classList.add('is-active');
    nodes[cursor].scrollIntoView({ block: 'nearest' });
  }

  function openSearch() {
    if (!overlay) return;
    buildIndex();
    overlay.hidden = false;
    input.value = '';
    render('');
    input.focus();
  }

  function closeSearch() {
    if (overlay) overlay.hidden = true;
  }

  if (searchTrigger && overlay && input && results) {
    searchTrigger.addEventListener('click', openSearch);
    input.addEventListener('input', function () { render(input.value); });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); moveCursor(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); moveCursor(-1); }
      else if (e.key === 'Enter') {
        var active = results.querySelector('.search-hit.is-active');
        if (active) { e.preventDefault(); window.location.href = active.href; }
      }
    });

    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeSearch();
    });

    document.addEventListener('keydown', function (e) {
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
      if (e.key === 'Escape') { closeSearch(); return; }
      if ((e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        openSearch();
        return;
      }
      if (e.key === '/' && !typing) { e.preventDefault(); openSearch(); }
    });
  }

  // ---------- Header: menu nhom chu de ----------
  var groups = Array.prototype.slice.call(document.querySelectorAll('.nav-group'));

  groups.forEach(function (group) {
    group.addEventListener('toggle', function () {
      if (!group.open) return;
      groups.forEach(function (other) {
        if (other !== group) other.open = false;   // chi mo mot nhom mot luc
      });
    });
  });

  document.addEventListener('click', function (e) {
    if (e.target.closest('.nav-group')) return;
    groups.forEach(function (group) { group.open = false; });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') groups.forEach(function (group) { group.open = false; });
  });

  // ---------- Header: cuon toi nhom dang xem (thanh nhom cuon ngang) ----------
  var activeTopic = document.querySelector('.nav-group.has-active > summary');

  function centerActiveTopic() {
    if (!activeTopic) return;
    var bar = document.querySelector('.topbar-nav');
    if (!bar) return;
    // Tinh bang toa do thuc te tren man hinh roi cong don vao scrollLeft hien tai
    // (offsetLeft khong dung duoc vi no tinh theo .topbar chu khong theo thanh menu)
    var delta =
      activeTopic.getBoundingClientRect().left -
      bar.getBoundingClientRect().left -
      (bar.clientWidth - activeTopic.offsetWidth) / 2;
    bar.scrollLeft += delta; // trinh duyet tu gioi han trong [0, maxScroll]
  }

  centerActiveTopic();
  // Font Google tai bat dong bo: khi font doi, be rong cac link thay doi
  // nen phai tinh lai vi tri mot lan nua, neu khong menu se bi lech.
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(centerActiveTopic);
  }
  window.addEventListener('load', centerActiveTopic);

  // ---------- Mobile nav toggle ----------
  var toggle = document.getElementById('navToggle');
  var sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    // Dong sidebar sau khi chon link tren man hinh nho
    sidebar.addEventListener('click', function (e) {
      if (e.target.closest('a') && window.innerWidth <= 900) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Danh dau link dang doc, bo danh dau cac link khac trong cung nhom
  function spy(links, targets) {
    var byId = {};
    targets.forEach(function (el, i) {
      if (!el.id) el.id = 'sec-' + (i + 1);
      if (links[i]) byId[el.id] = links[i];
    });
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var link = byId[entry.target.id];
          if (!link || !entry.isIntersecting) return;
          Object.keys(byId).forEach(function (id) {
            byId[id].classList.remove('active');
          });
          link.classList.add('active');
        });
      },
      { rootMargin: '-12% 0px -72% 0px', threshold: 0 }
    );
    targets.forEach(function (el) { observer.observe(el); });
  }

  // ---------- Sidebar dang anchor: highlight muc dang doc ----------
  var anchorLinks = Array.prototype.slice.call(
    document.querySelectorAll('.nav-list a[href^="#"]')
  );
  if (anchorLinks.length) {
    var sections = anchorLinks
      .map(function (a) { return document.querySelector(a.getAttribute('href')); })
      .filter(Boolean);
    spy(anchorLinks, sections);
  }

  // ---------- Muc luc trong trang ----------
  var tocMount = document.getElementById('pageToc');
  var headings = Array.prototype.slice.call(
    document.querySelectorAll('main h3.sub')
  );
  if (!tocMount) return;
  if (headings.length === 0) {
    tocMount.parentNode.style.display = 'none';
    return;
  }

  var list = document.createElement('ul');
  list.className = 'toc-list';
  var tocLinks = [];

  headings.forEach(function (h, i) {
    if (!h.id) h.id = 'sec-' + (i + 1);
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent.trim();
    h.style.scrollMarginTop = '90px';
    li.appendChild(a);
    list.appendChild(li);
    tocLinks.push(a);
  });
  tocMount.appendChild(list);
  spy(tocLinks, headings);
})();
"""


# ---------------------------------------------------------------- helpers
def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)


def plain(text):
    return html.unescape(strip_tags(text)).strip()


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


# ---------------------------------------------------------------- layout
def render_topbar(root, active_slug):
    """Header menu tong: cac chu de duoc gom thanh nhom dang <details>."""
    groups = []
    for group_name, slugs in GROUPS:
        links = []
        has_active = False
        for slug in slugs:
            topic = TOPIC_BY_SLUG[slug]
            active = slug == active_slug
            has_active = has_active or active
            links.append(
                '        <a href="{root}{slug}/index.html"{cls}>{nav}</a>'.format(
                    root=root, slug=slug,
                    cls=' class="active"' if active else "", nav=topic["nav"]
                )
            )
        groups.append(
            '    <details class="nav-group{active}">\n'
            "      <summary>{name}</summary>\n"
            '      <div class="nav-dropdown">\n{links}\n      </div>\n'
            "    </details>".format(
                active=" has-active" if has_active else "",
                name=group_name, links="\n".join(links),
            )
        )

    return """<header class="topbar">
  <a class="topbar-brand" href="{root}index.html" aria-label="Interview Knowledge — trang chủ">
    {mark}
    <span class="brand-text">Interview Knowledge</span>
  </a>
  <nav class="topbar-nav">
{groups}
  </nav>
  <button class="search-trigger" id="searchTrigger" aria-label="Tìm kiếm nội dung">
    <span class="search-icon" aria-hidden="true">⌕</span>
    <span class="search-label">Tìm kiếm</span>
    <kbd>/</kbd>
  </button>
</header>""".format(root=root, groups="\n".join(groups), mark=BRAND_SVG)


def render_sidebar(topic, items, active_href, show_toc):
    """items = [(nhan hien thi, href, so thu tu hoac None)]"""
    lis = []
    for label, href, num in items:
        cls = ' class="active"' if href == active_href else ""
        num_html = (
            '<span class="nav-num">{:02d}</span>'.format(num) if num else ""
        )
        lis.append(
            '        <li><a href="{href}"{cls}>{num}<span class="nav-text">{label}</span></a></li>'.format(
                href=href, cls=cls, num=num_html, label=label
            )
        )

    toc = ""
    if show_toc:
        toc = (
            '\n    <div class="nav-block">\n'
            '      <p class="nav-label">Trong trang này</p>\n'
            '      <div id="pageToc"></div>\n'
            "    </div>\n"
        )

    return """  <aside class="sidebar" id="sidebar">
    <div class="brand">{title}</div>
    <div class="brand-sub">{count} mục &middot; sổ tay ôn phỏng vấn</div>

    <div class="nav-block">
      <p class="nav-label">Nội dung</p>
      <ul class="nav-list">
{items}
      </ul>
    </div>
{toc}  </aside>""".format(
        title=topic["title"], count=len(items), items="\n".join(lis), toc=toc
    )


def layout(root, title, body, active_slug=None, sidebar_html="", description=""):
    shell_cls = "shell" if sidebar_html else "shell no-sidebar"
    toggle = ""
    if sidebar_html:
        toggle = (
            '  <button class="mobile-toggle" id="navToggle" aria-label="Mở mục lục">'
            "☰ Mục lục</button>\n"
        )
    return """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{root}assets/css/main.css">
</head>
<body data-root="{root}">

{topbar}

<div class="search-overlay" id="searchOverlay" hidden>
  <div class="search-box" role="dialog" aria-label="Tìm kiếm nội dung">
    <input type="search" id="searchInput" autocomplete="off" spellcheck="false"
           placeholder="Tìm trong toàn bộ nội dung — closure, saga, index, rebase…">
    <div class="search-results" id="searchResults"></div>
    <div class="search-hint">Enter mở mục · ↑↓ chọn · Esc đóng</div>
  </div>
</div>

<div class="{shell_cls}">
{toggle}{sidebar}
  <main>
{body}
  </main>
</div>

<footer>
  {site_name} — sổ tay ôn phỏng vấn tổng hợp từ ghi chép cá nhân.
  Ưu tiên trả lời theo cấu trúc: vấn đề → giải pháp → vì sao chọn cách này thay vì cách khác.
</footer>

<script src="{root}assets/search-index.js" defer></script>
<script src="{root}assets/js/main.js" defer></script>
</body>
</html>
""".format(
        desc=description or SITE_TAGLINE,
        title=title,
        root=root,
        topbar=render_topbar(root, active_slug),
        shell_cls=shell_cls,
        toggle=toggle,
        sidebar=sidebar_html,
        body=body,
        site_name=SITE_NAME,
    )


def hero(topic):
    return """    <div class="hero">
      <div class="hero-kicker">{kicker}</div>
      <h1>{heading}</h1>
      <p class="lede">{lede}</p>
    </div>""".format(**topic)


# ---------------------------------------------------------------- home
def build_home(topic_counts):
    cards = []
    for i, topic in enumerate(TOPICS, start=1):
        cards.append(
            """      <a class="topic-card" href="{slug}/index.html">
        <span class="card-num">CHỦ ĐỀ {i:02d}</span>
        <h3>{title}</h3>
        <p>{blurb}</p>
        <span class="card-meta">{count} mục</span>
      </a>""".format(
                slug=topic["slug"], i=i, title=topic["title"],
                blurb=topic["blurb"], count=topic_counts[topic["slug"]],
            )
        )

    total = sum(topic_counts.values())
    body = """    <div class="hero">
      <div class="hero-kicker">Interview prep · Fullstack</div>
      <h1>Sổ tay ôn phỏng vấn</h1>
      <p class="lede">Toàn bộ ghi chép kỹ thuật được sàng lọc và sắp theo chủ đề: câu hỏi backend chuyên sâu, khái niệm hạ tầng, phía client và công cụ, quy trình test &amp; môi trường, nền tảng SaaS, auth và Web3. Chọn một chủ đề ở menu trên hoặc trong danh sách bên dưới.</p>
      <div class="hero-meta">
        <span><b>{topics}</b> chủ đề</span>
        <span><b>{total}</b> mục nội dung</span>
        <span><b>Định dạng:</b> câu hỏi → giải pháp → câu trả lời mẫu</span>
      </div>
    </div>

    <p class="nav-label">Chủ đề</p>
    <div class="topic-grid">
{cards}
    </div>""".format(topics=len(TOPICS), total=total, cards="\n".join(cards))

    write(
        os.path.join(ROOT, "index.html"),
        layout("", "{} — {}".format(SITE_NAME, SITE_TAGLINE), body),
    )


# ---------------------------------------------------------------- Q&A topic
def extract_qa_sections(src):
    return {
        int(m.group(1)): m.group(2)
        for m in re.finditer(r'<section class="qa" id="q(\d+)">(.*?)</section>', src, re.S)
    }


def qa_sidebar_items():
    """Danh sach 12 cau hoi cho sidebar; cac trang deu nam cung thu muc."""
    return [
        (label, "{:02d}-{}.html".format(num, slug), num)
        for num, slug, label, _ in QA_PAGES
    ]


def build_qa_index():
    topic = TOPIC_BY_SLUG["advanced-backend"]
    cards = []
    for num, slug, label, blurb in QA_PAGES:
        cards.append(
            """      <a class="topic-card" href="{n:02d}-{slug}.html">
        <span class="card-num">CÂU {n:02d}</span>
        <h3>{label}</h3>
        <p>{blurb}</p>
      </a>""".format(n=num, slug=slug, label=label, blurb=blurb)
        )

    body = """{hero}

    <p class="nav-label">Mục lục</p>
    <div class="topic-grid">
{cards}
    </div>""".format(hero=hero(topic), cards="\n".join(cards))

    sidebar_html = render_sidebar(
        topic, qa_sidebar_items(), None, show_toc=False
    )
    write(
        os.path.join(ROOT, QA_DIR, "index.html"),
        layout("../", "{} — {}".format(plain(topic["title"]), SITE_NAME),
               body, topic["slug"], sidebar_html, plain(topic["blurb"])),
    )


def qa_pager(index):
    parts = []
    if index > 0:
        num, slug, label, _ = QA_PAGES[index - 1]
        parts.append(
            '      <a class="prev" href="{n:02d}-{slug}.html">'
            '<span class="pager-dir">← Câu trước</span>'
            '<span class="pager-title">{n:02d}. {label}</span></a>'.format(
                n=num, slug=slug, label=label)
        )
    else:
        parts.append(
            '      <a class="prev" href="index.html">'
            '<span class="pager-dir">← Quay lại</span>'
            '<span class="pager-title">Mục lục Advanced Backend</span></a>'
        )
    if index < len(QA_PAGES) - 1:
        num, slug, label, _ = QA_PAGES[index + 1]
        parts.append(
            '      <a class="next" href="{n:02d}-{slug}.html">'
            '<span class="pager-dir">Câu tiếp theo →</span>'
            '<span class="pager-title">{n:02d}. {label}</span></a>'.format(
                n=num, slug=slug, label=label)
        )
    else:
        parts.append(
            '      <a class="next" href="index.html">'
            '<span class="pager-dir">Hoàn thành →</span>'
            '<span class="pager-title">Về mục lục Advanced Backend</span></a>'
        )
    return '    <nav class="pager">\n' + "\n".join(parts) + "\n    </nav>"


def build_qa_pages(sections):
    topic = TOPIC_BY_SLUG["advanced-backend"]
    items = qa_sidebar_items()
    for i, (num, slug, label, _) in enumerate(QA_PAGES):
        href = "{:02d}-{}.html".format(num, slug)
        section_html = sections[num]
        q_title = plain(re.search(r'<h2 class="q-title">(.*?)</h2>', section_html, re.S).group(1))

        body = """    <div class="crumb">
      <a href="index.html">{topic}</a>
      <span class="sep">/</span>
      <span>Câu {n:02d}</span>
    </div>

    <section class="qa" id="q{n}">{content}</section>

{pager}""".format(topic=topic["title"], n=num, content=section_html, pager=qa_pager(i))

        add_search_entry(
            "{:02d}. {}".format(num, label), topic["title"],
            "{}/{}".format(QA_DIR, href), section_html,
        )

        sidebar_html = render_sidebar(topic, items, href, show_toc=True)
        write(
            os.path.join(ROOT, QA_DIR, href),
            layout("../",
                   "{n:02d}. {label} — {topic}".format(
                       n=num, label=plain(label), topic=plain(topic["title"])),
                   body, topic["slug"], sidebar_html,
                   q_title.strip('"“”')[:180]),
        )


# ---------------------------------------------------------------- partial topic
def load_partial(topic_slug):
    """Ghep noi dung viet tay (neu co) truoc phan sinh tu docx."""
    parts = []
    for path in (os.path.join(CONTENT_DIR, topic_slug + ".html"),
                 os.path.join(CONTENT_DIR, "generated", topic_slug + ".html")):
        if os.path.isfile(path):
            parts.append(read(path).strip())
    return "\n\n".join(parts)


def renumber_tags(partial):
    """Danh lai so thu tu o the muc (.q-tag .n) theo dung thu tu tren page."""
    counter = [0]

    def bump(match):
        counter[0] += 1
        return '<span class="n">{}</span>'.format(counter[0])

    return re.sub(r'<span class="n">\d+</span>', bump, partial)


def build_partial_topic(topic):
    """Mot chu de = mot page, moi muc la mot <section class="qa"> trong partial."""
    partial = renumber_tags(load_partial(topic["slug"]))
    entries = re.findall(
        r'<section class="qa" id="([^"]+)"(?:\s+data-nav="([^"]*)")?>(.*?)</section>',
        partial, re.S,
    )
    if not entries:
        raise SystemExit("Partial rong: " + topic["slug"])

    items = []
    for i, (sec_id, nav_label, sec_html) in enumerate(entries, start=1):
        m = re.search(r'<h2 class="q-title">(.*?)</h2>', sec_html, re.S)
        heading = m.group(1).strip() if m else sec_id
        if not nav_label:
            nav_label = heading
        items.append((nav_label, "#" + sec_id, i))
        add_search_entry(
            heading, topic["title"],
            "{}/index.html#{}".format(topic["slug"], sec_id), sec_html,
        )

    body = "{hero}\n\n{content}".format(hero=hero(topic), content=partial.strip())
    sidebar_html = render_sidebar(topic, items, None, show_toc=False)

    ensure_dir(os.path.join(ROOT, topic["slug"]))
    write(
        os.path.join(ROOT, topic["slug"], "index.html"),
        layout("../", "{} — {}".format(plain(topic["title"]), SITE_NAME),
               body, topic["slug"], sidebar_html, plain(topic["blurb"])),
    )
    return len(entries)


# ---------------------------------------------------------------- assets
# --------------------------------------------------------------- tim kiem
# Moi phan tu: {"t": tieu de, "g": ten chu de, "u": duong dan tu goc site,
#               "b": noi dung dang text de tim kiem}
SEARCH_ENTRIES = []
SEARCH_BODY_LIMIT = 4000


def to_text(fragment):
    """HTML -> text thuan de dua vao chi muc tim kiem."""
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def add_search_entry(title, topic_title, url, body_html):
    # Bo the muc (so thu tu + nhan tab) va tieu de ra khoi phan noi dung,
    # neu khong doan trich se luon mo dau bang "8 SQL ..." rat kho doc
    body = re.sub(r'<div class="q-tag">.*?</div>', " ", body_html, flags=re.S)
    body = re.sub(r'<h2 class="q-title">.*?</h2>', " ", body, flags=re.S)
    SEARCH_ENTRIES.append({
        "t": plain(title),
        "g": plain(topic_title),
        "u": url,
        "b": to_text(body)[:SEARCH_BODY_LIMIT],
    })


def write_search_index():
    """Xuat chi muc duoi dang .js (khong dung fetch de mo bang file:// van chay)."""
    payload = json.dumps(SEARCH_ENTRIES, ensure_ascii=False, separators=(",", ":"))
    write(os.path.join(ROOT, "assets", "search-index.js"),
          "window.SEARCH_INDEX = " + payload + ";\n")


def build_assets():
    css = re.search(r"<style>(.*?)</style>", read(SOURCE_QA), re.S).group(1)
    write(os.path.join(ROOT, "assets", "css", "main.css"),
          css.strip("\n") + "\n" + EXTRA_CSS)
    write(os.path.join(ROOT, "assets", "js", "main.js"), JS)


def main():
    for sub in ("assets/css", "assets/js", QA_DIR):
        ensure_dir(os.path.join(ROOT, *sub.split("/")))

    build_assets()

    sections = extract_qa_sections(read(SOURCE_QA))
    missing = [n for n, _, _, _ in QA_PAGES if n not in sections]
    if missing:
        raise SystemExit("Thieu section cho cau: {}".format(missing))

    counts = {"advanced-backend": len(QA_PAGES)}
    build_qa_index()
    build_qa_pages(sections)

    for topic in TOPICS:
        if topic["kind"] == "partial":
            counts[topic["slug"]] = build_partial_topic(topic)

    build_home(counts)
    write_search_index()
    print("Built: index.html + {} topics ({} muc)".format(
        len(TOPICS), sum(counts.values())))


if __name__ == "__main__":
    main()
