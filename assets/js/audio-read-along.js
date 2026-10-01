/* Doc theo audio: to sang tu tieng Anh dang duoc doc.
   Moi tu la <span class="w" data-s data-e> (sinh boi tools/audio_read_along.py).
   Moi <section class="qa"> co audio rieng nen xu ly doc lap tung muc. */
(function () {
  var lastUserScroll = 0;

  // Nguoi dung tu cuon thi tam ngung tu-cuon trong vai giay, tranh giat man hinh
  ['wheel', 'touchmove', 'keydown'].forEach(function (ev) {
    window.addEventListener(ev, function () { lastUserScroll = Date.now(); }, { passive: true });
  });

  function setupSection(section) {
    var audio = section.querySelector('.audio-dock audio');
    var words = Array.prototype.slice.call(section.querySelectorAll('.w[data-s]'));
    if (!audio || !words.length) return;

    var starts = words.map(function (w) { return parseFloat(w.dataset.s); });
    var current = -1;
    var activeCard = null;
    var rafId = 0;

    // Tim tu cuoi cung co start <= t (tim nhi phan vi danh sach da sap theo thoi gian)
    function indexAt(t) {
      var lo = 0, hi = starts.length - 1, ans = -1;
      while (lo <= hi) {
        var mid = (lo + hi) >> 1;
        if (starts[mid] <= t) { ans = mid; lo = mid + 1; } else { hi = mid - 1; }
      }
      return ans;
    }

    function setCard(card) {
      if (card === activeCard) return;
      if (activeCard) activeCard.classList.remove('is-active');
      activeCard = card;
      if (!card) return;
      card.classList.add('is-active');
      if (audio.paused || Date.now() - lastUserScroll < 2500) return;
      // Chi cuon khi doan dang doc nam ngoai vung nhin (duoi header + dock)
      var r = card.getBoundingClientRect();
      var dockBottom = audio.closest('.audio-dock').getBoundingClientRect().bottom;
      if (r.top < dockBottom || r.bottom > window.innerHeight) {
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function paint() {
      var i = indexAt(audio.currentTime);
      if (i === current) return;
      if (current >= 0) words[current].classList.remove('is-reading');
      current = i;
      if (i >= 0) {
        words[i].classList.add('is-reading');
        setCard(words[i].closest('.bilingual'));
      } else {
        setCard(null);
      }
    }

    function loop() {
      paint();
      if (!audio.paused) rafId = requestAnimationFrame(loop);
    }

    function reset() {
      cancelAnimationFrame(rafId);
      if (current >= 0) words[current].classList.remove('is-reading');
      current = -1;
      setCard(null);
    }

    audio.addEventListener('play', function () {
      cancelAnimationFrame(rafId);
      loop();
    });
    audio.addEventListener('pause', function () { cancelAnimationFrame(rafId); });
    audio.addEventListener('seeked', paint);
    audio.addEventListener('ended', reset);

    // Bam vao 1 tu de nghe tu cho do
    words.forEach(function (w, i) {
      w.addEventListener('click', function () {
        audio.currentTime = starts[i];
        audio.play();
      });
    });

  }

  document.querySelectorAll('section.qa').forEach(setupSection);
})();
