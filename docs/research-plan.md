# Research plan: are Taiwanese judgments consistent, or do they depend on the judge?

## Aim

Measure how much court outcomes in Taiwan depend on things the law says should not matter: which judge is assigned, the judge's background, the defendant's identity, and the circumstances of the decision. Report consistency measures that the judiciary and the public can act on.

## Agreed scope (October 2026)

**Central question.** In Taiwan, do criminal-court outcomes depend on things the law says should not matter: which judge is assigned, who the judge is, who the defendant is, and which party the defendant is linked to? The study follows cases from the prosecutor, through the trial judge, to appeal.

| | Scope |
|---|---|
| Courts | All 22 district courts, first-instance criminal cases; High Courts for appeals |
| Period | 2013–2026 (years covered by the open terminated-case microdata) |
| Offences | Fraud and money-mule cases, theft, drugs, assault, negligent traffic injury, drunk driving; for politics, vote buying (公職人員選舉罷免法, 妨害投票) and corruption (貪污治罪條例) |
| Outcomes | Conviction, prison length, convertibility, extra fines, probation, trial-stage detention and bail |
| Module 1 – judge lottery | Judge-dependence by offence, court and year; effect of the 2018 sentencing guidance and the 2023 AI sentencing system; **whether appeals correct outlier judges** |
| Module 2 – who the judge is | Seniority and experience, training cohort, entry route, gender where officially documented |
| Module 3 – who the defendant is | Indigenous, foreign nationals and migrant workers, legal aid or public defender vs retained counsel, gender; **trial-stage detention and bail decisions by judge** |
| Module 4 – politics | Outcomes for KMT-, DPP- and TPP-linked defendants in vote-buying and corruption trials, before and after the 2016 and 2024 changes of power; **the prosecutor stage** (charging, deferred prosecution) separated from the judge stage |
| Optional later | Administrative courts: government win rates and judge variation |
| Out of scope | Civil and family cases, Constitutional Court, time-of-day effects (only dates are recorded), investigation-stage detention (mostly unpublished), new opinion surveys |
| Judges | Named, but only where enough cases support a reliable estimate, always with confidence intervals and rank ranges, in factual wording |
| Output | One public report with charts, plus this repository |

Consistency is not the same as justice: a system can treat like cases alike and still be too harsh or biased as a whole. The study measures consistency and group differences; it does not judge whether average sentences are right.

## Status (9 October 2026)

| Planned | Done | Not done / why |
|---|---|---|
| Module 1: judge lottery by offence, court, year | 12 offences, 1.56 million single-judge first-instance cases 2013–2026; prison length, probation, extra fine, conviction; named-judge table (2022–2026) with safeguards | Convertibility analysed only in the pilot |
| Module 1: reforms (2018, 2023) | Difference-in-differences, randomisation inference, leave-one-out | Citizen-judge (國民法官) cases too few and panel-decided |
| Module 1: appeals | District appellate and High Court links; appeal and correction by judge stringency | Supreme Court stage; appellate–trial judge ties |
| Module 2: who the judge is | Experience from a career panel built from all case types; persistence; cross-offence; court movers | Training cohort, entry route and gender: not in open data; personnel notices (人審會) and court sites refused connections from outside Taiwan. Judge gender deliberately not inferred |
| Module 3: who the defendant is | Foreign nationals and gender (2024–2026 texts), Indigenous divisions, counsel type, trial-stage bail rulings | Age not published in judgments; migrant-worker status beyond nationality |
| Module 4: politics | All 2,283 election-offence district judgments 2013–2026 linked to candidates' parties; prosecution share vs candidate share before/after 2016; outcomes; opposition test; appeals | Corruption trials of politicians; non-prosecution decisions (不起訴) not in court data; TPP too few cases |
| Optional: administrative courts | — | Not started |
| RQ5 consequences (reoffending) | — | Needs linked criminal records |

## Research questions

| # | Question | Main outcome measures |
|---|---|---|
| RQ1 | **How large is the judge lottery** across offences, courts and years? | Noise-corrected between-judge variance; expected gap between two randomly drawn judges for the same case; split-half reliability of judge leniency. Outcomes: prison term, conviction, probation, fine add-ons, convertibility, detention. |
| RQ2 | **Which judge characteristics predict leniency?** | Effects of being assigned a judge with a given seniority, training cohort (期別), entry route (exam vs lateral from lawyers or prosecutors), prior prosecutorial service, appellate experience, and gender where officially documented. |
| RQ3 | **Are some defendants treated differently**, and does it depend on the judge? | Gaps for Indigenous defendants, foreign nationals and migrant workers, legal-aid and public-defender clients, and women, net of case facts; judge × defendant interactions within assignment pools. |
| RQ4 | **Do circumstances move decisions?** | Month-end reporting pressure, holiday and typhoon-day calendars, caseload shocks, high-profile media cases, release of sentencing tools. Pre-registered, with strong null priors. |
| RQ5 | **Does inconsistency have consequences?** | Reversal rates of outlier judges (accounting for appellate-trial judge ties); effect of randomly assigned leniency on reoffending. |
| RQ6 | **Did reforms reduce disparity?** | Changes in between-judge variance around the 2018 sentencing-trend guidance, the 2023 AI sentencing information system, and the 2023 citizen-judge system. |

