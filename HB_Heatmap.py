#! python3
"""HB_Heatmap.py - colour Honeybee sensor-grid meshes from simulation result files.

Run in Rhino 8 (ScriptEditor, or command: _-RunPythonScript "path\\HB_Heatmap.py").

For every study folder it reads
    <study>\\<model>.hbjson                                  sensor-grid meshes (one face per sensor)
    <study>\\annual_irradiance\\metrics\\<METRIC>\\<grid>.res   one value per sensor
    <study>\\annual_irradiance\\metrics\\<METRIC>\\vis_metadata.json   unit
and adds a coloured mesh + legend on layer  HB Heatmaps::<study>::<METRIC>.
All studies share one legend range, so the images are directly comparable.
Optionally it saves one PNG per study from the chosen view.
"""
import os
import glob
import json

import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import System.Drawing as sd

# ------------------------------------------------------------------ settings
STUDIES = sorted(glob.glob(r"C:\Users\Vishnu\simulation\DFF-context-zones\Radiation_HB_Model_D*"))
# e.g. add the cube baseline:  STUDIES += [r"C:\Users\Vishnu\simulation\DFF-context\Radiation_Cube_1m_Ground035"]
METRIC = "cumulative_radiation"      # "cumulative_radiation" (kWh/m2), "peak_irradiance" (W/m2), "average_irradiance" (W/m2)
# Legend and colours replicate the native GH group 'CUMULATIVE HEATMAP (native)' (LB Spatial Heatmap):
LEGEND_MIN = 0                       # None = common minimum of all studies
LEGEND_MAX = 500                     # None = common maximum of all studies
SEGMENTS = 11                        # legend segments = LB 'seg_count_' (labels at min + i*(max-min)/(SEGMENTS-1))
CAPTURE = True                       # save one PNG per study
VIEW_NAME = None                     # named view to restore before capturing (None = active view)
IMAGE_FOLDER = r"C:\LocalDev\DFF - Robotic Lab Expansion\Heatmaps"
IMAGE_SIZE = (1920, 1080)
# Ladybug default legend colours (low -> high)
COLOURS = [(75, 107, 169), (115, 147, 202), (170, 200, 247), (193, 213, 208), (245, 239, 103),
           (252, 230, 74), (239, 156, 21), (234, 123, 0), (234, 74, 0), (234, 38, 0)]
# ---------------------------------------------------------------------------

doc = sc.doc


def colour_at(t):
    """Continuous colour along the Ladybug gradient, t in [0, 1]."""
    t = min(max(t, 0.0), 1.0) * (len(COLOURS) - 1)
    i = min(int(t), len(COLOURS) - 2)
    f = t - i
    a, b = COLOURS[i], COLOURS[i + 1]
    return sd.Color.FromArgb(*[int(round(a[k] + (b[k] - a[k]) * f)) for k in range(3)])


def colour_for(value, vmin, vmax):
    """Continuous colour, identical to Ladybug's ColorRange(colors, (min, max)) used by LB Spatial Heatmap:
    the 10 colours are spread evenly over min..max and blended linearly; values outside are clamped."""
    t = 0.0 if vmax <= vmin else (value - vmin) / (vmax - vmin)
    return colour_at(t)


def load_study(folder):
    """Return (name, unit, [(grid_id, vertices, faces, values)])."""
    hbjson = glob.glob(os.path.join(folder, "*.hbjson"))
    if not hbjson:
        raise IOError("no .hbjson in " + folder)
    model = json.load(open(hbjson[0]))
    scale = Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Meters, doc.ModelUnitSystem) \
        if model.get("units", "Meters") == "Meters" else 1.0
    mdir = os.path.join(folder, "annual_irradiance", "metrics", METRIC)
    unit = ""
    meta = os.path.join(mdir, "vis_metadata.json")
    if os.path.isfile(meta):
        unit = json.load(open(meta)).get("unit", "")
    grids = []
    for g in model["properties"]["radiance"].get("sensor_grids", []):
        res = os.path.join(mdir, g["identifier"] + ".res")
        if not os.path.isfile(res) or not g.get("mesh"):
            print("skipped grid {} (no .res or no mesh)".format(g["identifier"]))
            continue
        values = [float(v) for v in open(res).read().split()]
        mesh = g["mesh"]
        if len(values) != len(mesh["faces"]):
            print("skipped grid {}: {} values vs {} faces".format(g["identifier"], len(values), len(mesh["faces"])))
            continue
        verts = [rg.Point3d(v[0] * scale, v[1] * scale, v[2] * scale) for v in mesh["vertices"]]
        grids.append((g["identifier"], verts, mesh["faces"], values))
    return os.path.basename(folder.rstrip("\\/")), unit, grids


def coloured_mesh(verts, faces, values, vmin, vmax):
    m = rg.Mesh()
    for f, v in zip(faces, values):
        c = colour_for(v, vmin, vmax)
        idx = []
        for vi in f:
            idx.append(m.Vertices.Add(verts[vi]))
            m.VertexColors.Add(c)
        if len(idx) == 4:
            m.Faces.AddFace(idx[0], idx[1], idx[2], idx[3])
        else:
            m.Faces.AddFace(idx[0], idx[1], idx[2])
    m.Normals.ComputeNormals()
    return m


