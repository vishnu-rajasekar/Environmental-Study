---
name: grasshopper-ladybug-honeybee
description: Build, edit and check Ladybug/Honeybee (LBT 1.8+) Grasshopper studies in the user's live Rhino 8 through the Rhino MCP server - radiation, annual daylight (sDA/ASE), materials from spectraldb, glazing from supplier NFRC reports, sensor grids from Rhino layers, image capture and deck export. Use for any Grasshopper/Ladybug/Honeybee/Radiance task in this project or when driving the user's Rhino.
---

# Grasshopper + Ladybug/Honeybee in the user's Rhino (lessons from the DFF Robotic Lab study)

## Non-negotiables (user preferences)

- **Native components only**: Grasshopper, Ladybug, Honeybee and Rhino 8 "Model" components. Script components only when no native route exists, and say so.
- **Reusable without AI**: whatever is built must keep working when the user opens the .gh, edits a panel and presses a toggle. No logic hidden in agent-side scripts; agent scripts are for *placing/wiring* components and for *independent checks* only.
- **Traceable inputs**: every number on the canvas sits in a panel whose nickname says what it is and where it came from (URL, report, page). Group labels carry the source URL.
- **No assumptions**: missing data becomes a question (AskUserQuestion), not a guess. Check units the user typed (e.g. % vs fraction).
- **Never overwrite deliverables** (.3dm/.gh/.xlsx/.pptx): write a new dated copy. Don't save the user's .gh for them unless asked; tell them to save.
- **Don't run simulations unless asked.** Results live under `C:\Users\Vishnu\simulation\<model name>\`.
- Excel: raw exports pasted in, every result a short visible formula, one step per column, named inputs on an Inputs sheet.

## Connecting to the user's Rhino

- The MCP router may spawn a *new empty* Rhino instead of adopting the user's (its `list_slots` was empty). The user's Rhino serves JSON-RPC on `http://localhost:10500/`. Post `tools/call` → `run_python` directly (helper below). Don't leave spawned empty Rhinos; ask the user to close them if `close_slot` is blocked.
- Read the script with `[IO.File]::ReadAllText` - `Get-Content -Raw` adds PS properties and the server rejects the argument.

```powershell
param([string]$PyFile, [int]$Timeout = 120)
$py = [System.IO.File]::ReadAllText($PyFile, [System.Text.Encoding]::UTF8)
$body = @{jsonrpc="2.0";id=1;method="tools/call";params=@{name="run_python";arguments=@{script=$py}}} | ConvertTo-Json -Depth 5
$r = (Invoke-WebRequest -Uri http://localhost:10500/ -Method Post -Body ([Text.Encoding]::UTF8.GetBytes($body)) -ContentType "application/json; charset=utf-8" -UseBasicParsing -TimeoutSec $Timeout).Content | ConvertFrom-Json
foreach ($c in $r.result.content) { $c.text }
```

- In the script use `__rhino_doc__` / `Rhino.RhinoDoc.ActiveDoc`; get the GH doc by file path: `[g for g in Grasshopper.Instances.DocumentServer if "Daylight" in (g.FilePath or "")][0]` (several .gh files are usually open, including other projects - never touch those).
- While a Honeybee recipe runs, Rhino's UI thread is blocked: MCP calls time out. Watch the recipe log on disk instead (`<sim>\<recipe>\__logs__\logs.log`, finished when it prints "This progress looks :)").
- **The user edits the canvas live.** Check `doc.UndoServer.UndoNames` before and after your edits; ask them to pause while you rewire or while a run is armed.

## Editing the canvas from Python (GH1)

