# 주식 분석 리포트

Weinstein 스테이지 · Minervini Trend Template · Turtle ATR 3레이어 프레임워크 기반
종목 분석 결과를 공개하는 정적 사이트입니다. ([stock-agent](https://github.com/) 프로젝트의 리포트 발행물)

> ⚠️ **투자 권유 아님.** 기술적 분석 프레임워크의 판정 기록일 뿐이며, 매매 추천이 아닙니다.
> 모든 투자 책임은 투자자 본인에게 있습니다.

## 구조

- `docs/` — 발행 보고서 (gen.py가 자동 생성, 직접 편집 금지)
- `gen.py` — 워치리스트 분석 → 사이트 docs 변환
- `mkdocs.yml` — MkDocs Material 설정
- `.github/workflows/deploy.yml` — push 시 GitHub Pages 자동 배포

## 갱신 방법

```bash
python gen.py          # 최신 분석 반영
git add -A && git commit -m "update reports" && git push
# → GitHub Actions가 자동 빌드·배포
```

## 로컬 미리보기

```bash
pip install -r requirements.txt
mkdocs serve   # http://127.0.0.1:8000
```
