// MkDocs Material — 표 정렬 + 필터. instant navigation 대응(document$).
document$.subscribe(function () {
  var tables = document.querySelectorAll("article table:not([class])");
  tables.forEach(function (table) {
    new Tablesort(table);
  });

  // 필터 상태: verdict/stage → 스냅샷, market → 워치리스트
  var filterState = { verdict: '', stage: '', market: '' };

  function applyFilters() {
    var table = document.querySelector('article table');
    if (!table) return;
    table.querySelectorAll('tbody tr').forEach(function (row) {
      var cells = row.querySelectorAll('td');

      // 판정 (스냅샷 col 3, CSS 클래스 일치)
      var verdictMatch = true;
      if (filterState.verdict && cells.length > 3) {
        var span = cells[3].querySelector('.verdict');
        verdictMatch = !!span && span.classList.contains('verdict-' + filterState.verdict);
      }

      // Stage (스냅샷 col 4, 텍스트 일치)
      var stageMatch = true;
      if (filterState.stage && cells.length > 4) {
        stageMatch = cells[4].textContent.trim() === filterState.stage;
      }

      // 시장 (워치리스트 col 2, 텍스트 일치)
      var marketMatch = true;
      if (filterState.market && cells.length === 3) {
        marketMatch = cells[2].textContent.trim() === filterState.market;
      }

      row.style.display = (verdictMatch && stageMatch && marketMatch) ? '' : 'none';
    });
  }

  document.querySelectorAll('.sf-select').forEach(function (sel) {
    sel.addEventListener('change', function () {
      filterState[sel.dataset.f] = sel.value;
      applyFilters();
    });
  });
});
