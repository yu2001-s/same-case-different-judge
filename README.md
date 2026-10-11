**English** · [繁體中文白話版](README.zh-TW.md)

# Same Case, Different Judge

Do criminal judgments in Taiwan follow the law and the facts, or do they also depend on who the judge is, who the defendant is, and politics? This report follows 1,560,890 first-instance criminal cases decided by single judges in all district courts from 2013 to 2026, plus 2,283 election-crime judgments, to measure how much the outcome depends on things the law says should not matter.

<sub>Data: Judicial Yuan open terminated-case microdata (終結案件資料), the judgment database (裁判書) and Central Election Commission candidate records</sub><br>
<sub>Judges are named only where the safeguards in §1.3 are met</sub><br>

## What we found

| Number | What it means |
|---|---|
| <b>4%–15%</b> | of the variation in prison terms that the recorded case facts do not explain is tied to which judge happened to be assigned, depending on the offence |
| <b>38 days</b> | expected gap in a fraud sentence between two randomly drawn judges of the same court, for comparable cases (average sentence 333 days) |
| <b>77%–99%</b> | of the typical judge-to-judge gap in prison terms survives the appeal stage, depending on the offence |
| <b>−14 / +16 pts</b> | chance of release on bail before verdict with a strict vs a lenient presiding judge (10th vs 90th percentile, relative to the same court and year; an upper bound) |

1. **Conviction depends little on the judge; punishment depends on it a lot.** Almost everyone in these single-judge cases is convicted, and conviction rates differ between judges by at most 2.2 percentage points (one standard deviation) in any high-volume offence. But how long the sentence is, whether it is suspended (probation) and whether a fine is added differ systematically between judges of the same court who receive comparable cases by lottery.
2. **The differences are real and follow the judge.** A judge's leniency measured on one random half of her or his cases predicts the other half (split-half correlation 0.85 for drunk driving), so it is not chance. It persists for years and carries over when a judge moves to another court (correlation 0.53 across 270 judges who moved), so it is not just the court's local practice.
3. **Sentencing tools have not visibly narrowed the gaps.** After the 2018 sentencing-trend guidance, the spread between judges in covered offences fell about 14% relative to other offences, but with only three covered offences this is not statistically distinguishable from zero (p = 0.21). After the 2023 AI sentencing system it *rose* relative to uncovered offences (+27%, p = 0.009); tougher fraud and drunk-driving laws arrived at the same time, so this cannot be attributed to the tool.
4. **Appeals correct little of the lottery.** Only 5.9% of these cases are appealed. Defendants of harsher judges appeal a little more and prosecutors appeal lenient judges a little more, but after the second instance 77%–99% of the typical judge-to-judge gap remains.
5. **Experience does not explain it.** Judges in their first three years sentence within 4.2% of judges with five or more years in every offence, and their spread is similar in most offences. A judge's style is lasting: correlations of 0.53–0.78 between consecutive four-year periods.
6. **Who the defendant is matters at the margins.** In a six-court 2025 sample where alcohol level, prior offences and vehicle are known, foreign nationals received drunk-driving sentences about 11% shorter than comparable Taiwanese defendants; women receive shorter sentences, especially for theft and assault. Gaps for cases heard in Indigenous divisions are small and mixed in direction.
7. **Release from detention also depends on who decides.** Of 23,123 trial-stage motions for release from detention (聲請具保停止羈押), 23% were granted. Within the same court and year the chance varies by about 13 percentage points (one standard deviation) between presiding judges; because motions are not randomly filed, this is an upper bound.
8. **Party and power in election-crime trials: no sign of targeted prosecution, but a probation gap.** Among 4,223 vote-buying and other election-offence defendants linked to a candidate, conviction rates show no detectable party difference, and the KMT-linked share of prosecutions did not rise after the DPP took power in 2016. DPP-linked defendants received shorter prison terms than KMT- or independent-linked ones in elections under both governments (+3.4 and +2.7 months, KMT minus DPP), which follows the party label rather than who held power. But defendants linked to the party *out of power* were less likely to have their prison terms suspended: −12 percentage points (p = 0.013; 0.038 after correcting for three outcomes), −17 points with stricter matching. This is the clearest political signal in the data and deserves follow-up.

## How you can measure a judge

Taiwanese district courts assign incoming cases to judges by a numbered rotation or lottery (分案), not by choice. Within the same court, case type and quarter, a defendant who drew judge A is therefore comparable to one who drew judge B. Differences between judges' outcomes in these **assignment pools** can be read as the effect of the judge, the same design used for US federal sentencing and asylum courts<sup>1,2</sup>.

We use the Judicial Yuan's open **terminated-case microdata**: every criminal case closed from January 2013 to July 2026, with the judge's name, the charge, the sentence, probation, fines, aggravating and mitigating factors recorded by the court, and how any appeal ended (2,993,332 defendant records). For a clean comparison we keep first-instance cases decided by a single judge, with one defendant charge, and remove plea bargains and juvenile cases. That leaves 1,560,890 cases across 12 common offences.

For each outcome we remove pool averages and the case factors recorded in the data (recidivism, attempt, accomplice role, confession, self-surrender, §59 mitigation, simplified procedure, counsel type, exact statutory sub-provision) and then estimate how much of what is left is tied to the judge. The estimate is **noise-corrected**: a judge with few cases will look extreme by chance, and a variance-components estimator subtracts an estimate of that chance component<sup>3</sup>. Some of these factors (§59 reductions, simplified procedure) are themselves the judge's choices; dropping them changes the judge's share of prison-term variation by at most 0.2 percentage points. Full methods are in the appendix.

## 1The judge lottery, offence by offence

Across the nine high-volume offences, the judge accounts for 4% to 15% of the unexplained variation in prison terms. In everyday terms: two judges drawn at random from the same court would, on average, sentence a comparable case differently by 8–21% of the typical sentence (more in the smaller offences in the table below). For drunk driving that is 8.6 days on an average of 101; for theft 9.9 days on 87; for fraud 38 days on 333.

**Expected sentence gap between two randomly drawn judges, same court, comparable case**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-gap-dark.png">
  <img alt="Expected sentence gap between two randomly drawn judges, same court, comparable case" src="figures/en/c-gap-light.png">
</picture>

<sub>Days of prison or detention, after legal factors and assignment pool; in brackets, the gap as a share of the offence's average sentence.</sub>

Prison length is not the only lever. Whether a sentence is suspended and whether a fine is added on top are even more judge-dependent. In drunk-driving cases the judge accounts for 12% of the variation in probation and 26% of the variation in extra fines (fines are recorded in the microdata only from 2024, so fine results cover 2024–2026; 30% of drunk-driving prison sentences carried one). In fraud the extra fine is rare (4.6% of cases) but highly judge-driven (40%): most judges almost never add one, while a small minority add one regularly.

**How much each decision depends on the judge**

<sub>Share of the variation not explained by legal factors and assignment pool that is tied to the judge (noise-corrected). Split-half: correlation of a judge's estimated leniency between two random halves of her or his cases (judges with 40+ cases); 1 = perfectly stable.</sub>

### 1.3 Named judges

Court judgments in Taiwan are public and carry the judge's name (法院組織法 §83). We therefore show how each judge's recent decisions compare with other judges *of the same court* deciding comparable cases. To avoid unfair labels the table follows strict rules: only cases from 2022 onward; only judges with at least 100 such cases; every estimate is shrunk toward the court average in proportion to its uncertainty; every estimate carries a 95% interval and a 90% range for the judge's rank among the court's listed judges. A judge is marked as *higher* or *lower* only when the whole 95% interval lies on one side of the court average **and** the rank range lies entirely in the top or bottom fifth of the court, in courts with at least five listed judges. Extra-fine rows use 2024–2026 cases only.

For drunk driving, 442 judges qualify; 41 are clearly above and 41 clearly below their court's average. A difference is not misconduct: all of these sentences are within the legal range. The table shows how much the person who happens to decide a case shapes its result.

<b>Judges compared with their own court</b>

Difference from the average judge of the same court for comparable cases (2022–2026; extra fines 2024–2026). Days of prison, or percentage points for probation and extra-fine rates. Rank = 90% range among the court's listed judges.

Below are only the judges flagged *clearly higher* or *clearly lower*, grouped by offence and decision; click a line to open its table. *Higher* means more of that outcome: longer prison terms, more probation or more extra fines. All 1,946 estimates, including judges who are not flagged, are in [`data/named_judges.csv`](data/named_judges.csv); GitHub shows it as a searchable table.

<details>
<summary><b>Drunk/drugged driving · prison length</b>: 41 clearly higher, 41 clearly lower, of 442 judges</summary>

