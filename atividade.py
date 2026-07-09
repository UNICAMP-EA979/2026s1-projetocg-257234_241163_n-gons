from collections import deque

import numpy as np
import urenderer
from OpenGL import GL
from urenderer.node import Node
from urenderer.renderer.opengl import Material, Shader, Texture
from urenderer.geometry.mesh import Mesh
from icosphere import icosphere

def color_texture(r, g, b):
    data = np.array([[[r, g, b]]], dtype=np.uint8)
    return Texture(data, GL.GL_RGB, GL.GL_RGB)


def solid_material(shader, color_rgb, metallic=0.0, roughness=0.7, tiling=1.0):
    r, g, b = [int(c * 255) for c in color_rgb]
    base = color_texture(r, g, b)
    black_r = Texture(np.zeros((1, 1), np.uint8), GL.GL_RED, GL.GL_R8)
    rough_val = int(np.clip(roughness, 0, 1) * 255)
    rough_tex = Texture(np.full((1, 1), rough_val, np.uint8), GL.GL_RED, GL.GL_R8)
    mat = Material(shader)
    mat.set_texture(0, "baseColorTexture", base)
    mat.set_texture(1, "metallicTexture", black_r)
    mat.set_texture(2, "roughnessTexture", rough_tex)
    mat.set_uniform("tiling", tiling)
    return mat


def grid_mesh(size, subdiv):
    half = size / 2
    verts, uv, norms = [], [], []
    idx = []
    for z in range(subdiv + 1):
        for x in range(subdiv + 1):
            verts.append([-half + size * x / subdiv, 0, -half + size * z / subdiv])
            uv.append([x / subdiv, z / subdiv])
            norms.append([0, 1, 0])
    for z in range(subdiv):
        for x in range(subdiv):
            i0 = z * (subdiv + 1) + x
            i1 = i0 + 1
            i2 = (z + 1) * (subdiv + 1) + x
            i3 = i2 + 1
            idx += [i0, i1, i2, i1, i3, i2]
    return Mesh(
        np.array(verts, np.float32),
        np.array(idx, np.uint32),
        np.array(uv, np.float32),
        normal=np.array(norms, np.float32),
    )


def rock_mesh(subdiv=2):
    vertices, faces = icosphere(subdiv)
    vertices = vertices.astype(np.float32)
    faces = faces.astype(np.uint32)
    for i in range(vertices.shape[0]):
        v = vertices[i]
        noise = 1.0 + 0.25 * np.sin(v[0] * 3.7 + v[1] * 5.2 + v[2] * 2.3)
        noise *= 1.0 + 0.15 * np.sin(v[0] * 7.1 + v[1] * 11.3 + v[2] * 4.7)
        vertices[i] = v * noise
    uv = np.empty((vertices.shape[0], 2), dtype=np.float32)
    normals = np.empty_like(vertices)
    for i in range(vertices.shape[0]):
        x, y, z = vertices[i]
        uv[i] = [0.5 + np.arctan2(z, x) / (2 * np.pi), 0.5 - np.arcsin(np.clip(y, -1, 1)) / np.pi]
        l = np.sqrt(x * x + y * y + z * z)
        normals[i] = [x / l, y / l, z / l]
    return Mesh(vertices, faces, uv, normal=normals)


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
    node.light_intensity = float(intensity * 3.0)


def update_boat(node: Node, dt: float, t: float):
    node.translation = np.array([0.7, -0.12 + 0.005 * np.sin(1.5 * t), 1], np.float32)
    node.rotation[0] = 5 * np.sin(1.0 * t)
    node.rotation[2] = 3 * np.sin(0.6 * t + 0.5)


def create_sky_gradient():
    h = 256
    grad = np.zeros((h, 1, 3), dtype=np.uint8)
    top = np.array([0.05, 0.08, 0.25])
    mid = np.array([0.40, 0.25, 0.40])
    horizon = np.array([0.95, 0.50, 0.20])
    for i in range(h):
        t = i / (h - 1)
        if t < 0.4:
            u = t / 0.4
            c = top * (1 - u) + mid * u
        else:
            u = (t - 0.4) / 0.6
            c = mid * (1 - u) + horizon * u
        grad[i, 0] = (np.clip(c, 0, 1) * 255).astype(np.uint8)
    return grad

