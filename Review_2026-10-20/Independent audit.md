# DFF Robotic Lab Expansion — independent solar/HVAC audit

20 October 2026. Read-only review. No Rhino/Grasshopper/Radiance simulations were run and no original deliverables were edited.

## 1. Executive verdict

**The export arithmetic is sound; the study is not ready to issue as an HVAC acceptance assessment.** Independent integration of the existing `.ill` files for all 12 runs reproduces the workbook’s July, June and annual heat-gain maxima within **0.00000008 kW**. Every numerical table entry on slides 8–9 matches its underlying Excel heat-gain result at the displayed precision. The weather-period labels on slides 9 and 14 are wrong. This establishes internal numerical consistency, not the correctness of every modelling assumption or the proposed acceptance criterion.

Correct before issue:

1. **D1250 roof geometry is anomalous in both saved simulation models.** Its exported horizontal roof underside is only 5.98 m²; the comparable underside is 257.78 m² at D1000 and 276.53 m² at D1500. Treat D1250 results as unresolved, even though Excel reproduces them correctly.
2. **4.7 kW has no demonstrated status as an allowable load.** It is a rounded historical HAP solar cooling-load component, not established spare capacity, a new-façade limit or a compliance test. Remove acceptance language and pass/fail interpretation until MEP confirms a criterion.
3. **The current “design-hour” results use every day of the month and two adjacent samples.** They are not specifically the 21st and not exact HAP-hour values. Either change the selection later, or label the present calculation accurately throughout.
4. **The two quantities being compared differ.** Excel calculates instantaneous solar heat gain with constant SHGC; HAP reports a cooling-load component. “Conservative compared with HAP” is not demonstrated.
5. **Tau coefficient/data compatibility needs resolution.** The native component uses Ladybug’s default 2009 coefficients; the STAT labels its design data as ASHRAE 2025. The files establish that implementation, but do not establish that this pairing is appropriate or matches HAP.
6. **The TMYx source-period label is incorrect.** The saved solar data match the cached EPW exactly; its metadata declares 1973–2025, not the 2007–2021 stated on slides 9 and 14.

Other corrections concern peak definitions, a misleading general “pass” for D1500/SC 0.25, an unsafe interpretation of the peak-hour SC calculation, and slide 9’s clear-sky/TMYx difference. Exact wording is provided below. Supplier performance, tower geometry and radiance/grid convergence remain assumptions requiring confirmation.

## 2. Numerical audit

The accompanying [Numerical audit.csv](<Numerical audit.csv>) contains **286 checks**, with run, source cell, independent value, saved Excel value, slide value and numerical pass/fail. All **282 calculation comparisons** pass, including the displayed result-table numbers/dates. Four additional metadata checks flag the incorrect TMYx start/end years repeated on slides 9 and 14. A numerical PASS means agreement with the stated calculation, **not design acceptance**. D1250 carries a geometry qualification on every result row.

For each run, the independent calculation reads sensor irradiance from `annual_irradiance/results/total/*.ill`, derives face areas from the HBJSON sensor meshes, maps sun-up half-hours into the corresponding 8,760 hour-start rows, integrates sensor-area × irradiance, aggregates by zone, then applies each zone’s actual glazing-area/sensor-area ratio and the stated SC conversion. Actual glazing areas come from the workbook’s Brep-area export; their provenance is not independently certified by this arithmetic check.

### Headline heat-gain results

All figures below are independently recomputed and agree with Excel. July means all July days at hour starts 13/14; June means all June days at hour starts 12/13. They are **current-method bracket maxima**, not exact HAP conditions. Skylight SC is 0.25 throughout. Hours follow the Dubai weather file’s local standard time, UTC+4. Dates use the workbook’s display year, 2026; a TMY date is not an actual 2026 weather observation.

