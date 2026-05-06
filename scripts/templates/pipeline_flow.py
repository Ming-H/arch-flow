"""Staged pipeline flow template for arch-flow."""

import json
import os
from collections import defaultdict

from manim import *


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node_shape(node, node_color, text_color):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])

    if node_type == "document":
        shape = Rectangle(width=1.8, height=0.9, fill_color=node_color, fill_opacity=0.85,
                          stroke_color=WHITE, stroke_width=1.5)
    elif node_type == "database":
        shape = Rectangle(width=1.8, height=0.9, fill_color=node_color, fill_opacity=0.85,
                          stroke_color=YELLOW, stroke_width=2)
    elif node_type == "cloud":
        shape = Ellipse(width=2.2, height=1.1, fill_color=node_color, fill_opacity=0.85,
                        stroke_color=WHITE, stroke_width=1.5)
    elif node_type == "api":
        shape = RoundedRectangle(width=1.6, height=0.8, corner_radius=0.2,
                                 fill_color=node_color, fill_opacity=0.85,
                                 stroke_color=WHITE, stroke_width=1.5)
    else:
        shape = RoundedRectangle(width=2.0, height=0.9, corner_radius=0.3,
                                 fill_color=node_color, fill_opacity=0.85,
                                 stroke_color=WHITE, stroke_width=1.5)

    text = Text(label, font_size=18, color=text_color)
    text.move_to(shape.get_center())
    return VGroup(shape, text)


def auto_detect_stages(nodes_cfg, edges_cfg):
    node_ids = [n["id"] for n in nodes_cfg]
    in_edges = defaultdict(list)
    out_edges = defaultdict(list)
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
            if remaining:
                stage = remaining[:1]
            else:
                break
        stages.append(stage)
        for nid in stage:
            visited.add(nid)
        next_nodes = []
        for nid in stage:
            for neighbor in out_edges[nid]:
                if neighbor not in visited:
                    next_nodes.append(neighbor)
        if next_nodes:
            current = next_nodes
        else:
            current = []

    for nid in node_ids:
        if nid not in visited:
            if stages:
                stages[-1].append(nid)
            else:
                stages.append([nid])

    return [{"name": f"Stage {i + 1}", "nodes": stage} for i, stage in enumerate(stages)]


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


class PipelineFlow(Scene):
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
        title.to_edge(UP, buff=0.4)
        self.play(Write(title, run_time=1.5))
        self.wait(0.3)

        node_map = {n["id"]: n for n in nodes_cfg}

        if "stages" in data:
            stages = data["stages"]
        else:
            stages = auto_detect_stages(nodes_cfg, edges_cfg)

        num_stages = len(stages)
        stage_width = 3.0
        total_width = num_stages * stage_width
        start_x = -total_width / 2 + stage_width / 2

        stage_bg_color = ManimColor.from_rgb(
            tuple(max(0, int(c) - 30) for c in node_color.to_rgb()[:3])
        )

        node_groups = {}
        node_positions = {}

        for stage_idx, stage in enumerate(stages):
            stage_x = start_x + stage_idx * stage_width
            stage_nodes = stage["nodes"]
            n_in_stage = len(stage_nodes)
            y_spacing = 1.4
            y_start = (n_in_stage - 1) * y_spacing / 2

            stage_bg = RoundedRectangle(
                width=stage_width - 0.3, height=max(n_in_stage * y_spacing + 1.0, 2.4),
                fill_color=stage_bg_color, fill_opacity=0.4,
                stroke_color=text_color, stroke_width=1, stroke_opacity=0.3,
                corner_radius=0.2
            )
            stage_bg.move_to(RIGHT * stage_x + DOWN * 0.5)

            stage_label = Text(stage["name"], font_size=16, color=text_color, fill_opacity=0.7)
            stage_label.next_to(stage_bg, UP, buff=0.1)

            self.play(FadeIn(stage_bg, run_time=1.0), Write(stage_label, run_time=1.0))
            self.wait(0.2)

            for i, nid in enumerate(stage_nodes):
                node = node_map[nid]
                group = build_node_shape(node, node_color, text_color)
                y = y_start - i * y_spacing if n_in_stage > 1 else 0
                group.move_to(RIGHT * stage_x + DOWN * 0.5 + UP * y)
                node_groups[nid] = group
                node_positions[nid] = group.get_center()

                self.play(FadeIn(group, run_time=1.2))
                self.wait(0.1)

            self.wait(0.2)

        self.wait(0.3)

        arrows = []
        paths = []
        for edge in edges_cfg:
            if edge["from"] not in node_positions or edge["to"] not in node_positions:
                continue
            src_pos = node_positions[edge["from"]]
            dst_pos = node_positions[edge["to"]]
            src_shape = node_groups[edge["from"]][0]
            dst_shape = node_groups[edge["to"]][0]

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
