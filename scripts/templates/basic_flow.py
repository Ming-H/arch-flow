"""Basic linear left-to-right flow — global layout optimized."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import *

def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


class BasicFlow(Scene):
    def construct(self):
        data = load_config()
        nodes_cfg = data["nodes"]
        edges_cfg = data["edges"]
        style = data.get("style", {})
        title_text = data.get("title", "Architecture")

        self.camera.background_color = BG_COLOR
        add_title(self, title_text)

        center_y, usable_h = content_area()
        usable_w = CANVAS_W - 2 * MARGIN

        # Build all nodes first to measure total width
        n = len(nodes_cfg)
        built = []
        total_node_w = 0
        for node in nodes_cfg:
            group, w = build_node(node)
            built.append((group, w))
            total_node_w += w

        # Spacing: fit nodes + gaps within usable width
        min_gap = 0.8
        max_gap = 2.0
        gap = (usable_w - total_node_w) / max(n - 1, 1) if n > 1 else 0
        gap = max(min_gap, min(max_gap, gap))

        # If total width exceeds canvas, scale down
        total_w = total_node_w + gap * (n - 1)
        scale = 1.0
        if total_w > usable_w:
            scale = usable_w / total_w

        start_x = -total_w * scale / 2

        node_groups = {}
        node_positions = {}
        x_offset = start_x

        for i, (node, (group, w)) in enumerate(zip(nodes_cfg, built)):
            if scale != 1.0:
                group.scale(scale)
            pos = RIGHT * (x_offset + w * scale / 2) + UP * center_y
            group.move_to(pos)
            node_groups[node["id"]] = (group, w * scale)
            node_positions[node["id"]] = group.get_center()
            x_offset += w * scale + gap * scale

        # Animate nodes
        node_anims = []
        for node in nodes_cfg:
            g = node_groups[node["id"]][0]
            g.set_opacity(0)
            self.add(g)
            node_anims.append(g.animate.set_opacity(1))

        self.play(LaggedStart(*node_anims, lag_ratio=0.12, run_time=1.5))
        self.wait(0.4)

        # Edges + step numbers + flow dots
        paths = add_edges(self, edges_cfg, node_groups, node_positions)
        animate_flow_dots(self, paths)

        self.wait(1.5)


if __name__ == "__main__":
    pass