## Identification strategy

1. **Random assignment is the backbone.** Each court distributes cases by advance, general rules (分案; 釋字665). Compare judges only within an assignment pool: court × case type (字別, which also marks the summary-court location) × period. Collect each court's written assignment rules to define pools exactly.
2. **Test balance; don't assume it.** The pilot found that case facts are not perfectly balanced across judges (related cases go to the same judge). Always control for case facts, report balance tests, and compare judge differences in a case-mix index (sentence predicted from facts) with judge differences in actual sentencing.
3. **Noise-corrected disparity.** Use REML / empirical-Bayes variance components or leave-out estimators (Kline–Saggio–Sølvsten), split-half reliability and within-pool permutation tests. Never interpret raw fixed-effect spreads.
4. **Judge characteristics** are estimated as "effects of being assigned such a judge" within pools. Traits are bundled (cohort, age, seniority), so report them jointly.
5. **Judge-stringency instruments** only for downstream questions (RQ5), with the Frandsen–Lefgren–Leslie tests of exclusion and monotonicity. Judges choose several margins at once (term, convertibility, fine, probation), which threatens exclusion.
6. **Rotation and transfer designs**: annual division reassignments (法院組織法 §79) and transfers let us separate judge style from court culture (movers designs, event studies).
7. **Extraneous factors**: only calendar-level shocks are testable with published data (decision date only). Hearing-time analyses would need prospectively collected 庭期表 calendars.
8. **Ranking**: if any judge-level estimates are reported at all, use rank confidence sets and shrinkage; the main text reports only distributions.

## Data

See [`data-sources.md`](data-sources.md). Plan:

- Terminated-case microdata 2013–2026, all courts (open): outcomes, judges, counsel type, coded reasons.
- Full texts for selected high-volume offences: drunk driving, fraud (including money-mule cases), theft, drug possession, traffic injury, assault. Bulk archives via a member account, collected from a Taiwan-based machine.
- Judge career panel from personnel decisions (人審會), division assignments and exam lists.
- Benchmarks: 涉外案件 statistics, legal-aid data, sentencing information system aggregates.

## Phases

| Phase | Time | Work |
|---|---|---|
| 0 | Done | Pilot: 2025 drunk driving, six courts with full text and all courts with microdata; parser validated by blind coding and against official records. |
| 1 | Months 1–2 | Load all microdata 2013–2026; map assignment pools per court; replicate RQ1 for six offences; write and register the pre-analysis plan (OSF or AEA registry). |
| 2 | Months 2–4 | Collect full texts for the selected offences; build and validate extractors for each; build the judge career panel. |
| 3 | Months 4–6 | Confirmatory analyses for RQ2–RQ4 on held-out years (explore 2013–2020, confirm 2021–2026); robustness; multiple-testing correction (Romano–Wolf or sharpened q-values). |
| 4 | Months 6–9 | Consequences and reforms (RQ5–RQ6); papers for a Taiwanese law review and an international empirical-legal-studies journal; release anonymised data and code. |

## Pre-analysis plan outline

- Primary outcomes per offence (fixed in advance): prison term in days, any extra fine, probation, convertibility.
- Assignment pool definition and exclusions.
- Primary estimands: noise-corrected judge SD; expected absolute gap between two random judges for the same case; split-half reliability.
- Trait list for RQ2 and defendant groups for RQ3.
- Shock list for RQ4 with expected sign and size, and the correction method.
- Power: from the pilot, about 30+ cases per judge are needed for useful judge-level reliability; small courts need multi-year windows.

## Threats and how to handle them

| Threat | Response |
|---|---|
| Non-random assignment (related cases, specialised divisions, 審查庭 routing) | Exact pools from written rules; balance tests; case-mix index comparison; sensitivity to pool definitions. |
| Text-extraction error | Blind double-coding samples per offence; cross-check against microdata by JID; report agreement. |
| Judge-specific writing style creating fake "facts" | Prefer facts with objective anchors (measured alcohol, statute, official 累犯 flag); test sensitivity to each extracted control. |
| Multiple testing and forking paths | Pre-registration; held-out confirmation years; corrected p-values. |
| Published-decision selection (about 80% of terminations) | Compare microdata counts with official termination statistics; analyse published decisions only and say so. |
| Panels (合議庭) | Identify the authoring judge; analyse single-judge decisions first. |

## Ethics

- Judgments and judges' names are public (法院組織法 §83); research use of published personal data has a basis in the PDPA.
- Judges may be named, but only with enough cases for a reliable estimate, with confidence intervals and rank ranges, and in factual language (no labels such as 藍/綠法官).
- Never store or share defendants' names; keep raw texts out of public repositories; honour takedowns (the API terms require deleting removed judgments).
- Share findings with the Judicial Yuan before publication and invite comment.
