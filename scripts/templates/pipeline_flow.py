"""Pipeline flow — global layout optimized with stage groups."""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import *


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
    visited, stages = set(), []
    sources = [nid for nid in node_ids if len(in_edges[nid]) == 0]
    if not sources:
        sources = [node_ids[0]]
    current = sources[:]
    while current and len(visited) < len(node_ids):
        stage = [nid for nid in current if nid not in visited]
        if not stage:
            remaining = [nid for nid in node_ids if nid not in visited]
            stage = remaining[:1] if remaining else []
            if not stage: break
        stages.append(stage)
        for nid in stage: visited.add(nid)
        current = []
        for nid in stage:
            for nb in out_edges[nid]:
                if nb not in visited: current.append(nb)
    for nid in node_ids:
        if nid not in visited:
            stages[-1].append(nid) if stages else stages.append([nid])
    return [{"name": f"Stage {i+1}", "nodes": s} for i, s in enumerate(stages)]


class PipelineFlow(Scene):
    def construct(self):
        data = load_config()
        nodes_cfg = data["nodes"]
        edges_cfg = data["edges"]
        title_text = data.get("title", "Architecture")

        self.camera.background_color = BG_COLOR
        add_title(self, title_text)

        center_y, usable_h = content_area()
        usable_w = CANVAS_W - 2 * MARGIN

        node_map = {n["id"]: n for n in nodes_cfg}
        stages = data.get("stages") if "stages" in data else auto_detect_stages(nodes_cfg, edges_cfg)

        # Build nodes and measure widths
        built = {}
        for node in nodes_cfg:
            built[node["id"]] = build_node(node, scale=0.85)

        num_stages = len(stages)
        stage_gap = 0.6

        # Measure each stage width
        stage_widths = []
        for stage in stages:
            sw = sum(built[nid][1] for nid in stage["nodes"]) + 0.5 * (len(stage["nodes"]) - 1)
            stage_widths.append(max(sw, 2.0))

        total_w = sum(stage_widths) + stage_gap * (num_stages - 1)

        # Scale down if exceeds canvas
        scale_factor = 1.0
        if total_w > usable_w:
            scale_factor = usable_w / total_w

        x_cursor = -total_w * scale_factor / 2

        node_groups = {}
        node_positions = {}

        for si, stage in enumerate(stages):
            sw = stage_widths[si] * scale_factor
            cx = x_cursor + sw / 2

            nl = len(stage["nodes"])
            node_spacing = 1.2
            bg_h = max(nl * node_spacing + 0.8, 2.0)

            # Stage background
            sbg = RoundedRectangle(
                width=sw + 0.3, height=bg_h, corner_radius=0.2,
                fill_color=hex_to_color("#F5F5F5"), fill_opacity=0.5,
                stroke_color=hex_to_color("#E0E0E0"), stroke_width=1.2,
            )
            sbg.move_to(RIGHT * cx + UP * center_y)

            slbl = Text(stage["name"], font_size=13, color=hex_to_color(TITLE_COLOR), weight=BOLD)
            slbl.next_to(sbg, UP, buff=0.08)

            self.play(FadeIn(sbg, run_time=0.3), Write(slbl, run_time=0.3))

            # Place nodes vertically within stage
            y_start = (nl - 1) * node_spacing / 2
            for i, nid in enumerate(stage["nodes"]):
                g, w = built[nid]
                if scale_factor != 1.0:
                    g.scale(scale_factor)
                y = center_y + (y_start - i * node_spacing) if nl > 1 else center_y
                g.move_to(RIGHT * cx + UP * y)
                node_groups[nid] = (g, w * scale_factor)
                node_positions[nid] = g.get_center()

                g.set_opacity(0)
                self.add(g)
                self.play(g.animate.set_opacity(1), run_time=0.3)

            x_cursor += sw + stage_gap * scale_factor

        self.wait(0.3)

        paths = add_edges(self, edges_cfg, node_groups, node_positions)
        animate_flow_dots(self, paths)

        self.wait(1.5)


if __name__ == "__main__":
    pass
