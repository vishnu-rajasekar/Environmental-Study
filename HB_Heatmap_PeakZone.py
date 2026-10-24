#! python3
"""HB_Heatmap_PeakZone.py - heatmap of the PEAK INCIDENT SOLAR [kW] per zone, for several overhang studies.

Run in Rhino 8 (ScriptEditor, or command: _-RunPythonScript "path\\HB_Heatmap_PeakZone.py").
Set up the view first (camera, layers); the script draws on top of it and captures it.

For every study folder and every zone it:
  1. reads the hourly sensor results (.ill, W/m2) and the sensor meshes + glazing faces (.hbjson),
  2. computes the zone's hourly incident solar  sum(a_i x I_i(t)) / sum(a_i) x A_glz  [W]
     (a_i = sensor face area, A_glz = real glazed area of the zone) and takes the maximum over the year,
     = PEAK INCIDENT SOLAR [kW], the same value as Summary table 1 / the D#### sheets 'Peak incident [kW]',
  3. colours every sensor (gradient) with  I_i(peak hour) x A_glz / 1000  [kW] = the zone's peak kW if the whole
     zone received this sensor's irradiance. The area-weighted mean of a zone's colours = the zone's peak kW.
     One kW legend for all studies.
  4. writes a column of zone labels (kW + peak hour); the worst-case zone of each study is red.

Zones are taken from the sensor-grid names '<zone>_<n>' (e.g. 'North_Pantry_0' -> 'North_Pantry').
Real glazed area per zone = the HB glazing faces (modifier GLASS_MODIFIER) assigned to the nearest zone sensors.
Layers:  HB Heatmaps::Peak per zone::<study>   (coloured zones + zone labels)
         HB Heatmaps::Peak per zone::Legend    (one kW legend for all studies, 0 .. rounded maximum)
"""
import os
import glob
import json
import math
import datetime

import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import System.Drawing as sd

# ------------------------------------------------------------------ settings
STUDIES = sorted(glob.glob(r"C:\Users\Vishnu\simulation\DFF-context-zones\Radiation_HB_Model_D*"))
RESULTS = r"annual_irradiance\results\total"     # sub-folder with the .ill files
GLASS_MODIFIER = "Transparent_Facade_Material"   # HB modifier of the glazing faces (for the real glazed area)
LEGEND_MAX = None        # None = highest sensor kW value of all studies, rounded up to ROUND_TO
ROUND_TO = 5             # rounding step for the automatic legend maximum [kW]
SEGMENTS = 10            # legend colours / steps
YEAR = 2026              # only used for the peak date in the labels
SHOW_LEGEND = True
SHOW_TITLE = True        # study name above the label column
LABEL_SIDE = 1           # +1 = label column right of the facade (as seen in the view), -1 = left
WORST_COLOUR = sd.Color.FromArgb(255, 0, 0)
LABEL_COLOUR = sd.Color.White
CAPTURE = True           # save one PNG per study from the active view
DISPLAY_MODE = "Shaded"  # vertex colours need Shaded / Rendered
IMAGE_FOLDER = r"C:\LocalDev\DFF - Robotic Lab Expansion\Heatmaps\Peak per zone"
IMAGE_SIZE = (1920, 1080)
ROOT_LAYER = "HB Heatmaps::Peak per zone"
# Ladybug default legend colours (low -> high)
COLOURS = [(75, 107, 169), (115, 147, 202), (170, 200, 247), (193, 213, 208), (245, 239, 103),
           (252, 230, 74), (239, 156, 21), (234, 123, 0), (234, 74, 0), (234, 38, 0)]
# ---------------------------------------------------------------------------

doc = sc.doc


# ---------------- colours ----------------
def colour_at(t):
    t = min(max(t, 0.0), 1.0) * (len(COLOURS) - 1)
    i = min(int(t), len(COLOURS) - 2)
    f = t - i
    a, b = COLOURS[i], COLOURS[i + 1]
    return sd.Color.FromArgb(*[int(round(a[k] + (b[k] - a[k]) * f)) for k in range(3)])


