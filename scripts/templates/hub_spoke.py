"""Hub-and-spoke template — high contrast, professional style."""

import json
import math
import os
from collections import defaultdict

from manim import *

NODE_COLORS = {
    "document": "#2196F3",
    "process": "#9C27B0",
    "database": "#4CAF50",
    "cloud": "#FF9800",
    "api": "#FFC107",
    "user": "#E91E63",
    "queue": "#00BCD4",
    "default": "#9C27B0",
}

NODE_ICONS = {
    "document": "☰",
    "process": "⚙",
    "database": "⬢",
    "cloud": "☁",
    "api": "➤",
    "user": "●",
    "queue": "≡",
}


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node(node, is_hub=False):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])
    color = hex_to_color(NODE_COLORS.get(node_type, NODE_COLORS["default"]))

    scale = 1.3 if is_hub else 1.0
    w, h = 2.0 * scale, 1.1 * scale

    body = RoundedRectangle(
        width=w, height=h, corner_radius=0.15,
        fill_color=BLACK, fill_opacity=0.6,
        stroke_color=color, stroke_width=3 if is_hub else 2.5,
    )

    stripe = Rectangle(
        width=0.1 * scale, height=h - 0.15,
        fill_color=color, fill_opacity=1.0,
        stroke_width=0,
    ).move_to(body.get_left() + RIGHT * 0.1 * scale)

    icon_bg = Circle(
        radius=0.15 * scale,
        fill_color=color, fill_opacity=0.3,
        stroke_width=0,
    ).move_to(body.get_top() + DOWN * 0.3 * scale + RIGHT * 0.35 * scale)

    icon = Text(NODE_ICONS.get(node_type, "●"), font_size=12 * scale, color=color)
    icon.move_to(icon_bg.get_center())

    txt = Text(label, font_size=16 * scale, color=WHITE, weight=BOLD)
    txt.move_to(body.get_center() + DOWN * 0.08 + RIGHT * 0.08)

    return VGroup(body, stripe, icon_bg, icon, txt)


def detect_hub(nodes_cfg, edges_cfg):
    edge_count = defaultdict(int)
    for edge in edges_cfg:
        edge_count[edge["from"]] += 1
        edge_count[edge["to"]] += 1
    return max(edge_count, key=edge_count.get) if edge_count else nodes_cfg[0]["id"]


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
        edge_color = hex_to_color(style.get("edge_color", "#00BCD4"))
        dot_color = hex_to_color(style.get("flow_dot_color", "#FFD740"))

        self.camera.background_color = "#0D1117"

        title = Text(title_text, font_size=32, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        accent = Line(title.get_left(), title.get_right(), color=edge_color, stroke_width=2)
        accent.next_to(title, DOWN, buff=0.1)
        self.play(Write(title, run_time=1.0), Create(accent, run_time=0.6))
        self.wait(0.2)

        hub_id = data.get("hub", detect_hub(nodes_cfg, edges_cfg))
        node_map = {n["id"]: n for n in nodes_cfg}
        spoke_ids = [n["id"] for n in nodes_cfg if n["id"] != hub_id]
        num_spokes = len(spoke_ids)

        # Hub node
        hub_group = build_node(node_map[hub_id], is_hub=True)
        hub_group.move_to(DOWN * 0.2)

        hub_group.set_opacity(0)
        self.add(hub_group)
        self.play(hub_group.animate.set_opacity(1), run_time=0.6)

        # Hub glow pulse
        hub_color = hex_to_color(NODE_COLORS.get(node_map[hub_id].get("type", "default"), "#9C27B0"))
        pulse = Circle(radius=0.6, stroke_color=hub_color, stroke_width=3, fill_opacity=0)
        pulse.move_to(hub_group.get_center())
        self.play(
            pulse.animate.scale(2.5).set_stroke(width=0.5, opacity=0),
            run_time=0.7, rate_func=smooth,
        )
        self.remove(pulse)

        node_groups = {hub_id: hub_group}
        node_positions = {hub_id: hub_group.get_center()}

        # Spoke nodes in circle
        radius = 2.8
        spoke_groups = []
        for i, spoke_id in enumerate(spoke_ids):
            angle = -math.pi / 2 + (2 * math.pi * i / num_spokes)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) - 0.2

            group = build_node(node_map[spoke_id])
            group.move_to(RIGHT * x + UP * y)
            node_groups[spoke_id] = group
            node_positions[spoke_id] = group.get_center()
            spoke_groups.append(group)

        # Animate spokes with stagger
        for group in spoke_groups:
            group.set_opacity(0)
            self.add(group)
        self.play(
            *[g.animate.set_opacity(1) for g in spoke_groups],
            run_time=0.8, lag_ratio=0.2,
        )
        self.wait(0.3)

        # Draw edges
        arrows = []
        paths = []
        for edge in edges_cfg:
            src_id, dst_id = edge["from"], edge["to"]
            if src_id not in node_positions or dst_id not in node_positions:
                continue

            src_body = node_groups[src_id][0]
            dst_body = node_groups[dst_id][0]
            src_pos = node_positions[src_id]
            dst_pos = node_positions[dst_id]

            direction = dst_pos - src_pos
            norm = np.linalg.norm(direction)
            if norm > 0:
                direction = direction / norm
            else:
                direction = RIGHT

            start = src_body.get_boundary_point(direction)
            end = dst_body.get_boundary_point(-direction)

            arrow = Arrow(
                start=start, end=end, color=edge_color, stroke_width=2.5,
                buff=0.05, max_tip_length_to_length_ratio=0.12,
                tip_shape=StealthTip,
            )
            arrows.append(arrow)
            paths.append(Line(start=start, end=end))

        for arrow in arrows:
            self.play(Create(arrow, run_time=0.5))
        self.wait(0.3)

        for path in paths:
            dot = Dot(radius=0.1, color=dot_color, fill_opacity=1.0)
            dot.move_to(path.get_start())
            self.add(dot)
            self.play(MoveAlongPath(dot, path, run_time=0.8), rate_func=smooth)
            self.remove(dot)

        self.wait(1.0)


if __name__ == "__main__":
    pass
