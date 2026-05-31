// MkDocs Material 정렬 가능한 표 — 헤더 클릭 시 컬럼별 정렬.
// 클래스 없는 본문 표(생성된 Markdown 표)에 적용. instant navigation 대응(document$).
document$.subscribe(function () {
  var tables = document.querySelectorAll("article table:not([class])");
  tables.forEach(function (table) {
    new Tablesort(table);
  });
});