| North canopy [mm] | Jul bracket SC .25 / .32 / .40 [kW] | Jun bracket SC .25 / .32 / .40 [kW] | Clear-sky annual max SC .40 [kW; hour start] | TMYx Jul / annual max SC .40 [kW; peak hour start] | Numeric reconciliation |
|---|---|---|---|---|---|
| 0 | 6.92 / 8.78 / 10.90 | 7.31 / 9.29 / 11.54 | 19.62; 20-Jun 09:00 | 8.60 / 19.49; 12-Jun 09:00 | PASS |
| 500 | 5.75 / 7.28 / 9.03 | 6.48 / 8.21 / 10.19 | 16.43; 20-Jun 09:00 | 6.94 / 16.17; 12-Jun 09:00 | PASS |
| 750 | 5.42 / 6.86 / 8.51 | 6.21 / 7.87 / 9.76 | 14.47; 20-Jun 09:00 | 6.71 / 15.47; 24-Jun 08:00 | PASS |
| 1000 | 5.15 / 6.51 / 8.07 | 5.78 / 7.33 / 9.09 | 13.51; 16-Jun 08:00 | 6.42 / 14.55; 12-Jun 08:00 | PASS |
| 1250 * | 4.84 / 6.12 / 7.58 | 5.53 / 6.99 / 8.66 | 12.42; 16-Jun 08:00 | 6.09 / 13.53; 11-Jun 08:00 | PASS |
| 1500 | 4.66 / 5.89 / 7.28 | 5.19 / 6.56 / 8.14 | 11.31; 18-Jun 08:00 | 5.82 / 12.35; 11-Jun 08:00 | PASS |

Source map: each run’s `U5:U7` = July; `V5:V7` = June; `W5:W7` = annual heat-gain maxima; `X5:X7` = their dates. `Summary!D8:L13` and `D18:L23` link these results. Slides 8–9 show the July values and SC 0.40 annual maxima. June values are not shown on those slides. `*` D1250 geometry is unresolved.

### Actual façade-incident peaks

These are maxima of **façade incident power**, excluding skylight and before SC/SHGC. They are not necessarily the combined heat-gain peaks quoted on slides 8–9.

| North canopy [mm] | Clear-sky facade incident maximum [kW] | Hour start | TMYx facade incident maximum [kW] | Hour start |
|---|---:|---|---:|---|
| 0 | 53.5858 | 24-Jun 09:00 | 53.1134 | 12-Jun 09:00 |
| 500 | 44.3652 | 20-Jun 09:00 | 43.9635 | 28-May 08:00 |
| 750 | 39.4412 | 23-Jun 08:00 | 42.1896 | 24-Jun 08:00 |
| 1000 | 36.6926 | 16-Jun 08:00 | 39.4640 | 12-Jun 08:00 |
| 1250 | 33.5506 | 16-Jun 08:00 | 36.5479 | 11-Jun 08:00 |
| 1500 | 30.3722 | 18-Jun 08:00 | 33.1691 | 11-Jun 08:00 |

Source: each run’s `AD21:AD8780 → O11/P11`. For example, D0000 clear-sky façade incident peaks on **24 June**, whereas its combined SC 0.40 heat gain peaks on **20 June**. D0500 TMYx façade incident peaks on **28 May**, whereas combined heat gain peaks on **12 June**. The slide numbers are valid heat-gain maxima; the headings “at façade peak” and “façade peak hour” identify the wrong metric.

Combined façade-plus-skylight incident maxima also reconcile: `AE21:AE8780 → O12/P12`. They are independently recoverable from the SC 0.25 maximum because both glazing types then have SHGC 0.2175. See the numerical audit for all 12 runs.

### Monthly maximum versus the 21st

The following comparison retains the existing sky and adjacent-hour convention, changing only the day filter. It is not a replacement simulation or an exact HAP-hour calculation.

| North canopy [mm] | Current Jul all-day bracket SC .40 [kW] | 21 Jul bracket SC .40 [kW] | Current Jun all-day bracket SC .40 [kW] | 21 Jun bracket SC .40 [kW] |
|---|---:|---:|---:|---:|
| 0 | 10.902 | 9.002 | 11.541 | 11.523 |
| 500 | 9.026 | 7.679 | 10.194 | 10.174 |
| 750 | 8.507 | 7.220 | 9.762 | 9.741 |
| 1000 | 8.070 | 6.816 | 9.093 | 9.075 |
| 1250 | 7.580 | 6.405 | 8.663 | 8.645 |
| 1500 | 7.284 | 6.152 | 8.140 | 8.124 |

At D1500, July falls from **7.284 to 6.152 kW**, a 15.5% reduction. June is almost unchanged: **8.140 to 8.124 kW**. The intended day convention therefore materially affects the coordination comparison.

### Areas, SC and source HAP conditions

