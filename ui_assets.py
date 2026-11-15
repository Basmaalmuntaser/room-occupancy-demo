"""Visual assets for the Streamlit demo: colours, CSS, icons, the illustrated room and small HTML builders.

Everything is drawn locally with SVG/CSS (no external images). The room picture is an illustration only:
the AI never sees it, it only receives the 16 sensor readings through the API.
"""
import random

# ----------------------------------------------------------------------------------------------------------------
# Line icons (one consistent stroke style)
# ----------------------------------------------------------------------------------------------------------------
_PATHS = {
    "temp": '<path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>',
    "light": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 '
             '1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "sound": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>'
             '<path d="M19 5a10 10 0 0 1 0 14"/>',
    "co2": '<path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/>'
           '<path d="M17.7 7.7A2.5 2.5 0 1 1 19.5 12H2"/>',
    "motion": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "person": '<circle cx="12" cy="7" r="3.5"/><path d="M5 21c0-4.4 3-7 7-7s7 2.6 7 7"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "cross": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "up": '<line x1="7" y1="17" x2="17" y2="7"/><polyline points="8 7 17 7 17 16"/>',
    "flat": '<line x1="4" y1="12" x2="20" y2="12"/><polyline points="14 6 20 12 14 18"/>',
    "down": '<line x1="7" y1="7" x2="17" y2="17"/><polyline points="17 8 17 17 8 17"/>',
    "flame": '<path d="M12 22c4 0 7-2.7 7-7 0-3.5-2.2-6-4-8 .2 2.3-.9 3.6-2 4 0-3.5-1.5-6.4-4-9 .3 3.6-4 6.4-4 '
             '12 0 4.3 3 8 7 8z"/>',
    "lock": '<rect x="4.5" y="11" width="15" height="10" rx="2"/><path d="M8 11V7.5a4 4 0 0 1 8 0V11"/>',
}


def icon(name: str, size: int = 20, cls: str = "ic") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_PATHS[name]}</svg>')


LOGO = ('<svg class="logo" viewBox="0 0 64 64" fill="none" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true"><path d="M14 56V22l18-12 18 12v34" stroke="#d9a35f" stroke-width="3"/>'
        '<rect x="25" y="34" width="14" height="22" rx="2" stroke="#d9a35f" stroke-width="3"/>'
        '<circle cx="35.5" cy="46" r="1.6" fill="#d9a35f"/>'
        '<path d="M24 25a11 11 0 0 1 16 0" stroke="#3cc8b4" stroke-width="2.6"/>'
        '<path d="M28 29a5 5 0 0 1 8 0" stroke="#3cc8b4" stroke-width="2.6"/></svg>')


# ----------------------------------------------------------------------------------------------------------------
# The room (isometric illustration, same camera before and after the reveal)
# ----------------------------------------------------------------------------------------------------------------
C, S, H = 32.0, 18.5, 30.0      # iso step x / y / height in pixels per room unit
OX, OY = 400.0, 196.0           # screen position of the back floor corner
N, WALL = 8.0, 5.6              # floor size and wall height in room units


def P(x: float, y: float, z: float = 0.0):
    return OX + (x - y) * C, OY + (x + y) * S - z * H


def _pts(ps) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)


def _poly(ps, fill, extra="") -> str:
    return f'<polygon points="{_pts(ps)}" fill="{fill}" {extra}/>'


def _box(x0, y0, z0, dx, dy, dz, top, left, right, extra="") -> str:
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
    face_y = [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)]   # faces the viewer's left
    face_x = [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)]   # faces the viewer's right
    face_t = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
    return _poly(face_y, left, extra) + _poly(face_x, right, extra) + _poly(face_t, top, extra)


_DEFS = (
    '<defs>'
    '<linearGradient id="gWallL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d2e33"/>'
    '<stop offset="1" stop-color="#15232a"/></linearGradient>'
    '<linearGradient id="gWallR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#253a40"/>'
    '<stop offset="1" stop-color="#1b2c33"/></linearGradient>'
    '<linearGradient id="gFloor" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4a3424"/>'
    '<stop offset="1" stop-color="#2c1f17"/></linearGradient>'
    '<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d3a40"/>'
    '<stop offset="1" stop-color="#0a1d24"/></linearGradient>'
    '<linearGradient id="gDoorway" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffdca0"/>'
    '<stop offset="1" stop-color="#e5a457"/></linearGradient>'
    '<linearGradient id="gBeam" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3cc8b4" stop-opacity=".22"/>'
    '<stop offset="1" stop-color="#3cc8b4" stop-opacity="0"/></linearGradient>'
    '<radialGradient id="gWarm" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#ffd38a" stop-opacity=".30"/>'
    '<stop offset="1" stop-color="#ffd38a" stop-opacity="0"/></radialGradient>'
    '<radialGradient id="gLamp" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffe2a8" stop-opacity=".85"/>'
    '<stop offset="1" stop-color="#ffe2a8" stop-opacity="0"/></radialGradient>'
    '<radialGradient id="gMoon" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#e8fff8" stop-opacity=".9"/>'
    '<stop offset="1" stop-color="#8be8d8" stop-opacity="0"/></radialGradient>'
    '</defs>'
)


