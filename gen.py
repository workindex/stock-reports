"""워치리스트 분석을 MkDocs 사이트 docs/로 변환·생성.

소스: ../docs/watchlist/*.md (관찰 종목) + ../docs/watchlist/snapshots/*.md (스냅샷)
출력: ./docs/  (index.md + watchlist/ + snapshots/)

Obsidian 콜아웃·위키링크는 mkdocs-callouts / mkdocs-roamlinks 플러그인이 빌드 시 처리.
이 스크립트는 파일 복사 + 인덱스/면책 생성만 담당.
"""
from __future__ import annotations

import re
import shutil
from datetime import date
from pathlib import Path

ROOT      = Path(__file__).parent
SRC_WL    = ROOT.parent / "docs" / "watchlist"
SRC_SNAP  = SRC_WL / "snapshots"
OUT       = ROOT / "docs"
OUT_WL    = OUT / "watchlist"
OUT_SNAP  = OUT / "snapshots"

DISCLAIMER = """\
!!! warning "투자 유의 / Disclaimer"
    이 사이트는 기술적 분석 프레임워크(Weinstein·Minervini·Turtle)의 **판정 결과를 기록**한 것으로,
    **투자 권유나 매매 추천이 아닙니다.** 모든 투자 책임은 투자자 본인에게 있습니다.
    수치는 분석 시점의 yfinance 데이터 기준이며 지연·오류가 있을 수 있습니다.
"""


def _frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm


def _reset_dir(p: Path):
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)


def main():
    _reset_dir(OUT)
    OUT_WL.mkdir()
    OUT_SNAP.mkdir()

    # 워치리스트 엔트리 (type=watchlist) 복사 + 메타 수집
    entries = []
    for md in sorted(SRC_WL.glob("*.md")):
        fm = _frontmatter(md.read_text(encoding="utf-8"))
        if fm.get("type") != "watchlist":
            continue
        shutil.copy(md, OUT_WL / md.name)
        entries.append((fm.get("ticker", md.stem), fm.get("market", ""), md.name))

    # 스냅샷 복사 + 메타 수집
    snaps = []
    for md in sorted(SRC_SNAP.glob("*.md")):
        fm = _frontmatter(md.read_text(encoding="utf-8"))
        shutil.copy(md, OUT_SNAP / md.name)
        snaps.append((
            fm.get("ticker", md.stem), fm.get("created", ""),
            fm.get("verdict", ""), fm.get("stage", ""),
            fm.get("trend-template-score", ""), md.name,
        ))

    # index.md 생성
    lines = [
        "# 주식 분석 리포트",
        "",
        "Weinstein 스테이지 · Minervini Trend Template · Turtle ATR 3레이어 프레임워크 기반 종목 분석.",
        "",
        DISCLAIMER,
        "",
        "## 관찰 종목",
        "",
        "| 종목 | 시장 | 상세 |",
        "|------|------|------|",
    ]
    for ticker, market, fname in sorted(entries):
        lines.append(f"| **{ticker}** | {market} | [{fname}](watchlist/{fname}) |")

    lines += ["", "## 분석 스냅샷 (최신순)", "",
              "| 종목 | 분석일 | 판정 | Stage | TT | 상세 |",
              "|------|--------|------|-------|----|----|"]
    for ticker, created, verdict, stage, tt, fname in sorted(snaps, key=lambda x: x[1], reverse=True):
        lines.append(f"| {ticker} | {created} | {verdict} | {stage} | {tt}/8 | [{fname}](snapshots/{fname}) |")

    lines += ["", "---", f"_생성: {date.today()} · 프레임워크 자동 판정_"]
    (OUT / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"생성 완료: 워치리스트 {len(entries)}개, 스냅샷 {len(snaps)}개")


if __name__ == "__main__":
    main()
