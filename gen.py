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

import json
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
FEAR_INDEX_JSON = ROOT.parent / "data" / "fear_index.json"

DISCLAIMER = """\
!!! warning "투자 유의 / Disclaimer"
    이 사이트는 기술적 분석 프레임워크(Weinstein·Minervini·Turtle)의 **판정 결과를 기록**한 것으로,
    **투자 권유나 매매 추천이 아닙니다.** 모든 투자 책임은 투자자 본인에게 있습니다.
    수치는 분석 시점의 yfinance 데이터 기준이며 지연·오류가 있을 수 있습니다.
"""

SNAP_FILTERS = """\
<div class="snap-filters">
<label class="sf-label" for="sf-verdict">판정</label>
<select class="sf-select" id="sf-verdict" data-f="verdict">
<option value="">전체</option>
<option value="cand">매수후보</option>
<option value="watch">매수관찰</option>
<option value="nobuy">매수불가</option>
</select>
<label class="sf-label" for="sf-stage">Stage</label>
<select class="sf-select" id="sf-stage" data-f="stage">
<option value="">전체</option>
<option value="1">1</option>
<option value="2">2</option>
<option value="3">3</option>
<option value="4">4</option>
</select>
</div>
"""

WL_FILTERS = """\
<div class="snap-filters">
<label class="sf-label" for="sf-market">시장</label>
<select class="sf-select" id="sf-market" data-f="market">
<option value="">전체</option>
<option value="KRX">KRX</option>
<option value="NASDAQ">NASDAQ</option>
<option value="NYSE">NYSE</option>
</select>
</div>
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


_VERDICT_KIND = {"매수후보": "cand", "매수관찰": "watch", "매수불가": "nobuy"}


def _verdict_cell(verdict: str, reason: str) -> str:
    """판정을 색상 배지 HTML로 렌더 (사유는 옆에 옅은 글씨).

    md_in_html 확장으로 표 셀 내 인라인 HTML이 렌더된다. 정렬(tablesort)은
    셀 텍스트 기준이라 같은 판정끼리 묶인다.
    """
    kind = _VERDICT_KIND.get(verdict, "nobuy")
    badge = f'<span class="verdict verdict-{kind}">{verdict}</span>'
    if reason:
        return f'{badge} <span class="verdict-reason">({reason})</span>'
    return badge


def _company_name(title: str) -> str:
    """워치리스트 title('NVIDIA 관찰 종목')에서 기업명만 추출."""
    return re.sub(r"\s*관찰\s*종목\s*$", "", title).strip()


# --- 소스 → 출력 복사 + 메타 수집 ---

def _collect_watchlist() -> list[tuple[str, str, str, str]]:
    """type=watchlist 만 복사하고 (ticker, market, name, fname) 리스트 반환."""
    _reset_dir(OUT_WL)
    entries = []
    for md in sorted(SRC_WL.glob("*.md")):
        fm = _frontmatter(md.read_text(encoding="utf-8"))
        if fm.get("type") != "watchlist":
            continue
        shutil.copy(md, OUT_WL / md.name)
        entries.append((fm.get("ticker", md.stem), fm.get("market", ""),
                        _company_name(fm.get("title", "")), md.name))
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


def _latest_per_ticker(snaps: list[dict]) -> list[dict]:
    """종목당 최신 스냅샷 1건만 반환.

    snaps은 날짜 내림차순 정렬 상태여야 한다 (_collect_snapshots 반환값).
    파일은 모두 복사되므로 히스토리 URL은 그대로 유지된다.
    """
    seen: set[str] = set()
    result = []
    for s in snaps:
        if s["ticker"] not in seen:
            seen.add(s["ticker"])
            result.append(s)
    return result


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

def _dashboard(entries, snaps, alerts, names) -> str:
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
        "- 📊 **대시보드** (섹터 히트맵·공포 지수) — [보기](fear-index.md)",
        "",
        "> 관찰 종목은 *무엇을 추적하는가*, 스냅샷은 *특정 시점의 판정 기록*, "
        "알림은 *임계선을 넘은 순간의 이벤트*입니다. (자세한 구분: 분석 스냅샷의 판정 어휘 참고)",
        "",
    ]
    if snaps:
        lines += [
            "## 최근 분석",
            "",
            "| 종목 | 기업명 | 분석일 | 판정 | Stage | TT |",
            "|------|--------|--------|------|-------|----|",
        ]
        for s in snaps[:5]:
            name = names.get(s['ticker'], '')
            lines.append(
                f"| [**{s['ticker']}**](snapshots/{s['fname']}) | [{name}](snapshots/{s['fname']}) | {s['created']} | {_verdict_cell(s['verdict'], s['reason'])} "
                f"| {s['stage']} | {s['tt']}/8 |"
            )
        lines += ["", "[→ 전체 스냅샷](snapshots/index.md)", ""]
    lines += [
        "## 용어 설명",
        "",
        '??? info "📘 Stage (Weinstein 스테이지)란?"',
        "    주가 생명주기를 4단계로 분류하는 Stan Weinstein의 프레임워크. **30주 이동평균(≈150일 MA)** 방향과 가격 위치로 판단합니다.",
        "",
        "    | Stage | 명칭 | MA 방향 | 가격 위치 | 대응 |",
        "    |-------|------|---------|---------|------|",
        "    | **1** | 바닥 다지기 | 수평 | MA 위아래 | 대기 |",
        "    | **2** | 상승 국면 | 우상향 | MA 위 | **매수 구간** |",
        "    | **3** | 천장 분배 | 수평화 | MA 근처 | 매도 준비 |",
        "    | **4** | 하락 국면 | 우하향 | MA 아래 | 절대 금지 |",
        "",
        "    이 시스템은 **Stage 2** 종목만 매수 후보로 분류합니다.",
        "",
        '??? info "📘 TT (Trend Template — Minervini 8조건)란?"',
        "    Mark Minervini가 정의한 상승 구조 체크리스트. **충족 조건 수 / 8** 로 점수화.",
        "",
        "    | # | 조건 |",
        "    |---|------|",
        "    | 1 | 현재가 > 150일 MA, 200일 MA |",
        "    | 2 | 150일 MA > 200일 MA |",
        "    | 3 | 200일 MA 최소 1개월째 상승 중 |",
        "    | 4 | 50일 MA > 150일 MA, 200일 MA |",
        "    | 5 | 현재가 > 50일 MA |",
        "    | 6 | 현재가 ≥ 52주 저점 × 1.25 (+25% 이상) |",
        "    | 7 | 현재가 ≥ 52주 고점 × 0.75 (-25% 이내) |",
        "    | 8 | RS Rating(상대강도 등급) ≥ 70 |",
        "",
        "    **8/8**: 매수후보 조건 충족 · **6~7/8**: 매수관찰 · **5/8 이하**: 기준미달",
        "",
    ]
    lines += ["---", f"_생성: {date.today()} · 프레임워크 자동 판정_"]
    return "\n".join(lines) + "\n"


def _watchlist_index(entries) -> str:
    lines = [
        "# 관찰 종목",
        "",
        "모니터링 대상 종목. 30분 폴링으로 상태 변화 시 [알림](../alerts/index.md)이 발송됩니다.",
        "",
        WL_FILTERS,
        "| 종목 | 기업명 | 시장 |",
        "|------|--------|------|",
    ]
    for ticker, market, name, fname in sorted(entries):
        lines.append(f"| [**{ticker}**]({fname}) | [{name}]({fname}) | {market} |")
    return "\n".join(lines) + "\n"


def _snapshots_index(snaps, names) -> str:
    lines = [
        "# 분석 스냅샷",
        "",
        "특정 시점의 **판정 기록**(최신순). 판정 어휘 — "
        "**매수후보**(Stage 2 + TT 8/8) · **매수관찰**(Stage 2 + TT 6~7) · "
        "**매수불가**(사유: 과열·시장국면·하락국면·천장권·기준미달).",
        "",
        SNAP_FILTERS,
        "| 종목 | 기업명 | 분석일 | 판정 | Stage | TT |",
        "|------|--------|--------|------|-------|----|",
    ]
    for s in snaps:
        name = names.get(s['ticker'], '')
        lines.append(
            f"| [{s['ticker']}]({s['fname']}) | [{name}]({s['fname']}) | {s['created']} | {_verdict_cell(s['verdict'], s['reason'])} "
            f"| {s['stage']} | {s['tt']}/8 |"
        )
    return "\n".join(lines) + "\n"


def _alerts_index(alerts, names) -> str:
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
    lines += ["| 발생일 | 종목 | 기업명 | 유형 |", "|--------|------|--------|------|"]
    for a in alerts:
        lines.append(f"| {a['created']} | [{a['ticker']}]({a['fname']}) | [{names.get(a['ticker'], '')}]({a['fname']}) | {a['alert']} |")
    return "\n".join(lines) + "\n"


_REGIME_KO = {
    "STRONG_UPTREND":   "강한 상승",
    "UPTREND":          "상승",
    "RANGING":          "횡보",
    "DOWNTREND":        "하락",
    "STRONG_DOWNTREND": "강한 하락",
    "UNKNOWN":          "N/A",
}

_REGIME_ENTRY = {
    "STRONG_UPTREND":   "✅ 신규 진입 허용",
    "UPTREND":          "✅ 신규 진입 허용",
    "RANGING":          "⚠️ 신규 진입 자제",
    "DOWNTREND":        "🚫 신규 진입 금지",
    "STRONG_DOWNTREND": "🚫 신규 진입 금지",
    "UNKNOWN":          "—",
}


_TV_HEATMAP = """\
## 섹터 히트맵 (S&P 500)