def _room_static() -> str:
    """Walls, floor and furniture. Identical in every round, so nothing here can give the answer away."""
    out = []
    # walls and floor
    out.append(_poly([P(0, 0, 0), P(0, N, 0), P(0, N, WALL), P(0, 0, WALL)], "url(#gWallL)"))
    out.append(_poly([P(0, 0, 0), P(N, 0, 0), P(N, 0, WALL), P(0, 0, WALL)], "url(#gWallR)"))
    out.append(_poly([P(0, 0, 0), P(N, 0, 0), P(N, N, 0), P(0, N, 0)], "url(#gFloor)"))
    for i in range(1, int(N)):  # floor planks
        a, b = P(i, 0, 0), P(i, N, 0)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#1d140e" '
                   f'stroke-opacity=".55" stroke-width="1"/>')
    # wall panelling lines + skirting + crown moulding (copper)
    out.append(_poly([P(0, 0, 0), P(0, N, 0), P(0, N, .32), P(0, 0, .32)], "#2a1c13"))
    out.append(_poly([P(0, 0, 0), P(N, 0, 0), P(N, 0, .32), P(0, 0, .32)], "#33231a"))
    for a, b in ((P(0, N, WALL), P(0, 0, WALL)), (P(0, 0, WALL), P(N, 0, WALL)),
                 (P(0, 0, 0), P(0, 0, WALL))):
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#b9824a" '
                   f'stroke-opacity=".55" stroke-width="1.6"/>')
    # window on the right wall + moon + light beam on the floor
    w = [P(2.6, 0, 2.0), P(5.4, 0, 2.0), P(5.4, 0, 4.5), P(2.6, 0, 4.5)]
    out.append(_poly(w, "url(#gSky)", 'stroke="#b9824a" stroke-width="3"'))
    m = P(4.55, 0, 3.75)
    out.append(f'<circle cx="{m[0]:.1f}" cy="{m[1]:.1f}" r="26" fill="url(#gMoon)"/>'
               f'<circle cx="{m[0]:.1f}" cy="{m[1]:.1f}" r="8" fill="#eafff9"/>')
    for a, b in ((P(4.0, 0, 2.0), P(4.0, 0, 4.5)), (P(2.6, 0, 3.25), P(5.4, 0, 3.25))):
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#b9824a" stroke-width="2.4"/>')
    out.append(_poly([P(2.6, 0, 1.92), P(5.4, 0, 1.92), P(5.5, .35, 1.92), P(2.5, .35, 1.92)], "#8a5c34"))  # sill
    out.append(_poly([P(2.6, 0, 0), P(5.4, 0, 0), P(6.6, 4.2, 0), P(3.8, 4.2, 0)], "url(#gBeam)"))
    # framed picture on the left wall
    f = [P(0, 4.5, 2.9), P(0, 6.5, 2.9), P(0, 6.5, 4.3), P(0, 4.5, 4.3)]
    out.append(_poly(f, "#13262b", 'stroke="#c58f55" stroke-width="3"'))
    out.append(_poly([P(0, 4.9, 3.1), P(0, 5.7, 3.1), P(0, 5.3, 3.9)], "#3cc8b4", 'opacity=".55"'))
    out.append(_poly([P(0, 5.4, 3.1), P(0, 6.2, 3.1), P(0, 5.8, 3.6)], "#d9a35f", 'opacity=".7"'))
    # rug
    out.append(_poly([P(2.0, 2.0), P(5.8, 2.0), P(5.8, 5.6), P(2.0, 5.6)], "#5b2f2a", 'stroke="#c58f55" stroke-width="2"'))
    out.append(_poly([P(2.45, 2.45), P(5.35, 2.45), P(5.35, 5.15), P(2.45, 5.15)], "none",
                     'stroke="#c58f55" stroke-opacity=".55" stroke-width="1.2" stroke-dasharray="6 5"'))
    # plant in the back corner
    out.append(_box(.35, .45, 0, .75, .75, .7, "#a8673a", "#7d4a29", "#93582f"))
    base = P(.72, .82, .72)
    leaves = [(-14, -26, -35), (12, -30, 30), (-4, -40, -5), (-22, -14, -60), (20, -16, 60)]
    for dx, dy, rot in leaves:
        out.append(f'<ellipse cx="{base[0] + dx:.1f}" cy="{base[1] + dy:.1f}" rx="7" ry="19" fill="#2f6b55" '
                   f'transform="rotate({rot} {base[0] + dx:.1f} {base[1] + dy:.1f})"/>')
    # bookshelf against the right wall
    out.append(_box(5.8, 0, 0, 2.0, .7, 3.8, "#3a2a1f", "#2a1d15", "#22170f"))
    colors = ["#c58f55", "#3cc8b4", "#e9dcc3", "#8f3f37", "#d9a35f", "#2b6f78", "#b98a4a", "#e9dcc3"]
    rnd = random.Random(7)
    for z in (.35, 1.5, 2.65):
        x = 5.95
        out.append(_poly([P(5.8, .7, z - .08), P(7.8, .7, z - .08), P(7.8, .7, z), P(5.8, .7, z)], "#4a3527"))
        while x < 7.55:
            w_ = rnd.uniform(.12, .2)
            h_ = rnd.uniform(.6, .95)
            out.append(_poly([P(x, .7, z), P(x + w_, .7, z), P(x + w_, .7, z + h_), P(x, .7, z + h_)],
                             rnd.choice(colors), 'opacity=".9"'))
            x += w_ + .03
    # desk + lamp against the left wall
    out.append(_box(0, 4.3, 1.3, 1.25, 2.8, .18, "#7a5232", "#5b3b23", "#4a2f1c"))
    for lx, ly in ((1.1, 4.4), (1.1, 6.95)):
        out.append(_box(lx, ly, 0, .1, .1, 1.3, "#5b3b23", "#4a2f1c", "#3b2516"))
    out.append(_box(.2, 4.6, 1.48, .55, .7, .08, "#e9dcc3", "#cbbd9f", "#b9ab8d"))  # notebook
    lb = P(.55, 6.4, 1.48)
    lt = P(.55, 6.4, 2.55)
    out.append(f'<line x1="{lb[0]:.1f}" y1="{lb[1]:.1f}" x2="{lt[0]:.1f}" y2="{lt[1]:.1f}" stroke="#c58f55" stroke-width="3"/>')
    out.append(f'<ellipse cx="{lb[0]:.1f}" cy="{lb[1]:.1f}" rx="9" ry="4" fill="#c58f55"/>')
    out.append(f'<path d="M{lt[0] - 14:.1f} {lt[1] + 6:.1f} L{lt[0] - 8:.1f} {lt[1] - 14:.1f} L{lt[0] + 8:.1f} '
               f'{lt[1] - 14:.1f} L{lt[0] + 14:.1f} {lt[1] + 6:.1f} Z" fill="#d9a35f"/>')
    # armchair (front right, away from where people stand)
    ax, ay = 6.0, 4.5
    out.append(_box(ax, ay, 0, 1.5, 1.5, .7, "#a9653c", "#7d4527", "#93542f"))
    out.append(_box(ax, ay, .7, .36, 1.5, 1.1, "#b8744a", "#8a4e2d", "#9d5b34"))
    out.append(_box(ax + .36, ay, .7, 1.14, .3, .46, "#b8744a", "#8a4e2d", "#9d5b34"))
    out.append(_box(ax + .36, ay + 1.2, .7, 1.14, .3, .46, "#b8744a", "#8a4e2d", "#9d5b34"))
    return "".join(out)


