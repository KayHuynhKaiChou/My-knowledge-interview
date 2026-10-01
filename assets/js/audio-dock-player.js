/* Player tu lam cho .audio-dock: thay giao dien <audio controls> mac dinh bang
   thanh dieu khien co nut lui/tien 10s, 5s, thanh tua va toc do doc.
   The <audio> goc van giu lai (an controls) nen JS loi thi van nghe duoc. */
(function () {
  var RATES = [1, 1.25, 1.5, 0.75];
  var players = [];

  var ICON_PLAY = '<svg class="i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z"/></svg>';
  var ICON_PAUSE = '<svg class="i-pause" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/></svg>';

  function fmt(sec) {
    if (!isFinite(sec) || sec < 0) sec = 0;
    var m = Math.floor(sec / 60), s = Math.floor(sec % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function skipBtn(delta) {
    var label = (delta > 0 ? '+' : '−') + Math.abs(delta) + 's';
    var aria = (delta > 0 ? 'Tiến ' : 'Lùi ') + Math.abs(delta) + ' giây';
    return '<button type="button" class="ap-btn" data-skip="' + delta + '" aria-label="' + aria + '" title="' + aria + '">' + label + '</button>';
  }

  function build(dock) {
    var audio = dock.querySelector('audio');
    if (!audio) return;
    audio.removeAttribute('controls');
    audio.preload = 'metadata'; // chi tai header de hien tong thoi luong

    var ui = document.createElement('div');
    ui.className = 'ap';
    ui.innerHTML =
      '<div class="ap-controls">' +
        skipBtn(-10) + skipBtn(-5) +
        '<button type="button" class="ap-btn ap-play" aria-label="Phát">' + ICON_PLAY + ICON_PAUSE + '</button>' +
        skipBtn(5) + skipBtn(10) +
        '<button type="button" class="ap-btn ap-rate" aria-label="Tốc độ đọc" title="Tốc độ đọc">1×</button>' +
      '</div>' +
      '<div class="ap-track">' +
        '<span class="ap-time is-current">0:00</span>' +
        '<input type="range" class="ap-seek" min="0" max="1000" value="0" step="1" aria-label="Tua audio">' +
        '<span class="ap-time ap-dur">0:00</span>' +
      '</div>';
    dock.appendChild(ui);

    var playBtn = ui.querySelector('.ap-play');
    var rateBtn = ui.querySelector('.ap-rate');
    var seek = ui.querySelector('.ap-seek');
    var cur = ui.querySelector('.ap-time.is-current');
    var dur = ui.querySelector('.ap-dur');
    var seeking = false;

    function render() {
      var d = audio.duration;
      var p = isFinite(d) && d > 0 ? audio.currentTime / d : 0;
      if (!seeking) seek.value = Math.round(p * 1000);
      seek.style.setProperty('--p', (seek.value / 10) + '%');
      cur.textContent = fmt(audio.currentTime);
      dur.textContent = fmt(d);
    }

    playBtn.addEventListener('click', function () {
      if (audio.paused) audio.play(); else audio.pause();
    });

    ui.querySelectorAll('[data-skip]').forEach(function (b) {
      b.addEventListener('click', function () {
        var t = audio.currentTime + parseFloat(b.dataset.skip);
        var d = isFinite(audio.duration) ? audio.duration : t;
        audio.currentTime = Math.max(0, Math.min(t, d));
        render();
      });
    });

    rateBtn.addEventListener('click', function () {
      var next = RATES[(RATES.indexOf(audio.playbackRate) + 1) % RATES.length];
      audio.playbackRate = next;
      rateBtn.textContent = next + '×';
    });

    // Keo thanh tua: cap nhat hien thi ngay, tua audio khi tha tay
    seek.addEventListener('input', function () {
      seeking = true;
      var d = audio.duration;
      if (isFinite(d)) cur.textContent = fmt(seek.value / 1000 * d);
      seek.style.setProperty('--p', (seek.value / 10) + '%');
    });
    seek.addEventListener('change', function () {
      var d = audio.duration;
      if (isFinite(d)) audio.currentTime = seek.value / 1000 * d;
      seeking = false;
    });

    audio.addEventListener('play', function () {
      // Chi 1 audio phat tai 1 thoi diem
      players.forEach(function (a) { if (a !== audio) a.pause(); });
      ui.classList.add('is-playing');
      playBtn.setAttribute('aria-label', 'Tạm dừng');
    });
    audio.addEventListener('pause', function () {
      ui.classList.remove('is-playing');
      playBtn.setAttribute('aria-label', 'Phát');
    });
    ['timeupdate', 'loadedmetadata', 'durationchange', 'seeked', 'ended'].forEach(function (ev) {
      audio.addEventListener(ev, render);
    });

    players.push(audio);
    render();
  }

  document.querySelectorAll('.audio-dock').forEach(build);
})();