def colour_for(value, vmax):
    """Stepped colour so the mesh matches the legend bands exactly."""
    step = min(int(max(value, 0.0) / vmax * SEGMENTS), SEGMENTS - 1) if vmax > 0 else 0
    return colour_at((step + 0.5) / SEGMENTS)


def nice_max(v):
    """Highest value rounded up to the next multiple of ROUND_TO (e.g. 23.8 kW -> 25 kW)."""
    return max(ROUND_TO, math.ceil(v / float(ROUND_TO)) * ROUND_TO)


# ---------------- geometry helpers ----------------
def zone_of(grid_name):
    return grid_name.rsplit("_", 1)[0] if "_" in grid_name else grid_name


def face_area(verts, f):
    p = [verts[i] for i in f]
    a = 0.5 * rg.Vector3d.CrossProduct(p[1] - p[0], p[2] - p[0]).Length
    if len(p) == 4:
        a += 0.5 * rg.Vector3d.CrossProduct(p[2] - p[0], p[3] - p[0]).Length
    return a


def polygon_area_centroid(pts):
    """Area (Newell) and vertex centroid of a planar polygon given as [[x,y,z], ...]."""
    nx = ny = nz = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1, z1 = pts[i]; x2, y2, z2 = pts[(i + 1) % n]
        nx += (y1 - y2) * (z1 + z2); ny += (z1 - z2) * (x1 + x2); nz += (x1 - x2) * (y1 + y2)
    c = rg.Point3d(sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n)
    return 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz), c


def glass_faces(model):
    """All faces (incl. faces of rooms) whose radiance modifier is the glazing modifier."""
    faces = list(model.get("faces", [])) + list(model.get("orphaned_faces", []))
    for room in model.get("rooms", []):
        faces += room.get("faces", [])
    out = []
    for f in faces:
        mod = f.get("properties", {}).get("radiance", {}).get("modifier")
        if mod == GLASS_MODIFIER:
            out.append(f["geometry"]["boundary"])
    return out


# ---------------- reading ----------------
def load_study(folder):
    hbjson = glob.glob(os.path.join(folder, "*.hbjson"))[0]
    model = json.load(open(hbjson))
    scale = Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Meters, doc.ModelUnitSystem)
    res = os.path.join(folder, RESULTS)
    hoys = [float(x) for x in open(os.path.join(res, "sun-up-hours.txt")).read().split()]
    grids = []
    for g in model["properties"]["radiance"]["sensor_grids"]:
        ill = os.path.join(res, g["identifier"] + ".ill")
        if not os.path.isfile(ill) or not g.get("mesh"):
            print("  skipped {} (no .ill or mesh)".format(g["identifier"]))
            continue
        name = g.get("display_name", g["identifier"])
        verts = [rg.Point3d(v[0] * scale, v[1] * scale, v[2] * scale) for v in g["mesh"]["vertices"]]
        grids.append({"name": name, "zone": zone_of(name), "ill": ill, "verts": verts, "faces": g["mesh"]["faces"],
                      "areas": [face_area(verts, f) for f in g["mesh"]["faces"]],
                      "sensors": [rg.Point3d(*[c * scale for c in s["pos"]]) for s in g["sensors"]]})
    order = []
    for g in grids:
        if g["zone"] not in order:
            order.append(g["zone"])
    # real glazed area per zone: each glazing face goes to the zone of its nearest sensor
    glz = dict((z, 0.0) for z in order)
    for boundary in glass_faces(model):
        area, c = polygon_area_centroid(boundary)
        c = rg.Point3d(c.X * scale, c.Y * scale, c.Z * scale)
        best = min(((c.DistanceTo(p), g["zone"]) for g in grids for p in g["sensors"]), key=lambda t: t[0])
        glz[best[1]] += area * scale * scale
    # pass 1: zone sum(a_i * I_i(t)) per sun-up hour
    zsum = dict((z, [0.0] * len(hoys)) for z in order)
    for g in grids:
        acc = zsum[g["zone"]]
        with open(g["ill"]) as fh:
            for a, line in zip(g["areas"], fh):
                for t, v in enumerate(line.split()):
                    if v != "0" and v != "0.0":
                        acc[t] += a * float(v)
    peak = dict((z, max(range(len(hoys)), key=lambda t: s[t])) for z, s in zsum.items())
    # pass 2: each sensor's irradiance at its zone's peak hour -> zone-equivalent kW
    for g in grids:
        col = peak[g["zone"]]
        with open(g["ill"]) as fh:
            g["values"] = [float(line.split()[col]) * glz[g["zone"]] / 1000.0 for line in fh]
    zones = {}
    for z in order:
        sa = sum(sum(g["areas"]) for g in grids if g["zone"] == z)
        mean = zsum[z][peak[z]] / sa                                  # W/m2 at the peak hour
        when = datetime.datetime(YEAR, 1, 1) + datetime.timedelta(hours=math.floor(hoys[peak[z]]))
        zones[z] = {"mean": mean, "glazed": glz[z], "kw": mean * glz[z] / 1000.0, "when": when.strftime("%d-%b %H:00")}
    return {"name": os.path.basename(folder.rstrip("\\/")), "grids": grids, "zones": zones, "order": order}