<div class="tradingview-widget-container" style="height:520px;margin-bottom:1rem;">
<div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>
{
  "exchanges": [],
  "dataSource": "SPX500",
  "grouping": "sector",
  "blockSize": "market_cap_basic",
  "blockColor": "change",
  "locale": "ko",
  "colorTheme": "dark",
  "hasTopBar": true,
  "isDataSetEnabled": true,
  "isZoomEnabled": true,
  "hasSymbolTooltip": true,
  "isMonoSize": false,
  "width": "100%",
  "height": 500
}
</script>
</div>

> 출처: TradingView · 실시간 데이터 (페이지 로드 시점 기준)
"""


def _fear_index_page() -> str:
    """data/fear_index.json → fear-index.md 마크다운."""
    if not FEAR_INDEX_JSON.exists():
        return (
            "---\nhide:\n  - toc\n---\n\n"
            "# 대시보드\n\n"
            + _TV_HEATMAP
            + "\n"
            '!!! info "공포 지수 데이터 없음"\n'
            "    `python monitor.py --scan` 을 실행하면 아래 공포 지수가 채워집니다.\n"
        )

    data = json.loads(FEAR_INDEX_JSON.read_text(encoding="utf-8"))
    updated = data.get("updated_at", "")
    vix    = data.get("vix")
    vkospi = data.get("vkospi")
    us_r   = data.get("us_regime", "UNKNOWN")
    kr_r   = data.get("kr_regime", "UNKNOWN")
    cnn_fg = data.get("cnn_fear_greed")

    def _row(label: str, entry, regime: str) -> str:
        if entry is None:
            return f"| {label} | N/A | — | — | — | — |"
        change = entry.get("change", 0.0)
        sign = "+" if change > 0 else ""
        return (
            f"| {label} | {entry.get('value', 'N/A')} "
            f"| {sign}{change} "
            f"| {entry.get('grade_emoji', '')} {entry.get('grade', 'N/A')} "
            f"| {_REGIME_KO.get(regime, regime)} "
            f"| {_REGIME_ENTRY.get(regime, '—')} |"
        )

    def _cnn_section(fg: dict) -> list[str]:
        if not fg:
            return []
        score   = fg.get("score", 0)
        prev    = fg.get("prev_score", score)
        change  = fg.get("change", 0.0)
        sign    = "+" if change > 0 else ""
        emoji   = fg.get("rating_emoji", "⚪")
        rating  = fg.get("rating_ko", "—")

        rows = [
            "## CNN Fear & Greed Index",
            "",
            f"> 수집: {updated} · 출처: [CNN Markets](https://edition.cnn.com/markets/fear-and-greed)",
            "",
            f"| 점수 | 전일比 | 등급 |",
            f"|------|--------|------|",
            f"| **{score}** / 100 | {sign}{change} | {emoji} **{rating}** |",
            "",
            "### 구성 지표 (7개)",
            "",
            "| 지표 | 점수 | 등급 |",
            "|------|------|------|",
        ]
        for comp in fg.get("components", []):
            s = comp.get("score")
            s_str = f"{s:.1f}" if s is not None else "—"
            rows.append(
                f"| {comp['label']} | {s_str} "
                f"| {comp['rating_emoji']} {comp['rating_ko']} |"
            )
        rows.append("")
        return rows

    lines = [
        "---",
        "hide:",
        "  - toc",
        "---",
        "",
        "# 대시보드",
        "",
        _TV_HEATMAP,
        "",
        DISCLAIMER,
        "",
        *_cnn_section(cnn_fg),
        "## VIX / VKOSPI",
        "",
        f"> 수집: {updated} · `python monitor.py --scan` 실행 시 갱신",
        "",
        "| 지수 | 현재값 | 전일比 | 등급 | 시장 국면 | 신규 진입 |",
        "|------|--------|--------|------|---------|---------|",
        _row("VIX (미국 S&P500)", vix, us_r),
        _row("VKOSPI (한국 KOSPI)", vkospi, kr_r),
        "",
        "## 등급 기준",
        "",
        "| 등급 | VIX | VKOSPI | 의미 |",
        "|------|-----|--------|------|",
        "| 🔴 극공포 | > 40 | > 35 | 패닉 매도 구간, 저점 매수 기회일 수 있음 |",
        "| 🟠 공포   | 30–40 | 25–35 | 시장 불안 고조, 변동성 확대 |",
        "| 🟡 주의   | 20–30 | 20–25 | 불확실성 존재, 선별적 접근 |",
        "| ⚪ 중립   | 15–20 | 15–20 | 안정적 흐름, 정상 변동성 |",
        "| 🟢 탐욕   | < 15  | < 15  | 과열 주의, 변동성 낮음 |",
        "",
        "## 시장 국면 해석",
        "",
        "| 국면 | 한국어 | 신규 진입 |",
        "|------|--------|---------|",
        "| STRONG_UPTREND | 강한 상승 | ✅ 허용 |",
        "| UPTREND | 상승 | ✅ 허용 |",
        "| RANGING | 횡보 | ⚠️ 자제 |",
        "| DOWNTREND | 하락 | 🚫 금지 |",
        "| STRONG_DOWNTREND | 강한 하락 | 🚫 금지 |",
        "",
        "> 시장 국면은 S&P500 / KOSPI의 50·150·200일 MA 정렬 기반으로 판정합니다.",
        "",
        "---",
        f"_생성: {date.today()} · 프레임워크 자동 판정_",
    ]
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    entries = _collect_watchlist()
    snaps   = _collect_snapshots()          # 전체 히스토리 (파일 복사 완료)
    latest  = _latest_per_ticker(snaps)     # 인덱스·대시보드용: 종목당 최신 1건
    alerts  = _scan_alerts()
    names   = {ticker: name for ticker, _market, name, _fname in entries}

    (OUT / "index.md").write_text(_dashboard(entries, latest, alerts, names), encoding="utf-8")
    (OUT / "fear-index.md").write_text(_fear_index_page(), encoding="utf-8")
    (OUT_WL / "index.md").write_text(_watchlist_index(entries), encoding="utf-8")
    (OUT_SNAP / "index.md").write_text(_snapshots_index(latest, names), encoding="utf-8")
    (OUT_ALERT / "index.md").write_text(_alerts_index(alerts, names), encoding="utf-8")

    print(f"생성 완료: 관찰 {len(entries)}개 · 스냅샷 {len(latest)}종목({len(snaps)}건) · 알림 {len(alerts)}건")


if __name__ == "__main__":
    main()