| Court | Judge | Cases | Vs court average (days) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 桃園 Taoyuan | 蔡旻穎 | 286 | +44.3 | +40.4 to +48.1 | 99th pct of 80 | clearly higher |
| 新竹 Hsinchu | 王怡蓁 | 144 | +35.8 | +30.5 to +41.0 | 98th pct of 21 | clearly higher |
| 臺中 Taichung | 陳培維 | 156 | +30.7 | +25.7 to +35.8 | 99th pct of 61 | clearly higher |
| 桃園 Taoyuan | 葉宇修 | 130 | +28.0 | +22.5 to +33.5 | 94th–98th pct of 80 | clearly higher |
| 桃園 Taoyuan | 高世軒 | 122 | +26.0 | +20.3 to +31.7 | 93rd–98th pct of 80 | clearly higher |
| 桃園 Taoyuan | 方楷烽 | 181 | +25.7 | +21.0 to +30.4 | 93rd–98th pct of 80 | clearly higher |
| 臺南 Tainan | 莊政達 | 120 | +23.6 | +17.8 to +29.3 | 94th–99th pct of 56 | clearly higher |
| 桃園 Taoyuan | 郭鍵融 | 120 | +23.0 | +17.3 to +28.7 | 92nd–97th pct of 80 | clearly higher |
| 臺南 Tainan | 周紹武 | 266 | +22.6 | +18.6 to +26.6 | 94th–99th pct of 56 | clearly higher |
| 彰化 Changhua | 王祥豪 | 335 | +22.2 | +18.7 to +25.8 | 99th pct of 35 | clearly higher |
| 臺南 Tainan | 林欣玲 | 312 | +21.9 | +18.2 to +25.5 | 92nd–99th pct of 56 | clearly higher |
| 桃園 Taoyuan | 陳藝文 | 134 | +21.3 | +15.8 to +26.7 | 92nd–96th pct of 80 | clearly higher |
| 臺南 Tainan | 林政斌 | 169 | +19.9 | +15.0 to +24.8 | 88th–99th pct of 56 | clearly higher |
| 桃園 Taoyuan | 黃弘宇 | 188 | +18.5 | +13.9 to +23.2 | 91st–94th pct of 80 | clearly higher |
| 基隆 Keelung | 李岳 | 135 | +18.3 | +12.9 to +23.7 | 90th pct of 5 | clearly higher |
| 苗栗 Miaoli | 顏碩瑋 | 205 | +18.0 | +13.5 to +22.5 | 97th pct of 15 | clearly higher |
| 臺中 Taichung | 徐煥淵 | 164 | +17.8 | +12.8 to +22.7 | 93rd–98th pct of 61 | clearly higher |
| 臺南 Tainan | 鄧希賢 | 279 | +17.5 | +13.6 to +21.4 | 87th–94th pct of 56 | clearly higher |
| 新北 New Taipei | 楊肅宇 | 314 | +17.4 | +13.8 to +21.1 | 92nd–97th pct of 19 | clearly higher |
| 新竹 Hsinchu | 翁禎翊 | 128 | +17.4 | +11.9 to +23.0 | 88th–93rd pct of 21 | clearly higher |
| 臺南 Tainan | 陳碧玉 | 259 | +17.4 | +13.4 to +21.4 | 87th–96th pct of 56 | clearly higher |
| 嘉義 Chiayi | 陳威憲 | 161 | +17.3 | +12.3 to +22.3 | 83rd–98th pct of 26 | clearly higher |
| 嘉義 Chiayi | 何啓榮 | 127 | +16.9 | +11.3 to +22.5 | 83rd–98th pct of 26 | clearly higher |
| 臺中 Taichung | 湯有朋 | 148 | +16.4 | +11.2 to +21.6 | 91st–98th pct of 61 | clearly higher |
| 臺南 Tainan | 蔡奇秀 | 201 | +16.0 | +11.5 to +20.5 | 83rd–94th pct of 56 | clearly higher |
| 新竹 Hsinchu | 江永楨 | 133 | +15.6 | +10.1 to +21.0 | 83rd–93rd pct of 21 | clearly higher |
| 士林 Shilin | 黃雅君 | 488 | +15.2 | +12.2 to +18.1 | 95th pct of 10 | clearly higher |
| 花蓮 Hualien | 王龍寬 | 120 | +15.0 | +9.3 to +20.7 | 96th pct of 14 | clearly higher |
| 臺中 Taichung | 陳建宇 | 122 | +14.0 | +8.3 to +19.7 | 84th–98th pct of 61 | clearly higher |
| 彰化 Changhua | 巫美蕙 | 311 | +13.2 | +9.5 to +16.8 | 90th–96th pct of 35 | clearly higher |
| 桃園 Taoyuan | 黃筱晴 | 240 | +13.1 | +8.9 to +17.2 | 84th–91st pct of 80 | clearly higher |
| 臺中 Taichung | 王曼寧 | 135 | +13.0 | +7.5 to +18.4 | 83rd–96th pct of 61 | clearly higher |
| 雲林 Yunlin | 梁智賢 | 125 | +12.9 | +7.3 to +18.6 | 85th–97th pct of 17 | clearly higher |
| 彰化 Changhua | 許淞傑 | 187 | +12.0 | +7.3 to +16.7 | 90th–96th pct of 35 | clearly higher |
| 臺中 Taichung | 吳欣哲 | 171 | +11.8 | +6.9 to +16.6 | 81st–96th pct of 61 | clearly higher |
| 桃園 Taoyuan | 鄧瑋琪 | 225 | +11.7 | +7.4 to +16.0 | 81st–91st pct of 80 | clearly higher |
| 臺中 Taichung | 呂超群 | 129 | +11.7 | +6.2 to +17.2 | 81st–96th pct of 61 | clearly higher |
| 臺中 Taichung | 陳嘉宏 | 210 | +10.8 | +6.4 to +15.2 | 81st–94th pct of 61 | clearly higher |
| 彰化 Changhua | 吳永梁 | 105 | +10.3 | +4.2 to +16.4 | 84th–96th pct of 35 | clearly higher |
| 宜蘭 Yilan | 蕭淳元 | 103 | +10.2 | +4.1 to +16.4 | 82nd–96th pct of 14 | clearly higher |
| 高雄 Kaohsiung | 李承曄 | 1,066 | +6.0 | +4.0 to +8.0 | 88th–98th pct of 20 | clearly higher |
| 嘉義 Chiayi | 王品惠 | 189 | −21.1 | −25.7 to −16.4 | 2nd–6th pct of 26 | clearly lower |
| 桃園 Taoyuan | 呂秉炎 | 121 | −20.8 | −26.5 to −15.1 | 1st–4th pct of 80 | clearly lower |
| 臺南 Tainan | 黃毓庭 | 126 | −20.4 | −26.0 to −14.8 | 1st–6th pct of 56 | clearly lower |
| 新竹 Hsinchu | 黃美盈 | 101 | −19.0 | −25.2 to −12.8 | 2nd–7th pct of 21 | clearly lower |
| 新北 New Taipei | 劉安榕 | 128 | −18.8 | −24.4 to −13.3 | 3rd–8th pct of 19 | clearly lower |
| 新北 New Taipei | 潘長生 | 1,182 | −18.7 | −20.6 to −16.8 | 3rd–8th pct of 19 | clearly lower |
| 臺南 Tainan | 卓穎毓 | 189 | −18.4 | −23.0 to −13.7 | 1st–8th pct of 56 | clearly lower |
| 臺中 Taichung | 李昇蓉 | 105 | −18.2 | −24.3 to −12.1 | 1st–9th pct of 61 | clearly lower |
| 桃園 Taoyuan | 張英尉 | 221 | −17.5 | −21.8 to −13.1 | 1st–7th pct of 80 | clearly lower |
| 苗栗 Miaoli | 紀雅惠 | 265 | −17.1 | −21.0 to −13.1 | 3rd–10th pct of 15 | clearly lower |
| 桃園 Taoyuan | 曾煒庭 | 173 | −16.9 | −21.7 to −12.0 | 1st–8th pct of 80 | clearly lower |
| 桃園 Taoyuan | 何信儀 | 138 | −16.7 | −22.1 to −11.4 | 1st–8th pct of 80 | clearly lower |
| 臺中 Taichung | 張美眉 | 134 | −16.3 | −21.8 to −10.9 | 1st–12th pct of 61 | clearly lower |
| 新竹 Hsinchu | 蔡玉琪 | 204 | −16.1 | −20.5 to −11.6 | 2nd–12th pct of 21 | clearly lower |
| 臺中 Taichung | 彭國能 | 148 | −15.7 | −20.9 to −10.5 | 1st–12th pct of 61 | clearly lower |
| 臺南 Tainan | 周宛瑩 | 319 | −15.5 | −19.1 to −11.9 | 3rd–13th pct of 56 | clearly lower |
| 嘉義 Chiayi | 卓春慧 | 241 | −15.3 | −19.4 to −11.1 | 6th–17th pct of 26 | clearly lower |
| 臺南 Tainan | 蕭雅毓 | 226 | −15.2 | −19.5 to −10.9 | 3rd–13th pct of 56 | clearly lower |
| 臺中 Taichung | 黃佳琪 | 140 | −15.1 | −20.5 to −9.8 | 1st–14th pct of 61 | clearly lower |
| 臺中 Taichung | 吳逸儒 | 130 | −15.1 | −20.6 to −9.6 | 1st–14th pct of 61 | clearly lower |
| 桃園 Taoyuan | 羅杰治 | 192 | −15.0 | −19.6 to −10.3 | 2nd–12th pct of 80 | clearly lower |
| 臺南 Tainan | 鄭燕璘 | 245 | −14.9 | −19.0 to −10.8 | 3rd–15th pct of 56 | clearly lower |
| 嘉義 Chiayi | 郭振杰 | 190 | −14.8 | −19.5 to −10.2 | 6th–17th pct of 26 | clearly lower |
| 臺中 Taichung | 丁智慧 | 126 | −14.8 | −20.4 to −9.2 | 1st–14th pct of 61 | clearly lower |
| 臺中 Taichung | 戰諭威 | 142 | −14.6 | −19.9 to −9.3 | 2nd–16th pct of 61 | clearly lower |
| 臺南 Tainan | 高如宜 | 275 | −13.9 | −17.8 to −10.0 | 4th–17th pct of 56 | clearly lower |
| 臺東 Taitung | 姚亞儒 | 305 | −13.8 | −17.6 to −10.2 | 5th–15th pct of 10 | clearly lower |
| 臺南 Tainan | 王惠芬 | 264 | −13.6 | −17.6 to −9.7 | 4th–17th pct of 56 | clearly lower |
| 嘉義 Chiayi | 粘柏富 | 105 | −13.5 | −19.6 to −7.4 | 6th–17th pct of 26 | clearly lower |
| 士林 Shilin | 張明儀 | 825 | −13.2 | −15.5 to −10.9 | 5th pct of 10 | clearly lower |
| 嘉義 Chiayi | 官怡臻 | 167 | −13.1 | −18.1 to −8.2 | 6th–17th pct of 26 | clearly lower |
| 雲林 Yunlin | 楊謹瑜 | 143 | −13.1 | −18.4 to −7.8 | 3rd–15th pct of 17 | clearly lower |
| 桃園 Taoyuan | 孫立婷 | 192 | −12.4 | −17.0 to −7.8 | 4th–19th pct of 80 | clearly lower |
| 雲林 Yunlin | 蔡宗儒 | 104 | −12.2 | −18.4 to −6.2 | 3rd–15th pct of 17 | clearly lower |
| 彰化 Changhua | 高郁茹 | 192 | −10.8 | −15.4 to −6.1 | 1st–13th pct of 35 | clearly lower |
| 臺東 Taitung | 林涵雯 | 196 | −10.2 | −14.8 to −5.6 | 5th–15th pct of 10 | clearly lower |
| 宜蘭 Yilan | 陳嘉瑜 | 314 | −9.7 | −13.4 to −6.1 | 4th–18th pct of 14 | clearly lower |
| 彰化 Changhua | 李淑惠 | 295 | −9.3 | −13.1 to −5.6 | 1st–16th pct of 35 | clearly lower |
| 高雄 Kaohsiung | 張震 | 715 | −8.1 | −10.5 to −5.6 | 2nd–12th pct of 20 | clearly lower |
| 高雄 Kaohsiung | 林英奇 | 426 | −8.0 | −11.1 to −4.8 | 2nd–18th pct of 20 | clearly lower |
| 橋頭 Ciaotou | 洪柏鑫 | 519 | −7.0 | −9.9 to −4.2 | 3rd–10th pct of 15 | clearly lower |