def _door(open_: bool) -> str:
    """Door on the left wall. Closed: a thin warm line under it. Open: lit doorway and the swung leaf."""
    y0, y1, top = 1.5, 3.3, 4.2
    frame = _poly([P(0, y0 - .12, 0), P(0, y1 + .12, 0), P(0, y1 + .12, top + .12), P(0, y0 - .12, top + .12)], "#b9824a")
    if not open_:
        leaf = _poly([P(0, y0, 0), P(0, y1, 0), P(0, y1, top), P(0, y0, top)], "#4a2f1d")
        panels = (_poly([P(0, y0 + .25, 2.35), P(0, y1 - .25, 2.35), P(0, y1 - .25, 3.9), P(0, y0 + .25, 3.9)], "#3b2516")
                  + _poly([P(0, y0 + .25, .35), P(0, y1 - .25, .35), P(0, y1 - .25, 2.0), P(0, y0 + .25, 2.0)], "#3b2516"))
        k = P(0, y1 - .3, 1.95)
        knob = f'<circle cx="{k[0]:.1f}" cy="{k[1]:.1f}" r="3.2" fill="#e0b46a"/>'
        a, b = P(.05, y0, .02), P(.05, y1, .02)
        glow = (f'<line class="gap" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#ffcf86" '
                f'stroke-width="3" stroke-linecap="round"/>')
        return f'<g class="door-closed">{frame}{leaf}{panels}{knob}{glow}</g>'
    doorway = _poly([P(0, y0, 0), P(0, y1, 0), P(0, y1, top), P(0, y0, top)], "url(#gDoorway)")
    spill = _poly([P(0, y0, 0), P(0, y1, 0), P(2.4, y1 + .9, 0), P(2.4, y0 + 1.2, 0)], "#ffd38a", 'opacity=".22"')
    leaf = _poly([P(0, y0, 0), P(1.45, y0 + .85, 0), P(1.45, y0 + .85, top), P(0, y0, top)], "#5a3a24")
    edge = _poly([P(1.45, y0 + .85, 0), P(1.53, y0 + .72, 0), P(1.53, y0 + .72, top), P(1.45, y0 + .85, top)], "#2f1d12")
    return f'<g class="door-open">{frame}{doorway}{spill}{leaf}{edge}</g>'


# Person figures: (coat, trousers, skin, hair)
_LOOKS = [("#2b8f87", "#1d2a30", "#e1b48c", "#2a1a12"),
          ("#c8813f", "#2a2522", "#9b6a49", "#16110d"),
          ("#e9dcc3", "#3a4a52", "#c99472", "#5a3a24")]
_SLOTS = {1: [(3.8, 3.8)], 2: [(3.0, 3.6), (4.6, 2.8)], 3: [(2.5, 3.9), (4.7, 2.5), (4.2, 4.2)]}


def _person(fx: float, fy: float, look, i: int) -> str:
    coat, pants, skin, hair = look
    s = (f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="19" ry="7" fill="#000" opacity=".35"/>'
         f'<rect x="{fx - 10:.1f}" y="{fy - 36:.1f}" width="8.5" height="36" rx="3.5" fill="{pants}"/>'
         f'<rect x="{fx + 1.5:.1f}" y="{fy - 36:.1f}" width="8.5" height="36" rx="3.5" fill="{pants}"/>'
         f'<rect x="{fx - 21:.1f}" y="{fy - 74:.1f}" width="8" height="35" rx="4" fill="{coat}" opacity=".85"/>'
         f'<rect x="{fx + 13:.1f}" y="{fy - 74:.1f}" width="8" height="35" rx="4" fill="{coat}" opacity=".85"/>'
         f'<rect x="{fx - 15:.1f}" y="{fy - 78:.1f}" width="30" height="46" rx="13" fill="{coat}"/>'
         f'<rect x="{fx - 4:.1f}" y="{fy - 84:.1f}" width="8" height="8" rx="3" fill="{skin}"/>'
         f'<circle cx="{fx:.1f}" cy="{fy - 94:.1f}" r="12" fill="{skin}"/>'
         f'<path d="M{fx - 12.5:.1f} {fy - 95:.1f} a12.5 12.5 0 0 1 25 0 q-6 -6 -12.5 -5 q-7 -1 -12.5 5z" fill="{hair}"/>')
    return f'<g class="pp" style="animation-delay:{.55 + i * .22:.2f}s">{s}</g>'


