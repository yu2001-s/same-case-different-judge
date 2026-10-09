# Full programme methods (Modules 1–4, 2013–2026)

How the combined report ([`../report/index.html`](../report/index.html)) was produced. The drunk-driving pilot methods are in [`methods.md`](methods.md).

## 1. Data

| Step | Script | Output |
|---|---|---|
| Download all 75 terminated-case microdata archives (category 001, 2013-01 to 2026-07) | `opendata.judicial.gov.tw/api/FilesetLists/{id}/file` (open) | 7z archives, extracted locally (not committed) |
| Parse every district and High Court criminal litigation file (Big5 for 2013–2020, UTF-8 later; 72 vs 73 defendant fields; High Court rows carry the appeal outcome as an extra field) | `code/analysis/micro_all.py` | `defendants.parquet` (2,993,332 rows), `charges.parquet` (3,690,548 rows) |
| Appellants and defendant outcomes for district appellate cases (簡上 etc.) | `code/analysis/micro_appellants.py` | `dist_appellants.parquet` |
| Judge career panel: every judge-name appearance in every case type and court, by year | `code/analysis/judge_panel.py` | `judge_panel.parquet` |
| Repair judge names containing characters the Big5 files could not encode: fetch two of the judge's single-judge judgments and read the signing judge; accept only if both agree | `code/analysis/fix_names.py` | `data/results/name_fix.json` (26 of 30 repaired) |
| Analysis frame: district first instance, single named judge, single charge, no plea bargain, no juvenile case, 12 offences | `code/analysis/m1_prep.py` | `frame.parquet` (1.56 million cases) |
| Bulk judgment texts 2024-01 to 2026-07 (category 051, member token): district and summary-court criminal judgments only; defendant name strings, Latin-script names, stated nationality, interpreter use, sex/age where the charging document states them | `code/scraper/bulk_text.py` | per-month parquet (private; contains names) |
| Election-offence judgments: all district judgments whose charges fall under 公職人員選舉罷免法, 總統副總統選舉罷免法 or 刑法 §§143–148, by JID from the microdata | `code/scraper/fetch_jid.py` | 2,283 judgment texts (private) |
| Central Election Commission candidate files (2012–2024 elections; mirror `kiang/db.cec.gov.tw`), and a given-name gender model trained on candidates' recorded sex | `code/analysis/cec_build.py` | `candidates.parquet`, `data/results/name_gender.json` |

Offences are classified from the first (only) charge: 刑法 §185-3 drunk/drugged driving; §339 fraud (money mule if the accomplice flag is set); §§320–321 theft; §277 assault; §284 negligent injury; §354 criminal damage; §§309–310 defamation; 洗錢防制法 money laundering (money mule if accomplice); 毒品危害防制條例 §10 use, §11 possession.

## 2. Module 1: judge lottery

- **Assignment pool**: court × case word (字別) × quarter; pools with at least two judges.
- **Controls** (recorded in the microdata): 累犯, attempt, accomplice, coded mitigation (自首, 自白, §59, mental condition, minor), any aggravation, simplified procedure, Indigenous-division case word, domestic violence, counsel type, exact statutory sub-provision.
- **Residualise** each outcome on pool fixed effects and controls (within transformation + OLS).
- **Between-judge variance** τ² by the one-way ANOVA (method-of-moments) estimator with unequal group sizes: τ² = (MSB − σ²)/n₀, where σ² is the pooled within-judge variance. Judge share = τ²/(τ² + σ²). Two-random-judge expected gap = 2τ/√π.
- **Extra fines**: the microdata record fine amounts only from 2024, so the extra-fine outcome uses 2024–2026 cases only.
- **Robustness**: judge shares re-estimated without the §59, simplified-procedure and exemption controls (themselves judge decisions); they change by at most 0.2 percentage points.
- **Split-half reliability**: judges with 40+ cases; 20 random splits.
- **Named judges** (`m1_named.py`): cases from 2022 on; judges with 100+ cases; empirical-Bayes posterior mean and SD; 95% interval; 90% rank interval within the court from 2,000 posterior draws. Flag only if the 95% interval excludes zero **and** the rank interval lies wholly in the top or bottom 20% of the court, and only in courts with at least five listed judges.
- **Reforms** (`m1_reform.py`): τ of log prison length by offence × year. Difference-in-differences of log τ with offence and year fixed effects, weighted by cases. 2018 reform covers drunk driving, fraud, theft; 2023 reform adds assault, drug use, drug possession. Exact randomisation inference over all relabellings of which offences are covered; leave-one-covered-offence-out robustness.
- **Appeals** (`m1_appeals.py`): link single-defendant first-instance cases (decided by end-2024) to appeal records through the appeal's original-case fields; final sentence = appellate sentence where the appeal changed the judgment, else the first-instance sentence; remands dropped. Judge stringency = leave-one-out mean residual sentence. Report the reduction in τ² from first-instance to final sentence and the slopes of appeal by defendant / prosecutor on stringency (judge-clustered SEs).

## 3. Module 2: who the judge is

- **Experience**: first year a name decides litigation cases (any case type) in the microdata; novice = first appearance 2015+ and in years 0–2; experienced = 5+ years. τ compared between novice and experienced subsamples; level gap in pools containing both.
- **Persistence**: correlation of judges' mean residuals (standardised log prison length) between periods (2013–16, 2017–20, 2021–24), judges with 30+ cases in both, disattenuated by each period's reliability.
- **Cross-offence**: same calculation across offences for the same judge and court.
- **Movers**: judges with 30+ cases in two different courts in consecutive spells; correlation of relative harshness in the old and new court.
- Judge gender, cohort and entry route were **not** analysed: they are not in the open data and we did not infer them for individual judges.