NOME_DA_CENA = "lighthouse_scene"

if __name__ == "__main__":
    urenderer.utils.clear_workdir(NOME_DA_CENA)
    renderer = urenderer.renderer.OpenGLRenderer(1920, 1080)
    renderer.background_color = np.array([0.05, 0.08, 0.25, 1.0], np.float32)
    renderer.ambient_color = np.array([0.15, 0.12, 0.18], dtype=np.float32)
    runtime = urenderer.application.Runtime(renderer, name=NOME_DA_CENA)
    runtime.camera.vertical_fov = 45.0

    shader = Shader("assets/vertex.vs", "assets/05-fragment.fs")

    white_mat = solid_material(shader, (0.96, 0.96, 0.93), roughness=0.6)
    red_mat = solid_material(shader, (0.85, 0.15, 0.10), roughness=0.5)
    roof_mat = solid_material(shader, (0.65, 0.08, 0.04), roughness=0.4)
    rock_mat = solid_material(shader, (0.55, 0.50, 0.44), roughness=0.9)
    water_mat = solid_material(shader, (0.03, 0.08, 0.12), roughness=0.4, metallic=0.05)
    door_mat = solid_material(shader, (0.28, 0.18, 0.08), roughness=0.7)
    rail_mat = solid_material(shader, (0.25, 0.25, 0.25), roughness=0.3, metallic=0.5)
    dark_rock_mat = solid_material(shader, (0.38, 0.34, 0.30), roughness=0.9)
    wood_mat = solid_material(shader, (0.55, 0.33, 0.15), roughness=0.6)

    sphere_mesh = urenderer.geometry.mesh.get_mesh_sphere()
    cube_mesh = urenderer.geometry.mesh.get_mesh_cube()

    scene_root = Node("scene")
    scene_root.translation = np.array([0, -0.25, -6.5], np.float32)
    scene_root.rotation = np.array([12, 0, 0], np.float32)
    runtime.scene.add_child(scene_root)

    # === SKY DOME ===
    sky_shader = Shader("assets/sky.vs", "assets/sky.fs")
    sky_grad = create_sky_gradient()
    sky_tex = Texture(sky_grad, GL.GL_RGB, GL.GL_RGB)
    sky_mat = Material(sky_shader)
    sky_mat.set_texture(0, "skyTexture", sky_tex)
    sky_dome = Node("sky")
    sky_dome.render_data["mesh"] = sphere_mesh
    sky_dome.render_data["material"] = sky_mat
    sky_dome.scale = np.array([80, 80, 80], np.float32)
    runtime.scene.add_child(sky_dome)

    # === ISLAND ===
    rock = rock_mesh(2)
    island = Node("island")
    island.render_data["mesh"] = rock
    island.render_data["material"] = rock_mat
    island.scale = np.array([1.4, 0.5, 1.2], np.float32)
    island.translation = np.array([0, 0, 0], np.float32)
    scene_root.add_child(island)

    rock2 = Node("rock_side")
    rock2.render_data["mesh"] = rock
    rock2.render_data["material"] = dark_rock_mat
    rock2.scale = np.array([1.0, 0.3, 0.8], np.float32)
    rock2.translation = np.array([-0.7, -0.08, 0.5], np.float32)
    scene_root.add_child(rock2)

    rock3 = Node("rock_back")
    rock3.render_data["mesh"] = rock
    rock3.render_data["material"] = dark_rock_mat
    rock3.scale = np.array([0.9, 0.35, 0.7], np.float32)
    rock3.translation = np.array([0.6, -0.05, -0.4], np.float32)
    scene_root.add_child(rock3)

    # === GLB LIGHTHOUSE ===
    glb_lh = urenderer.geometry.mesh.load_glb("assets/external_meshes/low_poly_lighthouse.glb")
    glb_lh.translation = np.array([0.75, 0.35, 0.75], np.float32)
    glb_lh.scale = np.array([0.25, 0.25, 0.25], np.float32)
    glb_lh.rotation = np.array([0, -70, 0], np.float32)

    beacon = urenderer.node.Light(urenderer.node.LightType.POINT)
    beacon.light_color = np.array([1.0, 0.85, 0], np.float32)
    # debug shape for the light:
    # beacon.render_data["mesh"] = sphere_mesh
    # beacon.render_data["material"] = solid_material(shader, (1.0, 0, 0), roughness=0.2)
    beacon.translation = np.array([1.0, 0, 0.4], np.float32)
    beacon.scale = np.array([0.25, 0.25, 0.25], np.float32)
    beacon.light_reference_distance = 2.5
    beacon.callbacks = [update_beacon]

    # copy beacon to the other side of the tower:
    beacon2 = urenderer.node.Light(urenderer.node.LightType.POINT)
    beacon2.light_color = np.array([1.0, 0.85, 0], np.float32)
    # debug shape for the light:
    # beacon2.render_data["mesh"] = sphere_mesh
    # beacon2.render_data["material"] = solid_material(shader, (1.0, 0, 0), roughness=0.2)
    beacon2.translation = np.array([-1.0, 0, 0.4], np.float32)
    beacon2.scale = np.array([0.25, 0.25, 0.25], np.float32)
    beacon2.light_reference_distance = 2.5
    beacon2.callbacks = [update_beacon]

    nodes = deque([glb_lh])
    while nodes:
        n = nodes.pop()
        if "base" in n.name:
            n.render_data["material"] = red_mat
        elif n.name == "top tower_Material_0":
            n.render_data["material"] = white_mat
        elif n.name == "top tower":
            # n.rotation = np.array([-90, 70, 0], np.float32)
            n.add_child(beacon)
            n.add_child(beacon2)
            n.callbacks.append(lambda node, dt, t: setattr(node, "rotation", np.array([-90, 30 * t, 0], np.float32)))
        elif "door" in n.name:
            n.render_data["material"] = door_mat
        elif "raling" in n.name or "ladder" in n.name:
            n.render_data["material"] = rail_mat
        elif "stair" in n.name:
            n.render_data["material"] = white_mat
        nodes += n.children
    scene_root.add_child(glb_lh)

    # === BOAT ===
    boat_root = urenderer.geometry.mesh.load_glb("assets/external_meshes/stylized_low_poly_rowboat_with_paddles.glb")
    boat_root.translation = np.array([0.7, 0.00, 0.9], np.float32)
    boat_root.scale = np.array([0.013, 0.013, 0.013], np.float32)
    boat_root.rotation = np.array([0, 30, 0], np.float32)
    nodes = deque([boat_root])
    while nodes:
        n = nodes.pop()
        n.render_data["material"] = wood_mat
        nodes += n.children
    boat_root.callbacks = [update_boat]
    scene_root.add_child(boat_root)

    # === WATER ===
    water_mesh = grid_mesh(16.0, 24)
    water = Node("water")
    water.render_data["mesh"] = water_mesh
    water.render_data["material"] = water_mat
    water.translation = np.array([0, -0.05, 0], np.float32)
    water.render_data["subdiv"] = 24
    water.render_data["size"] = 16.0
    water.callbacks = [update_water]
    scene_root.add_child(water)
  
    fill_light = urenderer.node.Light(urenderer.node.LightType.DIRECTIONAL)
    # shape for debug:
    fill_light.rotation = np.array([25, 110, 0], np.float64)
    fill_light.light_color = np.array([0.7, 0.65, 1.0], np.float32)
    fill_light.light_intensity = 0.8
    runtime.scene.add_child(fill_light)

    # === RENDER ===
    video = True
    if video:
        runtime.loop(n=4000, capture=np.arange(0, 4000, 40, dtype=np.int32))
        urenderer.utils.image_to_video(NOME_DA_CENA, fps=30)
        urenderer.utils.clear_workdir(NOME_DA_CENA, image_only=True)
    else:
        runtime.loop(capture=[1])
