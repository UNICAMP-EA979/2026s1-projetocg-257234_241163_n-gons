from collections import deque

import numpy as np
import urenderer
from OpenGL import GL
from urenderer.node import Node
from urenderer.renderer.opengl import Material, Shader, Texture

from src.atividade import *


NOME_DA_CENA = "lighthouse_scene"

if __name__ == "__main__":
    urenderer.utils.clear_workdir(NOME_DA_CENA)
    renderer = urenderer.renderer.OpenGLRenderer(1920, 1080)
    renderer.background_color = np.array([0.05, 0.08, 0.25, 1.0], np.float32)
    renderer.ambient_color = np.array([0.15, 0.12, 0.18], dtype=np.float32)
    runtime = urenderer.application.Runtime(renderer, name=NOME_DA_CENA)
    runtime.camera.vertical_fov = 45.0

    shader = Shader("assets/vertex.vs", "assets/05-fragment.fs")
    mats = create_materials(shader)

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
    island.render_data["material"] = mats["rock_mat"]
    island.scale = np.array([1.4, 0.5, 1.2], np.float32)
    island.translation = np.array([0, 0, 0], np.float32)
    scene_root.add_child(island)

    rock2 = Node("rock_side")
    rock2.render_data["mesh"] = rock
    rock2.render_data["material"] = mats["dark_rock_mat"]
    rock2.scale = np.array([1.0, 0.3, 0.8], np.float32)
    rock2.translation = np.array([-0.7, -0.08, 0.5], np.float32)
    scene_root.add_child(rock2)

    rock3 = Node("rock_back")
    rock3.render_data["mesh"] = rock
    rock3.render_data["material"] = mats["dark_rock_mat"]
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
    beacon.translation = np.array([1.0, 0, 0.4], np.float32)
    beacon.scale = np.array([0.25, 0.25, 0.25], np.float32)
    beacon.light_reference_distance = 2.5
    beacon.callbacks = [update_beacon]

    beacon2 = urenderer.node.Light(urenderer.node.LightType.POINT)
    beacon2.light_color = np.array([1.0, 0.85, 0], np.float32)
    beacon2.translation = np.array([-1.0, 0, 0.4], np.float32)
    beacon2.scale = np.array([0.25, 0.25, 0.25], np.float32)
    beacon2.light_reference_distance = 2.5
    beacon2.callbacks = [update_beacon]

    nodes = deque([glb_lh])
    while nodes:
        n = nodes.pop()
        if "base" in n.name:
            n.render_data["material"] = mats["red_mat"]
        elif n.name == "top tower_Material_0":
            n.render_data["material"] = mats["white_mat"]
        elif n.name == "top tower":
            n.add_child(beacon)
            n.add_child(beacon2)
            n.callbacks.append(lambda node, dt, t: setattr(node, "rotation", np.array([-90, 30 * t, 0], np.float32)))
        elif "door" in n.name:
            n.render_data["material"] = mats["door_mat"]
        elif "raling" in n.name or "ladder" in n.name:
            n.render_data["material"] = mats["rail_mat"]
        elif "stair" in n.name:
            n.render_data["material"] = mats["white_mat"]
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
        n.render_data["material"] = mats["wood_mat"]
        nodes += n.children
    boat_root.callbacks = [update_boat]
    scene_root.add_child(boat_root)

    # === WATER ===
    water_mesh = grid_mesh(16.0, 24)
    water = Node("water")
    water.render_data["mesh"] = water_mesh
    water.render_data["material"] = mats["water_mat"]
    water.translation = np.array([0, -0.05, 0], np.float32)
    water.render_data["subdiv"] = 24
    water.render_data["size"] = 16.0
    water.callbacks = [update_water]
    scene_root.add_child(water)

    fill_light = urenderer.node.Light(urenderer.node.LightType.DIRECTIONAL)
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