- Native component: `GH.Instances.ComponentServer.EmitObject(guid)`; find the guid by name: `[p.Guid for p in ComponentServer.ObjectProxies if p.Desc.Name=="Shift Paths" and not p.Obsolete]` - **never guess GUIDs** (a guessed one gave "Relative Items").
- Ladybug/Honeybee components are scripted user objects: instantiate with `GH.Kernel.GH_UserObject(r"C:\Program Files\ladybug_tools\grasshopper\<plugin>\user_objects\HB Glass Modifier.ghuser").InstantiateObject()`. `EmitObject(component.ComponentGuid)` gives an empty shell.
- Then `o.CreateAttributes(); o.Attributes.Pivot = PointF(x, y); doc.AddObject(o, False)`; wire with `input.AddSource(output)`; `doc.NewSolution(False)` to compute.
- Wire outputs **by NickName**, not index: many HB components put `report` first (HB Weekly Schedule: `report, schedule, ...`).
- Panels feeding lists: `panel.Properties.Multiline = False` (one item per line), otherwise "Type conversion failed from Text to float".
- Tree matching: `param.DataMapping = GH_DataMapping.Graft / Flatten` (e.g. graft room names into HB Sensor Grid `_name_`; flatten grids into HB Assign Grids).
- Telepathy: new `Remote Receiver` (guid 08cdcd26...) - set `NickName` to the sender's and `receiver.AddSource(sender)`.
- Find a free canvas strip before placing (check `o.Attributes.Bounds.IntersectsWith(rect)`), put new chains in a named Group plus a Scribble title.
- HB objects in GH outputs live in GH's own Python runtime - not readable from the MCP interpreter. To inspect a model, wire a temporary **HB Dump Objects** to write `.hbjson`, then read it with `C:\Program Files\ladybug_tools\python\python.exe` (`Model.from_hbjson`).
- Long runs: replace/keep a run toggle, set it True and call `doc.ScheduleSolution(500)` so the call returns before the solve starts. **While the toggle is True every upstream edit re-runs the recipe and deletes the previous results** (`reload_old=False`). Restore the user's `LB FalseStartToggle` afterwards.

## Materials (Radiance modifiers)

