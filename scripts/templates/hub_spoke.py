"""Hub-and-spoke — global layout optimized with auto radius."""

import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import *


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
        title_text = data.get("title", "Architecture")

        self.camera.background_color = BG_COLOR
        add_title(self, title_text)

        center_y, usable_h = content_area()
        usable_w = CANVAS_W - 2 * MARGIN

        hub_id = data.get("hub", detect_hub(nodes_cfg, edges_cfg))
        node_map = {n["id"]: n for n in nodes_cfg}
        spoke_ids = [n["id"] for n in nodes_cfg if n["id"] != hub_id]
        num_spokes = len(spoke_ids)

        # Hub
        hub_group, hub_w = build_node(node_map[hub_id], scale=1.2)
        hub_group.move_to(UP * center_y)

        hub_group.set_opacity(0)
        self.add(hub_group)
        self.play(hub_group.animate.set_opacity(1), run_time=0.5)

        # Hub pulse
        hub_accent = hex_to_color(NODE_ACCENTS.get(node_map[hub_id].get("type", "default"), "#283593"))
        pulse = Circle(radius=0.6, stroke_color=hub_accent, stroke_width=3, fill_opacity=0)
        pulse.move_to(hub_group.get_center())
        self.play(
            pulse.animate.scale(2.5).set_stroke(width=0.5, opacity=0),
            run_time=0.6, rate_func=smooth,
        )
        self.remove(pulse)

        node_groups = {hub_id: (hub_group, hub_w)}
        node_positions = {hub_id: hub_group.get_center()}

        # Calculate spoke radius based on canvas and node count
        # Ensure spokes don't overlap or go off-screen
        spoke_group, spoke_w = build_node(node_map[spoke_ids[0]]) if spoke_ids else (None, 2.0)
        min_radius = (hub_w / 2 + spoke_w / 2) + 0.8
        max_radius = min(usable_w / 2 - spoke_w / 2, usable_h / 2 - 0.8)
        # Scale radius with spoke count
        ideal_radius = min_radius + (max_radius - min_radius) * min(1.0, num_spokes / 8.0)
        radius = max(min_radius, min(max_radius, ideal_radius))

        spoke_groups = []
        for i, sid in enumerate(spoke_ids):
            g, w = build_node(node_map[sid])
            angle = -math.pi / 2 + (2 * math.pi * i / num_spokes)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            g.move_to(RIGHT * x + UP * y + UP * center_y)
            node_groups[sid] = (g, w)
            node_positions[sid] = g.get_center()
            spoke_groups.append(g)

        # Staggered spoke appearance
        for g in spoke_groups:
            g.set_opacity(0)
            self.add(g)
        self.play(
            *[g.animate.set_opacity(1) for g in spoke_groups],
            run_time=0.7, lag_ratio=0.15,
        )
        self.wait(0.3)

        paths = add_edges(self, edges_cfg, node_groups, node_positions)
        animate_flow_dots(self, paths)

        self.wait(1.5)


if __name__ == "__main__":
    pass