| Item | Verified value / location | Assessment |
|---|---|---|
| Façade glazing | 207.552936 m²; run `L11`, from `E5:E15` | Consistent across all runs |
| Skylight | 6.117051 m²; `E16/L10` | Included once in all window + skylight gains |
| Total glazing | 213.669987 m²; `L12` | Rounds to 213.7 or 214 m² |
| Sensor mesh area | Façade 208.217592 m²; skylight 6.117051 m²; 1,190 sensors | Excel correctly distinguishes mesh and glazing area |
| New/old combined area | 213.669987 / (56 + 8) = **3.338594** | “3.3 times” is correct for combined glazing |
| New/old vertical area | 207.552936 / 56 = **3.706302** | Use 3.71 times if discussing vertical glazing alone |
| SHGC cases | SC 0.25 / 0.32 / 0.40 → SHGC **0.2175 / 0.2784 / 0.3480** | 0.87 applied once |
| Historical zone sensible peak | July 14:00; solar component **4.752 kW** | `Inputs!D10–D13`; HAP report pp. 2, 5 |
| Historical air-system design-report condition | June 13:00; solar component **4.644 kW** | `Inputs!D10/D14–D16`; HAP pp. 2, 4 |
| Historical DOAS cooling-coil peak | **July 15:00** | HAP p. 1; June 13:00 must not be labelled the DOAS coil peak |

The per-area arithmetic on slide 8 is correct: current July heat gain at SC 0.40 is **34.09–51.02 W/m²** of new total glazing, versus **74.25 W/m²** for 4.752 kW / 64 m². The numerators describe different physical quantities under different model assumptions. These ratios do not prove better equivalent HVAC performance or prove that area alone explains the difference.

## 3. Methodology audit — the eight requested issues

| Issue | Verdict | Evidence and required action |
|---|---|---|
| 1. Tau methodology | **Partly correct** | GH component `9f624…` calls `Wea.from_stat_file(_stat_file, timestep_)`. It takes the Dubai STAT’s monthly optical depths, with no north rotation in the Wea component. Saved WEA has 8,760 half-hour timestamps and is consistent within integer-export precision with the default 2009 Tau calculation. All six clear-sky WEA files are identical; all six TMYx WEA files are identical. Paired DD/TMYx face geometry, sensor grids and modifiers match exactly. Coefficient/data edition compatibility and HAP equivalence cannot verify. |
| 2. Monthly day selection | **Incorrect for the intended 21st-day convention** | Run `U5:V7` use MAXIFS on month and hour only. `E21:E8780` contains day-of-month but is not a criterion. `U9/U10` likewise use every July day. Add a named day input of 21 and a day criterion to each relevant selection; use visible helpers if that improves readability. Do not change the annual clear-sky maximum without explicitly deciding whether its scope is all days or twelve representative days. |
| 3. HAP solar assumptions | **Cannot verify** | Workbook/PPT establish historical loads and reported times, not HAP’s solar algorithm, optical depths, clearness number, solar-time convention, shading inputs or angular glass model. No reviewed claim explicitly proves a shared Tau model. `Summary!A5` nevertheless overstates comparability. Ask MEP for design-weather/solar settings and hourly component reports. Do not assert either shared Tau or a legacy clearness-number method. |
| 4. June/July conditions | **Partly correct** | The two solar components and month/hour inputs match the available HAP report. `Inputs!A14` says “MEP system peak”; use “air-system design-report condition, June 13:00” to avoid confusion with the DOAS cooling-coil peak at July 15:00. No explicit June-as-DOAS-coil statement was found on slides 8–15. |
| 5. Meaning of 4.7 kW | **Incorrect as an established pass/fail criterion** | Neither the workbook nor deck demonstrates MEP approval of this criterion. See the complete inventory below. Preserve it only as a clearly identified historical reference unless MEP establishes an allowable metric and condition. |
| 6. Heat gain vs cooling load | **Partly correct** | Gain formula and SC conversion are correct. `AF21=SHGCperSC*(SC_1*AD21+SC_sky*AC21)`; AG/AH use SC_2/SC_3. AD sums five coincident zone powers; AC is skylight power. These are watts; summaries divide by 1,000. No HAP thermal response, conduction, angular SHGC, frame fraction or system-capacity calculation is present. Exact reproduction of HAP cooling load cannot verify. |
| 7. Time convention | **Partly correct** | WEA and `sun-up-hours.txt` use .5-hour timestamps. Excel uses integer HOY and `DATE(Year,1,1)+HOY/24` as hour-start labels. HAP July 14:00 is represented by the higher result among July hour starts 13/14, i.e. solar positions 13:30/14:30; June 13:00 uses 12:30/13:30. This is an approximation intended to be conservative, not an exact temporal match or guaranteed bound across changing shadows. Confirm HAP’s own timestamp meaning with MEP. |
| 8. Façade vs HVAC peak | **Partly correct** | All reported heat-gain maxima and dates on slides 8–9 are genuine maxima of the relevant Excel/raw heat-gain series. Some differ from façade-incident peaks, as shown above. Retain both the historical-condition comparison and new-façade heat-gain maximum, naming each precisely. The old HAP zone peak does not establish the new building’s peak. |