</details>

<details>
<summary><b>Drunk/drugged driving · probation rate</b>: 52 clearly higher, 4 clearly lower, of 442 judges</summary>

| Court | Judge | Cases | Vs court average (points) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 新竹 Hsinchu | 馮俊郎 | 105 | +46.2 | +43.3 to +49.2 | 98th pct of 21 | clearly higher |
| 桃園 Taoyuan | 羅杰治 | 192 | +31.7 | +29.5 to +33.9 | 98th–99th pct of 80 | clearly higher |
| 桃園 Taoyuan | 劉得為 | 128 | +29.1 | +26.4 to +31.8 | 96th–99th pct of 80 | clearly higher |
| 桃園 Taoyuan | 林育駿 | 251 | +29.0 | +27.1 to +30.9 | 96th–98th pct of 80 | clearly higher |
| 基隆 Keelung | 施添寶 | 105 | +28.4 | +25.5 to +31.4 | 90th pct of 5 | clearly higher |
| 嘉義 Chiayi | 粘柏富 | 105 | +28.1 | +25.2 to +31.1 | 98th pct of 26 | clearly higher |
| 桃園 Taoyuan | 曾煒庭 | 173 | +27.5 | +25.2 to +29.8 | 94th–98th pct of 80 | clearly higher |
| 桃園 Taoyuan | 莊劍郎 | 108 | +26.5 | +23.6 to +29.4 | 94th–97th pct of 80 | clearly higher |
| 臺北 Taipei | 姚念慈 | 106 | +25.4 | +22.4 to +28.3 | 96th pct of 11 | clearly higher |
| 彰化 Changhua | 李怡昕 | 237 | +23.3 | +21.3 to +25.3 | 99th pct of 35 | clearly higher |
| 高雄 Kaohsiung | 李承曄 | 1,066 | +22.2 | +21.3 to +23.2 | 98th pct of 20 | clearly higher |
| 臺南 Tainan | 鄭文祺 | 129 | +21.6 | +18.9 to +24.2 | 99th pct of 56 | clearly higher |
| 橋頭 Ciaotou | 陳明呈 | 247 | +20.9 | +18.9 to +22.8 | 97th pct of 15 | clearly higher |
| 桃園 Taoyuan | 謝長志 | 171 | +20.2 | +17.9 to +22.6 | 89th–93rd pct of 80 | clearly higher |
| 桃園 Taoyuan | 陳藝文 | 134 | +19.8 | +17.2 to +22.4 | 89th–93rd pct of 80 | clearly higher |
| 新北 New Taipei | 張誌洋 | 112 | +19.1 | +16.2 to +21.9 | 92nd–97th pct of 19 | clearly higher |
| 桃園 Taoyuan | 何宇宸 | 277 | +18.7 | +16.8 to +20.5 | 88th–93rd pct of 80 | clearly higher |
| 桃園 Taoyuan | 古御詩 | 163 | +18.6 | +16.2 to +21.0 | 88th–93rd pct of 80 | clearly higher |
| 彰化 Changhua | 陳怡潔 | 312 | +18.4 | +16.6 to +20.1 | 96th pct of 35 | clearly higher |
| 新北 New Taipei | 俞兆安 | 220 | +17.5 | +15.4 to +19.6 | 92nd–97th pct of 19 | clearly higher |
| 桃園 Taoyuan | 林述亨 | 463 | +17.2 | +15.8 to +18.7 | 88th–91st pct of 80 | clearly higher |
| 花蓮 Hualien | 劉孟昕 | 181 | +15.4 | +13.1 to +17.7 | 82nd–96th pct of 14 | clearly higher |
| 花蓮 Hualien | 鍾晴 | 105 | +14.7 | +11.8 to +17.6 | 82nd–96th pct of 14 | clearly higher |
| 宜蘭 Yilan | 游欣怡 | 133 | +14.4 | +11.8 to +17.1 | 96th pct of 14 | clearly higher |
| 桃園 Taoyuan | 施育傑 | 106 | +13.4 | +10.4 to +16.3 | 84th–87th pct of 80 | clearly higher |
| 花蓮 Hualien | 黃夢萱 | 100 | +13.2 | +10.2 to +16.2 | 82nd–96th pct of 14 | clearly higher |
| 臺南 Tainan | 黃毓庭 | 126 | +11.9 | +9.2 to +14.6 | 94th–97th pct of 56 | clearly higher |
| 桃園 Taoyuan | 郭鍵融 | 120 | +11.8 | +9.0 to +14.5 | 83rd–87th pct of 80 | clearly higher |
| 士林 Shilin | 許凱翔 | 100 | +11.8 | +8.8 to +14.8 | 95th pct of 10 | clearly higher |
| 彰化 Changhua | 余仕明 | 115 | +11.7 | +8.8 to +14.5 | 93rd pct of 35 | clearly higher |
| 桃園 Taoyuan | 潘曉萱 | 277 | +10.6 | +8.7 to +12.4 | 83rd–86th pct of 80 | clearly higher |
| 臺南 Tainan | 廖建瑋 | 204 | +10.5 | +8.3 to +12.6 | 92nd–97th pct of 56 | clearly higher |
| 桃園 Taoyuan | 陳韋如 | 268 | +10.3 | +8.5 to +12.2 | 83rd–86th pct of 80 | clearly higher |
| 宜蘭 Yilan | 劉致欽 | 156 | +9.9 | +7.5 to +12.3 | 89th pct of 14 | clearly higher |
| 臺南 Tainan | 潘明彥 | 380 | +9.9 | +8.3 to +11.4 | 92nd–96th pct of 56 | clearly higher |
| 臺南 Tainan | 王惠芬 | 264 | +8.9 | +7.0 to +10.8 | 92nd–96th pct of 56 | clearly higher |
| 臺中 Taichung | 鄭咏欣 | 152 | +8.1 | +5.6 to +10.5 | 99th pct of 61 | clearly higher |
| 新竹 Hsinchu | 李建慶 | 194 | +7.9 | +5.7 to +10.1 | 83rd–93rd pct of 21 | clearly higher |
| 橋頭 Ciaotou | 李冠儀 | 689 | +7.8 | +6.7 to +9.0 | 90th pct of 15 | clearly higher |
| 桃園 Taoyuan | 方楷烽 | 181 | +7.8 | +5.5 to +10.0 | 82nd–83rd pct of 80 | clearly higher |
| 苗栗 Miaoli | 高御庭 | 110 | +7.6 | +4.7 to +10.4 | 97th pct of 15 | clearly higher |
| 彰化 Changhua | 宋庭華 | 189 | +7.4 | +5.2 to +9.6 | 84th–90th pct of 35 | clearly higher |
| 新竹 Hsinchu | 楊祐庭 | 147 | +7.1 | +4.6 to +9.6 | 83rd–93rd pct of 21 | clearly higher |
| 新北 New Taipei | 何奕萱 | 387 | +7.1 | +5.5 to +8.6 | 87th pct of 19 | clearly higher |
| 士林 Shilin | 葛名翔 | 664 | +7.0 | +5.8 to +8.2 | 85th pct of 10 | clearly higher |
| 彰化 Changhua | 梁義順 | 111 | +5.9 | +3.0 to +8.8 | 81st–90th pct of 35 | clearly higher |
| 彰化 Changhua | 黃佩穎 | 125 | +5.6 | +2.9 to +8.3 | 81st–90th pct of 35 | clearly higher |
| 臺東 Taitung | 姚亞儒 | 305 | +5.5 | +3.7 to +7.2 | 95th pct of 10 | clearly higher |
| 臺中 Taichung | 黃建都 | 143 | +4.7 | +2.1 to +7.2 | 94th–98th pct of 61 | clearly higher |
| 臺中 Taichung | 黃凡瑄 | 112 | +3.9 | +1.1 to +6.8 | 89th–98th pct of 61 | clearly higher |
| 臺南 Tainan | 茆怡文 | 179 | +3.6 | +1.3 to +5.9 | 85th–90th pct of 56 | clearly higher |
| 臺南 Tainan | 周宛瑩 | 319 | +2.9 | +1.1 to +4.6 | 83rd–90th pct of 56 | clearly higher |
| 橋頭 Ciaotou | 許博鈞 | 665 | −9.1 | −10.2 to −7.8 | 3rd pct of 15 | clearly lower |
| 高雄 Kaohsiung | 賴建旭 | 967 | −5.5 | −6.5 to −4.5 | 2nd–18th pct of 20 | clearly lower |
| 橋頭 Ciaotou | 林永村 | 422 | −5.1 | −6.6 to −3.6 | 10th pct of 15 | clearly lower |
| 士林 Shilin | 林銘宏 | 180 | −4.8 | −7.1 to −2.6 | 5th–6th pct of 10 | clearly lower |

</details>

