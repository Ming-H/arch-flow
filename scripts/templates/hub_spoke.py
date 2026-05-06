"""Hub-and-spoke — clean light theme."""

import json
import math
import os
from collections import defaultdict

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


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node(node, is_hub=False):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])
    fill = hex_to_color(NODE_FILLS.get(node_type, NODE_FILLS["default"]))
    accent = hex_to_color(NODE_ACCENTS.get(node_type, NODE_ACCENTS["default"]))

    scale = 1.25 if is_hub else 1.0
    w, h = 2.2 * scale, 1.2 * scale

    shadow = RoundedRectangle(width=w, height=h, corner_radius=0.18,
        fill_color=BLACK, fill_opacity=0.08, stroke_width=0).shift(DOWN * 0.03 + RIGHT * 0.03)
    body = RoundedRectangle(width=w, height=h, corner_radius=0.18,
        fill_color=fill, fill_opacity=1.0,
        stroke_color=hex_to_color("#BDBDBD"), stroke_width=2.0 if is_hub else 1.5)
    icon = Text(NODE_ICONS.get(node_type, "●"), font_size=18 * scale, color=accent)
    icon.move_to(body.get_left() + RIGHT * 0.4 * scale)
    txt = Text(label, font_size=15 * scale, color=hex_to_color("#212121"), weight=BOLD)
    txt.move_to(body.get_center() + RIGHT * 0.08)
    return VGroup(shadow, body, icon, txt)


def detect_hub(nodes_cfg, edges_cfg):
    ec = defaultdict(int)
    for e in edges_cfg:
        ec[e["from"]] += 1
        ec[e["to"]] += 1
    return max(ec, key=ec.get) if ec else nodes_cfg[0]["id"]


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


class HubSpoke(Scene):
    def construct(self):
        data = load_config()
        nodes_cfg = data["nodes"]
        edges_cfg = data["edges"]
        style = data.get("style", {})
        title_text = data.get("title", "Architecture")

        self.camera.background_color = "#FAFAFA"

        title_bg = Rectangle(width=14, height=0.7,
            fill_color=hex_to_color("#4CAF50"), fill_opacity=1.0, stroke_width=0
        ).to_edge(UP, buff=0.1)
        title = Text(title_text, font_size=28, color=WHITE, weight=BOLD)
        title.move_to(title_bg.get_center())
        self.play(FadeIn(title_bg, run_time=0.5), Write(title, run_time=0.8))
        self.wait(0.2)

        hub_id = data.get("hub", detect_hub(nodes_cfg, edges_cfg))
        node_map = {n["id"]: n for n in nodes_cfg}
        spoke_ids = [n["id"] for n in nodes_cfg if n["id"] != hub_id]
        num_spokes = len(spoke_ids)

        # Hub
        hg = build_node(node_map[hub_id], is_hub=True)
        hg.move_to(DOWN * 0.2)
        hg.set_opacity(0)
        self.add(hg)
        self.play(hg.animate.set_opacity(1), run_time=0.5)

        hub_accent = hex_to_color(NODE_ACCENTS.get(node_map[hub_id].get("type", "default"), "#283593"))
        pulse = Circle(radius=0.5, stroke_color=hub_accent, stroke_width=3, fill_opacity=0)
        pulse.move_to(hg.get_center())
        self.play(pulse.animate.scale(2.2).set_stroke(width=0.5, opacity=0), run_time=0.6, rate_func=smooth)
        self.remove(pulse)

        node_groups = {hub_id: hg}
        node_positions = {hub_id: hg.get_center()}

        radius = 2.6
        spoke_groups = []
        for i, sid in enumerate(spoke_ids):
            angle = -math.pi / 2 + (2 * math.pi * i / num_spokes)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) - 0.2
            g = build_node(node_map[sid])
            g.move_to(RIGHT * x + UP * y)
            node_groups[sid] = g
            node_positions[sid] = g.get_center()
            spoke_groups.append(g)

        for g in spoke_groups:
            g.set_opacity(0)
            self.add(g)
        self.play(*[g.animate.set_opacity(1) for g in spoke_groups], run_time=0.7, lag_ratio=0.15)
        self.wait(0.2)

        arrow_color = hex_to_color("#757575")
        arrows, paths = [], []
        for idx, edge in enumerate(edges_cfg):
            sid, did = edge["from"], edge["to"]
            if sid not in node_positions or did not in node_positions: continue
            sb = node_groups[sid][1]
            db = node_groups[did][1]
            sp, dp = node_positions[sid], node_positions[did]
            d = dp - sp
            n = np.linalg.norm(d)
            if n > 0: d = d / n
            else: d = RIGHT
            s, e = sb.get_boundary_point(d), db.get_boundary_point(-d)
            arr = Arrow(start=s, end=e, color=arrow_color, stroke_width=2,
                        buff=0.05, max_tip_length_to_length_ratio=0.12, tip_shape=StealthTip)
            mid = (s + e) / 2
            sc = Circle(radius=0.18, fill_color=hex_to_color("#FFC107"), fill_opacity=1.0, stroke_width=0).move_to(mid)
            sn = Text(str(idx + 1), font_size=11, color=hex_to_color("#212121"), weight=BOLD).move_to(mid)
            arrows.append((arr, sc, sn))
            paths.append(Line(start=s, end=e))

        for arr, sc, sn in arrows:
            self.play(Create(arr, run_time=0.4), FadeIn(sc, run_time=0.3), FadeIn(sn, run_time=0.3))
        self.wait(0.3)

        for path in paths:
            dot = Dot(radius=0.08, color=hex_to_color("#42A5F5"), fill_opacity=1.0)
            dot.move_to(path.get_start())
            self.add(dot)
            self.play(MoveAlongPath(dot, path, run_time=0.6), rate_func=smooth)
            self.remove(dot)

        self.wait(1.0)


if __name__ == "__main__":
    pass
