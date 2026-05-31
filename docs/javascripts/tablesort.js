// MkDocs Material — 표 정렬 + 스냅샷 필터. instant navigation 대응(document$).
document$.subscribe(function () {
  var tables = document.querySelectorAll("article table:not([class])");
  tables.forEach(function (table) {
    new Tablesort(table);
  });

  // 스냅샷 인덱스 페이지에서만 동작 (판정·Stage AND 필터)
  var filterState = { verdict: '', stage: '' };

  function applySnapFilters() {
    var table = document.querySelector('article table');
    if (!table) return;
    table.querySelectorAll('tbody tr').forEach(function (row) {
      var cells = row.querySelectorAll('td');
      if (cells.length < 5) return;

      // 판정: 4번째 셀의 .verdict 클래스로 판별
      var verdictSpan = cells[3].querySelector('.verdict');
      var verdictMatch = !filterState.verdict ||
        (verdictSpan && verdictSpan.classList.contains('verdict-' + filterState.verdict));

      // Stage: 5번째 셀 텍스트 (1~4)
      var stageMatch = !filterState.stage ||
        cells[4].textContent.trim() === filterState.stage;

      row.style.display = (verdictMatch && stageMatch) ? '' : 'none';
    });
  }

  document.querySelectorAll('.sf').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var field = btn.dataset.f;
      filterState[field] = btn.dataset.v;

      document.querySelectorAll('.sf[data-f="' + field + '"]').forEach(function (b) {
        b.classList.toggle('active', b === btn);
      });

      applySnapFilters();
    });
  });
});