def room_scene(revealed: bool, people: int = 0, animate: bool = False, celebrate: bool = False,
               caption: str = "") -> str:
    """HTML for the room. Before the reveal it never depends on the answer (dark room, closed door, no people)."""
    room_outline = [P(0, N, WALL), P(0, 0, WALL), P(N, 0, WALL), P(N, 0, 0), P(N, N, 0), P(0, N, 0)]
    parts = [_DEFS, _room_static()]
    parts.append(_door(False))
    if revealed:
        parts.append(_door(True))
        lt = P(.55, 6.4, 2.45)
        parts.append(f'<circle class="lampglow" cx="{lt[0]:.1f}" cy="{lt[1]:.1f}" r="70" fill="url(#gLamp)"/>')
        parts.append(_poly(room_outline, "url(#gWarm)", 'class="warm"'))
        slots = sorted(_SLOTS.get(people, []), key=lambda p: p[0] + p[1])  # back to front
        for i, (x, y) in enumerate(slots):
            fx, fy = P(x, y, 0)
            parts.append(_person(fx, fy, _LOOKS[i % 3], i))
    parts.append(_poly(room_outline, "#03080a", 'class="dim"'))
    state = "lit" if revealed else "closed"
    motion = "anim" if (revealed and animate) else "still"
    svg = (f'<svg class="room" viewBox="40 0 720 500" role="img" aria-label="Illustrated room">{"".join(parts)}</svg>')
    confetti = _confetti() if (celebrate and animate) else ""
    cap = f'<div class="scene-cap">{caption}</div>' if caption else ""
    return f'<div class="scene {state} {motion}">{svg}{confetti}{cap}</div>'


def _confetti() -> str:
    rnd = random.Random()
    cols = ["#e0b46a", "#c8813f", "#f2e8d5", "#3cc8b4", "#f5d48f"]
    bits = []
    for _ in range(34):
        bits.append(f'<i style="left:{rnd.uniform(4, 96):.1f}%;background:{rnd.choice(cols)};'
                    f'animation-delay:{rnd.uniform(0, .5):.2f}s;--dx:{rnd.uniform(-60, 60):.0f}px;'
                    f'--r:{rnd.uniform(-540, 540):.0f}deg;width:{rnd.uniform(5, 9):.0f}px;height:{rnd.uniform(9, 15):.0f}px"></i>')
    return f'<div class="confetti" aria-hidden="true">{"".join(bits)}</div>'