<details>
<summary><b>Drunk/drugged driving · extra-fine rate (2024–2026)</b>: 30 clearly higher, 11 clearly lower, of 219 judges</summary>

| Court | Judge | Cases | Vs court average (points) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 新北 New Taipei | 黎錦福 | 544 | +63.0 | +60.0 to +66.0 | 97th pct of 15 | clearly higher |
| 桃園 Taoyuan | 吳宜珍 | 111 | +60.8 | +54.3 to +67.4 | 92nd–99th pct of 43 | clearly higher |
| 桃園 Taoyuan | 林其玄 | 160 | +60.7 | +55.2 to +66.2 | 92nd–99th pct of 43 | clearly higher |
| 桃園 Taoyuan | 李信龍 | 143 | +56.5 | +50.7 to +62.3 | 90th–99th pct of 43 | clearly higher |
| 桃園 Taoyuan | 蔡旻穎 | 132 | +56.5 | +50.5 to +62.5 | 90th–99th pct of 43 | clearly higher |
| 臺南 Tainan | 盧鳳田 | 189 | +52.5 | +47.4 to +57.5 | 99th pct of 38 | clearly higher |
| 桃園 Taoyuan | 黃筱晴 | 154 | +49.7 | +44.1 to +55.2 | 87th–92nd pct of 43 | clearly higher |
| 新北 New Taipei | 吳丁偉 | 236 | +48.8 | +44.2 to +53.3 | 90th pct of 15 | clearly higher |
| 桃園 Taoyuan | 何信儀 | 138 | +48.5 | +42.6 to +54.4 | 87th–90th pct of 43 | clearly higher |
| 士林 Shilin | 楊峻宇 | 590 | +45.8 | +42.9 to +48.7 | 90th pct of 5 | clearly higher |
| 新竹 Hsinchu | 王怡蓁 | 116 | +45.2 | +38.8 to +51.6 | 95th pct of 10 | clearly higher |
| 臺南 Tainan | 陳本良 | 103 | +42.0 | +35.1 to +48.8 | 96th pct of 38 | clearly higher |
| 桃園 Taoyuan | 范振義 | 124 | +39.7 | +33.5 to +46.0 | 85th pct of 43 | clearly higher |
| 新北 New Taipei | 俞兆安 | 220 | +38.5 | +33.8 to +43.2 | 83rd pct of 15 | clearly higher |
| 高雄 Kaohsiung | 賴建旭 | 506 | +37.3 | +34.2 to +40.4 | 96th pct of 13 | clearly higher |
| 臺東 Taitung | 陳偉達 | 230 | +31.5 | +26.9 to +36.0 | 94th pct of 9 | clearly higher |
| 苗栗 Miaoli | 顏碩瑋 | 131 | +31.3 | +25.2 to +37.3 | 95th pct of 10 | clearly higher |
| 彰化 Changhua | 許家偉 | 166 | +30.8 | +25.4 to +36.2 | 94th–98th pct of 23 | clearly higher |
| 臺南 Tainan | 潘明彥 | 210 | +30.8 | +25.9 to +35.6 | 91st–93rd pct of 38 | clearly higher |
| 臺南 Tainan | 周紹武 | 186 | +30.5 | +25.4 to +35.6 | 91st–93rd pct of 38 | clearly higher |
| 桃園 Taoyuan | 邱筠雅 | 127 | +29.1 | +23.0 to +35.3 | 80th–83rd pct of 43 | clearly higher |
| 彰化 Changhua | 張琇涵 | 168 | +27.5 | +22.1 to +32.9 | 89th–98th pct of 23 | clearly higher |
| 宜蘭 Yilan | 程明慧 | 144 | +27.0 | +21.2 to +32.8 | 96th pct of 11 | clearly higher |
| 花蓮 Hualien | 劉孟昕 | 121 | +23.9 | +17.6 to +30.2 | 90th pct of 5 | clearly higher |
| 彰化 Changhua | 熊霈淳 | 152 | +21.4 | +15.8 to +27.0 | 80th–94th pct of 23 | clearly higher |
| 彰化 Changhua | 林慧欣 | 170 | +20.5 | +15.2 to +25.8 | 80th–89th pct of 23 | clearly higher |
| 彰化 Changhua | 簡仲頤 | 174 | +18.5 | +13.2 to +23.8 | 80th–89th pct of 23 | clearly higher |
| 新竹 Hsinchu | 江宜穎 | 104 | +16.9 | +10.1 to +23.7 | 85th pct of 10 | clearly higher |
| 臺東 Taitung | 陳昱維 | 228 | +16.7 | +12.1 to +21.3 | 83rd pct of 9 | clearly higher |
| 屏東 Pingtung | 楊青豫 | 463 | +15.6 | +12.3 to +18.8 | 90th pct of 5 | clearly higher |
| 高雄 Kaohsiung | 李承曄 | 607 | −53.5 | −56.4 to −50.7 | 4th pct of 13 | clearly lower |
| 臺中 Taichung | 黃渙文 | 125 | −41.5 | −47.7 to −35.3 | 5th pct of 10 | clearly lower |
| 桃園 Taoyuan | 高世軒 | 122 | −34.0 | −40.3 to −27.7 | 1st–13th pct of 43 | clearly lower |
| 桃園 Taoyuan | 張明宏 | 166 | −32.8 | −38.2 to −27.4 | 1st–15th pct of 43 | clearly lower |
| 高雄 Kaohsiung | 林軒鋒 | 598 | −32.5 | −35.4 to −29.7 | 12th pct of 13 | clearly lower |
| 臺南 Tainan | 鄭雅文 | 341 | −25.7 | −29.5 to −21.9 | 1st–12th pct of 38 | clearly lower |
| 高雄 Kaohsiung | 呂明燕 | 112 | −24.8 | −31.3 to −18.2 | 19th pct of 13 | clearly lower |
| 新北 New Taipei | 楊肅宇 | 314 | −24.2 | −28.1 to −20.2 | 3rd–10th pct of 15 | clearly lower |
| 臺南 Tainan | 林岳葳 | 274 | −23.1 | −27.3 to −18.9 | 1st–20th pct of 38 | clearly lower |
| 新北 New Taipei | 徐子涵 | 906 | −23.1 | −25.4 to −20.7 | 3rd–10th pct of 15 | clearly lower |
| 屏東 Pingtung | 黃紀錄 | 931 | −8.4 | −10.7 to −6.1 | 10th pct of 5 | clearly lower |

</details>

<details>
<summary><b>Theft · prison length</b>: 19 clearly higher, 12 clearly lower, of 216 judges</summary>

| Court | Judge | Cases | Vs court average (days) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 臺北 Taipei | 宋恩同 | 156 | +34.2 | +28.1 to +40.4 | 97th pct of 16 | clearly higher |
| 基隆 Keelung | 李岳 | 143 | +33.2 | +26.8 to +39.6 | 92nd pct of 6 | clearly higher |
| 臺南 Tainan | 張婉寧 | 106 | +28.2 | +20.9 to +35.5 | 98th pct of 23 | clearly higher |
| 彰化 Changhua | 王祥豪 | 162 | +26.4 | +20.4 to +32.5 | 92nd–97th pct of 19 | clearly higher |
| 臺北 Taipei | 賴鵬年 | 189 | +22.1 | +16.5 to +27.8 | 91st pct of 16 | clearly higher |
| 彰化 Changhua | 林怡君 | 130 | +21.3 | +14.6 to +27.9 | 87th–97th pct of 19 | clearly higher |
| 苗栗 Miaoli | 朱俊瑋 | 220 | +20.8 | +15.5 to +26.0 | 88th–96th pct of 12 | clearly higher |
| 新竹 Hsinchu | 王怡蓁 | 105 | +20.1 | +12.7 to +27.4 | 94th pct of 9 | clearly higher |
| 臺中 Taichung | 陳盈睿 | 141 | +18.1 | +11.7 to +24.6 | 88th–96th pct of 13 | clearly higher |
| 苗栗 Miaoli | 顏碩瑋 | 144 | +17.2 | +10.8 to +23.6 | 88th–96th pct of 12 | clearly higher |
| 臺中 Taichung | 王曼寧 | 109 | +16.9 | +9.7 to +24.1 | 88th–96th pct of 13 | clearly higher |
| 桃園 Taoyuan | 陳布衣 | 169 | +16.8 | +10.8 to +22.7 | 89th–98th pct of 32 | clearly higher |
| 士林 Shilin | 黃雅君 | 100 | +15.8 | +8.3 to +23.2 | 95th pct of 10 | clearly higher |
| 彰化 Changhua | 陳建文 | 121 | +14.8 | +7.9 to +21.6 | 82nd–92nd pct of 19 | clearly higher |
| 桃園 Taoyuan | 蔡旻穎 | 155 | +14.5 | +8.3 to +20.7 | 86th–98th pct of 32 | clearly higher |
| 桃園 Taoyuan | 黃弘宇 | 104 | +14.3 | +7.0 to +21.6 | 83rd–98th pct of 32 | clearly higher |
| 高雄 Kaohsiung | 張震 | 483 | +12.8 | +9.2 to +16.4 | 92nd–98th pct of 20 | clearly higher |
| 桃園 Taoyuan | 曾雨明 | 319 | +12.7 | +8.3 to +17.1 | 83rd–95th pct of 32 | clearly higher |
| 新北 New Taipei | 徐蘭萍 | 677 | +9.7 | +6.6 to +12.7 | 84th–98th pct of 22 | clearly higher |
| 臺北 Taipei | 翁毓潔 | 134 | −20.9 | −27.5 to −14.4 | 3rd–9th pct of 16 | clearly lower |
| 臺南 Tainan | 鄭銘仁 | 139 | −20.6 | −27.1 to −14.2 | 2nd–6th pct of 23 | clearly lower |
| 苗栗 Miaoli | 洪振峰 | 141 | −19.2 | −25.6 to −12.8 | 4th pct of 12 | clearly lower |
| 新北 New Taipei | 張誌洋 | 104 | −17.8 | −25.2 to −10.5 | 2nd–7th pct of 22 | clearly lower |
| 彰化 Changhua | 李淑惠 | 140 | −16.7 | −23.2 to −10.3 | 3rd–13th pct of 19 | clearly lower |
| 桃園 Taoyuan | 鄧瑋琪 | 107 | −15.1 | −22.4 to −7.9 | 2nd–17th pct of 32 | clearly lower |
| 臺南 Tainan | 高如宜 | 116 | −14.5 | −21.5 to −7.5 | 2nd–11th pct of 23 | clearly lower |
| 基隆 Keelung | 鄭虹眞 | 112 | −13.6 | −20.7 to −6.5 | 8th pct of 6 | clearly lower |
| 新竹 Hsinchu | 楊惠芬 | 114 | −13.0 | −20.0 to −5.9 | 6th–17th pct of 9 | clearly lower |
| 高雄 Kaohsiung | 林英奇 | 259 | −12.9 | −17.8 to −8.1 | 2nd–12th pct of 20 | clearly lower |
| 宜蘭 Yilan | 陳嘉瑜 | 141 | −12.0 | −18.4 to −5.5 | 7th pct of 7 | clearly lower |
| 橋頭 Ciaotou | 陳箐 | 507 | −10.1 | −13.6 to −6.5 | 4th–11th pct of 14 | clearly lower |

