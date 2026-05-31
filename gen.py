"""워치리스트·스냅샷·알림을 MkDocs 사이트 docs/로 변환·생성.

소스(메인 저장소):
  ../docs/watchlist/*.md            관찰 종목 (type=watchlist)
  ../docs/watchlist/snapshots/*.md  분석 스냅샷

출력(이 저장소 docs/):
  index.md            홈 대시보드 (요약 + 면책)
  watchlist/index.md  관찰 종목 목록  + 종목 상세 페이지 복사본
  snapshots/index.md  분석 스냅샷 목록 + 스냅샷 상세 페이지 복사본
  alerts/index.md     알림 타임라인 (이벤트 기록)

알림 상세(alerts/{uid}.md)는 monitor.py가 직접 push하므로 이 스크립트는
**삭제하지 않고** 인덱스만 다시 만든다. (과거 _reset_dir(OUT)가 alerts/를
통째로 지우던 버그를 회피 — 워치리스트/스냅샷 디렉터리만 재생성한다.)

판정 어휘·메뉴 구조 설명: ../docs/verdict-taxonomy.md
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
OUT_ALERT = OUT / "alerts"

DISCLAIMER = """\
!!! warning "투자 유의 / Disclaimer"
    이 사이트는 기술적 분석 프레임워크(Weinstein·Minervini·Turtle)의 **판정 결과를 기록**한 것으로,
    **투자 권유나 매매 추천이 아닙니다.** 모든 투자 책임은 투자자 본인에게 있습니다.
    수치는 분석 시점의 yfinance 데이터 기준이며 지연·오류가 있을 수 있습니다.
