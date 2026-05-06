"""Hub-and-spoke layout template for arch-flow."""

import json
import os
import math
from collections import defaultdict

from manim import *


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node_shape(node, node_color, text_color, is_hub=False):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])

    scale = 1.3 if is_hub else 1.0
    font = 24 if is_hub else 20

    if node_type == "document":
        shape = Rectangle(width=2.0 * scale, height=1.2 * scale,
                          fill_color=node_color, fill_opacity=0.9,
                          stroke_color=WHITE, stroke_width=2)
    elif node_type == "database":
        shape = Rectangle(width=2.0 * scale, height=1.2 * scale,
                          fill_color=node_color, fill_opacity=0.9,
                          stroke_color=YELLOW, stroke_width=2.5)
    elif node_type == "cloud":
        shape = Ellipse(width=2.4 * scale, height=1.4 * scale,
                        fill_color=node_color, fill_opacity=0.9,
                        stroke_color=WHITE, stroke_width=2)
    elif node_type == "api":
        shape = RoundedRectangle(width=1.8 * scale, height=1.0 * scale, corner_radius=0.2,
                                 fill_color=node_color, fill_opacity=0.9,
                                 stroke_color=WHITE, stroke_width=2)
    else:
        shape = RoundedRectangle(width=2.2 * scale, height=1.2 * scale, corner_radius=0.3,
                                 fill_color=node_color, fill_opacity=0.9,
                                 stroke_color=WHITE, stroke_width=2)

    text = Text(label, font_size=font, color=text_color)
    text.move_to(shape.get_center())
    return VGroup(shape, text)


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

        bg_color = hex_to_color(style.get("bg_color", "#1a1a2e"))
        node_color = hex_to_color(style.get("node_color", "#0f3460"))
        edge_color = hex_to_color(style.get("edge_color", "#e94560"))
        text_color = hex_to_color(style.get("text_color", "#ffffff"))
        dot_color = hex_to_color(style.get("flow_dot_color", "#f5c518"))

        self.camera.background_color = bg_color

        title = Text(title_text, font_size=36, color=text_color, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title, run_time=1.5))
        self.wait(0.3)

        hub_id = data.get("hub", detect_hub(nodes_cfg, edges_cfg))
        node_map = {n["id"]: n for n in nodes_cfg}

        spoke_ids = [n["id"] for n in nodes_cfg if n["id"] != hub_id]
        num_spokes = len(spoke_ids)

        hub_group = build_node_shape(node_map[hub_id], node_color, text_color, is_hub=True)
        hub_group.move_to(DOWN * 0.3)

        self.play(Create(hub_group, run_time=1.5))

        pulse_ring = Circle(radius=0.5, stroke_color=node_color, stroke_width=3, fill_opacity=0)
        pulse_ring.move_to(hub_group.get_center())
        self.play(
            pulse_ring.animate.scale(3).set_stroke(width=0.5, opacity=0.2),
            run_time=1.0,
            rate_func=smooth
        )
        self.play(FadeOut(pulse_ring, run_time=0.3))

        node_groups = {hub_id: hub_group}
        node_positions = {hub_id: hub_group.get_center()}

        radius = 3.0
        spoke_groups_list = []
        for i, spoke_id in enumerate(spoke_ids):
            angle = -math.pi / 2 + (2 * math.pi * i / num_spokes)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) - 0.3

            node = node_map[spoke_id]
            group = build_node_shape(node, node_color, text_color, is_hub=False)
            group.move_to(RIGHT * x + UP * y)
            node_groups[spoke_id] = group
            node_positions[spoke_id] = group.get_center()
            spoke_groups_list.append(group)

        self.play(
            *[FadeIn(g, run_time=1.2) for g in spoke_groups_list],
            lag_ratio=0.3
        )
        self.wait(0.3)

        arrows = []
        paths = []
        for edge in edges_cfg:
            src_id = edge["from"]
            dst_id = edge["to"]
            if src_id not in node_positions or dst_id not in node_positions:
                continue

            src_pos = node_positions[src_id]
            dst_pos = node_positions[dst_id]
            src_shape = node_groups[src_id][0]
            dst_shape = node_groups[dst_id][0]

            direction = dst_pos - src_pos
            norm = np.linalg.norm(direction)
            if norm > 0:
                direction = direction / norm
            else:
                direction = RIGHT

            start = src_shape.get_boundary_point(direction)
            end = dst_shape.get_boundary_point(-direction)

            arrow = Arrow(start=start, end=end, color=edge_color,
                          stroke_width=3, buff=0.05, max_tip_length_to_length_ratio=0.12)
            arrows.append(arrow)
            paths.append(Line(start=start, end=end))

        for arrow in arrows:
            self.play(Create(arrow, run_time=0.8))

        self.wait(0.3)

        for path in paths:
            dot = Dot(radius=0.1, color=dot_color, fill_opacity=1)
            dot.move_to(path.get_start())
            self.play(MoveAlongPath(dot, path, run_time=2), rate_func=smooth)
            self.play(FadeOut(dot, run_time=0.2))

        self.wait(1.0)


if __name__ == "__main__":
    pass