# ----------------------------------------------------------------------------------------------------------------
# Answer cards
# ----------------------------------------------------------------------------------------------------------------
def guess_glyph(n: int) -> str:
    if n == 0:
        body = ('<rect x="34" y="6" width="28" height="38" rx="3" stroke-dasharray="4 4"/>'
                '<circle cx="56" cy="27" r="1.6" fill="currentColor"/>')
    else:
        xs = {1: [48], 2: [36, 60], 3: [26, 48, 70]}[n]
        body = "".join(f'<circle cx="{x}" cy="16" r="7"/><path d="M{x - 12} 44c0-9 5.5-14 12-14s12 5 12 14"/>'
                       for x in xs)
    return (f'<svg class="glyph" viewBox="0 0 96 48" fill="none" stroke="currentColor" stroke-width="2.2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def pick_card(n: int, label: str, selected: bool, locked: bool) -> str:
    cls = "pick" + (" sel" if selected else "") + (" lock" if locked else "")
    return f'<div class="{cls}">{guess_glyph(n)}<div class="pn">{n}</div><div class="pl">{label}</div></div>'


# ----------------------------------------------------------------------------------------------------------------
# Evidence panel (play tab)
# ----------------------------------------------------------------------------------------------------------------
TEMP = ["S1_Temp", "S2_Temp", "S3_Temp", "S4_Temp"]
LIGHT = ["S1_Light", "S2_Light", "S3_Light", "S4_Light"]
SOUND = ["S1_Sound", "S2_Sound", "S3_Sound", "S4_Sound"]
SLOPE_FLAT = 0.1
# visual scales for the meters (lo, hi, typical empty-room value) - just for drawing, not used by the model
SCALES = {"temp": (24.0, 27.0, 25.3), "light": (0.0, 200.0, 0.0), "sound": (0.0, 0.5, 0.07), "co2": (340.0, 1000.0, 355.0)}


def _avg(r, names) -> float:
    return sum(float(r[n]) for n in names) / len(names)


def _pct(v: float, lo: float, hi: float) -> float:
    return max(0.0, min(100.0, (v - lo) / (hi - lo) * 100))


def _meter(kind: str, v: float) -> str:
    lo, hi, ref = SCALES[kind]
    return (f'<div class="meter"><span class="mf" style="width:{_pct(v, lo, hi):.0f}%"></span>'
            f'<span class="mt" style="inset-inline-start:{_pct(ref, lo, hi):.0f}%"></span></div>')


def ltr(text: str) -> str:
    return f'<bdi dir="ltr">{text}</bdi>'


def trend_of(slope: float) -> int:
    return 0 if slope > SLOPE_FLAT else (2 if slope < -SLOPE_FLAT else 1)


def evidence_panel(r, t: dict) -> str:
    temp, light, sound, co2 = _avg(r, TEMP), _avg(r, LIGHT), _avg(r, SOUND), float(r["S5_CO2"])
    tr = trend_of(float(r["S5_CO2_Slope"]))
    pir = [int(round(float(r["S6_PIR"]))), int(round(float(r["S7_PIR"])))]
    rows = [
        ("temp", t["c_temp"], ltr(f'{temp:.1f}<small>°C</small>'), t["h_avg4"], _meter("temp", temp)),
        ("light", t["c_light"], ltr(f'{light:.0f}<small>lux</small>'), t["h_avg4"], _meter("light", light)),
        ("sound", t["c_sound"], ltr(f'{sound:.2f}<small>V</small>'), t["h_avg4v"], _meter("sound", sound)),
        ("co2", t["c_co2"], ltr(f'{co2:.0f}<small>ppm</small>'),
         f'<span class="trend">{icon(("up", "flat", "down")[tr], 15)}{t["trend"][tr]}</span>', _meter("co2", co2)),
        ("motion", t["c_motion"], t["motion_val"][1 if sum(pir) else 0],
         t["h_motion"].format(n=sum(pir)),
         '<div class="dots">' + "".join(f'<span class="d{" on" if p else ""}"></span>' for p in pir) + "</div>"),
    ]
    html = "".join(
        f'<div class="ev"><div class="evi">{icon(ic, 19)}</div><div class="evb"><div class="evh"><span class="evn">{name}'
        f'</span><span class="evv{" txt" if ic == "motion" else ""}">{val}</span></div><div class="evs">{sub}</div>{viz}</div></div>'
        for ic, name, val, sub, viz in rows)
    return (f'<div class="evidence"><div class="eyebrow">{t["evidence"]}</div>{html}'
            f'<div class="evnote"><span class="mt-key"></span>{t["evidence_note"]}</div></div>')


# ----------------------------------------------------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------------------------------------------------
FONTS = ("<style>@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&"
         "family=Tajawal:wght@400;500;700;800&family=Amiri:wght@700&display=swap');</style>")

CSS = """
<style>
:root{--ink:#0b1114;--ink2:#0f171b;--panel:#121c21;--panel2:#18252b;--ivory:#f2e8d5;--mute:#a69f8f;--dim:#6f7a78;
--copper:#c8813f;--gold:#e0b46a;--teal:#3cc8b4;--line:rgba(242,232,213,.10);--bad:#e07b6f;
--fd:'Playfair Display','Amiri',Georgia,'Times New Roman',serif}
.stApp{background:radial-gradient(1100px 520px at 12% -8%,rgba(60,200,180,.07),transparent 60%),
 radial-gradient(900px 520px at 100% 0%,rgba(200,129,63,.09),transparent 60%),var(--ink)}
.block-container{max-width:1240px;padding-top:1rem;padding-bottom:3rem}
header[data-testid="stHeader"]{background:transparent}
.brand{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.brand .logo{width:34px;height:34px;flex:0 0 34px}
.brand .bn{font-family:var(--fd);font-weight:800;font-size:1.25rem;color:var(--ivory);letter-spacing:.3px}
.status{display:inline-flex;align-items:center;gap:7px;font-size:.78rem;color:var(--mute);padding:3px 10px;border-radius:999px;
 background:rgba(242,232,213,.05)}
.status .dot{width:7px;height:7px;border-radius:50%;background:#4fd39b;box-shadow:0 0 8px #4fd39b}
.status.off .dot{background:var(--bad);box-shadow:0 0 8px var(--bad)}
.eyebrow{font-size:.74rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);font-weight:700}
/* scoreboard */
.scorebar{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;padding:8px 22px;border-radius:18px;
 background:linear-gradient(90deg,rgba(224,180,106,.10),rgba(18,28,33,.6) 35%,rgba(18,28,33,.6) 65%,rgba(60,200,180,.09));margin:4px 0 14px 0}
.sb-side{display:flex;align-items:baseline;gap:12px}
.sb-side.ai{justify-content:flex-end}
.sb-who{font-size:.8rem;letter-spacing:.2em;font-weight:800;color:var(--mute)}
.sb-pts{font-family:var(--fd);font-size:2.1rem;font-weight:800;line-height:1;color:var(--ivory)}
.sb-side.you .sb-pts{color:var(--gold)}.sb-side.ai .sb-pts{color:var(--teal)}
.sb-mid{text-align:center}
.sb-round{font-size:.74rem;letter-spacing:.22em;color:var(--mute);font-weight:700}
.sb-vs{font-family:var(--fd);font-size:1.05rem;color:var(--ivory);opacity:.8}
.streak{display:inline-flex;align-items:center;gap:5px;font-size:.78rem;color:var(--gold);font-weight:700;margin-top:2px}
.streak.zero{color:var(--dim)}
.sb-pts.pop{animation:pop .9s cubic-bezier(.2,1.6,.4,1) .9s both;text-shadow:0 0 18px rgba(224,180,106,.7)}
@keyframes pop{0%{transform:scale(1)}40%{transform:scale(1.45)}100%{transform:scale(1)}}
/* headline */
.headline{margin:0 0 6px 0}
.only-mobile{display:none}
.pick-q{margin:16px 0 8px 0}
.headline .ttl{font-family:var(--fd);font-size:2.15rem;font-weight:800;color:var(--ivory);line-height:1.15;margin-top:4px}
.headline .sub{color:var(--mute);margin-top:6px;font-size:1rem;line-height:1.55;max-width:46rem}
.headline.win .ttl{color:var(--gold);text-shadow:0 0 28px rgba(224,180,106,.35)}
.headline.anim .ttl{animation:fadeUp .6s ease .7s both}
/* scene */
.scene{position:relative;border-radius:24px;overflow:hidden;
 background:radial-gradient(circle at 50% 30%,#14232a 0%,#0c1418 70%);box-shadow:0 30px 60px -30px rgba(0,0,0,.7)}
.scene .room{display:block;width:100%;height:auto}
.scene .scene-cap{position:absolute;inset-inline-start:18px;bottom:14px;font-size:.74rem;color:var(--mute);opacity:.85;
 max-width:70%;line-height:1.4}
.scene.closed .dim{opacity:.62}
.scene.closed .gap{animation:gapGlow 2.6s ease-in-out infinite}
.scene.lit.still .dim{opacity:0}
.scene.lit.still .door-closed{opacity:0}
.scene.lit.anim .dim{animation:dimOut 1.1s ease .15s both}
.scene.lit.anim .door-closed{animation:fadeOut .45s ease .05s both}
.scene.lit.anim .door-open{animation:doorIn .6s ease .05s both}
.scene.lit.anim .warm,.scene.lit.anim .lampglow{animation:fadeIn 1.1s ease .2s both}
.scene.lit.anim .pp{animation:rise .55s cubic-bezier(.2,.8,.3,1) both}
@keyframes dimOut{from{opacity:.62}to{opacity:0}}
@keyframes fadeOut{to{opacity:0}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes doorIn{from{opacity:0}to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes gapGlow{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.confetti{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.confetti i{position:absolute;top:-16px;border-radius:2px;opacity:0;animation:fall 1.9s cubic-bezier(.25,.6,.4,1) forwards}
@keyframes fall{0%{opacity:1;transform:translate(0,0) rotate(0)}100%{opacity:0;transform:translate(var(--dx),520px) rotate(var(--r))}}
/* evidence */
.evidence{padding:4px 2px}
.ev{display:flex;gap:14px;padding:10px 0;border-bottom:1px solid var(--line)}
.ev:last-of-type{border-bottom:0}
.evi{width:38px;height:38px;flex:0 0 38px;border-radius:12px;display:flex;align-items:center;justify-content:center;
 background:rgba(224,180,106,.10);color:var(--gold)}
.evb{flex:1;min-width:0}
.evh{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.evn{color:var(--ivory);font-weight:600;font-size:.95rem}
.evv{font-family:var(--fd);font-size:1.45rem;font-weight:700;color:var(--ivory);white-space:nowrap}
.evv small{font-family:inherit;font-size:.8rem;color:var(--mute);margin-inline-start:4px;font-weight:600}
.evv.txt{font-size:1.05rem}
.evs{font-size:.8rem;color:var(--mute);margin-top:1px}
.trend{display:inline-flex;align-items:center;gap:4px;color:var(--teal);font-weight:600}
.meter{position:relative;height:5px;border-radius:999px;background:rgba(242,232,213,.08);margin-top:8px}
.meter .mf{position:absolute;inset-block:0;inset-inline-start:0;border-radius:999px;background:linear-gradient(90deg,var(--copper),var(--gold))}
.meter .mt{position:absolute;top:-4px;width:2px;height:13px;background:var(--teal);border-radius:2px}
.dots{display:flex;gap:8px;margin-top:8px}
.dots .d{width:12px;height:12px;border-radius:50%;background:rgba(242,232,213,.10)}
.dots .d.on{background:var(--gold);box-shadow:0 0 10px rgba(224,180,106,.8)}
.evnote{display:flex;align-items:center;gap:8px;font-size:.76rem;color:var(--dim);margin-top:8px}
.mt-key{width:2px;height:12px;background:var(--teal);border-radius:2px;display:inline-block}
/* answer cards (the transparent Streamlit button sits on top of each card) */
[class*="st-key-pickrow"] [data-testid="stHorizontalBlock"]{gap:12px}
[class*="st-key-pickc"]{position:relative}
[class*="st-key-pickb"]{position:absolute !important;inset:0;z-index:2;margin:0 !important}
[class*="st-key-pickb"] .stButton,[class*="st-key-pickb"] button{width:100%;height:100%;opacity:0;cursor:pointer}
.pick{border-radius:20px;padding:16px 10px 14px;text-align:center;color:var(--ivory);
 background:linear-gradient(180deg,rgba(242,232,213,.06),rgba(242,232,213,.02));box-shadow:inset 0 0 0 1px var(--line);
 transition:transform .18s ease,box-shadow .18s ease,background .18s ease}
.pick .glyph{width:84px;height:42px;color:var(--mute);transition:color .18s}
.pick .pn{font-family:var(--fd);font-size:2.3rem;font-weight:800;line-height:1.1;margin-top:4px}
.pick .pl{font-size:.82rem;color:var(--mute)}
[class*="st-key-pickc"]:hover .pick:not(.lock){transform:translateY(-3px);box-shadow:inset 0 0 0 1px rgba(224,180,106,.45),0 12px 30px -16px rgba(224,180,106,.6)}
[class*="st-key-pickc"]:hover .pick:not(.lock) .glyph{color:var(--gold)}
[class*="st-key-pickc"]:has(button:focus-visible) .pick{box-shadow:inset 0 0 0 2px var(--teal)}
.pick.sel{background:linear-gradient(180deg,rgba(224,180,106,.22),rgba(200,129,63,.10));
 box-shadow:inset 0 0 0 2px var(--gold),0 0 34px -8px rgba(224,180,106,.55)}
.pick.sel .glyph,.pick.sel .pn{color:var(--gold)}
.pick.lock{opacity:.35}
.pick.lock.sel{opacity:1}
/* result comparison */
.versus{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:6px 0 4px 0}
.vs-card{border-radius:18px;padding:14px 12px;text-align:center;background:rgba(242,232,213,.04)}
.vs-card .vl{font-size:.74rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mute);font-weight:700}
.vs-card .vv{font-family:var(--fd);font-size:1.5rem;font-weight:800;color:var(--ivory);margin-top:4px;display:flex;
 align-items:center;justify-content:center;gap:8px}
.vs-card .ok{color:#7fe0b0}.vs-card .no{color:var(--bad)}
.vs-card.truth{background:linear-gradient(180deg,rgba(60,200,180,.14),rgba(60,200,180,.04))}
.vs-card.truth .vv{color:var(--teal)}
.locked-chip{display:inline-flex;align-items:center;gap:10px;padding:10px 16px;border-radius:14px;background:rgba(224,180,106,.10);
 color:var(--gold);font-weight:700}
.locked-chip b{font-family:var(--fd);font-size:1.4rem}
.foot{font-size:.76rem;color:var(--dim);margin-top:26px;line-height:1.5}
/* prob bars */
.bars{display:flex;flex-direction:column;gap:9px;margin:6px 0}
.bar{display:grid;grid-template-columns:110px 1fr 56px;gap:12px;align-items:center;font-size:.9rem;color:var(--ivory)}
.bar .bt{height:8px;background:rgba(242,232,213,.08);border-radius:999px;overflow:hidden}
.bar .bf{height:100%;background:rgba(60,200,180,.45);border-radius:999px}
.bar.top .bf{background:var(--teal)}
.bar.top{font-weight:700}
.bar .bp{text-align:end;font-variant-numeric:tabular-nums;color:var(--mute)}
/* buttons */
.stButton>button{border-radius:14px;font-weight:700;padding:.55rem 1.2rem}
.stButton>button[kind="primary"]{background:linear-gradient(180deg,#e7bd74,#c8813f);color:#1a120b;border:0;
 box-shadow:0 10px 26px -12px rgba(224,180,106,.8)}
.stButton>button[kind="primary"]:hover{filter:brightness(1.07);color:#1a120b}
.stButton>button[kind="primary"]:disabled{background:rgba(242,232,213,.08);color:var(--dim);box-shadow:none}
/* tabs */
.stTabs [data-baseweb="tab-list"]{gap:22px}
.stTabs [data-baseweb="tab"] p{font-size:.95rem;font-weight:600}
/* lab + shared panels */
.step{display:flex;align-items:center;gap:10px;margin:28px 0 10px 0}
.step .n{width:26px;height:26px;border-radius:50%;background:rgba(224,180,106,.16);color:var(--gold);display:inline-flex;
 align-items:center;justify-content:center;font-weight:800;font-size:.85rem;flex:0 0 26px}
.step .t{font-family:var(--fd);font-size:1.3rem;font-weight:700;color:var(--ivory)}
.intro{border-radius:18px;padding:16px 18px;color:var(--ivory);line-height:1.6;background:rgba(60,200,180,.07)}
.intro b{color:var(--teal)}
.note{color:var(--mute);font-size:.86rem;line-height:1.55}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.tile{border-radius:18px;padding:14px 16px;background:rgba(242,232,213,.04);color:var(--ivory);display:flex;flex-direction:column;gap:4px}
.tile .tn{font-weight:700;color:var(--ivory)}
.tile .td{font-size:.86rem;color:var(--mute);line-height:1.45}
.tile .big{font-family:var(--fd);font-size:1.6rem;font-weight:800;color:var(--gold)}
.clues{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px}
.clue{border-radius:18px;padding:14px 16px;background:rgba(242,232,213,.04);color:var(--ivory);display:flex;flex-direction:column;gap:6px;min-width:0}
.clue .ch{display:flex;align-items:center;gap:9px;color:var(--gold);font-weight:700;font-size:.92rem}
.clue .ch .cn{color:var(--ivory)}
.clue .cv{font-family:var(--fd);font-size:1.55rem;font-weight:800;line-height:1.15;min-height:2.2rem;display:flex;align-items:center;flex-wrap:wrap}
.clue .cv small{font-family:inherit;font-size:.85rem;color:var(--mute);margin-inline-start:4px;font-weight:600}
.clue .cv.sm{font-size:1.15rem}
.clue .cd{font-size:.82rem;color:var(--mute);line-height:1.4}
.clue .cd b{color:var(--teal)}
.clue .cr{margin-top:auto;padding-top:9px;border-top:1px solid var(--line);font-size:.78rem;color:var(--teal);font-weight:600}
.result{border-radius:20px;padding:18px 20px;color:var(--ivory);background:linear-gradient(180deg,rgba(224,180,106,.12),rgba(224,180,106,.03))}
.result .rl{font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;color:var(--mute);font-weight:700}
.result .rv{font-family:var(--fd);font-size:2.2rem;font-weight:800;color:var(--gold);line-height:1.2}
.result .rc{margin-top:8px;font-size:.92rem;line-height:1.55}
.stale{border-radius:14px;padding:12px 16px;background:rgba(224,180,106,.10);color:var(--gold)}
.tbl-wrap{overflow-x:auto;border-radius:16px;background:rgba(242,232,213,.03);margin:8px 0 14px 0}
.stMarkdown table.tbl{width:100%;border-collapse:collapse;table-layout:fixed;margin:0;color:var(--ivory)}
.stMarkdown table.tbl th,.stMarkdown table.tbl td{padding:10px 14px;text-align:center;border:0;border-bottom:1px solid var(--line);
 font-variant-numeric:tabular-nums;white-space:nowrap;background:transparent}
.stMarkdown table.tbl th{color:var(--gold);font-weight:700;font-size:.86rem}
.stMarkdown table.tbl th:first-child,.stMarkdown table.tbl td:first-child{text-align:start;width:28%;font-weight:700}
.stMarkdown table.tbl tr:last-child td{border-bottom:0}
/* compare-with-typical (play tab) */
.cmp-row{padding:10px 0;border-bottom:1px solid var(--line)}
.cmp-h{display:flex;justify-content:space-between;align-items:baseline;gap:8px;color:var(--ivory);font-weight:600;font-size:.9rem;margin-bottom:8px}
.cmp-h small{color:var(--mute);font-weight:500}
.cmp-v{color:var(--mute);font-weight:500;font-size:.85rem;white-space:nowrap}
.cmp-v b{color:var(--gold);font-size:1rem}
.chips{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
.chip{border-radius:10px;padding:6px 4px;text-align:center;background:rgba(242,232,213,.05)}
.chip .cp{display:flex;align-items:center;justify-content:center;gap:3px;font-size:.72rem;color:var(--mute)}
.chip .cv{font-size:.92rem;font-weight:700;color:var(--ivory);font-variant-numeric:tabular-nums}
.chip.near{background:rgba(60,200,180,.16);box-shadow:inset 0 0 0 1px var(--teal)}
.chip.near .cv,.chip.near .cp{color:var(--teal)}
.cmp-note{font-size:.76rem;color:var(--dim);margin-top:10px;line-height:1.5}
/* splash */
.splash{position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;pointer-events:none;
 background:radial-gradient(circle at 50% 42%,#16252b 0%,#0b1114 62%);animation:sOut .6s ease 2.2s forwards}
.splash .si{display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center;padding:0 20px;animation:sIn .9s cubic-bezier(.2,.7,.2,1) both}
.splash .logo{width:96px;height:96px;filter:drop-shadow(0 0 24px rgba(224,180,106,.35))}
.splash .logo path,.splash .logo rect{stroke-dasharray:90;stroke-dashoffset:90;animation:sDraw 1.3s ease .25s forwards}
.splash .st{font-family:var(--fd);font-size:2.7rem;font-weight:800;color:var(--ivory);line-height:1.15}
.splash .sa{font-family:'Amiri',var(--fd);font-size:1.9rem;font-weight:700;color:var(--gold)}
.splash .ss{color:var(--mute);font-size:.95rem;letter-spacing:.2em;text-transform:uppercase}
@keyframes sIn{from{opacity:0;transform:translateY(14px) scale(.97)}to{opacity:1;transform:none}}
@keyframes sDraw{to{stroke-dashoffset:0}}
@keyframes sOut{to{opacity:0;visibility:hidden}}
@media (prefers-reduced-motion:reduce){
 .scene *,.headline .ttl,.sb-pts.pop,.splash,.splash *{animation-duration:.01s !important;animation-delay:0s !important;animation-iteration-count:1 !important}
 .splash{animation-delay:.8s !important;animation-duration:.2s !important}
 .confetti{display:none}.pick{transition:none}}
@media (max-width:640px){
 .only-mobile{display:block}.only-desktop{display:none}
 .headline .ttl{font-size:1.75rem}.scorebar{padding:10px 14px}.sb-pts{font-size:1.7rem}
 [class*="st-key-pickrow"] [data-testid="stHorizontalBlock"]{display:grid !important;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px !important}
 [class*="st-key-pickrow"] [data-testid="stColumn"]{width:auto !important;min-width:0 !important}
 .versus{gap:8px}.vs-card{padding:10px 6px}.vs-card .vl{font-size:.6rem;letter-spacing:.06em}.vs-card .vv{font-size:1.02rem;flex-direction:column;gap:2px}
 .scene .scene-cap{position:static;max-width:none;padding:0 16px 12px}.ev{padding:7px 0}.evi{width:32px;height:32px;flex-basis:32px}.evv{font-size:1.25rem}.bar{grid-template-columns:84px 1fr 48px}.splash .st{font-size:2rem}}
</style>
"""

RTL_CSS = ("<style>.stApp{direction:rtl;font-family:'Tajawal','Source Sans Pro',sans-serif}"
           ".stApp p,.stApp h1,.stApp h2,.stApp h3,.stApp li,.stApp label{text-align:right}"
           ":root{--fd:'Amiri','Playfair Display',Georgia,serif}"
           ".eyebrow,.sb-who,.sb-round,.vs-card .vl,.result .rl{letter-spacing:0}"
           ".bar .bp{text-align:start}.clue .cv{direction:ltr;justify-content:flex-end}"
           ".scene .room{direction:ltr}</style>")