## 4. Module 3: who the defendant is

- **Text-based attributes** (`m3_text.py`): single-defendant judgments 2024–2026 matched to the frame by JID. Foreign national = Latin-script name or stated foreign nationality (mainland China, Hong Kong, Macau separate). Gender = sex stated in the charging document where available, otherwise the given-name model (balanced prior; classify only if |log-odds| ≥ 2). Validation: 98.5% held-out accuracy among candidates; 97.9% against recorded sex in 4,488 pilot drunk-driving cases (81% coverage).
- **Gaps**: coefficients on foreign / mainland / female indicators in the same within-pool regressions, judge-clustered SEs; prison length in logs (reported as % = e^b − 1).
- **Pilot re-check** (`pilot_identity.py`): the foreign and gender gaps re-estimated in the 2025 six-court drunk-driving sample with alcohol band, prior drunk-driving count, vehicle, injury, education and economic status.
- **Indigenous divisions**: 原 case words compared with ordinary cases of the same court, case type (without 原) and year.
- **Counsel**: coefficients on counsel type (descriptive; counsel is not randomly assigned).
- **Detention**: all district 刑事其他 rulings on motions to stop detention (案由 containing 停止羈押; investigation-stage 偵聲 excluded); granted = 准許, partly granted, or a release form (具保, 責付, 限制住居). Judge = first-listed judge; pool = court × year; τ by ANOVA; permutation test (200 within-pool shuffles).

## 5. Module 4: politics

- **Candidate link** (`m4_parse.py`): for each judgment, candidates of the election named in the microdata's 選舉類別 field (else elections in the three years before the judgment), the office level implied by that field, and the court's counties. Score = number of mentions directly preceded by 候選人/支持/投票給/為使… or followed by 當選/參選/競選…; top score wins; cases aimed at making a candidate lose (不當選) and judgments where candidates of different parties tie are excluded; elections outside the candidate files (pre-2012, by-elections) are not linked. Robustness: score ≥ 2; excluding the 24% of links where the microdata name no election.
- **Prosecution intensity**: party share of cases in partisan races vs party share of candidates (and winners) in the same offices, weighted by the office mix of cases, for elections up to 2016 (KMT executive) vs 2018–2024 (DPP executive).
- **Outcomes** (`m4_analyze.py`): conviction, prison months (longest sentence on an election count) and probation, OLS with court, election-year and office fixed effects, number of counts, number of co-defendants and candidate-is-defendant; SEs clustered by judgment. Opposition test: indicator for the party not controlling the executive at the election, among KMT- and DPP-linked defendants.
- **Appeals**: High Court reversal (whole or part) by party.

## 6. Reproduce

```bash
python3 -I code/analysis/micro_all.py MICRO_DIR data/m1/parts       # then concatenate and deduplicate on court, year, case word, number, defendant
python3 -I code/analysis/micro_appellants.py MICRO_DIR data/m1/dist_appellants.parquet
python3 -I code/analysis/judge_panel.py MICRO_DIR data/m1/judge_panel.parquet
python3 -I code/analysis/m1_prep.py data/m1
python3 -I code/analysis/m1_analyze.py data/m1 data/results/m1_results.json
python3 -I code/analysis/m1_reform.py data/m1 data/results/m1_reform.json
python3 -I code/analysis/m1_appeals.py data/m1 data/results/m1_appeals.json
python3 -I code/analysis/m1_named.py data/m1 data/results/m1_named.json 2022-01-01 100
python3 -I code/analysis/m2_judges.py data/m1 data/results/m2_results.json
python3 -I code/analysis/m3_micro.py MICRO_DIR data/m1 data/results/m3_micro.json
python3 -I code/analysis/cec_build.py CEC_VOTEDATA_DIR data/cec
python3 -I code/analysis/m3_text.py BULK_PARSED_DIR data/m1 data/cec/name_gender.json data/results/m3_text.json
python3 -I code/analysis/m4_parse.py ELECTION_RAW_DIR data/m1 data/cec data/pol/cases.parquet
python3 -I code/analysis/m4_analyze.py data/pol/cases.parquet data/m1 data/cec data/results/m4_results.json
python3 -I code/report/build_final.py data/results data/pilot/results.json data/national/national_results.json data/results/pilot_identity.json LIT_REFS report/index.html
```

Bulk judgment downloads need a free Judicial Yuan open-data member account; the token is read from a private header file and never stored in the repository.

### Rebuilding the reports

```bash
python3 -I code/report/build_final.py data/results data/pilot/results.json data/national/national_results.json data/results/pilot_identity.json LIT_REFS report/index.html
python3 -I code/report/build_zh.py   data/results data/pilot/results.json data/national/national_results.json data/results/pilot_identity.json LIT_REFS report/index-zh.html
node code/report/figshots.js report/index.html figures/en && node code/report/figshots.js report/index-zh.html figures/zh
python3 -I code/report/html2md.py report/index.html figures/en README.md code/report/head_en.md code/report/tail_en.md
python3 -I code/report/html2md.py report/index-zh.html figures/zh README.zh-TW.md code/report/head_zh.md code/report/tail_zh.md
```
