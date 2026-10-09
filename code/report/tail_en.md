
---

## About this repository

| Path | Contents |
|---|---|
| `README.md` | This report (English, full) |
| `README.zh-TW.md` | Plain-language report in Traditional Chinese |
| `figures/` | Chart images used in the reports (light and dark versions) |
| `data/named_judges.csv` | Named-judge table (2022–2026, judges with 100+ cases) |
| `data/results/` | Aggregate results for every module (JSON) |
| `data/pilot/`, `data/national/`, `data/validation/` | 2025 drunk-driving pilot: sample (no names), results, parser validation |
| `docs/` | Research plan and status, methods, data sources, literature review, verified bibliography |
| `code/analysis/` | Microdata parsers and the analysis scripts for each module |
| `code/scraper/` | Collectors for the public judgment search and the bulk judgment archives |
| `code/report/` | Report builders (every number in the reports comes from the result files) |
| `report/` | Interactive HTML versions of both reports (download and open in a browser) |

Methods and reproduction steps: [`docs/methods-full-programme.md`](docs/methods-full-programme.md). Raw microdata and judgment texts are not included: the texts contain defendants' names. Bulk judgment downloads need a free Judicial Yuan open-data member account.

All data come from public sources (Judicial Yuan open data and judgment database; Central Election Commission). Court judgments, including judges' names, are public under 法院組織法 §83. Differences between judges described here are within the legal sentencing ranges and do not indicate misconduct.