# ---------------- Rhino helpers ----------------
def layer_index(path, colour=sd.Color.Black):
    idx = doc.Layers.FindByFullPath(path, -1)
    if idx >= 0:
        return idx
    parent = None
    for part in path.split("::"):
        full = part if parent is None else doc.Layers[parent].FullPath + "::" + part
        idx = doc.Layers.FindByFullPath(full, -1)
        if idx < 0:
            lay = Rhino.DocObjects.Layer(); lay.Name = part; lay.Color = colour
            if parent is not None:
                lay.ParentLayerId = doc.Layers[parent].Id
            idx = doc.Layers.Add(lay)
        parent = idx
    return parent


def clear_layer(idx):
    for o in doc.Objects.FindByLayer(doc.Layers[idx]) or []:
        doc.Objects.Delete(o, True)


def attr_on(idx, name=None, colour=None):
    a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = idx
    if name: a.Name = name
    if colour is not None:
        a.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject; a.ObjectColor = colour
    return a


def coloured_mesh(verts, faces, values, vmax):
    """One colour per sensor face (stepped to the legend bands)."""
    m = rg.Mesh()
    for f, v in zip(faces, values):
        c = colour_for(v, vmax)
        ids = []
        for vi in f:
            ids.append(m.Vertices.Add(verts[vi])); m.VertexColors.Add(c)
        if len(ids) == 4: m.Faces.AddFace(ids[0], ids[1], ids[2], ids[3])
        else: m.Faces.AddFace(ids[0], ids[1], ids[2])
    m.Normals.ComputeNormals()
    return m


def view_frame(view, bbox):
    """Camera axes and the extents of bbox projected on them (screen-aligned layout)."""
    cam = view.ActiveViewport.GetCameraFrame()[1] if view else rg.Plane.WorldZX
    xa, ya = cam.XAxis, cam.YAxis
    c = bbox.Center
    pts = bbox.GetCorners()
    return xa, ya, c, min((p - c) * xa for p in pts), max((p - c) * xa for p in pts), \
        min((p - c) * ya for p in pts), max((p - c) * ya for p in pts)


def add_legend(idx, bbox, view, vmax):
    xa, ya, c, left, right, bottom, top = view_frame(view, bbox)
    h = max((top - bottom) * 0.8, 0.5); w = h * 0.06
    corner = c + xa * (left - 0.25 * (right - left) * 0.3 - w * 4) + ya * bottom   # left of the facade
    if ya.Z > 1e-6 and corner.Z < bbox.Min.Z:
        corner += ya * ((bbox.Min.Z - corner.Z) / ya.Z)
    step = h / SEGMENTS
    for s in range(SEGMENTS):
        o = corner + ya * (s * step)
        seg = rg.Mesh()
        for p in (o, o + xa * w, o + xa * w + ya * step, o + ya * step):
            seg.Vertices.Add(p); seg.VertexColors.Add(colour_at((s + 0.5) / SEGMENTS))
        seg.Faces.AddFace(0, 1, 2, 3)
        doc.Objects.AddMesh(seg, attr_on(idx))
    for s in range(SEGMENTS + 1):
        doc.Objects.AddTextDot(rg.TextDot("{:g}".format(vmax * s / SEGMENTS), corner + xa * (w * 2.5) + ya * (s * step)), attr_on(idx))
    doc.Objects.AddTextDot(rg.TextDot("Peak incident solar [kW] (zone-equivalent)", corner + ya * (h + step * 1.2)), attr_on(idx))