def layer_index(path, colour=sd.Color.Black):
    idx = doc.Layers.FindByFullPath(path, -1)
    if idx >= 0:
        return idx
    parent = None
    for part in path.split("::"):
        full = part if parent is None else doc.Layers[parent].FullPath + "::" + part
        idx = doc.Layers.FindByFullPath(full, -1)
        if idx < 0:
            lay = Rhino.DocObjects.Layer()
            lay.Name = part
            lay.Color = colour
            if parent is not None:
                lay.ParentLayerId = doc.Layers[parent].Id
            idx = doc.Layers.Add(lay)
        parent = idx
    return parent


def clear_layer(idx):
    for o in doc.Objects.FindByLayer(doc.Layers[idx]) or []:
        doc.Objects.Delete(o, True)


def add_legend(idx, bbox, view, vmin, vmax, unit, title):
    """Stepped legend bar next to the heatmap, facing the given view."""
    cam = view.ActiveViewport.GetCameraFrame()[1] if view else rg.Plane.WorldZX
    xa, ya = cam.XAxis, cam.YAxis
    # place the bar just right of the heatmap as seen from the view, bottom aligned with it
    c = bbox.Center
    corners = bbox.GetCorners()
    right = max((p - c) * xa for p in corners)
    bottom = min((p - c) * ya for p in corners)
    top = max((p - c) * ya for p in corners)
    h = max(top - bottom, 0.5)
    w = h * 0.06
    corner = c + xa * (right + 0.08 * h) + ya * bottom
    if ya.Z > 1e-6 and corner.Z < bbox.Min.Z:          # keep the bar above the ground plane
        corner += ya * ((bbox.Min.Z - corner.Z) / ya.Z)
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = idx
    # like LB: SEGMENTS boxes, each coloured at its segment number min + i*(max-min)/(SEGMENTS-1)
    step = h / SEGMENTS
    for s in range(SEGMENTS):
        o = corner + ya * (s * step)
        seg = rg.Mesh()
        for p in (o, o + xa * w, o + xa * w + ya * step, o + ya * step):
            seg.Vertices.Add(p)
            seg.VertexColors.Add(colour_at(s / float(SEGMENTS - 1)))
        seg.Faces.AddFace(0, 1, 2, 3)
        doc.Objects.AddMesh(seg, attr)
        val = vmin + (vmax - vmin) * s / float(SEGMENTS - 1)
        doc.Objects.AddTextDot(rg.TextDot("{:.0f}".format(val), corner + xa * (w * 2.5) + ya * (s * step + step * 0.5)), attr)
    doc.Objects.AddTextDot(rg.TextDot("{}  [{}]".format(title, unit), corner + ya * (h + step * 1.2)), attr)


# ------------------------------------------------------------------ main
studies = [load_study(f) for f in STUDIES]
all_vals = [v for _, _, grids in studies for g in grids for v in g[3]]
if not all_vals:
    raise ValueError("no results found - check STUDIES and METRIC")
vmin = min(all_vals) if LEGEND_MIN is None else LEGEND_MIN
vmax = max(all_vals) if LEGEND_MAX is None else LEGEND_MAX
print("legend range {:.1f} - {:.1f}".format(vmin, vmax))

view = doc.Views.ActiveView
if VIEW_NAME:
    i = doc.NamedViews.FindByName(VIEW_NAME)
    if i >= 0:
        doc.NamedViews.Restore(i, view.ActiveViewport)

layers = []
for name, unit, grids in studies:
    idx = layer_index("HB Heatmaps::{}::{}".format(name, METRIC))
    clear_layer(idx)
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = idx
    bbox = rg.BoundingBox.Empty
    for gid, verts, faces, values in grids:
        m = coloured_mesh(verts, faces, values, vmin, vmax)
        bbox.Union(m.GetBoundingBox(True))
        attr.Name = gid
        doc.Objects.AddMesh(m, attr)
    add_legend(idx, bbox, view, vmin, vmax, unit, "{} - {}".format(name, METRIC))
    layers.append((name, idx))
    print("{}: {} grids coloured".format(name, len(grids)))

if CAPTURE and view:
    if not os.path.isdir(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
    for name, idx in layers:
        for other_name, other in layers:           # show only this study's heatmap
            lay = doc.Layers[other]
            lay.IsVisible = (other == idx)
            lay.CommitChanges()
        doc.Views.Redraw()
        vc = Rhino.Display.ViewCapture()
        vc.Width, vc.Height = IMAGE_SIZE
        vc.ScaleScreenItems = False
        vc.DrawAxes = False
        vc.DrawGrid = False
        vc.TransparentBackground = False
        bmp = vc.CaptureToBitmap(view)
        path = os.path.join(IMAGE_FOLDER, "{}_{}.png".format(name, METRIC))
        bmp.Save(path, sd.Imaging.ImageFormat.Png)
        print("saved " + path)
    for name, idx in layers:
        doc.Layers[idx].IsVisible = True
        doc.Layers[idx].CommitChanges()
doc.Views.Redraw()
