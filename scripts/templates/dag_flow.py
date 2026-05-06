"""DAG flow — global layout optimized with layer-wise centering."""

import json
import os
import sys
from collections import defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import *


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


def compute_layers(nodes_cfg, edges_cfg):
    in_degree = defaultdict(int)
    adjacency = defaultdict(list)
    node_ids = [n["id"] for n in nodes_cfg]
    node_set = set(node_ids)
    for edge in edges_cfg:
        if edge["from"] in node_set and edge["to"] in node_set:
            adjacency[edge["from"]].append(edge["to"])
            in_degree[edge["to"]] += 1
    queue = deque([nid for nid in node_ids if in_degree[nid] == 0])
    layers, assigned = [], set()
    while queue:
        layer = list(queue)
        layers.append(layer)
        for nid in layer:
            assigned.add(nid)
        next_q = deque()
        for nid in layer:
            for nb in adjacency[nid]:
                in_degree[nb] -= 1
                if in_degree[nb] == 0 and nb not in assigned:
                    next_q.append(nb)
        queue = next_q
    for nid in node_ids:
        if nid not in assigned:
            layers[-1].append(nid)
    return layers


class DagFlow(Scene):
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
        layers = compute_layers(nodes_cfg, edges_cfg)

        num_layers = len(layers)

        # Measure max layer width to determine horizontal spacing
        built = {}
        for node in nodes_cfg:
            built[node["id"]] = build_node(node)

        # Layer spacing: divide usable height into layers
        layer_gap = min(2.5, usable_h / max(num_layers, 1))
        top_y = center_y + (num_layers - 1) * layer_gap / 2

        node_groups = {}
        node_positions = {}

        for li, layer in enumerate(layers):
            y = top_y - li * layer_gap
            # Center this layer horizontally
            layer_w = sum(built[nid][1] for nid in layer) + 0.8 * (len(layer) - 1)
            x_cursor = -layer_w / 2

            for nid in layer:
                group, w = built[nid]
                group.move_to(RIGHT * (x_cursor + w / 2) + UP * y)
                node_groups[nid] = (group, w)
                node_positions[nid] = group.get_center()
                x_cursor += w + 0.8

        # Animate layer by layer
        for layer in layers:
            anims = []
            for nid in layer:
                g = node_groups[nid][0]
                g.set_opacity(0)
                self.add(g)
                anims.append(g.animate.set_opacity(1))
            self.play(*anims, run_time=0.5, lag_ratio=0.1)
            self.wait(0.1)

        self.wait(0.3)

        paths = add_edges(self, edges_cfg, node_groups, node_positions)
        animate_flow_dots(self, paths)

        self.wait(1.5)


if __name__ == "__main__":
    pass
