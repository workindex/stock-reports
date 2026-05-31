# 주식 분석 리포트

Weinstein 스테이지 · Minervini Trend Template · Turtle ATR 3레이어 프레임워크 기반 종목 분석.

!!! warning "투자 유의 / Disclaimer"
    이 사이트는 기술적 분석 프레임워크(Weinstein·Minervini·Turtle)의 **판정 결과를 기록**한 것으로,
    **투자 권유나 매매 추천이 아닙니다.** 모든 투자 책임은 투자자 본인에게 있습니다.
    수치는 분석 시점의 yfinance 데이터 기준이며 지연·오류가 있을 수 있습니다.


## 한눈에 보기

- 📋 **관찰 종목** 18개 — [목록 보기](watchlist/index.md)
- 📊 **분석 스냅샷** 29건 — [최신순 보기](snapshots/index.md)
- 🔔 **알림** 0건 — [타임라인 보기](alerts/index.md)

> 관찰 종목은 *무엇을 추적하는가*, 스냅샷은 *특정 시점의 판정 기록*, 알림은 *임계선을 넘은 순간의 이벤트*입니다. (자세한 구분: 분석 스냅샷의 판정 어휘 참고)

## 최근 분석

| 종목 | 기업명 | 분석일 | 판정 | Stage | TT |
|------|--------|--------|------|-------|----|
| [**009150**](snapshots/009150-2026-05-31.md) | [삼성전기](snapshots/009150-2026-05-31.md) | 2026-05-31 | <span class="verdict verdict-nobuy">매수불가</span> <span class="verdict-reason">(과열)</span> | 2 | 8/8 |
| [**329180**](snapshots/329180-2026-05-31.md) | [HD현대중공업](snapshots/329180-2026-05-31.md) | 2026-05-31 | <span class="verdict verdict-watch">매수관찰</span> | 2 | 7/8 |
| [**APLD**](snapshots/APLD-2026-05-31.md) | [Applied Digital](snapshots/APLD-2026-05-31.md) | 2026-05-31 | <span class="verdict verdict-nobuy">매수불가</span> <span class="verdict-reason">(과열)</span> | 2 | 8/8 |
| [**AVGO**](snapshots/AVGO-2026-05-31.md) | [Broadcom](snapshots/AVGO-2026-05-31.md) | 2026-05-31 | <span class="verdict verdict-watch">매수관찰</span> | 2 | 7/8 |
| [**BE**](snapshots/BE-2026-05-31.md) | [Bloom Energy](snapshots/BE-2026-05-31.md) | 2026-05-31 | <span class="verdict verdict-nobuy">매수불가</span> <span class="verdict-reason">(과열)</span> | 2 | 8/8 |

[→ 전체 스냅샷](snapshots/index.md)

## 용어 설명

??? info "📘 Stage (Weinstein 스테이지)란?"
    주가 생명주기를 4단계로 분류하는 Stan Weinstein의 프레임워크. **30주 이동평균(≈150일 MA)** 방향과 가격 위치로 판단합니다.

    | Stage | 명칭 | MA 방향 | 가격 위치 | 대응 |
    |-------|------|---------|---------|------|
    | **1** | 바닥 다지기 | 수평 | MA 위아래 | 대기 |
    | **2** | 상승 국면 | 우상향 | MA 위 | **매수 구간** |
    | **3** | 천장 분배 | 수평화 | MA 근처 | 매도 준비 |
    | **4** | 하락 국면 | 우하향 | MA 아래 | 절대 금지 |

    이 시스템은 **Stage 2** 종목만 매수 후보로 분류합니다.

??? info "📘 TT (Trend Template — Minervini 8조건)란?"
    Mark Minervini가 정의한 상승 구조 체크리스트. **충족 조건 수 / 8** 로 점수화.

    | # | 조건 |
    |---|------|
    | 1 | 현재가 > 150일 MA, 200일 MA |
    | 2 | 150일 MA > 200일 MA |
    | 3 | 200일 MA 최소 1개월째 상승 중 |
    | 4 | 50일 MA > 150일 MA, 200일 MA |
    | 5 | 현재가 > 50일 MA |
    | 6 | 현재가 ≥ 52주 저점 × 1.25 (+25% 이상) |
    | 7 | 현재가 ≥ 52주 고점 × 0.75 (-25% 이내) |
    | 8 | RS Rating(상대강도 등급) ≥ 70 |

    **8/8**: 매수후보 조건 충족 · **6~7/8**: 매수관찰 · **5/8 이하**: 기준미달

---
_생성: 2026-06-01 · 프레임워크 자동 판정_
