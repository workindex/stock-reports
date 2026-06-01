// MkDocs Material — 표 정렬 + 필터 + 페이지네이션. instant navigation 대응(document$).
document$.subscribe(function () {
  var tables = document.querySelectorAll("article table:not([class])");
  tables.forEach(function (table) {
    new Tablesort(table);
  });

  // 페이지네이션은 .snap-filters가 있는 페이지(관찰 종목·스냅샷 인덱스)에만 적용
  var filterBar = document.querySelector('.snap-filters');
  if (!filterBar) return;

  var table = document.querySelector('article table');
  if (!table) return;

  // ── 상태 ──────────────────────────────────────────────────────────────
  var filterState = { verdict: '', stage: '', market: '' };
  var pageState   = { current: 1, perPage: 10 };

  // ── 필터 판정 ─────────────────────────────────────────────────────────
  function rowVisible(row) {
    var cells = row.querySelectorAll('td');

    var verdictOk = true;
    if (filterState.verdict && cells.length > 3) {
      var span = cells[3].querySelector('.verdict');
      verdictOk = !!span && span.classList.contains('verdict-' + filterState.verdict);
    }
    var stageOk = true;
    if (filterState.stage && cells.length > 4) {
      stageOk = cells[4].textContent.trim() === filterState.stage;
    }
    var marketOk = true;
    if (filterState.market && cells.length === 3) {
      marketOk = cells[2].textContent.trim() === filterState.market;
    }
    return verdictOk && stageOk && marketOk;
  }

  // ── 렌더: 필터 + 페이지네이션 동시 적용 ──────────────────────────────
  function render() {
    var allRows      = Array.from(table.querySelectorAll('tbody tr'));
    var filtered     = allRows.filter(rowVisible);
    var totalPages   = Math.max(1, Math.ceil(filtered.length / pageState.perPage));

    if (pageState.current > totalPages) pageState.current = totalPages;

    var start = (pageState.current - 1) * pageState.perPage;
    var end   = start + pageState.perPage;

    allRows.forEach(function (row) {
      if (!rowVisible(row)) {
        row.style.display = 'none';
      } else {
        var idx = filtered.indexOf(row);
        row.style.display = (idx >= start && idx < end) ? '' : 'none';
      }
    });

    renderPagination(filtered.length, totalPages);
  }

  // ── 페이지네이션 UI 렌더 ──────────────────────────────────────────────
  function renderPagination(totalRows, totalPages) {
    var ctrl = document.getElementById('pg-ctrl');
    if (!ctrl) return;

    var from = totalRows === 0 ? 0 : (pageState.current - 1) * pageState.perPage + 1;
    var to   = Math.min(pageState.current * pageState.perPage, totalRows);
    var info = '<span class="pg-info">' + totalRows + '개 중 ' + from + '–' + to + '</span>';

    // 페이지 번호 버튼 (최대 7개 표시)
    var btnHtml = '';
    var maxBtns = 7;
    var half    = Math.floor(maxBtns / 2);
    var s = Math.max(1, pageState.current - half);
    var e = Math.min(totalPages, s + maxBtns - 1);
    if (e - s < maxBtns - 1) s = Math.max(1, e - maxBtns + 1);

    btnHtml += '<button class="pg-btn" data-page="prev" ' + (pageState.current === 1 ? 'disabled' : '') + '>‹</button>';
    if (s > 1) btnHtml += '<button class="pg-btn" data-page="1">1</button>' + (s > 2 ? '<span class="pg-ellipsis">…</span>' : '');
    for (var i = s; i <= e; i++) {
      btnHtml += '<button class="pg-btn' + (i === pageState.current ? ' pg-active' : '') + '" data-page="' + i + '">' + i + '</button>';
    }
    if (e < totalPages) btnHtml += (e < totalPages - 1 ? '<span class="pg-ellipsis">…</span>' : '') + '<button class="pg-btn" data-page="' + totalPages + '">' + totalPages + '</button>';
    btnHtml += '<button class="pg-btn" data-page="next" ' + (pageState.current === totalPages ? 'disabled' : '') + '>›</button>';

    ctrl.innerHTML = info + '<div class="pg-pages">' + btnHtml + '</div>';

    ctrl.querySelectorAll('[data-page]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var p = btn.dataset.page;
        if      (p === 'prev') pageState.current = Math.max(1, pageState.current - 1);
        else if (p === 'next') pageState.current = Math.min(totalPages, pageState.current + 1);
        else                   pageState.current = parseInt(p);
        render();
        table.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  // ── 페이지당 행 수 버튼 필터바에 삽입 ────────────────────────────────
  if (filterBar) {
    var perWrap = document.createElement('span');
    perWrap.className = 'sf-per-wrap';
    perWrap.innerHTML =
      '<span class="sf-label">페이지당</span>' +
      '<button class="pg-per pg-per-active" data-per="10">10</button>' +
      '<button class="pg-per" data-per="20">20</button>' +
      '<button class="pg-per" data-per="30">30</button>';
    filterBar.appendChild(perWrap);

    perWrap.querySelectorAll('.pg-per').forEach(function (btn) {
      btn.addEventListener('click', function () {
        perWrap.querySelectorAll('.pg-per').forEach(function (b) { b.classList.remove('pg-per-active'); });
        btn.classList.add('pg-per-active');
        pageState.perPage = parseInt(btn.dataset.per);
        pageState.current = 1;
        render();
      });
    });
  }

  // ── 페이지네이션 컨트롤 컨테이너 삽입 ───────────────────────────────
  var ctrl = document.createElement('div');
  ctrl.id        = 'pg-ctrl';
  ctrl.className = 'pg-ctrl';
  table.parentNode.insertBefore(ctrl, table.nextSibling);

  // ── 필터 변경 이벤트 ─────────────────────────────────────────────────
  document.querySelectorAll('.sf-select').forEach(function (sel) {
    sel.addEventListener('change', function () {
      filterState[sel.dataset.f] = sel.value;
      pageState.current = 1;
      render();
    });
  });

  render();
});
