# Pilot methods: 2025 drunk-driving sentences

The full programme (Modules 1–4, 2013–2026) is documented in [`methods-full-programme.md`](methods-full-programme.md). This file covers the pilot in [`../report/index.html`](../report/index.html) was produced, and how to reproduce it with the code in [`../code/`](../code/).

## 1. Six-court full-text sample

**Collection** (`code/scraper/`). For each of six district courts (Taipei TPD, New Taipei PCD, Taoyuan TYD, Taichung TCD, Tainan TND, Kaohsiung KSD) and each month of 2025, `collect.py count` runs one advanced search on the public FJUD system (`Default_AD.aspx`: criminal, 案由 = 公共危險, date range). Months with more than 480 results are split into thirds because result lists stop at 500. `collect.py list` pages through each result list (20 per page) and stores judgment IDs; `collect.py fetch` downloads each judgment page and keeps only the judgment text. Requests went through `curl` at a polite rate (one request per 0.5–1.2 s per worker, six workers at most). The raw pages contain defendants' names and are **not** committed.

**Parsing** (`code/analysis/parse.py`). Rules written for the conventions of Taiwanese criminal judgments:

| Field | Rule |
|---|---|
| Court, year, case type (字別), number, date, 案由 | Header lines 裁判字號 / 裁判日期 / 裁判案由 |
| Procedure | 簡易判決 in the heading; appeals have 上 in the case type; 協商判決 marks plea bargains |
| Text sections | Judgment proper ends at the clerk's certification (以上正本證明 / 上列正本證明); the quoted statute appendix (附錄) is removed; the prosecutor's application (附件), which summary judgments incorporate, is kept |
| Offence | 刑法第185條之3第1項第1款 (alcohol); 第3/4款 (drugs, excluded); 第2項/第3項 (injury or death, excluded); 第185條之4 (hit-and-run, excluded) |
| Breath alcohol | First 每公升X毫克 not followed by 以上 (so the legal threshold is skipped); blood alcohol % × 5 if no breath value |
| Sentence | 主文: 處有期徒刑 (Chinese numerals, years and months), 處拘役, 併科罰金, 處罰金, conversion rate after 易科罰金, 緩刑 years |
| Repeat offender | 累犯 in 主文, or an un-negated "依刑法第47條第1項…加重其刑" |
| Prior drunk driving | "前因/曾因/前有…公共危險/酒駕…判處/前科/紀錄", "多次酒駕", counts such as "2次酒駕" |
| Crash | collision words (肇事, 擦撞, 追撞, 自摔…) not negated (幸未肇事) and not part of police form names (交通事故當事人酒精測定紀錄表) or risk language (肇事危險) |
| Vehicle, education, economic status | First vehicle word after 駕駛/騎乘; stated 智識程度 and 經濟狀況 |
| Judge | 法官 names in the signature block just before the certification; single-judge decisions only |
| Defendant sex/age | Only when the prosecutor's application states them (often masked) |

**Validation.** (a) Blind coding by independent reviewers: 60 judgments used to refine rules, then 44 held-out judgments from all six courts. On the held-out set, alcohol level, prison term, detention, extra fine, conversion rate, probation and judge matched 100%; prior record 91%; vehicle 91%; repeat-offender 98%; crash 98%. (b) Official cross-check: parsed judgments matched to the Judicial Yuan's microdata by judgment ID (see `data/pilot/results.json → microdata_check`).

**Sample** (`code/analysis/analyze.py`). First-instance, single-count, simple-procedure, alcohol-only convictions with a parsed sentence, alcohol level and a single identified judge.

## 2. Models

- Outcome: prison term in days = 有期徒刑 months × 30 + 拘役 days.
- Legal controls: alcohol band (0.25–0.39, 0.40–0.54, 0.55–0.79, 0.80–0.99, 1.00+) and linear level; number of prior drunk-driving cases (0, 1, 2, 3+); 累犯; crash; injury mention; vehicle; 自首; Art. 59; stated education and economic status (with "not stated" categories).
- Assignment pool: court × 字別 (case-type prefix, which also marks the summary-court location, e.g. 壢交簡, 桃交簡, 原交簡) × quarter. Robustness: court × 字別 × month.
- **Judge share**: residualise the outcome on pool and controls (OLS), then fit a random-intercept model by judge on the residuals (REML). ICC = judge variance / (judge + residual variance). Likelihood-ratio test against no judge effect (boundary-corrected).
- **F-test**: judge fixed effects added to pool + controls.
- **Permutation test**: shuffle judge labels within pools 1,000 times; statistic = case-weighted variance of judges' mean residuals.
- **Split-half reliability**: split each judge's cases at random; correlate judge mean residuals across halves (judges with 20+ cases in the six-court data, 30+ nationally), 200 splits.
- **Typical case**: predicted sentence for a first offence at 0.47 mg/L, car, no crash, no other factors, in each court's main pool, plus each judge's BLUP.
- **Balance**: regress each case fact on pool + judge dummies; F-test for judges. Case-mix index: sentence predicted from facts alone; compare its noise-corrected judge SD with the judge SD in sentencing.
- **Add-ons**: linear probability models for any extra fine and for probation, with the same controls and pools.
- **Timing**: within-judge regressions (pool, case facts and judge fixed effects partialled out of both sides, Frisch–Waugh) for weekday, last three working days of the month, working days before long holidays, days on which the judge signed 5+ of these judgments, and December; Benjamini–Hochberg q-values.
- **Indigenous-case comparison**: 原-prefixed case types vs others within court × quarter, with controls; clustered by judge.

## 3. National microdata

`code/analysis/micro.py` reads all 2025 monthly 終結案件資料 archives, keeps district courts' 刑事訴訟 files, and extracts §185-3 I charges (the microdata do not record the 款, so alcohol and drug cases are combined). `micro_analyze.py` keeps single-defendant, single-charge, first-instance, non-plea, single-judge prison sentences in pools with at least two judges, controls for 累犯 and coded aggravating and mitigating reasons, and repeats the judge-share, permutation, split-half, add-on and court comparisons.

## 4. Reproduce

```bash
# full text (six courts, 2025): about 2 hours at a polite rate
python3 code/scraper/collect.py count data/pilot.db TPD,PCD,TYD 114 1 12
python3 code/scraper/collect.py list  data/pilot.db TPD,PCD,TYD
python3 code/scraper/collect.py fetch data/pilot.db data/raw TPD,PCD,TYD
# national microdata: download the 12 monthly 7z files (fileset IDs in docs/data-sources.md), extract to micro/
python3 code/analysis/micro.py micro data/micro_out/dui_2025.csv
python3 code/analysis/micro_analyze.py data/micro_out/dui_2025.csv data/national/national_results.json
# analysis
MICRO=data/micro_out/dui_2025.csv python3 code/analysis/analyze.py data/raw data/pilot
```

Requires Python 3.11+, pandas, numpy, scipy, statsmodels; `curl`; `7z` for the microdata.