</details>

<details>
<summary><b>Money mule (laundering) · prison length</b>: 6 clearly higher, 8 clearly lower, of 143 judges</summary>

| Court | Judge | Cases | Vs court average (days) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 桃園 Taoyuan | 曾雨明 | 424 | +61.4 | +56.6 to +66.3 | 96th pct of 11 | clearly higher |
| 臺中 Taichung | 徐煥淵 | 120 | +50.9 | +42.0 to +59.8 | 96th pct of 11 | clearly higher |
| 新北 New Taipei | 黎錦福 | 231 | +21.2 | +14.7 to +27.7 | 88th–96th pct of 13 | clearly higher |
| 彰化 Changhua | 巫美蕙 | 110 | +19.4 | +10.1 to +28.6 | 93rd pct of 7 | clearly higher |
| 新北 New Taipei | 鄭淳予 | 117 | +17.5 | +8.6 to +26.5 | 88th–96th pct of 13 | clearly higher |
| 高雄 Kaohsiung | 陳力揚 | 144 | +17.3 | +9.1 to +25.5 | 96th pct of 12 | clearly higher |
| 桃園 Taoyuan | 陳彥年 | 146 | −45.7 | −53.8 to −37.6 | 4th pct of 11 | clearly lower |
| 臺南 Tainan | 李俊彬 | 160 | −42.2 | −50.0 to −34.5 | 2nd pct of 24 | clearly lower |
| 桃園 Taoyuan | 林慈雁 | 473 | −30.1 | −34.7 to −25.4 | 14th pct of 11 | clearly lower |
| 臺北 Taipei | 謝欣宓 | 161 | −28.2 | −36.0 to −20.5 | 4th–12th pct of 12 | clearly lower |
| 臺北 Taipei | 洪英花 | 124 | −26.2 | −35.0 to −17.4 | 4th–12th pct of 12 | clearly lower |
| 高雄 Kaohsiung | 林英奇 | 171 | −22.6 | −30.2 to −15.1 | 4th pct of 12 | clearly lower |
| 屏東 Pingtung | 蕭筠蓉 | 135 | −19.6 | −28.0 to −11.2 | 6th–19th pct of 8 | clearly lower |
| 苗栗 Miaoli | 紀雅惠 | 133 | −16.8 | −25.2 to −8.3 | 5th–15th pct of 10 | clearly lower |

</details>

<details>
<summary><b>Money mule (laundering) · probation rate</b>: 9 clearly higher, 4 clearly lower, of 143 judges</summary>

| Court | Judge | Cases | Vs court average (points) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 臺北 Taipei | 洪英花 | 124 | +20.4 | +14.6 to +26.1 | 88th–96th pct of 12 | clearly higher |
| 桃園 Taoyuan | 高上茹 | 306 | +17.9 | +14.0 to +21.7 | 96th pct of 11 | clearly higher |
| 臺北 Taipei | 謝欣宓 | 161 | +16.6 | +11.4 to +21.7 | 88th–96th pct of 12 | clearly higher |
| 臺南 Tainan | 陳貽明 | 102 | +12.8 | +6.6 to +19.1 | 85th–98th pct of 24 | clearly higher |
| 高雄 Kaohsiung | 張嘉芳 | 223 | +12.1 | +7.7 to +16.6 | 96th pct of 12 | clearly higher |
| 臺南 Tainan | 李俊彬 | 160 | +11.5 | +6.3 to +16.7 | 85th–98th pct of 24 | clearly higher |
| 新北 New Taipei | 鄭淳予 | 117 | +9.9 | +4.0 to +15.8 | 81st–96th pct of 13 | clearly higher |
| 新北 New Taipei | 白光華 | 150 | +9.8 | +4.5 to +15.2 | 81st–96th pct of 13 | clearly higher |
| 苗栗 Miaoli | 紀雅惠 | 133 | +9.4 | +3.8 to +15.0 | 85th–95th pct of 10 | clearly higher |
| 臺北 Taipei | 王星富 | 114 | −17.1 | −23.1 to −11.1 | 4th pct of 12 | clearly lower |
| 士林 Shilin | 蘇昌澤 | 107 | −13.7 | −19.8 to −7.6 | 10th pct of 5 | clearly lower |
| 屏東 Pingtung | 黃紀錄 | 221 | −11.6 | −16.1 to −7.2 | 6th–19th pct of 8 | clearly lower |
| 臺南 Tainan | 郭瓊徽 | 174 | −8.2 | −13.2 to −3.2 | 2nd–19th pct of 24 | clearly lower |

</details>

<details>
<summary><b>Fraud · prison length</b>: 12 clearly higher, 12 clearly lower, of 135 judges</summary>

| Court | Judge | Cases | Vs court average (days) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 臺中 Taichung | 徐煥淵 | 211 | +99.5 | +83.1 to +115.9 | 97th pct of 19 | clearly higher |
| 臺南 Tainan | 張郁昇 | 131 | +94.7 | +74.2 to +115.2 | 94th–98th pct of 23 | clearly higher |
| 臺南 Tainan | 周紹武 | 122 | +87.6 | +66.4 to +108.8 | 94th–98th pct of 23 | clearly higher |
| 桃園 Taoyuan | 林其玄 | 102 | +87.1 | +64.1 to +110.1 | 96th pct of 12 | clearly higher |
| 臺北 Taipei | 宋恩同 | 482 | +82.4 | +71.4 to +93.4 | 97th pct of 15 | clearly higher |
| 高雄 Kaohsiung | 許瑜容 | 235 | +74.2 | +58.6 to +89.7 | 85th–95th pct of 10 | clearly higher |
| 臺中 Taichung | 王曼寧 | 114 | +66.6 | +44.7 to +88.4 | 92nd pct of 19 | clearly higher |
| 彰化 Changhua | 張琇涵 | 125 | +61.9 | +41.0 to +82.9 | 90th–97th pct of 15 | clearly higher |
| 高雄 Kaohsiung | 吳書怡 | 126 | +56.5 | +35.6 to +77.3 | 85th–95th pct of 10 | clearly higher |
| 彰化 Changhua | 李欣恩 | 124 | +41.5 | +20.4 to +62.5 | 83rd–97th pct of 15 | clearly higher |
| 士林 Shilin | 古御詩 | 268 | +39.8 | +25.2 to +54.4 | 86th–96th pct of 11 | clearly higher |
| 新北 New Taipei | 黎錦福 | 283 | +37.4 | +23.2 to +51.6 | 93rd–98th pct of 22 | clearly higher |
| 臺南 Tainan | 鄭銘仁 | 202 | −96.2 | −113.0 to −79.5 | 2nd pct of 23 | clearly lower |
| 臺南 Tainan | 李俊彬 | 163 | −72.5 | −91.0 to −54.0 | 6th pct of 23 | clearly lower |
| 高雄 Kaohsiung | 黃政忠 | 308 | −61.4 | −75.0 to −47.7 | 5th–15th pct of 10 | clearly lower |
| 臺中 Taichung | 王品惠 | 124 | −60.8 | −81.8 to −39.8 | 3rd–13th pct of 19 | clearly lower |
| 彰化 Changhua | 李怡昕 | 120 | −60.5 | −81.9 to −39.2 | 3rd–10th pct of 15 | clearly lower |
| 桃園 Taoyuan | 郭于嘉 | 255 | −54.7 | −69.7 to −39.7 | 4th pct of 12 | clearly lower |
| 新北 New Taipei | 吳宗航 | 136 | −53.1 | −73.3 to −33.0 | 2nd–7th pct of 22 | clearly lower |
| 高雄 Kaohsiung | 郭振杰 | 124 | −51.3 | −72.3 to −30.2 | 5th–15th pct of 10 | clearly lower |
| 臺北 Taipei | 翁毓潔 | 503 | −51.2 | −62.0 to −40.4 | 3rd–17th pct of 15 | clearly lower |
| 臺南 Tainan | 林欣玲 | 193 | −47.4 | −64.5 to −30.3 | 11th–20th pct of 23 | clearly lower |
| 新北 New Taipei | 梁家贏 | 281 | −40.0 | −54.3 to −25.8 | 2nd–11th pct of 22 | clearly lower |
| 士林 Shilin | 黃柏仁 | 118 | −39.4 | −60.9 to −17.9 | 4th–14th pct of 11 | clearly lower |

</details>

<details>
<summary><b>Fraud · extra-fine rate (2024–2026)</b>: 9 clearly higher, 0 clearly lower, of 99 judges</summary>

