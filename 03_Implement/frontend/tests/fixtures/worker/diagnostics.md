# Diagnostics

## Outline quality report (I10)

- schemaVersion: 1
- totalIslands: 1
- totalCardsInPath: 3
- pathLength: 4
- findings: 4
- [WARN] Q002: Many islands are missing summaries
  - detail: [REDACTED] (len:51)
  - refs: island:i1
- [WARN] Q003: Unreviewed summaries dominate
  - detail: [REDACTED] (len:54)
  - refs: island:i1
- [INFO] Q005: Many islands are not connected to other islands
  - detail: [REDACTED] (len:67)
  - refs: island:i1
- [WARN] Q009: No cards outside islands (possible forced grouping)
  - detail: [REDACTED] (len:164)

## Recommendations (I11)

- count: 2
- rec-q003-review-unreviewed-summaries: 未承認サマリのレビューを優先する
  - targets: island:i1
- rec-q005-reconnect-islands: 島間の関係を再検討する
  - targets: island:i1

## Contradiction signals (I12)

- signals: 0

## Distribution signals (I13)

- islands: 1
- cards: 3
- findings: 1
- [WARN] D003: Many isolated islands
  - islands: i1

## Dialectic balance (I19)

- hypotheses: 0
- claims: 2
- facts: 1
- findings: 0

## Metrics

| metric | value |
| --- | ---: |
| cardCount | 3 |
| islandCount | 1 |
| evidenceLinkCount | 2 |
| evidenceLinkDensity | 0.6667 |
| isolatedCardCount | 0 |
| isolationRate | 0 |
| connectedComponentCount | 1 |
| largestComponentRatio | 1 |
| averageDegree | 1.3333 |
| degreeP95 | 2 |
| degreeSkewRatio | 1.5 |
| bridgeEdgeCount | 2 |
| contradictionRatio | 0.5 |

### islandSizeDistribution

| size | islands |
| ---: | ---: |
| 3 | 1 |
