// Dieu khien chung cho toan bo site tinh.
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
