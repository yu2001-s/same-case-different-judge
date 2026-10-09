# Data sources for studying Taiwanese judges

Status as tested on 2026-10-09 from a cloud container outside Taiwan. "Tested" means we downloaded or queried it ourselves.

## Core sources

| Source | What it contains | Access | Tested? | Use in this project |
|---|---|---|---|---|
| **終結案件資料與欄位說明** (terminated-case microdata), 司法院資料開放平臺, category 001 | One record per terminated case, all court levels. Yearly files 2013–2020 (102–109年), monthly files 2021-01 to 2026-07. Fields include court, case number, 案由, **法官名1–3**, termination date, outcome, defence type, probation and conditions, **累犯**, each charge's statute, sentence (有期徒刑 YYMM, 拘役 days, fine), convertibility, coded aggravating and mitigating reasons, and the judgment ID (JID, since 2021-09). Codebook: `統計系統資料欄位表` (DOCX). | **Open, no login.** `https://opendata.judicial.gov.tw/api/FilesetLists/{fileSetId}/file` returns a 7z archive of `!`-delimited text, records separated by `#`. | Yes: all 12 months of 2025 (about 15 MB) plus the codebook. | National analysis (28,202 §185-3 I records in 2025). Cross-check of our text parser by JID. |
| **裁判書查詢** FJUD (judgment.judicial.gov.tw) | Full text of every published judgment from district courts since 2000, with the signing judges, clerk and prosecutor. Party names are shown, birth dates and addresses are masked. Only the decision date is recorded. | Open web pages. Advanced search (`Default_AD.aspx`) by court, case type, date range, 案由 and full text; result lists capped at about 500 hits per query, so split queries by month. | Yes: 18,656 2025 公共危險 judgments from six courts. | Case facts that the microdata lack (alcohol level, crash, priors, vehicle, education, economic status). |
| **裁判書 monthly bulk archives**, 司法院資料開放平臺, category 051 | Monthly RAR of all judgments, 1996-01 to 2026-07, fields JID, JYEAR, JCASE, JNO, JDATE, JTITLE, JFULL, JPDF, plus a takedown list. | **Member account required** (free registration with e-mail; re-confirm every 3 months). Token from `POST /api/MemberTokens`. | Yes, with a member token: 2024-01 to 2026-07 (about 330 MB per month). Extract with `unar` (the container's 7z lacks RAR support). | Defendant nationality and names for Module 3. |
| **裁判書開放 API** (data.judicial.gov.tw/jdg) | `Auth`, `JList` (JIDs changed in the last 7 days), `JDoc` (one judgment). | Member account; service hours 00:00–06:00 Taiwan time only. Users must delete judgments that are later removed. | Endpoints exist; not usable outside service hours. | Keeping a corpus up to date. |
| **事實型量刑資訊系統** (intellisen.judicial.gov.tw) | Hand-coded sentencing factors for 10 offence groups, including 不能安全駕駛 (116,973 coded cases 2021–2025): alcohol band, vehicle, accident, licence, priors, 累犯, 自首, §59, probation. | Open JSON API for aggregates; per-judgment list blocked by a firewall. | Aggregate endpoints (via the literature sweep). | Codebook of legally relevant factors; benchmark distributions. |

| **Central Election Commission vote data** (mirror: github.com/kiang/db.cec.gov.tw, `voteData/`) | Candidate files (`elcand.csv`: name, party code, sex, birth date, elected flag), party codes (`elpaty.csv`) and area codes (`elbase.csv`) for every election, 2012–2024 used here. The CEC's own site refused connections from this container. | Public GitHub repository | Yes | Party of the candidate in election-crime cases; given-name gender model. |

## Judge characteristics

| Source | Content | Access notes |
|---|---|---|
| 司法院 人事審議委員會決議 / 人事訊息公告 | Named career events: passing 候補/試署 evaluations, transfers, promotions to 庭長/院長, second-instance postings, specialist certificates, often with 司法官班 cohort numbers. | Open HTML since about 2020; older notices in the legacy archive. Needs name disambiguation. |
| Each court's 法官事務分配 and 分案要點 | Which judge sits in which division each year; the rules that define assignment pools. | Linked from the Judicial Yuan site; individual court sites refused connections from outside Taiwan. |
| 考選部 exam pass lists | Exam year and rank of judicial-exam entrants (a proxy for cohort and age). | Query subdomains unreachable from outside Taiwan. |
| 法官評鑑委員會 decisions | Complaints and outcomes for named judges. | Open; misconduct only, not routine performance. |

Judge sex and age are not published per judge. Inferring sex from names is possible but noisy and ethically sensitive; prefer official sources.

## Benchmarks and context

- 各級法院各案類新收及終結件數 (monthly filings and terminations by court and case type, 2001–): denominators and caseload controls.
- 司法統計 portal: monthly and annual reports, gender statistics.
- 涉外案件 statistics: outcomes for foreign defendants (benchmark for nationality analyses).
- 法務部 檢察機關公開書類 (from 2018-06): indictments and summary-judgment applications, linked from each judgment; source of prosecutors' sentence requests where they exist.
- 司法院 annual public-perception survey (一般民眾對司法認知調查) and citizen-judge evaluation reports.

## Practical notes

- Download the microdata first: it is open, small (about 1–1.5 MB per month compressed) and already structured.
- 2013–2023 microdata files are Big5/CP950; names with characters outside Big5 (e.g. 凃, 温, 伃, 峯) decode as garbage. We repaired 26 of 30 affected judge names from the signatures of their judgments (`code/analysis/fix_names.py`). 2024+ files are UTF-8.
- High Court microdata case rows carry one extra field, so the judgment ID sits one position later than in district files.
- In the microdata, §185-3 charges have the paragraph (項) but not the subparagraph (款), so alcohol and drug cases cannot be separated without the text.
- For collegial panels, check which of 法官名1–3 is the authoring judge before attributing outcomes.
- Python 3.13's strict certificate checks reject some proxy certificates; using `curl` from Python avoided the problem in this container.
- Some court and ministry sites refuse connections from outside Taiwan. Run collection from a Taiwan-based machine for the full study.

## Legal footing

- 法院組織法 §83: courts must publish judgments; judges' names are part of the public record.
- 個人資料保護法 §6, §19, §20: research use of lawfully published personal data has a legal basis; the open-data licence places PDPA responsibility on the user.
- No Taiwanese rule comparable to France's 2019 ban on judge analytics was found.
- This project stores no defendant names in shared outputs. The pilot reported judges as codes; the full report names judges (published decision-makers) only under the safeguards described in the report: recent cases, at least 100 cases, shrunken estimates with intervals and rank ranges, and factual wording.
