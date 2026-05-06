"""Shared layout helpers for all arch-flow templates."""

from manim import *

NODE_FILLS = {
    "document": "#FFF3E0", "process": "#E8EAF6", "database": "#E8F5E9",
    "cloud": "#E3F2FD", "api": "#FFF8E1", "user": "#FCE4EC",
    "queue": "#E0F7FA", "default": "#E8EAF6",
}
NODE_ACCENTS = {
    "document": "#E65100", "process": "#283593", "database": "#2E7D32",
    "cloud": "#1565C0", "api": "#F57F17", "user": "#C2185B",
    "queue": "#00838F", "default": "#283593",
}
NODE_ICONS = {
    "document": "📄", "process": "⚙", "database": "🗄",
    "cloud": "☁", "api": "🔌", "user": "👤", "queue": "📨", "default": "●",
}

# Canvas constants
CANVAS_W = 14.2
CANVAS_H = 8.0
MARGIN = 1.0
TITLE_H = 0.8
TITLE_COLOR = "#4CAF50"
ARROW_COLOR = "#9E9E9E"
STEP_BG = "#FFC107"
DOT_COLOR = "#42A5F5"
TEXT_COLOR = "#212121"
BG_COLOR = "#FAFAFA"


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def label_font_size(label, max_width=2.4, base_size=16):
    """Shrink font size if label is too long."""
    if len(label) <= 8:
        return base_size
    elif len(label) <= 12:
        return base_size - 2
    elif len(label) <= 16:
        return base_size - 4
    else:
        return base_size - 6


def node_width(label, base=2.4):
    """Calculate node width based on label length."""
    chars = len(label)
    if chars <= 6:
        return base
    elif chars <= 10:
        return base + 0.4
    elif chars <= 14:
        return base + 0.8
    else:
        return base + 1.2


def build_node(node, scale=1.0):
    """Build a styled node with shadow, body, icon, label."""
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])
    fill = hex_to_color(NODE_FILLS.get(node_type, NODE_FILLS["default"]))
    accent = hex_to_color(NODE_ACCENTS.get(node_type, NODE_ACCENTS["default"]))

    w = node_width(label) * scale
    h = 1.3 * scale
    fs = label_font_size(label) * scale

    shadow = RoundedRectangle(
        width=w, height=h, corner_radius=0.2,
        fill_color=BLACK, fill_opacity=0.06, stroke_width=0,
    ).shift(DOWN * 0.05 + RIGHT * 0.05)

    body = RoundedRectangle(
        width=w, height=h, corner_radius=0.2,
        fill_color=fill, fill_opacity=1.0,
        stroke_color=hex_to_color("#E0E0E0"), stroke_width=1.5,
    )

    icon = Text(NODE_ICONS.get(node_type, "●"), font_size=int(20 * scale), color=accent)
    icon.move_to(body.get_left() + RIGHT * 0.4 * scale + UP * 0.02)

    txt = Text(label, font_size=int(fs), color=hex_to_color(TEXT_COLOR), weight=BOLD)
    txt.move_to(body.get_center() + RIGHT * 0.12 * scale + DOWN * 0.04)

    return VGroup(shadow, body, icon, txt), w


def add_title(self, title_text):
    """Render the green title bar at top. Returns title group."""
    title_bg = Rectangle(
        width=CANVAS_W, height=TITLE_H,
        fill_color=hex_to_color(TITLE_COLOR), fill_opacity=1.0,
        stroke_width=0,
    ).to_edge(UP, buff=0)

    title = Text(title_text, font_size=30, color=WHITE, weight=BOLD)
    title.move_to(title_bg.get_center())

    self.play(
        LaggedStart(FadeIn(title_bg, run_time=0.6), Write(title, run_time=0.8), lag_ratio=0.3),
    )
    self.wait(0.3)
    return title_bg


def add_edges(self, edges_cfg, node_groups, node_positions):
    """Draw arrows with step numbers. Returns list of paths for flow animation."""
    arrows = []
    paths = []

    for idx, edge in enumerate(edges_cfg):
        src_body = node_groups[edge["from"]][0][1]  # VGroup[0]=node_group, [1]=body
        dst_body = node_groups[edge["to"]][0][1]
        src_pos = node_positions[edge["from"]]
        dst_pos = node_positions[edge["to"]]

        direction = dst_pos - src_pos
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction = direction / norm

        start = src_body.get_boundary_point(direction)
        end = dst_body.get_boundary_point(-direction)

        arrow = Arrow(
            start=start, end=end,
            color=hex_to_color(ARROW_COLOR), stroke_width=2.5,
            buff=0.08, max_tip_length_to_length_ratio=0.12,
            tip_shape=StealthTip,
        )

        # Step badge — offset above the midpoint
        mid = (start + end) / 2
        step_bg = Circle(
            radius=0.25, fill_color=hex_to_color(STEP_BG), fill_opacity=1.0,
            stroke_width=0,
        ).move_to(mid + UP * 0.35)
        step_num = Text(str(idx + 1), font_size=13, color=hex_to_color(TEXT_COLOR), weight=BOLD)
        step_num.move_to(mid + UP * 0.35)

        arrows.append((arrow, step_bg, step_num))
        paths.append(Line(start=start, end=end))

    # Animate with stagger
    anims = []
    for arrow, step_bg, step_num in arrows:
        anims.extend([
            Create(arrow, run_time=0.3),
            GrowFromCenter(step_bg, run_time=0.2),
            FadeIn(step_num, run_time=0.15),
        ])
    self.play(LaggedStart(*anims, lag_ratio=0.1, run_time=2.0))
    self.wait(0.4)

    return paths


def animate_flow_dots(self, paths):
    """Animate blue data flow dots along paths."""
    for path in paths:
        dot = Dot(radius=0.08, color=hex_to_color(DOT_COLOR), fill_opacity=1.0)
        dot.move_to(path.get_start())
        self.add(dot)
        self.play(MoveAlongPath(dot, path, run_time=0.8), rate_func=smooth)
        self.remove(dot)


def content_area():
    """Return (center_y, usable_height) below title bar.

    Manim frame: y ranges from -4 to 4 (total height = 8).
    Title bar sits at the top. Content centered between title and bottom.
    """
    frame_top = 4.0
    frame_bottom = -4.0
    title_bottom = frame_top - TITLE_H  # 3.2
    bottom_margin = frame_bottom + MARGIN  # -3.0
    usable = title_bottom - bottom_margin  # 6.2
    center_y = (title_bottom + bottom_margin) / 2  # (3.2 + -3.0) / 2 = 0.1
    # Shift down slightly for visual balance (title bar feels "heavy")
    center_y -= 0.3
    return center_y, usable