| Court | Judge | Cases | Vs court average (points) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 臺中 Taichung | 徐煥淵 | 189 | +52.4 | +50.2 to +54.5 | 96th pct of 13 | clearly higher |
| 臺中 Taichung | 陳盈睿 | 212 | +45.2 | +43.2 to +47.3 | 88th pct of 13 | clearly higher |
| 臺南 Tainan | 盧鳳田 | 130 | +44.5 | +41.9 to +47.1 | 97th pct of 18 | clearly higher |
| 彰化 Changhua | 陳怡潔 | 106 | +23.9 | +21.1 to +26.8 | 95th pct of 10 | clearly higher |
| 新北 New Taipei | 鄭淳予 | 219 | +12.6 | +10.6 to +14.6 | 88th–96th pct of 12 | clearly higher |
| 新北 New Taipei | 吳宗航 | 116 | +10.1 | +7.3 to +12.8 | 88th–96th pct of 12 | clearly higher |
| 彰化 Changhua | 張琇涵 | 104 | +7.3 | +4.4 to +10.2 | 85th pct of 10 | clearly higher |
| 臺北 Taipei | 倪霈棻 | 511 | +4.7 | +3.4 to +6.0 | 89th–96th pct of 14 | clearly higher |
| 臺北 Taipei | 賴鵬年 | 343 | +4.4 | +2.8 to +6.0 | 89th–96th pct of 14 | clearly higher |

</details>

<details>
<summary><b>Negligent injury · prison length</b>: 4 clearly higher, 1 clearly lower, of 54 judges</summary>

| Court | Judge | Cases | Vs court average (days) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 高雄 Kaohsiung | 賴建旭 | 210 | +20.3 | +15.2 to +25.4 | 96th pct of 12 | clearly higher |
| 新北 New Taipei | 陳明珠 | 238 | +19.2 | +14.4 to +24.1 | 97th pct of 16 | clearly higher |
| 桃園 Taoyuan | 謝承益 | 121 | +14.2 | +7.7 to +20.8 | 92nd pct of 6 | clearly higher |
| 新北 New Taipei | 潘長生 | 172 | +12.6 | +7.0 to +18.2 | 84th–91st pct of 16 | clearly higher |
| 高雄 Kaohsiung | 黃政忠 | 224 | −24.9 | −29.8 to −19.9 | 4th pct of 12 | clearly lower |

</details>

<details>
<summary><b>Drug use · prison length</b>: 3 clearly higher, 4 clearly lower, of 53 judges</summary>

| Court | Judge | Cases | Vs court average (days) | 95% interval | Rank in court (90% range) | Flag |
|---|---|---|---|---|---|---|
| 桃園 Taoyuan | 曾雨明 | 134 | +18.0 | +12.9 to +23.1 | 90th pct of 5 | clearly higher |
| 新北 New Taipei | 徐蘭萍 | 562 | +12.9 | +10.4 to +15.4 | 88th–96th pct of 12 | clearly higher |
| 屏東 Pingtung | 黃紀錄 | 443 | +3.7 | +0.9 to +6.5 | 90th pct of 5 | clearly higher |
| 士林 Shilin | 張明儀 | 182 | −23.7 | −28.1 to −19.4 | 7th pct of 7 | clearly lower |
| 新北 New Taipei | 潘長生 | 750 | −22.0 | −24.2 to −19.9 | 4th pct of 12 | clearly lower |
| 桃園 Taoyuan | 李敬之 | 135 | −17.7 | −22.7 to −12.6 | 10th pct of 5 | clearly lower |
| 橋頭 Ciaotou | 黃逸寧 | 105 | −16.7 | −22.4 to −11.0 | 8th pct of 6 | clearly lower |

</details>

### 1.4 Did sentencing tools reduce the lottery?

The Judicial Yuan launched a sentencing-trend recommendation system on 21 December 2018 for drunk driving, fraud and theft (and sexual, robbery, homicide and firearms offences)<sup>4</sup>, and an AI sentencing information system on 6 February 2023 that added assault and drug offences<sup>5</sup>. If these tools work, judge-to-judge gaps should shrink in covered offences relative to uncovered ones. We measure the gap in proportional terms (percentage spread of sentences between judges), so that rising average sentences do not inflate it.

**Judge-to-judge spread in prison terms, by year**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-trend-dark.png">
  <img alt="Judge-to-judge spread in prison terms, by year" src="figures/en/c-trend-light.png">
</picture>

<sub>Noise-corrected between-judge standard deviation of log prison length, as a percentage; average across offences present in every year, with fixed weights, so changes in the offence mix do not move the lines (covered: assault, drug possession, drug use, fraud, drunk/drugged driving, theft; not covered: criminal damage, negligent injury). Dashed lines: launch of the two sentencing tools.</sub>

Holding the offence mix fixed, spread in covered offences went from 10.2% to 9.7% around 2018 while it went from 11.9% to 13.0% in uncovered offences. The difference-in-differences (with offence and year fixed effects) is −14%: a relative narrowing, but with only three covered offences it is not statistically distinguishable from zero (exact randomisation p = 0.21 over 165 relabellings; −16% to −13% when any one covered offence is dropped). Around 2023, spread in covered offences went from 10.9% to 12.9% and in uncovered ones from 18.2% to 17.6%: a relative increase of +27% (p = 0.009). It stays between +24% and +31% when any one covered offence is dropped, though without drunk driving it is no longer significant (p = 0.12).

> This is not proof that the AI system *caused* more disparity. 2023–2025 also brought heavier drunk-driving penalties and a crackdown on fraud (a new Fraud Crime Hazard Prevention Act in 2024; average fraud sentences in our data rose from 129 days in 2013 to 405 in 2025), and judges may adapt to new laws at different speeds; spread also rose in drug use. What the data do show is that the 2023 tool was not followed by narrower judge differences.

| Reform | Outcome | Covered offences | Spread, covered (before → after) | Spread, uncovered | Relative change | p (randomisation) |
|---|---|---|---|---|---|---|
| 2018 sentencing-trend guidance | Prison length | Fraud, Drunk/drugged driving, Theft | 10.2 → 9.7 | 11.9 → 13.0 | −14% | 0.21 |
| 2023 AI sentencing information system | Prison length | Assault, Drug possession, Drug use, Fraud, Drunk/drugged driving, Theft | 10.9 → 12.9 | 18.2 → 17.6 | +27% | 0.009 |
| 2018 sentencing-trend guidance | Probation | Fraud, Drunk/drugged driving, Theft | 7.0 → 5.7 | 2.4 → 2.3 | −10% | 0.89 |
| 2023 AI sentencing information system | Probation | Assault, Drug possession, Drug use, Fraud, Drunk/drugged driving, Theft | 4.8 → 4.7 | 5.3 → 4.4 | +14% | 0.66 |

### 1.5 Do appeals correct outlier judges?

We took 965,434 single-defendant first-instance prison sentences decided by the end of 2024 and linked them to any appeal (district appellate panels for summary cases, the High Court otherwise) through the appeal's record of the original case; 5.9% were appealed. If appeals corrected the lottery, the spread between first-instance judges should shrink once second-instance changes are applied. For the high-volume offences it hardly does: appeals remove 1.3% of the between-judge variance for drunk driving (where only 2.2% of cases are appealed), 2.6% for drug use and 7.2% for theft, and at most 40% (money mules). In terms of the typical gap in days, 77%–99% remains.

**Share of judge differences removed by appeals**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-appeal-dark.png">
  <img alt="Share of judge differences removed by appeals" src="figures/en/c-appeal-light.png">
</picture>

<sub>Reduction in between-judge variance of prison terms from first instance to the second-instance outcome.</sub>

**Who appeals, by how harsh the first judge was**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-appeal-bins-dark.png">
  <img alt="Who appeals, by how harsh the first judge was" src="figures/en/c-appeal-bins-light.png">
</picture>

<sub>Negligent-injury cases (27% appealed). x: the judge's leniency measured on her or his other cases (days vs court average). Each point is a tenth of cases.</sub>

Appeals respond to the lottery, but weakly: in negligent-injury cases, every 10 days of extra harshness in the first judge raises the chance that the defendant appeals by 2.2 points and lowers the chance that the prosecutor appeals by 0.6 points. Because so few cases are appealed and appellate courts usually confirm, most of the lottery passes into final judgments (the Supreme Court stage is not linked here).

## 2Who the judge is

We built a career record for every judge from all case types in the microdata (civil, family, criminal, administrative), so that “experience” means years deciding cases anywhere, not only in criminal divisions. Judges whose first appearance is in 2015 or later are new to the bench in our window.

**Experience.** Judges in their first three years sentence at about the same level as judges with five or more years: differences are at most 4.2% in any offence, and 2 of 9 offences show a statistically detectable difference (drunk/drugged driving +1.4%, negligent injury −4.2%). Their spread is similar in most offences (drunk driving 7.7% vs 7.9%), though higher in fraud (11.3% vs 9.5%); we did not estimate uncertainty for this comparison. Unlike Czech evidence that disparities shrink with experience<sup>6</sup>, the lottery here is not mainly a problem of beginners.

**Stability.** A judge's relative harshness is lasting. Comparing the same judges in the same court across consecutive four-year periods gives correlations of 0.53–0.78 (after correcting for sampling noise), and 0.35–0.65 across eight years. Harshness partly carries across offences: a judge's ranking in one offence correlates 0.26–0.48 with her or his ranking in another.

**It travels.** The strongest evidence that this is about the person, not the court, comes from 270 judges who moved between courts. Their harshness relative to colleagues in the old court predicts their harshness relative to colleagues in the new court (correlation 0.53 after noise correction; 0.47 raw).

**Same judge, two courts**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-movers-dark.png">
  <img alt="Same judge, two courts" src="figures/en/c-movers-light.png">
</picture>

<sub>Each dot is a judge who moved: harshness relative to colleagues before (x) and after (y) the move, in standard units pooled across offences.</sub>

**Novice vs experienced judges: spread of sentences**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-exp-dark.png">
  <img alt="Novice vs experienced judges: spread of sentences" src="figures/en/c-exp-light.png">
</picture>

<sub>Noise-corrected between-judge spread of prison terms (%), judges in their first three years vs judges with five or more years.</sub>

> Judges' gender, training cohort and earlier careers (for example, lawyers who became judges) are not in the open data. We did not infer judges' gender, so that no individual judge is labelled by an estimate.

