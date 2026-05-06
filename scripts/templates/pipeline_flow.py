"""Pipeline flow template — staged groups, high contrast style."""

import json
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


def build_node(node):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])
    color = hex_to_color(NODE_COLORS.get(node_type, NODE_COLORS["default"]))

    w, h = 1.8, 1.0

    body = RoundedRectangle(
        width=w, height=h, corner_radius=0.12,
        fill_color=BLACK, fill_opacity=0.6,
        stroke_color=color, stroke_width=2,
    )

    stripe = Rectangle(
        width=0.08, height=h - 0.12,
        fill_color=color, fill_opacity=1.0,
        stroke_width=0,
    ).move_to(body.get_left() + RIGHT * 0.08)

    icon_bg = Circle(
        radius=0.12,
        fill_color=color, fill_opacity=0.3,
        stroke_width=0,
    ).move_to(body.get_top() + DOWN * 0.25 + RIGHT * 0.3)

    icon = Text(NODE_ICONS.get(node_type, "●"), font_size=10, color=color)
    icon.move_to(icon_bg.get_center())

    txt = Text(label, font_size=14, color=WHITE, weight=BOLD)
    txt.move_to(body.get_center() + DOWN * 0.05 + RIGHT * 0.05)

    return VGroup(body, stripe, icon_bg, icon, txt)


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


def auto_detect_stages(nodes_cfg, edges_cfg):
    node_ids = [n["id"] for n in nodes_cfg]
    out_edges = defaultdict(list)
    in_edges = defaultdict(list)
    node_set = set(node_ids)

    for edge in edges_cfg:
        if edge["from"] in node_set and edge["to"] in node_set:
            out_edges[edge["from"]].append(edge["to"])
            in_edges[edge["to"]].append(edge["from"])

    visited = set()
    stages = []
    sources = [nid for nid in node_ids if len(in_edges[nid]) == 0]
    if not sources:
        sources = [node_ids[0]]

    current = sources[:]
    while current and len(visited) < len(node_ids):
        stage = [nid for nid in current if nid not in visited]
        if not stage:
            remaining = [nid for nid in node_ids if nid not in visited]
            stage = remaining[:1] if remaining else []
            if not stage:
                break
        stages.append(stage)
        for nid in stage:
            visited.add(nid)
        next_nodes = []
        for nid in stage:
            for neighbor in out_edges[nid]:
                if neighbor not in visited:
                    next_nodes.append(neighbor)
        current = next_nodes

    for nid in node_ids:
        if nid not in visited:
            stages[-1].append(nid) if stages else stages.append([nid])

    return [{"name": f"Stage {i + 1}", "nodes": stage} for i, stage in enumerate(stages)]


class PipelineFlow(Scene):
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
        title.to_edge(UP, buff=0.35)
        accent = Line(title.get_left(), title.get_right(), color=edge_color, stroke_width=2)
        accent.next_to(title, DOWN, buff=0.1)
        self.play(Write(title, run_time=1.0), Create(accent, run_time=0.6))
        self.wait(0.2)

        node_map = {n["id"]: n for n in nodes_cfg}

        stages = data.get("stages") if "stages" in data else auto_detect_stages(nodes_cfg, edges_cfg)

        num_stages = len(stages)
        stage_width = min(2.8, 12.0 / max(num_stages, 1))
        total_width = num_stages * stage_width
        start_x = -total_width / 2 + stage_width / 2

        node_groups = {}
        node_positions = {}

        stage_accent = hex_to_color("#00BCD4")

        for stage_idx, stage in enumerate(stages):
            stage_x = start_x + stage_idx * stage_width
            stage_nodes = stage["nodes"]
            n_in_stage = len(stage_nodes)
            y_spacing = 1.3
            y_start = (n_in_stage - 1) * y_spacing / 2

            # Stage background
            bg_h = max(n_in_stage * y_spacing + 0.8, 2.0)
            stage_bg = RoundedRectangle(
                width=stage_width - 0.2, height=bg_h,
                corner_radius=0.15,
                fill_color="#111827", fill_opacity=0.5,
                stroke_color=stage_accent, stroke_width=1.2, stroke_opacity=0.4,
            )
            stage_bg.move_to(RIGHT * stage_x + DOWN * 0.4)

            stage_label = Text(stage["name"], font_size=13, color=stage_accent, fill_opacity=0.8)
            stage_label.next_to(stage_bg, UP, buff=0.08)

            self.play(FadeIn(stage_bg, run_time=0.5), Write(stage_label, run_time=0.4))
            self.wait(0.1)

            for i, nid in enumerate(stage_nodes):
                group = build_node(node_map[nid])
                y = y_start - i * y_spacing if n_in_stage > 1 else 0
                group.move_to(RIGHT * stage_x + DOWN * 0.4 + UP * y)
                node_groups[nid] = group
                node_positions[nid] = group.get_center()

                group.set_opacity(0)
                self.add(group)
                self.play(group.animate.set_opacity(1), run_time=0.4)
                self.wait(0.05)

            self.wait(0.1)

        self.wait(0.3)

        # Draw edges
        arrows = []
        paths = []
        for edge in edges_cfg:
            if edge["from"] not in node_positions or edge["to"] not in node_positions:
                continue
            src_body = node_groups[edge["from"]][0]
            dst_body = node_groups[edge["to"]][0]
            src_pos = node_positions[edge["from"]]
            dst_pos = node_positions[edge["to"]]

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