- Opaque surfaces = Radiance **plastic** (HB Opaque Modifier / Opaque Modifier 3). Metal (`HB Metal Modifier 3`) tints the specular highlight - only for bare metal; a painted "white aluminium" mullion is plastic.
- spectraldb.com: the page's "Radiance Definition" line is the target (`void plastic name 0 0 5 R G B spec rough`). Specularity on the page is in **percent** (0.40 % → 0.004; 0.09 % → 0.0009) - users often paste the percent figure.
- `HB Opaque/Metal Modifier 3` call `from_reflected_specularity` and write `R/(1-spec)`. To reproduce spectraldb exactly feed each channel as **R × (1 − spec)** (native: panel "1" → Subtraction `1-spec` → Multiplication per channel).
- Verify every material against spectraldb: the home page holds an index `id,name,type,L,a,b,hex,V,M`; fetch `https://spectraldb.com/measurements/<id>/` and compare the 5 numbers with what GH writes. Label each material group with its own URL.
- Glazing for daylight: **HB Glass Modifier** with `_trans` = NFRC 300 Tvis from the supplier report (Guardian Performance Calculator PDF in `Reference\`); HB converts transmittance → transmissivity (0.62 → 0.6758). Glass must be single surfaces (a closed glass box applies glass twice). Radiance glass reflectance (~8 %) differs from the report's ρv - fine for sDA, note it for glare.
- Radiation-study "Transparent_*" opaque glass modifiers must not survive into a daylight model - check every HB Face's `rad_mod_`.

## Sensor grids from room curves (native, reusable)

`panel "Areas::*"` → Query Model Objects (L) → Model Object (G, L) → Model Layer (N) → Create Set (room names) + Member Index → List Item (curves per room) → Boundary Surfaces → LB Generate Point Grid (`_grid_size` ≤ 0.6 m for LM-83, `_offset_dist_` **0**) → Move by Unit Z × 0.76 (points and meshes) → Shift Paths −1 → Mesh Join → HB Sensor Grid (`_name_` grafted room names, no `_directions_` = +Z) → HB Assign Grids (flatten).

- A clockwise room curve gives a downward boundary surface; with an offset the sensors go *below* the floor facing down. Offset 0 + Move + default +Z avoids it without editing the user's Rhino file.
- Rooms with chamfers get irregular edge cells (more, smaller faces): always area-weight results with the grid meshes.
- A Geometry Pipeline filter `Areas` does not pick up sub-layers; it also gives no layer names.

## Annual daylight (sDA / ASE)

- HB Annual Daylight with `enhanced_ = True` (traces the sun per hour) - required for ASE. `-ab 5 -ad 15000 ...` from HB Radiance Parameter (recipe 2, detail 1).
- sDA300/50%: HB Spatial Daylight Autonomy with `mesh_` (area-weighted). ASE1000,250h: HB Annual Sunlight Exposure gives `hrs_above`; its ASE % is **unweighted** - feed `hrs_above` into a second HB Spatial Daylight Autonomy with target 250 and the meshes for an area-weighted ASE.
- Strict LM-83 sDA needs operable blinds (HB LEED Option I, Rooms + aperture groups). Without them label sDA "no blinds".
- Occupied hours: this project uses **08:00–18:00 Mon–Fri** (same as the radiation sun-path masks) via HB Weekly Schedule (weekday panel to Mon–Fri, zeros to Sat/Sun/holiday) into both the recipe `_schedule_` and ASE `_occ_sch_`. HB schedules start the year on a Sunday. LM-83's own window is 08:00–18:00 every day - report it as a sensitivity.
- **ASE image = overlit / non-overlit map** (the user's preferred style, not an hours heatmap): LB Legend Parameters Categorized on `hrs_above` with `_domain` = the 250 h target panel, colours grey 146,146,146 (same swatch as 'Not daylit') + orange 245,166,35, categories `Non-overlit / Overlit`. LB's categorized colour uses `value >= domain` → the same rule as HB (`h_above >= occ_hours`), so the map agrees with the ASE %. On the slide add a callout box 'Annual Sunlight Exposure ASE1000,250h  x %' (flat white fill, orange line - the theme default adds a gradient + shadow). Keep max hours in the table.
- Independent check: recompute DA/sDA/ASE from `results/.../total|direct` + `sun-up-hours.txt` + grid mesh face areas with numpy and compare with the GH outputs.

## Geometry checks before any run

- Face normals (glass/plastic are two-sided in Radiance, so flipped walls are harmless; flipped *sensor* surfaces are not).
- Coplanar overlaps (floor vs ground, tile vs paver, roof underside vs ceiling) - z-fighting.
- Option-dependent geometry hiding in fixed layers (the Ceiling layer ran out to the 1.5 m canopy soffit, so other overhang depths would all behave like 1.5 m).
- Openings: ceiling hole under the skylight; nothing horizontal between work plane and ceiling except intended bulkheads.
- Context: CADMapper towers are full prisms (over-shade).
- **No sensor inside a context solid.** Test every sensor with `Brep.IsPointInside` against each closed object on the context layers. A podium extrusion that ran through the office held 642 sensors at 0 lx all year, which showed as a straight DA cut line. Context that was harmless for façade sensors outside the glass can still swallow interior floor sensors.
- Sensors inside furniture or columns (pantry counter, column stubs) also read 0 lx all year. Count the sensors whose occupied maximum is 0 and report them.

- Sanity-check a "0 %" ASE before reporting it: probe the direct `.npy` (max lux, sensors and hours above 1000 lx, hour-of-day histogram) and compute the sun azimuth/altitude at the brightest instant (`ladybug.sunpath.Sunpath(25.25, 55.33, 4)`). Bright spots must sit next to glass or under the skylight at a geometrically possible sun angle; otherwise look for a light leak. Here: NNE glass lit 07:00-09:00 Apr-Sep (mostly before occupancy), skylight 09:00-12:00 → worst 158 occupied h < 250 → ASE 0 %.
- Run time for reference: enhanced recipe, 20 threads.
  - 2,019 sensors (0.4 m) ≈ 7.5 min.
  - 7,993 sensors (0.2 m) ≈ 21 min.
  - The post-processing logs "Failed to load CuPy … falling back to NumPy" and a NumPy "invalid value in scalar divide" warning. Both are harmless; check the results for NaN anyway.
- Panels in GH: `AddPersistentData` *adds* to a param's default. A List Item `i` became [0, 0] and duplicated everything downstream. Use `PersistentData.Clear()` + `SetPersistentData(...)`.
- LB/HB components **reset their NickName** when they solve - find them by `Name`, wiring or a neighbouring panel, never by a nickname you set.

## Images (native, reusable)

- Radiation images: named view "Iso" (camera direction -1,-1,-1, parallel), display mode **EOC-Arctic**, 1134 × 783 px. Daylight plans use the same camera saved as named view **Iso_Daylight** (zoomed to the building + legend).
- Canvas chain (group "DAYLIGHT IMAGES (native capture)"): Value List "Daylight image" → Stream Filters (values flattened / legend parameters / legend title / file name) → Mesh Join of all grid meshes → one LB Spatial Heatmap → LB Capture View (`viewport_` = named view, `mode_` = EOC-Arctic, 2268 × 1566) ← Button.
- LB Spatial Heatmap needs flattened values + ONE joined mesh (a 15-branch value tree against a flat mesh list silently produced 4 meshes).
- Legend readable in a parallel view: LB Legend Parameters `base_plane_` = Construct Plane with X = screen right, Y = screen up. For camera direction d = (-1,-1,-1): X = d × Z = (-1, 1, 0), Y = (-1, -1, 2). Getting X backwards mirrors the text. Set `num_decimals_` 0.
- This .gh previews **"Selected only"** (`doc.PreviewFilter`). For a capture: set it to None (`System.Enum.Parse(GH_PreviewFilter, "None")` - `.None` is a Python syntax error), hide other previews, capture, then restore both.
- Before capturing, check the heatmap's own preview (`hm.Hidden` - the user saves it off) and that the .gh is the canvas's active document (only that one previews); set both, restore both afterwards.
- A freshly opened .gh with the run toggle False has **empty** recipe outputs. Do not set `_run` True (even `reload_old_` starts a queenbee run that can rebuild everything): for captures/bakes temporarily wire a panel with `<sim>nnual_daylight_enhancedesults` into the metric component's `_results` (HB Annual Sunlight Exposure accepts the folder), then rewire to the recipe and delete the panel.
- LB Capture View restores the named view into the **active** viewport and renames it; afterwards restore the user's view (`rd.NamedViews.Restore(FindByName("ISo_Context"), vp)`).
- Crop the captures to a common box with Pillow (drop the world-axes icon and stray points) so the images line up on the slide.
- Hide the baked heatmap layers before capturing, because they coincide with the GH preview. Keep legend labels short: 3D legend text can be hidden behind context walls in the iso view ("Non-daylit Area" was clipped, so it became "Not daylit").

## Baking heatmaps into the .3dm (native, like the radiation layers)

- Target layer: `HB Heatmaps::<model name>::<metric>` (radiation: `…::cumulative_radiation`; daylight: `DA300`, `sDA300_50`, `ASE1000_hours`, `ASE1000_250`). Each layer holds the coloured mesh, the legend mesh and TextDot labels, and stays hidden.
- Rhino 8 native **Model Object** (Rhino/Objects): `G` = heatmap mesh + legend mesh + dots, flattened; `L` = full layer path as text. Nested layers are created on bake. Bake from the right-click menu (code: `mo.BakeGeometry(rd, None, ids)`). Mesh vertex colours survive.
- Model Object **rejects LB legend text** ("3D Text is not a valid model geometry type"). Rebuild the labels natively instead:
  - List Item 0 of `legend` → Face Normals `C` (segment centres) → Move by plane X × (2 × seg width) → **Annotation Dot** (Rhino/Annotations).
  - The text comes from **LB Create Legend** `label_text`, fed the same values, legend parameters and title.
  - Title dot: last label point + plane Y × (2 × seg height).
- Group on canvas: "DAYLIGHT HEATMAPS -> RHINO LAYERS (native bake)". The value list picks the metric; a Stream Filter supplies the layer name; Merge(root, model name, metric) → Text Join "::".
- Re-baking adds new objects, so clear the layer first (the scribble says so).

## Deck

- Client deck: `PPT\<yymmdd> EOC vr Facade - Environmental Study.pptx` - always write a **new dated copy**; never overwrite.
- Drive PowerPoint with pywin32 (`win32com.client.Dispatch("PowerPoint.Application")`): `Slides(n).Duplicate()(1).MoveTo(k)` from a slide of the same type (images slide 5, table slide 8, assumptions slide 10), delete unneeded shapes, keep the placeholders (title = Text Placeholder 2, subtitle = 3, numbered italic note = 1, e.g. "7 · …").
- House style: Arial, slate text RGB int 7299670, table header fill 14999772, 1 pt slate borders, green "meets reference" fill read from slide 8's table, table style "No Style, Table Grid" `{5940675A-B579-460E-94D1-54222C63F5DA}`.
- Setting `TextRange.Text` on a copied key-points box turns bullets into numbers: reset `Bullet.Type = 1`, `Character = 8226`. Use a non-breaking space between a number and its unit.
- QA: `Slide.Export(png, "PNG", 1600, 900)` and look at every new slide (overflow into the EOC logo at bottom-left is the usual defect).
- Editing a key-points box: rewrite the whole box (`keypoints()` = `TextRange.Text = "\r".join(...)`, then bullets). Setting `Paragraphs(i).Text` adds blank paragraphs and shifts the indices.
- To swap an image, delete it, then `AddPicture(..., -1, -1)` → `LockAspectRatio`, set `Height`, and centre it in the old column. A new crop may have a different aspect ratio.
- In Python `%` formatting, every literal "0 %" in the string must be written "0 %%".
