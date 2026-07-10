from urenderer.node import Node
import numpy as np

def update_water(node: Node, dt: float, t: float):
    mesh = node.render_data["mesh"]
    verts = mesh.vertex.copy().reshape(-1, 3)
    sd = node.render_data["subdiv"]
    sz = node.render_data["size"]
    half = sz / 2
    for z in range(sd + 1):
        for x in range(sd + 1):
            idx = z * (sd + 1) + x
            vx = -half + sz * x / sd
            vz = -half + sz * z / sd
            verts[idx, 1] = 0.02 * np.sin(2.5 * vx + 0.5 * t) + 0.025 * np.sin(1.8 * vz + 1 * t + 1.0)
    mesh.vertex = verts.flatten()

def update_beacon(node: Node, dt: float, t: float):
    parent_rot = node.parent.rotation[1]
    angle_deg = parent_rot % 360
    dist = min(angle_deg, 360 - angle_deg, abs(angle_deg - 180))
    raw = np.clip(1.0 - (dist / 70.0) ** 1.5, 0.0, 1.0)
    intensity = raw * np.exp(-(dist ** 2) / (2.0 * 50.0 ** 2))
    node.light_intensity = float(intensity * 1.5)


def update_boat(node: Node, dt: float, t: float):
    node.translation = np.array([0.7, -0.12 + 0.005 * np.sin(1.5 * t), 1], np.float32)
    node.rotation[0] = 5 * np.sin(1.0 * t)
    node.rotation[2] = 3 * np.sin(0.6 * t + 0.5)


def update_dolphin(node, dt, t):
    phase = node._phase
    period = node._period
    local_t = (t + phase) % period
    
    cycle = int((t + phase) // period)
    if cycle != getattr(node, "_last_cycle", -1):
        node._last_cycle = cycle
        node._jump_offset = np.random.uniform(0, 1)
    
    offset = getattr(node, "_jump_offset", 0.0)
    arc = ((local_t / period) + offset) % 1.0
    height = 0.50 * np.sin(arc * np.pi) ** 4
    x = 4.0 - (local_t / period) * 8.0
    node.translation = np.array([x, -0.45 + height, 2.5], np.float32)
    
    pitch = 60 * np.cos(arc * np.pi)
    node.rotation = np.array([pitch, 90, 0], np.float32)
