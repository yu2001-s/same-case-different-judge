"""Write README.md with headline numbers taken from the analysis outputs.

build_readme.py SIX_RESULTS NATIONAL_RESULTS HELDOUT_AGREEMENT OUT_MD [ARTIFACT_URL]
"""
import json, sys

six_p, nat_p, agr_p, out_p = sys.argv[1:5]
url = sys.argv[5] if len(sys.argv) > 5 else ''
S = json.load(open(six_p)); N = json.load(open(nat_p)); A = json.load(open(agr_p))
pct = lambda x, d=0: f'{x * 100:.{d}f}%'
mc = S['microdata_check']
timing_sig = sum(1 for t in S['timing'] if t['q_bh'] < 0.05)
link = f'**[Open the interactive report]({url})** · ' if url else ''

md = f"""# Same Case, Different Judge

Do court judgments in Taiwan follow the law and the facts, or do they also depend on which judge is assigned and the circumstances of the day? This repository holds the research plan, a verified literature map, and a pilot study on 2025 drunk-driving sentences.

{link}Report source: [`report/index.html`](report/index.html) (open in a browser)

## Pilot findings (2025 drunk-driving judgments, 刑法§185-3 I)

**Six district courts, full text** (Taipei, New Taipei, Taoyuan, Taichung, Tainan, Kaohsiung): {S['n_sample']:,} single-judge judgments by {S['n_judges']} judges, with breath-alcohol level, prior record, crash and vehicle extracted from each text.

| Finding | Result |
|---|---|
| Share of sentence variation (after case facts and court) tied to the assigned judge | **{pct(S['mixed']['icc'])}** (judge SD ≈ {S['mixed']['judge_sd_days']:.0f} days) |
| Gap between 10th- and 90th-percentile judges for the same typical first offence | **≈ {S['lottery']['gap_p90_p10_days']:.0f} days** on an average of {S['desc']['sentence_mean'] / 30:.1f} months |
| Judge leniency in one random half of cases predicts the other half | r = {S['split_half']['r_mean_200']:.2f} |
| Real between-judge variation vs. shuffled judge labels | {S['permutation']['ratio']:.1f}× ({S['permutation']['n_perm']:,} shuffles, p = {S['permutation']['p_value']:.3f}) |
| Extra fine on top of prison (併科罰金), lenient- vs strict-decile judges | {pct(max(0, S['addl_fine']['adj_p10']))} vs {pct(S['addl_fine']['adj_p90'])} of cases |
| Case mix across judges vs sentencing differences | {S['casemix']['judge_sd_casemix_days']:.0f} days vs {S['casemix']['judge_sd_sentencing_days']:.0f} days (SD) |
| Calendar effects (weekday, month-end, pre-holiday, heavy days, December) surviving multiple-testing correction | {timing_sig} of {len(S['timing'])} |

**All {N['n_courts']} district courts, official microdata** (終結案件資料): {N['n']:,} cases, {N['n_judges']:,} judges. Judge share {pct(N['mixed']['icc'])}; 10th–90th percentile gap ≈ {N['lottery']['gap']:.0f} days; split-half r = {N['split_half']['r_mean']:.2f}; extra-fine rate {pct(max(0, N['addl_fine']['p10']))} vs {pct(N['addl_fine']['p90'])}; {pct(N['probation']['share_judges_never'])} of judges with 30+ cases never granted probation.

**Data quality.** On {A['n']} held-out judgments coded blind, alcohol level, sentence, fines, probation and judge matched 100%; prior record {pct(A['fields']['Prior drunk-driving case'])}, vehicle {pct(A['fields']['Vehicle type'])}. Against the Judicial Yuan's own microdata ({mc['n_matched']:,} matched judgments): prison term {pct(mc['prison_months'], 1)}, probation {pct(mc['probation'], 1)}, extra fine {pct(mc['addl_fine'], 1)}, judge {pct(mc['judge'], 1)}.

**Caveats.** One offence, one year. Case assignment is close to random but not perfectly so (related cases go to the same judge), so all models control for case facts. Judges are shown only as anonymous codes. Published judgments carry only the decision date, so time-of-day ("hungry judge") effects cannot be tested.

## Repository layout

| Path | Contents |
|---|---|
| `report/index.html` | The full illustrated report (findings, literature, research plan, methods, references) |
| `docs/research-plan.md` | Research questions, identification strategy, phases, pre-analysis plan outline, ethics |
| `docs/literature-review.md` | What is known internationally and in Taiwan, by theme |
| `docs/bibliography.md` | Every source found, with its verification status |
| `docs/data-sources.md` | Taiwanese judicial data sources, access tested, legal footing |
| `docs/methods.md` | Pilot pipeline, parsing rules, models, reproduction steps |
| `code/scraper/` | Polite collector for the public judgment search (FJUD) |
| `code/analysis/` | Judgment parser, six-court analysis, national microdata analysis, validation scoring |
| `code/report/` | Report and README builders (every number comes from the result files) |
| `code/literature/` | Builds the verified bibliography from the literature workflow output |
| `data/pilot/` | Analysis sample (no defendant names; judges as codes) and results |
| `data/national/` | National microdata results |
| `data/validation/` | Parser agreement with blind coding |
| `data/literature/` | Verified source records |

Raw judgment texts contain defendants' names and are deliberately not committed (see `.gitignore`); re-collect them with `code/scraper/`.
"""
open(out_p, 'w', encoding='utf-8').write(md)
print('wrote', out_p)