"""


def _frontmatter(text: str) -> dict:
    """YAML 프론트매터에서 **최상위 단일 줄 스칼라**만 추출(들여쓰기·리스트 줄 무시).

    멀티라인 값은 지원하지 않는다 — 현재 쓰는 필드(verdict, verdict-reason, stage 등)는
    모두 단일 줄이라 충분하다. 멀티라인 필드를 추가하면 PyYAML로 교체할 것.
    """
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


def _verdict_cell(verdict: str, reason: str) -> str:
    """'매수불가 (과열)' 또는 '매수후보' 형태의 판정 셀."""
    return f"{verdict} ({reason})" if reason else verdict


# --- 소스 → 출력 복사 + 메타 수집 ---

def _collect_watchlist() -> list[tuple[str, str, str]]:
    """type=watchlist 만 복사하고 (ticker, market, fname) 리스트 반환."""
    _reset_dir(OUT_WL)
    entries = []
    for md in sorted(SRC_WL.glob("*.md")):
        fm = _frontmatter(md.read_text(encoding="utf-8"))
        if fm.get("type") != "watchlist":
            continue
        shutil.copy(md, OUT_WL / md.name)
        entries.append((fm.get("ticker", md.stem), fm.get("market", ""), md.name))
    return entries


def _collect_snapshots() -> list[dict]:
    """스냅샷 복사 + 메타 dict 리스트 반환."""
    _reset_dir(OUT_SNAP)
    snaps = []
    for md in sorted(SRC_SNAP.glob("*.md")):
        fm = _frontmatter(md.read_text(encoding="utf-8"))
        shutil.copy(md, OUT_SNAP / md.name)
        snaps.append({
            "ticker":  fm.get("ticker", md.stem),
            "created": fm.get("created", ""),
            "verdict": fm.get("verdict", ""),
            "reason":  fm.get("verdict-reason", ""),
            "stage":   fm.get("stage", ""),
            "tt":      fm.get("trend-template-score", ""),
            "fname":   md.name,
        })
    # 분석일 내림차순(동일 날짜는 종목 오름차순 — 안정 정렬)
    snaps.sort(key=lambda s: s["ticker"])
    snaps.sort(key=lambda s: s["created"], reverse=True)
    return snaps


def _scan_alerts() -> list[dict]:
    """alerts/ 의 알림 페이지(uid.md) 메타를 최신순으로 반환. (삭제하지 않음)"""
    OUT_ALERT.mkdir(parents=True, exist_ok=True)
    alerts = []
    for md in OUT_ALERT.glob("*.md"):
        if md.name == "index.md":
            continue
        fm = _frontmatter(md.read_text(encoding="utf-8"))
        alerts.append({
            "created": fm.get("created", ""),
            "ticker":  fm.get("ticker", md.stem),
            "alert":   fm.get("alert", fm.get("title", "")),
            "fname":   md.name,
        })
    alerts.sort(key=lambda a: a["created"], reverse=True)
    return alerts


# --- 페이지 빌더 ---

def _dashboard(entries, snaps, alerts) -> str:
    lines = [
        "# 주식 분석 리포트",
        "",
        "Weinstein 스테이지 · Minervini Trend Template · Turtle ATR 3레이어 프레임워크 기반 종목 분석.",
        "",
        DISCLAIMER,
        "",
        "## 한눈에 보기",
        "",
        f"- 📋 **관찰 종목** {len(entries)}개 — [목록 보기](watchlist/index.md)",
        f"- 📊 **분석 스냅샷** {len(snaps)}건 — [최신순 보기](snapshots/index.md)",
        f"- 🔔 **알림** {len(alerts)}건 — [타임라인 보기](alerts/index.md)",
        "",
        "> 관찰 종목은 *무엇을 추적하는가*, 스냅샷은 *특정 시점의 판정 기록*, "
        "알림은 *임계선을 넘은 순간의 이벤트*입니다. (자세한 구분: 분석 스냅샷의 판정 어휘 참고)",
        "",
    ]
    if snaps:
        lines += [
            "## 최근 분석",
            "",
            "| 종목 | 분석일 | 판정 | Stage | TT |",
            "|------|--------|------|-------|----|",
        ]
        for s in snaps[:5]:
            lines.append(
                f"| {s['ticker']} | {s['created']} | {_verdict_cell(s['verdict'], s['reason'])} "
                f"| {s['stage']} | {s['tt']}/8 |"
            )
        lines += ["", "[→ 전체 스냅샷](snapshots/index.md)", ""]
    lines += ["---", f"_생성: {date.today()} · 프레임워크 자동 판정_"]
    return "\n".join(lines) + "\n"


def _watchlist_index(entries) -> str:
    lines = [
        "# 관찰 종목",
        "",
        "모니터링 대상 종목. 30분 폴링으로 상태 변화 시 [알림](../alerts/index.md)이 발송됩니다.",
        "",
        "| 종목 | 시장 | 상세 |",
        "|------|------|------|",
    ]
    for ticker, market, fname in sorted(entries):
        lines.append(f"| **{ticker}** | {market} | [{fname}]({fname}) |")
    return "\n".join(lines) + "\n"


def _snapshots_index(snaps) -> str:
    lines = [
        "# 분석 스냅샷",
        "",
        "특정 시점의 **판정 기록**(최신순). 판정 어휘 — "
        "**매수후보**(Stage 2 + TT 8/8) · **매수관찰**(Stage 2 + TT 6~7) · "
        "**매수불가**(사유: 과열·시장국면·하락국면·천장권·기준미달).",
        "",
        "| 종목 | 분석일 | 판정 | Stage | TT | 상세 |",
        "|------|--------|------|-------|----|----|",
    ]
    for s in snaps:
        lines.append(
            f"| {s['ticker']} | {s['created']} | {_verdict_cell(s['verdict'], s['reason'])} "
            f"| {s['stage']} | {s['tt']}/8 | [{s['fname']}]({s['fname']}) |"
        )
    return "\n".join(lines) + "\n"


def _alerts_index(alerts) -> str:
    lines = [
        "# 알림",
        "",
        "관찰 종목이 임계선을 넘은 **순간**에 자동 기록되는 이벤트(최신순). "
        "유형 — 📈 매수신호 · 👀 매수근접 · 📉 매도신호 · 🚨 손절경고.",
        "",
    ]
    if not alerts:
        lines += [
            '!!! info "아직 발생한 알림이 없습니다"',
            "    관찰 종목이 매수·매도·손절 조건을 충족하면 이곳에 자동으로 기록됩니다.",
        ]
        return "\n".join(lines) + "\n"
    lines += ["| 발생일 | 종목 | 유형 | 상세 |", "|--------|------|------|------|"]
    for a in alerts:
        lines.append(f"| {a['created']} | {a['ticker']} | {a['alert']} | [{a['fname']}]({a['fname']}) |")
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    entries = _collect_watchlist()
    snaps   = _collect_snapshots()
    alerts  = _scan_alerts()

    (OUT / "index.md").write_text(_dashboard(entries, snaps, alerts), encoding="utf-8")
    (OUT_WL / "index.md").write_text(_watchlist_index(entries), encoding="utf-8")
    (OUT_SNAP / "index.md").write_text(_snapshots_index(snaps), encoding="utf-8")
    (OUT_ALERT / "index.md").write_text(_alerts_index(alerts), encoding="utf-8")

    print(f"생성 완료: 관찰 {len(entries)}개 · 스냅샷 {len(snaps)}건 · 알림 {len(alerts)}건")


if __name__ == "__main__":
    main()