## 3Who the defendant is

The microdata do not record a defendant's sex, age or nationality, so we matched 298,832 single-defendant judgments from January 2024 – July 2026 to their full text. A defendant is a **foreign national** when the judgment gives the name in Latin script or states a foreign nationality next to the word 被告 (9,282 cases; mainland China, Hong Kong and Macau are kept separate). This rule was not checked against an official record. **Gender** is the sex stated in the prosecutor's charging document where the text gives it (13% of cases), otherwise inferred from the given name with a model trained on 36,199 election candidates with recorded sex; checked against the sex written in 4,488 drunk-driving charging documents, the name model is right 97.9% of the time for the 81% of names it classifies. Results are reported only in aggregate.

All comparisons are within the same assignment pool and with the same legal controls as above, so they compare defendants who drew the same set of judges.

**Sentence gaps by who the defendant is**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-identity-dark.png">
  <img alt="Sentence gaps by who the defendant is" src="figures/en/c-identity-light.png">
</picture>

<sub>Percentage difference in prison length versus comparable defendants in the same court pool (95% interval). Foreign / woman: January 2024 – July 2026. Indigenous division: cases heard in 原住民專庭, 2013–2026, compared with ordinary cases of the same court, case type and year.</sub>

**Foreign nationals**' drunk-driving sentences differ by −19% from those of comparable Taiwanese defendants (95% interval −20% to −18%) and their probation rate differs by +2.8 points. Part of this is that the microdata lack two key facts: alcohol level and earlier drunk-driving convictions, which foreign defendants rarely have. Our 2025 six-court sample has both, so we re-estimated there: the gap is −18% without them, −10% with them, and −11% (95% interval −13% to −8%) after also adding vehicle, injury, education and self-described economic circumstances (932 foreign defendants). About 41% of the raw gap is explained by these facts; a gap of about 11% remains, which could still reflect facts we do not observe. Money-mule defendants who are foreign also receive shorter sentences (−10%).

**Women** receive shorter sentences than men in comparable cases: −6% for drunk driving (in the six-court sample with full facts, −3%), −27% for theft, where their chance of a custodial rather than a fine-only sentence differs by −14 points. Part of the theft gap may reflect smaller thefts, since the value taken is not recorded. A similar gap is found in France<sup>7</sup>.

**Indigenous divisions.** Cases heard in Indigenous divisions get sentences close to ordinary cases, with small differences in both directions: +1.6% for drunk driving, −5.0% for drug use and +7% for assault (the latter two clearly different from zero). Among 488 judges who decide both kinds of drunk-driving case, the gap differs modestly between judges (SD about 3.7%, a point estimate). In Hualien, culture-based sentence reductions in drunk-driving cases have been traced to a single judge<sup>8</sup>.

**Lawyers.** Most defendants in these cases have no lawyer. Where they do, defendants with a public defender or legal-aid lawyer receive shorter theft sentences (−12% and −17%) and those with retained counsel slightly longer (+5%). These comparisons are not random: who gets a lawyer depends on the case.

| Offence | Public defender | Legal aid | Retained lawyer | Share with any lawyer |
|---|---|---|---|---|
| Drunk/drugged driving | +5% | 0% | +1% | 1% |
| Theft | −12% | −17% | +5% | 4% |
| Drug use | −3% | −9% | −10% | 1% |
| Fraud | −3% | −7% | 0% | 17% |
| Money mule (laundering) | −6% | −7% | −2% | 21% |
| Negligent injury | −11% | +7% | +38% | 9% |

### 3.2 Detention before verdict

Defendants detained during trial can ask the trial court to release them on bail (聲請具保停止羈押). We found 23,123 such rulings in district courts from 2013 to 2026. 23% were granted, rising from 17% in 2013 to 29% in 2025. 76% of rulings are by three-judge panels, which we attribute to the first-listed (usually presiding) judge. Within the same court and year, the chance of release varies between presiding judges by about 13 percentage points (one standard deviation, noise-corrected; judge share 11%; the between-judge variance is 2.6× what random reshuffling of the same rulings produces). Among 205 judges with 30 or more rulings, shrunken estimates put the strictest tenth at −14 points and the most lenient tenth at +16 points relative to their court-year average.

> Motions are decided by the judge or panel holding the randomly assigned case, but the number and strength of motions is not random (detained defendants can apply repeatedly), and comparisons are only within court and year, so these figures are an upper bound on the judge effect.

## 4Politics: does the candidate's party matter in election-crime trials?

Before the 1990s, case assignment and promotion were tools of political control over Taiwan's courts<sup>9</sup>, and vote buying was a core campaign technique<sup>10</sup>. Today prosecutors belong to the Ministry of Justice, so a change of government changes who directs them. We collected all 2,283 district-court judgments in election-offence cases (公職人員選舉罷免法, 總統副總統選舉罷免法, 妨害投票) from 2013 to 2026, identified the candidate each offence was meant to help by matching names in the judgment against the Central Election Commission's candidate lists for the same election and county, and recorded the candidate's party. 1,476 judgments with 4,223 defendants could be linked unambiguously; most village-chief and township races involve independents. For 24% of linked judgments the microdata do not name the election, and we searched elections in the three years before the judgment; results excluding them are reported below.

We ask two questions taken from research on partisan prosecutions<sup>11</sup>: (1) is each party's share of prosecutions in line with its share of candidates, and did that change after the DPP took over the executive in May 2016? (2) Do conviction and sentence differ by party once court, election, office and case size are held constant? If prosecutors pursued opposition politicians with weaker cases, opposition-linked defendants would be acquitted more and sentenced more lightly.

**Share of prosecuted election-crime cases vs share of candidates**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/en/c-party-dark.png">
  <img alt="Share of prosecuted election-crime cases vs share of candidates" src="figures/en/c-party-light.png">
</picture>

<sub>Partisan races only (councils, mayors, legislature, township representatives), candidate shares weighted to the office mix of the cases. Elections up to 2016 were investigated under a KMT government, later ones under a DPP government.</sub>

**Prosecution intensity.** KMT-linked cases made up 37% of partisan-race cases from elections under the KMT government (KMT share of candidates 29%, of winners 36%) and 22% under the DPP government (candidates 19%, winners 28%). DPP-linked cases were 9% and 9% (candidates 17% and 13%, winners 26% and 16%). Under the KMT government, KMT-linked cases matched the KMT's share of winners; under the DPP government they fell below it. DPP-linked cases were below the DPP's share of candidates and winners in both periods. Nothing here suggests that the new government's prosecutors brought more cases against the opposition.

**Trial outcomes.** Conviction rates show no detectable difference between KMT- and DPP-linked defendants (−0.4 points, 95% interval −11 to +11). Prison terms (the longest sentence on an election count) do differ: KMT-linked defendants received 3.8 months more than DPP-linked ones (p < 0.001), and DPP-linked defendants −3.9 months relative to independents (p < 0.001). The KMT–DPP gap is similar under both governments (+3.4 months for elections under the KMT government, +2.7 under the DPP government; difference p = 0.51), so it follows the party label, not who held power, and likely reflects differences between the parties' cases.

**The opposition test.** Comparing defendants linked to the party *out of power* with those linked to the party in power, with court, election and case controls (408 judgments): conviction −5 points (p = 0.39) and prison −0.9 months (p = 0.44) show no difference, so the weaker-cases-against-the-opposition pattern Gordon's test looks for does not appear. Probation does differ: opposition-linked defendants were 12 points less likely to receive it (p = 0.013, 0.038 after a Bonferroni correction for three outcomes). The gap is −17 points (p = 0.003; corrected 0.008) with stricter name matching and −14 points (p = 0.018; corrected 0.054) when links without a recorded election are excluded. In raw rates, defendants linked to the governing party received probation more often in both periods: 80% (KMT-linked) vs 63% (DPP-linked) under the KMT government, and 81% (DPP-linked) vs 71% (KMT-linked) under the DPP government; the change for KMT-linked defendants after 2016 is −20 points (p = 0.003).

> How to read this: probation is decided by judges, often after prosecutors' sentencing arguments, and we cannot see either side's reasons. The comparison rests on few judgments, the party variable is the candidate's (not the defendant's), and the two periods differ in which elections and courts produced cases. The pattern is consistent with political favour on one margin, but also with differences between the two parties' cases that the controls miss. It should be re-tested on cases from the 2024 and 2026 elections and on prosecutors' sentencing requests.

**Appeals.** When appealed, first-instance judgments were overturned in whole or part at similar rates: 46% for KMT-linked, 40% for DPP-linked and 44% for independent-linked cases.

| Government at election | Candidate's party | Defendants | Judgments | Convicted | Longest election-count prison term if convicted (months) | Probation if convicted |
|---|---|---|---|---|---|---|
| KMT government | KMT | 561 | 167 | 88% | 14.9 | 80% |
| KMT government | DPP | 145 | 53 | 87% | 11.7 | 63% |
| KMT government | Independent | 1168 | 370 | 83% | 14.0 | 63% |
| KMT government | Other party | 15 | 7 | 93% | 21.1 | 57% |
| DPP government | KMT | 460 | 131 | 71% | 13.1 | 71% |
| DPP government | DPP | 130 | 57 | 81% | 13.9 | 81% |
| DPP government | Independent | 1708 | 676 | 86% | 14.4 | 75% |
| DPP government | Other party | 36 | 15 | 61% | 11.8 | 73% |

> What this cannot show: decisions not to prosecute (不起訴) are not in court data, so prosecutors' choices before charging are only visible through which cases reach court. Party is that of the candidate the offence was meant to help, not the defendant's own membership. Corruption trials of politicians are not covered.

## 5Drunk driving with the full case file