def add_labels(idx, study, bbox, view):
    """Column of zone labels beside the facade, in facade order; worst-case zone in red."""
    xa, ya, c, left, right, bottom, top = view_frame(view, bbox)
    n = len(study["order"])
    worst = max(study["order"], key=lambda z: study["zones"][z]["kw"])
    gap = (top - bottom) / max(n, 1) * 0.9
    x = (right + 0.12 * (right - left)) if LABEL_SIDE > 0 else (left - 0.12 * (right - left))
    y0 = bottom + (top - bottom) * 0.5 + gap * (n - 1) / 2.0
    for k, z in enumerate(study["order"]):
        d = study["zones"][z]
        text = "{}\n{:.2f} kW @ {}".format(z, d["kw"], d["when"])
        dot = rg.TextDot(text, c + xa * x + ya * (y0 - k * gap))
        dot.FontHeight = 14
        doc.Objects.AddTextDot(dot, attr_on(idx, z, WORST_COLOUR if z == worst else LABEL_COLOUR))
    if SHOW_TITLE:
        t = rg.TextDot("{}  -  peak incident solar per zone".format(study["name"]), c + xa * x + ya * (y0 + gap))
        t.FontHeight = 14
        doc.Objects.AddTextDot(t, attr_on(idx, "title", LABEL_COLOUR))


# ------------------------------------------------------------------ main
studies = []
for f in STUDIES:
    print("reading " + f)
    studies.append(load_study(f))
vmax_data = max(v for s in studies for g in s["grids"] for v in g["values"])
vmax = LEGEND_MAX if LEGEND_MAX else nice_max(vmax_data)
print("highest sensor value {:.2f} kW -> legend 0 - {:g} kW".format(vmax_data, vmax))

view = doc.Views.ActiveView
mode = Rhino.Display.DisplayModeDescription.FindByName(DISPLAY_MODE)
if view and mode:
    view.ActiveViewport.DisplayMode = mode
bbox_all = rg.BoundingBox.Empty
layers = []
for s in studies:
    idx = layer_index("{}::{}".format(ROOT_LAYER, s["name"]))
    clear_layer(idx)
    bbox = rg.BoundingBox.Empty
    for g in s["grids"]:
        m = coloured_mesh(g["verts"], g["faces"], g["values"], vmax)
        bbox.Union(m.GetBoundingBox(True))
        doc.Objects.AddMesh(m, attr_on(idx, g["name"]))
    bbox_all.Union(bbox)
    add_labels(idx, s, bbox, view)
    layers.append((s["name"], idx))
    print("{}: ".format(s["name"]) + " | ".join("{} {:.2f} kW (A_glz {:.2f} m2) @ {}".format(
        z, s["zones"][z]["kw"], s["zones"][z]["glazed"], s["zones"][z]["when"]) for z in s["order"]))

leg = layer_index(ROOT_LAYER + "::Legend")
clear_layer(leg)
if SHOW_LEGEND:
    add_legend(leg, bbox_all, view, vmax)

if CAPTURE and view:
    if not os.path.isdir(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
    for name, idx in layers:
        for _, other in layers:
            doc.Layers[other].IsVisible = (other == idx); doc.Layers[other].CommitChanges()
        doc.Layers[leg].IsVisible = SHOW_LEGEND; doc.Layers[leg].CommitChanges()
        doc.Views.Redraw()
        vc = Rhino.Display.ViewCapture()
        vc.Width, vc.Height = IMAGE_SIZE
        vc.ScaleScreenItems = False; vc.DrawAxes = False; vc.DrawGrid = False; vc.TransparentBackground = False
        bmp = vc.CaptureToBitmap(view)
        path = os.path.join(IMAGE_FOLDER, "{}_peak_per_zone.png".format(name))
        bmp.Save(path, sd.Imaging.ImageFormat.Png)
        print("saved " + path)
    for _, idx in layers:
        doc.Layers[idx].IsVisible = True; doc.Layers[idx].CommitChanges()
doc.Views.Redraw()