### What the sky verification establishes

June STAT optical depths are τb **0.721**, τd **1.493**; July **0.863 / 1.338**. The STAT labels its climatic design information as **2025 ASHRAE Handbook**. Local Ladybug `wea.py:327` defaults `use_2017=False`; the GH component does not override this argument. Reconstructing the two variants outside Radiance gives differences from the saved WEA below 1 W/m² with the default variant, versus up to approximately 11 W/m² beam and 66 W/m² diffuse with the 2017 variant. Saved WEA maxima are 814 W/m² DNI and 371 W/m² DHI; the unrounded default calculation reaches DNI 814.80 W/m².

This is evidence of the implemented variant, **not proof that it is the appropriate one for the supplied optical depths**. Ladybug documents the default explicitly; EnergyPlus distinguishes the 2009 and 2017 coefficient/optical-depth pairings. Confirm the provenance/compatible variant before calling this a validated ASHRAE design sky. [Ladybug source documentation](https://www.ladybug.tools/ladybug/docs/_modules/ladybug/wea.html), [EnergyPlus engineering reference](https://bigladdersoftware.com/epx/docs/9-1/engineering-reference/climate-calculations.html).

Recipe inputs and saved sky-matrix header show north **20°**, `-ab 3 -ad 1024 -lw 1e-3`, solar output, hourly timestep, and `gendaymtx -O1 -r 20.0`. Sensor directions are consistent with +Y main glazing, ±X side glazing and an upward skylight normal approximately (0, 0.1581, 0.9874). Opaque modifier reflectances match the stated 0.20/0.40/0.50/0.35/0.30; far-field sky ground is 0.20. No duplicate identical face boundaries were found; skylight occurs once as a 6.117 m² face. **Grid and ambient-bounce convergence cannot verify without additional runs, which were not performed.**

### Every use of the historical value as a criterion

| Location | Current use | Assessment / suggested fix |
|---|---|---|
| `Inputs!A10:C10`, named `Threshold` | “MEP design solar load threshold”, 4.7 | Unconfirmed acceptance status. Rename to historical/reference solar-load component if retaining it. `D10` correctly records the two distinct historical values. |
| `Summary!A1:A3/A5`, D7:L7 and N7:O7 | “vs”, “threshold”, clear sky “comparable with HAP”, maximum SC for threshold | Separate benchmark comparison from acceptance; identify approximate conditions and differing physical quantities. |
| `Summary!D8:L13`, `D18:L23` | Conditional formatting: value ≤ named `Threshold` | These are the workbook’s two conditional-format ranges. Green is mathematically consistent with 4.7, but no acceptance meaning is established. No native Excel charts were found. |
| All 12 runs `S3`, `Y4:Y7` | “compare with MEP threshold”; yes/no for July | July-only binary test. Replace with “at/below historical July reference?” if retained, or remove acceptance interpretation. |
| All 12 runs `S11:U12`; Summary N/O results | Derived SC caps | Valid reference algebra at the specified samples; not approved glazing limits. U12 is only at the façade-incident peak, not the year-wide limiting SC. |
| Slides 8–9 subtitles/table headings, legends, slide 8 key points and next step | “meets”, “within”, “exceeds”, revised design load | Reframe as comparison to an old component. Red/green static fills match 4.7 numerically; they imply unsupported pass/fail. No native PPT charts were found. |
| Slide 14 “MEP threshold” | Treats 4.7 as input criterion for all results | Replace with historical report references and MEP confirmation requirement. |
| Slide 2 “allowable peak solar gain (MEP engineer input)” | Future workflow input | A reasonable intended workflow, but this is not evidence that 4.7 has been approved. |

### Every affected monthly-design-day label

Flag `Inputs!A19` (“clear-sky: ~the 21st”), `Summary!A5` and July/June result sections; each run’s `A1`, `U4:V4`, `U5:V7`, and July incident/SC captions `S9:S11`; slide 8’s design-hour column headings and design-day footnote; slide 9’s title, “Design day” column headings and explanatory footnote; and slide 14’s weather statement. The footnotes disclose all-days selection, but this does not make the exact HAP-hour/design-day headings accurate. Use “full-year clear-sky screening” for annual maxima and “monthly adjacent-hour maximum” for the current July/June comparisons.

## 4. Findings and unsupported claims, ranked

### Modelling/result issues

**F1 — D1250 underside anomaly.** In both `Radiation_HB_Model_D1250_{DesignDay,TMYx}.hbjson`, `orphaned_faces` with `Shading_Material` contain only a 5.977 m² downward horizontal underside at z = 4.67. The large adjacent-option soffits are 257.784 and 276.531 m². The D1250 source underside is Rhino object `e054523c-f1ac-472d-90a0-0ae5f559a4ed` on `EOC::D1250::Roof`; inspect its trims/boundary and the Brep-to-HB conversion. A valid Rhino Brep flag does not prove the intended underside exported. This changes shading/reflections; neither magnitude nor direction of the resulting load error was quantified. **Suggested fix:** correct and validate that geometry/export in a new authorized revision, then review the affected results before relying on the D1250 row. No repair or rerun was performed.

**F2 — Tau variant compatibility unresolved; TMYx provenance label wrong.** See §3. The intended native Tau path is present, but coefficient edition matters. The cached EPW and STAT explicitly declare a **1973–2025** TMYx source period, and all 8,760 saved TMYx WEA DNI/DHI pairs match the EPW exactly (maximum difference **0 W/m²**). Thus slides 9 and 14 cannot describe these runs as TMYx 2007–2021. **Suggested fix:** correct the source-period label; confirm compatible optical-depth/coefficient editions and the desired coordination sky with MEP, and document the choice explicitly. Do not silently assume changing a day filter alone validates the sky.

**F3 — Peak-hour SC is not an all-hours safe SC.** Run `U12` subtracts skylight gain at the hour of maximum AD façade incident power and divides by that façade maximum. Changing SC changes the relative weight of skylight, so the limiting hour can move. For D0750 DD, U12 gives **0.116162**, but that SC produces **4.902911 kW** on 20 June at hour start 09:00. The all-hours reference cap is **0.110145**. D1000 DD similarly gives 0.124163 instead of 0.120970, producing 4.798106 kW. D0500 TMYx gives 0.100789 instead of 0.097093, producing 4.839929 kW. **Suggested fix:** either label U12 “SC corresponding to reference at façade-incident peak only”, or calculate `(reference − 0.87×SC_sky×Q_sky(t))/(0.87×Q_facade(t))` in a visible hourly helper and take the minimum over the intended hours, handling zero façade power explicitly. It remains a reference calculation until an acceptance criterion is agreed.

### Misleading conclusions/labels

**F4 — Historical component presented as allowable capacity.** Locations are inventoried above. The new gains do not demonstrate a cooling-system pass/fail. **Suggested fix:** replace “threshold/within/meets” with historical-reference wording, and obtain MEP assessment of updated whole-building loads and capacity.

**F5 — “Only D1500/SC 0.25 passes” overstates a July-only comparison.** Its current clear-sky July bracket is 4.661371 kW, June bracket **5.185128 kW**, annual maximum **7.347331 kW**. It also has only **38.63 W** margin to the arbitrary 4.7 reference. At the assumed skylight SHGC, an extra 0.178 kW incident on the skylight—about **29 W/m²**—would consume that margin if other terms stayed fixed. **Suggested fix:** report all three conditions and avoid acceptance language.

**F6 — Heat gain, cooling load and “conservative” are conflated.** `Inputs!A18`, `Summary!A5`, slides 8/9 quantity labels and slide 14 imply more equivalence than exists. Delayed solar cooling load at a particular hour need not be less than instantaneous gain at that same hour. Angular SHGC, sky and context uncertainties also prevent an overall bound. Carrier explains the heat-storage/time-delay distinction in its [HAP methodology note](https://www.shareddocs.com/hvac/docs/1004/public/01/hap_ehelp_004.pdf). **Suggested fix:** identify the new result as a screening heat gain; MEP must evaluate the cooling-load response. A generic 10–20% angular reduction cannot verify for the unconfirmed glass assembly.

**F7 — Slide 9 difference and causal claims.** At D1500, the morning-minus-July difference is **4.026762 kW clear sky** and **6.527544 kW TMYx**, not ~4 kW for both. “The HAP hour is set by outdoor temperature”, “more diffuse sky” as the established explanation, and “orientation, not the sky model, governs” are not demonstrated by this comparison. **Suggested fix:** report both differences and describe similar morning timing without claiming an isolated cause.

**F8 — Incident façade peak and combined gain peak are different series.** See the incident table. **Suggested fix:** relabel slide peak columns as combined window + skylight heat-gain maxima at SC 0.40. Use `X7` for that option’s date, not a generic façade-incident date or the SC 0.32 date. All present slide dates happen to match X7, but the distinction matters when inputs change.

### Weak assumptions and secondary issues

**F9 — Tower/skylight uncertainty is consequential to the marginal comparison.** Exported context reaches z ≈ 362.24 m. D1500 clear-sky skylight irradiation is **797.84 kWh/m²/year**, and its 21 June 12:30 irradiance is **196.78 W/m²**; these corroborate the strong-shading concern. The real tower silhouette and the size of any over-shading error **cannot verify** from these results. **Suggested fix:** verify the tower profile/survey before relying on the skylight contribution or the 38.63 W July margin. Do not dismiss it solely because its current calculated share is small.

**F10 — A 1 m side canopy is not established as adequate.** The saved series has zero side projection at D0000 and 1 m at every other depth, while north projection also changes. It does not isolate side-depth sensitivity or prove an adequacy criterion. The west-wing direct/diffuse explanation was not verified by component separation in this audit. **Suggested fix:** describe 1 m as the fixed study input; reserve “adequate” for evidence against an agreed criterion.

**F11 — Supplier, compliance and earlier-content qualifications.** SC–VLT pairs and “best available at ~70% VLT” in `Inputs!D7` are not demonstrated by a supplier certificate. Slides 10–13 appropriately flag EN precedent data awaiting NFRC data, but should label those numbers “EN g-value”, rather than imply an identical NFRC SHGC for the proposed assembly. Slides 5–7 remain superseded; slide 14’s “behind all results” should apply only to current results. The GH Overhang D list still contains the dropped D1130 entry: remove/disable it in a later authorized clean-up.

The brief’s Silver >60% WWR U/LT limits are out of date: the municipality’s January 2023 edition gives **U ≤ 1.7 W/m²K, SC ≤ 0.25, LT ≥ 0.25**, and separately caps non-residential WWR at 60% except shopfronts. Thus SC 0.25 alone does not establish an elemental compliance route at the stated WWR. Confirm applicability, envelope denominator, exceptions and Performance Method responsibility with the permit consultant. The full-envelope 78–82% WWR denominator was not demonstrated in the two deliverables. [Official Al Sa’fat 2023, 501.01 and 201.03](https://dmpmedia.dm.gov.ae/uploads/2023/01/Al-Safat-%E2%80%93-Dubai-Green-Building-System-2nd-editionJan2023.pdf).

Long MAXIFS/INDEX/MATCH formulas are a usability issue, not a discovered arithmetic failure. No workbook redesign was undertaken.

## 5. PPT corrections — exact replacement wording

The accompanying [Slide audit.csv](<Slide audit.csv>) is the requested **51-row slide/statement/source/correctness/issue/replacement table**, covering slides 8–15. Numerical cells are individually checked in the numerical audit. The following text can replace the main inaccurate passages without silently changing the current calculation.

### Slide 8

**Title:** “Window + skylight solar heat gain”

**Subtitle:** “Canopy depth and façade SC — comparison with the previous HAP solar-load component”

**Column headings:**

- “Façade incident power: July bracket maximum [kW]”
- “Window + skylight heat gain: July bracket maximum [kW]”
- “Annual maximum window + skylight heat gain, SC 0.40 [kW]”
- “Heat-gain peak: hour start”
- “Façade SC corresponding to the 4.7 kW July reference”

**Footnote:** “Current July values are maxima over all July days at hour starts 13:00 and 14:00; source solar positions are at 13:30 and 14:30. These approximate the previous HAP July 14:00 condition and are not a 21 July extraction. Solar heat gain = 0.87 × (SC_facade × Q_facade + 0.25 × Q_skylight). No safety factor is applied. The 4.7 kW reference is a rounded solar cooling-load component from the previous HAP model, not an agreed allowable load. Tau coefficient/data compatibility and D1250 geometry require confirmation. VLT and U-value require supplier data.”

**Legend:** “At/below or above the historical HAP reference — no HVAC acceptance implied.” Prefer neutral comparison colours until MEP agrees an acceptance criterion.

**Key points:**

- “At façade SC 0.40, the current July bracket maxima exceed the historical reference for every canopy depth; D1500 gives 7.28 kW.”
- “D1500 with SC 0.25 gives 4.66 kW in the July bracket, 5.19 kW in the June bracket and 7.35 kW at its annual clear-sky maximum. These values do not establish HVAC acceptance.”
- “New total glazing is 213.67 m² versus 64 m² in the previous HAP model, a factor of 3.34. The calculated July heat gain is 34–51 W/m²; the previous HAP solar cooling-load component is 74 W/m². These are different quantities.”
- “Next: MEP to assess shortlisted options using the July/June comparisons and morning profiles, updated conduction and available capacity. Agree the glazing with the architect after daylight assessment.”

The numerical table can retain its current values only as the current-method audit record, with D1250 clearly marked unresolved. A table intended to report the 21st requires recalculated values after the sky/day decisions; do not replace labels alone.

### Slide 9

**Title:** “Full-year clear-sky screening vs typical year”

**Subtitle:** “Window + skylight heat-gain maxima occur on June mornings in the current datasets”

**Headings:** “July bracket maximum heat gain [kW]”; “Annual maximum window + skylight heat gain [kW]”; “Heat-gain peak: hour start”. Replace “Design day” with “Full-year clear sky”.

**Footnote:** “Façade SC 0.40; skylight SC 0.25. July values are maxima over all July days at hour starts 13:00/14:00. Annual maxima use all 8,760 hours. TMYx is Dubai Intl. AP, source period 1973–2025. Hours are interval starts in Dubai local standard time; source solar positions are at half hours. No safety factor applied. These are solar heat gains, not recalculated HAP cooling loads. Clear-sky coefficient/data compatibility and D1250 geometry remain unresolved.”

**Key points:**

- “The previous HAP zone sensible peak is reported at July 14:00. The new combined solar heat-gain maximum occurs on a June morning in both datasets; MEP should assess the resulting cooling-load profile.”
- “At D1500, maximum heat gain is 11.31 kW under clear sky and 12.35 kW in TMYx, respectively 4.03 kW and 6.53 kW above their July bracket maxima.”
- “Both datasets place the combined heat-gain maximum on June mornings. Similar timing does not establish that sky assumptions have no material effect on magnitude.”
- “Current exports show lower maxima with greater north projection; confirm D1250 geometry before relying on that option. No option is accepted or rejected solely against the historical 4.7 kW component.”

Use the same historical-reference legend as slide 8.

### Slides 10–15

Slides 10–13: replace “g-value / SHGC” with **“Manufacturer EN g-value — reference assembly”**. Retain the caveat that the agreed assembly needs NFRC data. Correct “Precendents” to “Precedents”. Exact product performance and the specified built-assembly precedents cannot verify from the supplied evidence; do not present them as approved project specifications.

Slide 14 lead-in: **“Inputs for the current six-depth solar screening results on slides 8–9.”**

Slide 14 method: **“North canopy projections: 0, 0.5, 0.75, 1.0, 1.25 and 1.5 m. Side projections are 1.0 m except D0000, which has 0 m. Skylight included. Sensor grid 0.4 m; Radiance -ab 3. D1250 underside geometry requires correction; grid/bounce convergence has not been demonstrated.”**

Slide 14 weather: **“Dubai Intl. AP TMYx, source period 1973–2025, and a full-year Tau clear-sky screening dataset. Current monthly comparisons use all days; confirm Tau coefficient/data compatibility and the intended 21st-day comparison.”**

Slide 14 gain statement: **“Instantaneous solar heat gain uses constant SHGC = 0.87 × SC. It is not HAP cooling load; no overall conservatism is demonstrated.”**

Slide 14 reference statement: **“Previous HAP solar-load components: 4.752 kW at the July 14:00 zone peak and 4.644 kW at the June 13:00 air-system design-report condition, before its safety-factor allowance. Neither is an agreed new-façade limit. The DOAS cooling-coil peak is July 15:00.”**

Slide 14 schedule: **“08:00–18:00, Mon–Fri applies to the sun-path dome only. Solar-load maxima use all hours.”** Retain the reflectance values as model assumptions. Slide 15 has no technical correction.

## 6. Recommended final workflow and open questions

**The proposed dual-reporting/daylight workflow is technically defensible for early-stage optioneering, subject to the model and comparison qualifications above.**

1. Resolve the D1250 export and sky coefficient/data pairing before relying on revised results. Preserve a run manifest so geometry, weather, exports, workbook and deck can be tied to the same version.
2. Agree with MEP which historical report conditions to compare, which representative day to use, and how to interpret HAP hourly timestamps. If the intended monthly day is the 21st, add that explicit day criterion. Report July and June separately rather than averaging their old components into one acceptance number.
3. Report the new façade-plus-skylight **solar heat gain near those historical conditions**, with day/time approximation disclosed. Separately report the new **maximum clear-sky heat gain** and its complete morning profile; retain TMYx context. Distinguish full-year clear-sky maxima from maxima of twelve 21st-day profiles.
4. Keep 4.752/4.644 kW as historical cooling-load components until MEP confirms an appropriate allowable metric and available capacity. MEP must assess dynamic cooling load, updated glazing/roof conduction, schedules and controls; the heat-gain difference is not an increment that can simply be added to an old coil size.
5. Carry realistic canopy × glazing combinations into daylight assessment using supplier VLT and optical data, rather than rejecting them against the unapproved reference. Begin minimum-daylight checks with deeper canopy/lower VLT cases, and excessive-sun checks with less shade/higher transmission cases. SC alone does not determine daylight transmission. These are priorities for testing, not proof that untested combinations pass; confirm any monotonic screening assumptions.
6. Agree project daylight criteria and statutory requirements before using “daylight-compliant”. Where used, identify LM-83/LEED sDA/ASE criteria as project benchmarks and confirm the analysis method, occupied area/hours and shade operation. Return assessed options and solar profiles to architect/MEP for selection, together with a confirmed compliance route.

**Questions requiring answers:**

- **MEP:** Is any new-façade solar criterion approved? What are the available FCU/DOAS capacities and operating schedules? Provide the HAP solar/weather model, parameters, hour convention, glazing/shading inputs and hourly solar/total cooling-load reports, including June mornings. Is June 13:00 being used only as the air-system design-report condition?
- **Engineer/modeller:** Why does the D1250 underside export as a small strip? What Tau coefficient edition belongs with the STAT optical depths? Is a later, approved sensitivity/convergence check required after those issues are resolved?
- **Architect/supplier:** Confirm full glazing build-up, frame/glass area basis, VLT, U-value and angular solar properties; verify the tower silhouette relevant to skylight shading.
- **Permit consultant/client:** Confirm the applicable Al Sa’fat/DBC edition, WWR denominator and exceptions, energy-model responsibility and agreed daylight criteria. The present solar screening does not establish compliance.

## Verification record and limitations

- Reintegrated **all 12 runs × 12 grids** from raw `.ill` values and HBJSON mesh areas. Sum of hourly integration versus HB cumulative `.res` differs by at most **1.50 × 10⁻¹⁰ kWh**; versus the six-decimal exported HB check by at most **4.92 × 10⁻⁷ kWh**.
- For D1500 DD, all 105,120 pasted hourly grid entries match raw integration within **0.00000050 W**. Reconstructed façade/skylight power and gain differ only at the tiny level introduced by rounded exported areas. Headline gain maxima across all runs differ from Excel by at most **7.57 × 10⁻⁸ kW**.
- Inspected formulas, cached values, named inputs and conditional-format definitions without resaving Excel. No saved Excel error cells found. No live Excel recalculation/input-perturbation test was performed; cached agreement is not proof of future native-engine behaviour.
- Inspected all 15 slides’ text and native tables, including red/green table fills, without resaving PowerPoint. This is a content/numerical audit, not a full rendered typography/layout review. No native PPT chart objects were found.
- Read GH_IO archive and exported model geometry/settings without opening or executing the GH definition. Compared paired sky models’ geometry/grids/materials. No simulations, geometry repairs, workbook changes or deck changes were made.
- The original files changed on disk during this review. The later snapshot’s audited workbook headline cells and slide text match the earlier extracts. GH changes add native sun-path annotations; the Tau component code is unchanged. The raw 19 October simulation models/results remain the basis of this audit. The snapshot manifest records the reviewed file hashes and source modification times; later saves are not covered automatically.

Primary project sources: current workbook and deck in `261019_Design Day Run`, current GH archive, Rhino model, saved runs under `C:/Users/Vishnu/simulation/DFF-context-zones-261019`, Dubai STAT/EPW, and `Reference/DFL Heat Load New Office (1).pdf` (HAP 5.10, 21 August 2026). HAP settings absent from those sources remain unverified.

### Reviewed deliverable versions

| File | Source modified | SHA-256 (first 16 characters) |
|---|---|---|
| 261005 EOC vr Facade - Environmental Study.pptx | 2026-10-20T12:11:33.436721 | b69507cca664520b |
| 261019 EOC vr Incident Radiation_HB - 1.10_Context_Zones_Design Day.gh | 2026-10-20T12:17:48.018188 | 4c325f996c85debb |
| 261019 EOC vr Solar Radiation Study - v8 - Design Day.xlsx | 2026-10-20T11:51:57.693113 | 7b015dda539134e1 |
| 260929 EOC vr DFF-RLE_Facade Radiation_Context.3dm | 2026-10-20T12:17:47.286087 | 1e3609f032c489a0 |
