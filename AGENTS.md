# AGENTS.md — Review brief: DFF Robotic Lab Expansion, façade solar study

You are reviewing an environmental-design study prepared for Eckersley O'Callaghan (EOC). The work was done with a human engineer (the "user") and an AI assistant.

**Your job is to review it, not redo it.** Report errors, weak assumptions, inconsistencies between files, and anything that would mislead the architect or the MEP engineer. Do not change the deliverables unless the user explicitly asks.

---

## 1. Ground rules

- **Read-only by default.** Do not edit, move or overwrite any `.3dm`, `.gh`, `.xlsx` or `.pptx` in this folder. If you want to demonstrate a fix, write a new copy with a new name, or describe it.
- **Do not run simulations.** Each Honeybee run takes 4–6 min in Rhino/Grasshopper. The results already exist under `C:\Users\Vishnu\simulation\`.
- **The user's working preferences, which must not regress:**
  - **Native Grasshopper:** use native Ladybug, Honeybee and Grasshopper components. Use script components only if strictly necessary.
  - **Traceable Excel:** raw exports are pasted in, and every result is a visible formula. Never paste pre-computed numbers.
  - **Human-editable Excel:** short formulas, one step per column, helper columns rather than nested functions, named inputs on one Inputs sheet, clear units in headers.
  - **No assumptions:** flag missing information as a question, don't invent it.
  - **Standard terms:** irradiance [W/m²], irradiation [kWh/m²], incident solar power [kW], solar heat gain = incident × SHGC. The project now uses **SC (shading coefficient)**, with **SHGC = 0.87 × SC** (ASHRAE / Al Sa'fat definition).
- **Units:** metres, kW and kWh. Model north is **20°**: model +Y points to true N20°E.

---

## 2. Project in one paragraph

DFF (Dubai Future Foundation) "DFL Expansion" is a new single-storey **New Office** pavilion at the Emirates Towers podium, Dubai. It has a U-shaped, full-height glazed façade facing **NNE (main, 20°)**, **WNW (west wing, 290°)** and **ESE (east wing, 110°)**, plus a small skylight.

**The study:** a parametric screening of **roof overhang (canopy) depth × glass SC** against the MEP engineer's design solar load, followed later by daylight (sDA/ASE) on the shortlisted options. **Scope is early-stage optioneering, not certification.**

**Window-to-wall ratio** of the New Office envelope is about 78–82 %. That puts it in Al Sa'fat's **>60 %** band: Silver requires **SC ≤ 0.25, summer U ≤ 1.9, LT ≥ 0.10**. The architects want **VLT ≥ 70 %**, which realistically means SC 0.32–0.40, and that needs Al Sa'fat's Performance Method.

---

## 3. Folder map (`C:\LocalDev\DFF - Robotic Lab Expansion\`)

| Path | What it is |
|---|---|
| `260929 EOC vr DFF-RLE_Facade Radiation_Context.3dm` (24 MB) | Rhino model. Layers: `EOC::Glazed Facade::{West,North,East}`, `EOC::Opaque Facade`, `EOC::Skylight`, `EOC::D00 / D500 / D750 / D1000 / D1250 / D1500::Roof`, `EOC::Modelled Context`, `EOC::Context buildings` (CADMapper), `EOC::Ground`, `EOC::Dividers` (zone split lines). The `CAD::` layers are heavy linework. |
| `261019_Design Day Run\261019 EOC vr Incident Radiation_HB - 1.10_Context_Zones_Design Day.gh` | **Current Grasshopper script** (the latest runs used this). |
| `261019_Design Day Run\261019 EOC vr Solar Radiation Study - v8 - Design Day.xlsx` (40 MB) | **Current results workbook** (the user has since reformatted its Summary sheet). |
| `261019_Design Day Run\261005 EOC vr Facade - Environmental Study.pptx` | **Client deck**. Slides 8–9 are the new results slides (solar load vs threshold; design day vs typical year). |
| `261007_Shading Mask Run\…_Heatmap_v2_Sunpath.gh` | Sun-path + sky radiation + shading-mask diagram (native LB) for the North-West Open Office. |
| `261006 EOC vr Solar Radiation Study - v7 - Zones.xlsx` | Previous workbook (old geometry: D1130, no skylight, 11 grids). |
| `261006 …_Heatmap_v2.gh`, `HB_Heatmap.py`, `HB_Heatmap_PeakZone.py`, `Heatmaps\` | Earlier heatmap tooling and images (old geometry). |
| `Reference\DFL Heat Load New Office (1).pdf` | **MEP's HAP 5.10 load report** (21 Aug 2026; based on *old* drawings). `hl.txt` is a text extract. |
| `Reference\HVAC DRAWINGS…pdf`, `EXISTING & NEW OFFICE LOCATIONS.pdf` | MEP layout and location plan. |
| `Helper Scripts\Roof model.gh`, `Thermal Zones.gh` | The user's helper scripts. |
| `_ss\` | Superseded files. |

**Simulation outputs** (`C:\Users\Vishnu\simulation\`):
- `DFF-context-zones-261019\Radiation_HB_Model_<D>_<TMYx|DesignDay>\` — **current**: 6 depths × 2 skies.
  - Each run folder contains `<model>.hbjson` and `annual_irradiance\results\total\*.ill` (hourly, sun-up hours only, with `sun-up-hours.txt`).
  - It also contains `annual_irradiance\metrics\cumulative_radiation\*.res`.
- `DFF-context-zones\`, `DFF-context\`, `Radiation_HB_Model_D*` — earlier runs (old geometry or context; superseded).

**Weather:** `C:\Users\Vishnu\AppData\Roaming\ladybug_tools\weather\ARE_DU_Dubai.Intl.AP.411940_TMYx\` contains the `.epw` and `.stat` files. The source is climate.onebuilding.org, TMYx 2007–2021, Dubai Intl AP.

---

## 4. Method (what was done)

### 4.1 Geometry and model (Grasshopper → Honeybee)

**Glazing grids**
- Glazing comes from Rhino layers via Geometry Pipelines.
- It is split into **5 floor-plan zones**: West_Office Rooms (4 grids), North-West_Open Office, North_Pantry, North-East_Open Office, East_Office Rooms (4 grids).
- Zone dividers are at x = 6.35 / 18.15 / 23.65 / 35.79; grids are sorted anticlockwise.
- **Skylight** (6.1 m², tilted about 9° towards +Y) was added as the **12th grid, `Skylight_0`**. It is merged into the same tree as branch `{0;3;0;0}`, so the existing naming and export chain covers it.
- Sensor grid: `LB Generate Point Grid`, 0.4 m spacing, 0.05 m offset, sensors facing outward.
- Sensor counts: W 44/66/11/66, NW 319, N 143, NE 330, E 66/11/66/44, skylight 24; **1,190 in total**.

**Materials** (Radiance opaque modifiers, reflectance)

| Surface | Reflectance |
|---|---|
| Glass / skylight face | 0.20 |
| Opaque façade | 0.40 |
| Roof / overhang | 0.50 |
| Ground (light paver) | 0.35 |
| Context | 0.30 |

The context was dropped in Rhino to z = −0.01 so it doesn't overlap the ground at z = 0.

**Overhang options** (Rhino layers)
- North projection: 0 / 500 / 750 / 1000 / 1250 / 1500 mm.
- West and east projections are a constant **1.0 m** for every option except D00.
- D1130 (the old architect's option) was dropped by the user.

**Recipe**
- `HB Annual Irradiance`, `-ab 3 -ad 1024 -lw 1e-3`, north = 20.

**Two skies** (switched by the `Sky` value list → Stream Filter → `_wea`)
1. **TMYx typical year:** `HB Wea From EPW`.
2. **Design day:** `HB Wea From Tau Clear Sky` from the `.stat` file, i.e. the ASHRAE revised clear-sky (τ) model with Dubai's monthly τ values, over a **full year of clear-sky days** (8,760 h, 4,360 sun-up hours).

**Naming and output**
- Model name = `Radiation_HB_Model_` + `D0000…D1500` + `_TMYx | _DesignDay`.
- Folder = `simulation\DFF-context-zones-261019\`.

### 4.2 Post-processing (native GH chain → text export → Excel)

**Grasshopper chain:** `HB Annual Results to Data` → `LB Arithmetic` (× sensor area) → `LB Mass Arithmetic` (sum per grid, mapping None) → `LB Deconstruct Data` → Partition List (8760) → Flip Matrix → Text Join (TAB).

**Two export panels:**
- **EXPORT hourly:** 12 columns, header + 8,760 rows, Σ(a·I) per grid in W.
- **EXPORT grid table:** grid, zone, n sensors, Σa, A_glz, HB cumulative check in kWh.

The hourly export chain is normally **locked** in the GH file to avoid heavy recompute. It was unlocked only during export, and the locks were restored.

**Excel v8, per run sheet** (`<D> DD` / `<D> TMYx`)
- **Grid table** pasted at A4, **hourly data** at F20.
- **Zone mean irradiance:** I_z(t) = Σ zone grid columns ÷ zone Σa.
- **Zone incident power:** Q_z(t) = I_z × A_glz, where A_glz is the real glazed area from the Brep.
- **Façade total and façade + skylight:** coincident hourly sums.
- **Solar load (kW):**

  > **0.87 × SC_facade × Q_facade(t) + 0.87 × SC_sky × Q_skylight(t)**
  >
  > with SC_facade = 0.25 / 0.32 / 0.40 and SC_sky = 0.25.

- **Design-hour values:** the highest value **over all days** of July (hour starts 13 and 14) and of June (12 and 13). These bracket HAP's instantaneous 14:00 and 13:00.
- Also reported: peak over all hours and months (with date), and the **highest façade SC that meets the threshold**.

**Threshold:** **4.7 kW**. It is the MEP's HAP "Window & Skylight Solar Loads": 4.752 kW at the zone peak, **Jul 14:00** (45.7 / 23.8 °C), and 4.644 kW at the system peak, **Jun 13:00**. It is taken **before** HAP's 10 % sensible safety factor.

### 4.3 Deck (slides 8–9)

- Values come from the same exports and formulas (recomputed for the slides in a scratch script).
- Load cells are coloured **green ≤ 4.7 kW, red > 4.7 kW**.
- Total glazed area is **213.7 m²** (207.6 façade + 6.1 skylight).

---

## 5. Key results (verify these)

Design day, window + skylight solar load in kW:

| Overhang | Façade incident, Jul design hour | SC 0.25, Jul | SC 0.32, Jul | SC 0.40, Jul | SC 0.40 at façade peak (date) | Max SC for 4.7 kW (Jul) |
|---|---|---|---|---|---|---|
| 0 | 30.53 | 6.92 | 8.78 | 10.90 | 19.62 (20 Jun 09:00) | 0.17 |
| 500 | 25.13 | 5.75 | 7.28 | 9.03 | 16.43 (20 Jun 09:00) | 0.20 |
| 750 | 23.64 | 5.42 | 6.86 | 8.51 | 14.47 (20 Jun 09:00) | 0.21 |
| 1000 | 22.38 | 5.15 | 6.51 | 8.07 | 13.51 (16 Jun 08:00) | 0.23 |
| 1250 | 21.02 | 4.84 | 6.12 | 7.58 | 12.42 (16 Jun 08:00) | 0.24 |
| 1500 | 20.10 | **4.66** | 5.89 | 7.28 | 11.31 (18 Jun 08:00) | 0.25 |

**TMYx at SC 0.40:**
- July design hour: 8.60 / 6.94 / 6.71 / 6.42 / 6.09 / 5.82 kW (0 → 1500 mm).
- Peaks: 19.49 / 16.17 / 15.47 / 14.55 / 13.53 / 12.35 kW, on 11–24 June, 08:00–10:00.

**Conclusions stated to the client:**
1. At SC 0.40 (VLT ≈ 70 %), no depth meets 4.7 kW. Only 1500 mm with SC 0.25 does.
2. Per m² of glass the design takes in 34–51 W/m² at SC 0.40, against ≈ 74 W/m² in the old HAP model (4.75 kW on 64 m²). The total exceeds the threshold because the glazed area is about 3.3 times larger.
3. The façade's own peak is on **mid-June mornings** (low east-north-east sun), about 4 kW above the July 14:00 value at 1500 mm. The MEP should check that hour in HAP.
4. A side overhang of 1.0 m is adequate: the east wing responds strongly up to 1 m, while the west wing's peak is mostly diffuse and reflected light.

**Checks already passed:**
- Hourly sums equal HB cumulative values to within 5 × 10⁻⁷ kWh on all 12 runs.
- Grid sums equal hourly sums.
- Native GH heatmap colours and the Python heatmap colours match exactly (earlier geometry).

---

## 6. Known issues and open questions (scrutinise these)

1. **Emirates Office Tower context.** The CADMapper extrusion is a full prism up to z = 362 m, about 13 m south of the skylight. It blocks even the near-zenith June sun on the skylight: about 200 W/m² against 1,005 W/m² global horizontal on 21 Jun at 12:30, and 745–790 kWh/m²·yr against 2,269 open clear-sky. It probably **over-shades** the skylight, since the real tower tapers into a spire, so the skylight load is likely underestimated. Its share is small (about 0.3 kW at the design hour). Not yet resolved.
2. **Design day: all days or the 21st.** The workbook takes the highest value over all days of the month. ASHRAE/HAP use the 21st. July values fall by about 15–20 % on the 21st (e.g. 7.28 → 6.15 kW at 1500 mm, SC 0.40); June and the peaks are practically unchanged. Check which convention suits the like-for-like comparison.
3. **Clear-sky model unconfirmed.** HAP's clear-sky model and parameters (τ or clearness number) are unknown. We assumed ASHRAE τ from the `.stat` file. That sky is hazy: maximum DNI 815 W/m² against 916 W/m² in TMYx.
4. **Heat gain vs cooling load.** We compare instantaneous solar heat gain at SHGC × normal incidence with HAP's **cooling load** (transfer-function, time-delayed). Ours is conservative. There is no angle-dependent SHGC; the morning peak strikes at about 60–67° incidence, so it may be overstated by about 10–20 %.
5. **Threshold basis.** 4.7 kW comes from an **old** HAP model: 56 m² of windows + 8 m² skylight, SC 0.40, U 2.2, exposures NE/SW/SE, roof U 0.685. That model also has **glass conduction** about 3.3 times lower than the new façade would give; this is not part of our check.
6. **Hour convention.** Excel rows are hour **starts**; Radiance sun positions are at the half hour. HAP reports on the hour. See how "Jul 14:00" is bracketed (hour starts 13 and 14).
7. **SC and VLT pairs** (SC 0.25 ≈ VLT 45–50 %, SC 0.32 ≈ 65–70 %, SC 0.40 ≈ 70–72 %) are typical estimates, not supplier NFRC data. The 5-layer glass build-up is still to be confirmed with the architect.
8. **Out-of-date deck slides.** Slide 5 (incident radiation) and slide 7 (g-value table) still use the old geometry (D1130, no skylight) and EN-based g-values. Slide 6 (masks) uses old roof depths.
9. **Workbook usability.** v8 formulas are not yet "human-centric": there are long `MAX(_xlfn.MAXIFS…)` and `INDEX/MATCH/SUMIF` constructs. A v9 rebuild in a simpler style is pending the user's go-ahead.
10. **Compliance.** For SC above 0.25 under Al Sa'fat's Performance Method, it isn't yet known whether the client or the MEP will do the energy model. The window-to-wall ratio is measured on the New Office envelope only; this needs Dubai Municipality or the permit consultant to confirm.
11. **Daylight (next stage, not yet run).** No local sDA/ASE limit exists. Al Sa'fat 405.01 is qualitative; DBC Table B.8 requires a window-to-floor ratio ≥ 10 % (unofficial copy). The benchmarks are IES LM-83 / LEED: sDA300/50% ≥ 55 % (75 % preferred) and ASE1000,250 ≤ 10 %.

---

## 7. Suggested review checklist

1. **Geometry.**
   - Do the roof layers match the stated projections (north 0–1.5 m, sides 1.0 m)?
   - Do the sensor directions point outward (façade) and up (skylight)?
   - Is any glazing double-counted between `HB Face` (façade material) and the grid merge? The skylight is deliberately *not* fed to the façade HB Face.
2. **Simulation inputs.** Is `-ab 3` adequate for façade irradiance? Is the north angle applied once (recipe north = 20; clear-sky Wea built without north)? Are the ground and context settings right?
3. **Post-processing.**
   - Pick one run (e.g. `D1500_DesignDay`) and recompute from the `.ill` files and the `.hbjson` sensor areas, outside Excel.
   - Check the façade and skylight solar load at July 13:00 / 14:00, the peak and its date, and confirm they match the workbook and slide 8.
4. **Formulas.**
   - SHGC = 0.87 × SC.
   - The zone area scaling: Σa sensors vs A_glz (they differ by up to about 3 % on some grids).
   - The design-hour bracketing.
   - The "max SC" formula, which subtracts the skylight from the threshold.
5. **Consistency.** Do the numbers in the deck (slides 8–9) and the workbook Summary agree?
6. **Physics sanity.**
   - Clear-sky vs TMYx magnitudes.
   - The June-morning peak timing for an NNE façade at 25 °N.
   - The east and west wing behaviour.
   - The skylight shading by the tower.
7. **Communication.** Are any statements to the client or the MEP over-claimed or ambiguous? Pay particular attention to items 4–6 in §6.

---

## 8. How to inspect the files without Rhino

- **`.gh`:** binary GH_IO archive. Use `C:\Program Files\Rhino 8\Plug-ins\Grasshopper\GH_IO.dll` (`GH_Archive.ReadFromFile` → `Definition/DefinitionObjects/…/Container`) to list components, panels and value lists.
- **Components of interest** (GUID prefixes):
  - HB Annual Irradiance `e2b5`;
  - HB Model `f31e`, with model name panel `f42f`;
  - sensor grid generator `c675`;
  - grid Brep `e478`, plus the new "Facade + Skylight (grids)" merge;
  - export panels `de88` (hourly) and `1ead` (grid table);
  - value lists "Overhang D" and "Sky".
- **`.hbjson`:** JSON. Sensor grids are under `properties.radiance.sensor_grids`; faces and modifiers are under `orphaned_faces`.
- **`.ill`:** one row per sensor, one column per sun-up hour in `sun-up-hours.txt`; values in W/m².
- **`.xlsx`:** openpyxl (`data_only=False` for formulas, `True` for cached values). The v8 workbook is 40 MB.
- **Python:** a Ladybug Tools Python with `ladybug` / `honeybee` is at `C:\Program Files\ladybug_tools\python\python.exe`.

## 9. Output expected from the review

A short report with:
- **findings**, ranked by severity: wrong result → misleading statement → weak assumption → cosmetic. Each with file and location, the evidence, and the suggested fix;
- **open questions** for the user, the architect or the MEP engineer;
- **an explicit statement of what you verified and how**, e.g. "recomputed D1500 DesignDay from .ill: matches to 0.01 kW".