The microdata miss some facts that matter for sentencing, so we machine-coded 10,861 full 2025 drunk-driving judgments from six district courts (the parser was checked against about 100 hand-coded judgments and against the court microdata) for breath-alcohol level, prior drunk-driving convictions, crashes, injuries, vehicle, and the defendant's stated education and economic circumstances. Adding these facts leaves the judge spread unchanged (about 12 days); because the facts explain much of the rest, the judge's share of the remaining variation in prison terms is 19%. (A national 2025 prison-only sample with only the microdata's factors gives 20% over 26,567 cases; both are higher than the drunk-driving share in the table above, which covers 2013–2026 and all custodial sentences.) A lenient and a strict judge (10th vs 90th percentile) differ by 25 days for the same typical first offence. The observed between-judge variance is 6.2× what shuffling judges within pools produces, and judges' estimated leniency on one half of their cases predicts the other half (r = 0.79). Case facts are not perfectly balanced across judges (related cases go to the same judge), but the facts that differ explain only about 6 days of judge-to-judge spread.

We also tested the claims that judges are swayed by the day: weekday, month-end case-closing pressure, the day before holidays and unusually heavy days. 0 of 8 timing factors had a detectable effect after correcting for multiple tests, in line with the many failed replications of the “hungry judge” effect<sup>12,13,14</sup>.

## What this does and does not show

**Assignment is random, but not perfectly.** Related cases go to the same judge, and some courts route specialised cases to designated divisions. We compare judges only within pools of the same court, case type and quarter and control for recorded case facts. In the six-court sample, case facts do differ significantly across judges, but adding them leaves the judge spread unchanged. Remaining case-mix differences would inflate judge estimates; working the other way, our estimator understates the judge share somewhat (removing pool averages also removes part of each judge's own effect, by roughly a fifth to two-fifths in simulations), and some controls are judges' own choices (though dropping them hardly matters). The court-moving result is the strongest evidence that the effect belongs to the judge.

**Recorded facts are incomplete.** The microdata lack alcohol level, damage amounts and prior non-recidivist convictions; the drunk-driving deep dive shows the judge share survives when such facts are added.

**Variation is not error.** Taiwanese law gives judges wide ranges and asks them to weigh individual circumstances (刑法 §57). Some judge-to-judge variation is the price of individualised justice. The question this report answers is how large it is; whether it is too large is for the public, the Judicial Yuan and the legislature.

**Inferred attributes.** Gender inferred from names was about 98% accurate in two checks (covering about 80% of names); foreign nationality could not be validated. Random misclassification would shrink gaps toward zero, but systematic errors or the names left unclassified could bias them either way.

## Methods and data

**Sources.** (1) Judicial Yuan open data, terminated-case microdata (終結案件資料, category 001), January 2013 – July 2026, 75 archives, parsed into 2,993,332 defendant records and their charges; Big5 and UTF-8 versions reconciled, and judge names the Big5 files could not encode recovered from judgment signatures. (2) Bulk judgment texts (裁判書, category 051), January 2024 – July 2026, for defendant nationality, names and stated sex. (3) 2,283 election-offence judgments from the public judgment search (FJUD). (4) Central Election Commission candidate files, 2012–2024 elections. (5) For the deep dive, 10,861 machine-coded 2025 drunk-driving judgments from six district courts.

**Judge effects.** For each offence and outcome we demean within assignment pools (court × case word × quarter), regress on recorded legal factors, and estimate the between-judge variance with a one-way ANOVA (method-of-moments) estimator, which subtracts an estimate of each judge's sampling noise (simpler than, but in the spirit of, leave-out estimators). Judge share = between-judge variance ÷ total residual variance. The two-random-judge gap is 2τ/√π. Split-half reliability averages 20 random splits of each judge's cases. Named-judge estimates are empirical-Bayes posterior means with posterior SDs; rank ranges are 90% marginal posterior ranges from 2,000 draws within each court, treating the variance components as known (simpler than the rank confidence sets in the literature<sup>15,16</sup>). A robustness version without the §59, simplified-procedure and exemption controls is in the result files.

**Reforms.** Spread per offence and year on log prison length; difference-in-differences with offence and year fixed effects, case-weighted; exact randomisation inference over which offences are labelled covered. Money-mule cases tied to fraud are excluded (coverage ambiguous).

**Appeals.** Single-defendant first-instance prison sentences decided up to 2024 (to allow time for appeal), judges with 30+ such cases, pools with at least two judges; appeals linked through the appeal record's original-case fields; remanded cases dropped. A judge's stringency is the leave-one-out mean residual of her or his other cases. The share removed is 1 − τ²(final)/τ²(first instance); the share of the typical gap that remains is τ(final)/τ(first instance).

**Politics.** Beneficiary candidate = the candidate of the matching election, office and county whose name appears most often next to campaign words (候選人, 支持, 當選 …); cases aimed at making a candidate lose, and judgments where candidates of different parties tie, are excluded. Regressions with court, election-year and office fixed effects, number of counts and co-defendants, and whether the candidate was a defendant; standard errors clustered by judgment.

**Reproducibility.** All code, aggregate results and documentation are in the project repository. Raw judgment texts, which contain defendants' names, are not published.

### References

1. James M. Anderson, Jeffrey R. Kling, Kate Stith (1999). Measuring Interjudge Sentencing Disparity: Before and After the Federal Sentencing Guidelines. *Journal of Law and Economics 42(S1): 271–308*. [link](https://api.openalex.org/works/doi:10.1086/467426)
2. Jaya Ramji-Nogales, Andrew I. Schoenholtz, Philip G. Schrag (2007). Refugee Roulette: Disparities in Asylum Adjudication. *Stanford Law Review 60(2): 295*. [link](https://www.stanfordlawreview.org/print/article/feature-refugee-roulette-disparities-in-asylum-adjudication/)
3. Patrick Kline, Raffaele Saggio, Mikkel Sølvsten (2020). Leave-Out Estimation of Variance Components. *Econometrica 88(5):1859-1898*. [link](https://www.econometricsociety.org/doi/10.3982/ECTA16410)
4. 司法院 Judicial Yuan (2018). 量刑趨勢建議系統啟用 開放各界查詢 (Sentencing-trend recommendation system launched). *司法周刊 Judicial Weekly No. 1933, 28 December 2018*. [link](https://www.judicial.gov.tw/tw/cp-1429-66510-c88dd-1.html)
5. 司法院 Judicial Yuan (2023). 因應國民法官新制 司法院啟用AI量刑資訊系統 (AI sentencing information system launched). *Press release, 6 February 2023*. [link](https://www.judicial.gov.tw/tw/cp-1887-806741-d6471-1.html)
6. Jakub Drápal, Jose Pina-Sánchez (2023). What is the Value of Judicial Experience? Exploring Judge Trajectories Using Longitudinal Data. *Justice Quarterly 40(2): 211-240 (online 2022)*. [link](https://eprints.whiterose.ac.uk/id/eprint/182204/)
7. Arnaud Philippe (2020). Gender Disparities in Sentencing. *Economica 87(348): 1037-1077*. [link](https://ideas.repec.org/a/bla/econom/v87y2020i348p1037-1077.html)
8. 范耕維 (Keng-Wei Fan), 林俊儒 (2025). 初探臺灣原住民族刑事文化抗辯的適用與意義—以花蓮地方法院實證研究為起點 (A first look at the criminal cultural defence for Indigenous defendants in Taiwan: an empirical study of the Hualien District Court). *中研院法學期刊 (Academia Sinica Law Journal) 36: 287–394*. [link](https://publication.iias.sinica.edu.tw/03805152.pdf)
9. 王金壽 (Chin-Shou Wang) (2006). 台灣的司法獨立改革與國民黨侍從主義的崩潰 (Judicial Independence Reform and the Breakdown of the Kuomintang Clientelism in Taiwan). *台灣政治學刊 (Taiwanese Political Science Review) 10(1), June 2006. Page range not shown on the journal page. Chinese page: https://www.tpsr.tw/zh-hant/zh-hant/paper/tai-wan-de-si-fa-du-li-gai-ge-yu-guo-min-dang-shi-cong-zhu-yi-de-beng-kui*. [link](https://www.tpsr.tw/zh-hant/zh-hant/paper/tai-wan-de-si-fa-du-li-gai-ge-yu-guo-min-dang-shi-cong-zhu-yi-de-beng-kui)
10. Chin-Shou Wang, Charles Kurzman (2007). Dilemmas of Electoral Clientelism: Taiwan, 1993. *International Political Science Review 28(2): 225-245. Author PDF: http://kurzman.unc.edu/wp-content/uploads/sites/1410/2011/06/Wang_Kurzman_Dilemmas.pdf*. [link](http://kurzman.unc.edu/wp-content/uploads/sites/1410/2011/06/Wang_Kurzman_Dilemmas.pdf)
11. Sanford C. Gordon (2009). Assessing Partisan Bias in Federal Public Corruption Prosecutions. *American Political Science Review 103(4):534-554*. [link](https://doi.org/10.1017/S0003055409990207)
12. Shai Danziger, Jonathan Levav, Liora Avnaim-Pesso (2011). Extraneous factors in judicial decisions. *PNAS 108(17):6889-6892*. [link](https://pmc.ncbi.nlm.nih.gov/articles/PMC3084045/)
13. Keren Weinshall-Margel, John Shapard (2011). Overlooked factors in the analysis of parole decisions. *PNAS 108(42): E833 (letter)*. [link](https://pmc.ncbi.nlm.nih.gov/articles/PMC3198355/)
14. Andreas Glockner (2016). The irrational hungry judge effect revisited: Simulations reveal that the magnitude of the effect is overestimated. *Judgment and Decision Making 11(6):601-610*. [link](https://www.cambridge.org/core/product/identifier/S1930297500004812/type/journal_article)
15. Magne Mogstad, Joseph P. Romano, Azeem M. Shaikh, Daniel Wilhelm (2024). Inference for Ranks with Applications to Mobility across Neighbourhoods and Academic Achievement across Countries. *Review of Economic Studies 91(1):476-518*. [link](https://academic.oup.com/restud/article/91/1/476/7008541)
16. Jiaying Gu, Roger Koenker (2023). Invidious Comparisons: Ranking and Selection as Compound Decisions. *Econometrica 91(1):1-41*. [link](https://www.econometricsociety.org/doi/10.3982/ECTA19304)

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
