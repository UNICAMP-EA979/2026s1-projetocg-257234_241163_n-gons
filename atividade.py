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


def cylinder_body(r_bottom, r_top, height, segments):
    verts = []
    norms = []
    uvs = []
    idx = []
    for i in range(segments):
        a = 2 * np.pi * i / segments
        ca, sa = np.cos(a), np.sin(a)
        verts.append([ca * r_bottom, -height / 2, sa * r_bottom])
        verts.append([ca * r_top, height / 2, sa * r_top])
        n = np.array([ca, 0, sa], np.float32)
        n /= np.linalg.norm(n)
        norms.append(n)
        norms.append(n)
        uvs.append([i / segments, 0])
        uvs.append([i / segments, 1])
    for i in range(segments):
        b0 = 2 * i
        t0 = 2 * i + 1
        b1 = 2 * ((i + 1) % segments)
        t1 = 2 * ((i + 1) % segments) + 1
        idx += [b0, b1, t1, t1, t0, b0]
    return Mesh(
        np.array(verts, np.float32),
        np.array(idx, np.uint32),
        np.array(uvs, np.float32),
        normal=np.array(norms, np.float32),
    )


def capped_cylinder(r_bottom, r_top, height, segments):
    all_v, all_n, all_uv = [], [], []
    all_idx = []
    offset = 0

    # Body
    for i in range(segments):
        a = 2 * np.pi * i / segments
        ca, sa = np.cos(a), np.sin(a)
        all_v.append([ca * r_bottom, -height / 2, sa * r_bottom])
        all_v.append([ca * r_top, height / 2, sa * r_top])
        n = np.array([ca, 0, sa], np.float32)
        n /= np.linalg.norm(n)
        all_n.append(n)
        all_n.append(n)
        all_uv.append([i / segments, 0])
        all_uv.append([i / segments, 1])
    for i in range(segments):
        b0 = offset + 2 * i
        t0 = offset + 2 * i + 1
        b1 = offset + 2 * ((i + 1) % segments)
        t1 = offset + 2 * ((i + 1) % segments) + 1
        all_idx += [b0, b1, t1, t1, t0, b0]
    offset += 2 * segments

    # Bottom cap
    all_v.append([0, -height / 2, 0])
    all_n.append([0, -1, 0])
    all_uv.append([0.5, 0.5])
    c = offset
    offset += 1
    for i in range(segments):
        a = 2 * np.pi * i / segments
        ca, sa = np.cos(a), np.sin(a)
        all_v.append([ca * r_bottom, -height / 2, sa * r_bottom])
        all_n.append([0, -1, 0])
        all_uv.append([0.5 + 0.5 * ca, 0.5 + 0.5 * sa])
    for i in range(segments):
        all_idx += [c, offset + 1 + i, offset + 1 + (i + 1) % segments]
    offset += 1 + segments

    # Top cap
    all_v.append([0, height / 2, 0])
    all_n.append([0, 1, 0])
    all_uv.append([0.5, 0.5])
    c = offset
    offset += 1
    for i in range(segments):
        a = 2 * np.pi * i / segments
        ca, sa = np.cos(a), np.sin(a)
        all_v.append([ca * r_top, height / 2, sa * r_top])
        all_n.append([0, 1, 0])
        all_uv.append([0.5 + 0.5 * ca, 0.5 + 0.5 * sa])
    for i in range(segments):
        all_idx += [c, offset + 1 + (i + 1) % segments, offset + 1 + i]
    offset += 1 + segments

    return Mesh(
        np.array(all_v, np.float32),
        np.array(all_idx, np.uint32),
        np.array(all_uv, np.float32),
        normal=np.array(all_n, np.float32),
    )


def cone_mesh(radius, height, segments):
    all_v, all_n, all_uv = [], [], []
    all_idx = []
    offset = 0

    # Apex
    all_v.append([0, height / 2, 0])
    all_n.append([0, 1, 0])
    all_uv.append([0.5, 1.0])
    offset += 1

    # Base ring (sides)
    for i in range(segments):
        a = 2 * np.pi * i / segments
        ca, sa = np.cos(a), np.sin(a)
        all_v.append([ca * radius, -height / 2, sa * radius])
        n = np.array([ca, radius / height, sa], np.float32)
        n /= np.linalg.norm(n)
        all_n.append(n)
        all_uv.append([i / segments, 0])

    for i in range(segments):
        v1 = offset + i
        v2 = offset + (i + 1) % segments
        all_idx += [0, v1, v2]

    offset += segments

    # Base cap
    all_v.append([0, -height / 2, 0])
    all_n.append([0, -1, 0])
    all_uv.append([0.5, 0.5])
    c = offset
    offset += 1
    for i in range(segments):
        a = 2 * np.pi * i / segments
        ca, sa = np.cos(a), np.sin(a)
        all_v.append([ca * radius, -height / 2, sa * radius])
        all_n.append([0, -1, 0])
        all_uv.append([0.5 + 0.5 * ca, 0.5 + 0.5 * sa])
    for i in range(segments):
        all_idx += [c, offset + 1 + i, offset + 1 + (i + 1) % segments]
    offset += 1 + segments

    return Mesh(
        np.array(all_v, np.float32),
        np.array(all_idx, np.uint32),
        np.array(all_uv, np.float32),
        normal=np.array(all_n, np.float32),
    )


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


def update_water(node, dt, t):
    mesh = node.render_data["mesh"]
    verts = mesh.vertex.copy().reshape(-1, 3)
    sd = node._water_subdiv
    sz = node._water_size
    half = sz / 2
    for z in range(sd + 1):
        for x in range(sd + 1):
            idx = z * (sd + 1) + x
            vx = -half + sz * x / sd
            vz = -half + sz * z / sd
            verts[idx, 1] = 0.03 * np.sin(2.5 * vx + 3.5 * t) + 0.025 * np.sin(1.8 * vz + 2.2 * t + 1.0)
    mesh.vertex = verts.flatten()


def update_cloud(node, dt, t):
    speed = getattr(node, "_cloud_speed", 0.02)
    node.translation[0] += speed * max(dt, 0)



def create_sky_gradient():
    h = 256
    grad = np.zeros((h, 1, 3), dtype=np.uint8)
    top = np.array([0.02, 0.02, 0.18])
    mid = np.array([0.55, 0.18, 0.30])
    horizon = np.array([1.0, 0.50, 0.12])
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


def beam_mesh(length, radius, segments):
    verts = [[0, 0, 0]]
    uvs = [[0.5, 1.0]]
    slope = length / np.sqrt(length ** 2 + radius ** 2)
    radial = radius / np.sqrt(length ** 2 + radius ** 2)
    norms = [np.array([1, 0, 0], np.float32)]
    for i in range(segments):
        a = 2 * np.pi * i / segments
        ca, sa = np.cos(a), np.sin(a)
        verts.append([length, ca * radius, sa * radius])
        norms.append(np.array([slope, ca * radial, sa * radial], np.float32))
        uvs.append([i / segments, 0])
    idx = []
    for i in range(segments):
        v1 = 1 + i
        v2 = 1 + (i + 1) % segments
        idx += [0, v1, v2]
    return Mesh(
        np.array(verts, np.float32),
        np.array(idx, np.uint32),
        np.array(uvs, np.float32),
        normal=np.array(norms, np.float32),
    )


NOME_DA_CENA = "lighthouse_scene"

if __name__ == "__main__":
    urenderer.utils.clear_workdir(NOME_DA_CENA)
    renderer = urenderer.renderer.OpenGLRenderer(1920, 1080)
    renderer.background_color = np.array([0.02, 0.02, 0.18, 1.0], np.float32)
    renderer.ambient_color = np.array([0.15, 0.12, 0.18], dtype=np.float32)
    runtime = urenderer.application.Runtime(renderer, name=NOME_DA_CENA)
    runtime.camera.vertical_fov = 38.0

    shader = Shader("assets/vertex.vs", "assets/05-fragment.fs")

    white_mat = solid_material(shader, (0.96, 0.96, 0.93), roughness=0.6)
    red_mat = solid_material(shader, (0.85, 0.15, 0.10), roughness=0.5)
    roof_mat = solid_material(shader, (0.65, 0.08, 0.04), roughness=0.4)
    lantern_mat = solid_material(shader, (1.0, 0.95, 0.55), roughness=0.2, metallic=0.3)
    rock_mat = solid_material(shader, (0.55, 0.50, 0.44), roughness=0.9)
    water_mat = solid_material(shader, (0.15, 0.55, 0.78), roughness=0.25, metallic=0.1)
    cloud_mat = solid_material(shader, (1.0, 1.0, 1.0), roughness=0.95)
    window_mat = solid_material(shader, (0.75, 0.88, 1.0), roughness=0.1)
    door_mat = solid_material(shader, (0.28, 0.18, 0.08), roughness=0.7)
    rail_mat = solid_material(shader, (0.25, 0.25, 0.25), roughness=0.3, metallic=0.5)
    dark_rock_mat = solid_material(shader, (0.38, 0.34, 0.30), roughness=0.9)
    beam_mat = solid_material(shader, (1.0, 0.85, 0.2), roughness=0.1, metallic=0.0)

    blackTextureR = Texture(np.zeros((1, 1), np.uint8), GL.GL_RED, GL.GL_R8)

    brick_color = Texture.load_file("assets/external_materials/Bricks104_1K-JPG/Bricks104_1K-JPG_Color.jpg",
                                    srgb=True, drop_alpha=True)
    brick_roughness = Texture.load_file("assets/external_materials/Bricks104_1K-JPG/Bricks104_1K-JPG_Roughness.jpg",
                                        drop_alpha=True)
    brick_mat = Material(shader)
    brick_mat.set_texture(0, "baseColorTexture", brick_color)
    brick_mat.set_texture(1, "metallicTexture", blackTextureR)
    brick_mat.set_texture(2, "roughnessTexture", brick_roughness)
    brick_mat.set_uniform("tiling", 2.0)

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

    # === LIGHTHOUSE ===
    lh = Node("lighthouse")
    lh.translation = np.array([0, 0.35, 0], np.float32)
    scene_root.add_child(lh)

    tower_mesh = cylinder_body(0.55, 0.34, 1.5, 8)
    tower = Node("tower")
    tower.render_data["mesh"] = tower_mesh
    tower.render_data["material"] = brick_mat
    tower.translation = np.array([0, 0.75, 0], np.float32)
    lh.add_child(tower)

    stripe_mesh = capped_cylinder(0.39, 0.33, 0.13, 8)
    s1 = Node("stripe1")
    s1.render_data["mesh"] = stripe_mesh
    s1.render_data["material"] = red_mat
    s1.translation = np.array([0, 1.08, 0], np.float32)
    lh.add_child(s1)

    s2 = Node("stripe2")
    s2.render_data["mesh"] = stripe_mesh
    s2.render_data["material"] = red_mat
    s2.translation = np.array([0, 0.45, 0], np.float32)
    lh.add_child(s2)

    balcony = Node("balcony")
    balcony.render_data["mesh"] = capped_cylinder(0.44, 0.44, 0.05, 8)
    balcony.render_data["material"] = white_mat
    balcony.translation = np.array([0, 1.50, 0], np.float32)
    lh.add_child(balcony)

    for i in range(8):
        a = 2 * np.pi * i / 8
        post = Node(f"rail_{i}")
        post.render_data["mesh"] = cube_mesh
        post.render_data["material"] = rail_mat
        post.translation = np.array([0.41 * np.cos(a), 1.57, 0.41 * np.sin(a)], np.float32)
        post.scale = np.array([0.025, 0.08, 0.025], np.float32)
        lh.add_child(post)

    lantern = Node("lantern")
    lantern.render_data["mesh"] = capped_cylinder(0.32, 0.32, 0.22, 8)
    lantern.render_data["material"] = lantern_mat
    lantern.translation = np.array([0, 1.66, 0], np.float32)
    lh.add_child(lantern)

    roof = Node("roof")
    roof.render_data["mesh"] = cone_mesh(0.37, 0.30, 8)
    roof.render_data["material"] = roof_mat
    roof.translation = np.array([0, 1.86, 0], np.float32)
    lh.add_child(roof)

    finial = Node("finial")
    finial.render_data["mesh"] = sphere_mesh
    finial.render_data["material"] = roof_mat
    finial.translation = np.array([0, 2.08, 0], np.float32)
    finial.scale = np.array([0.05, 0.05, 0.05], np.float32)
    lh.add_child(finial)

    door = Node("door")
    door.render_data["mesh"] = cube_mesh
    door.render_data["material"] = door_mat
    door.translation = np.array([0, 0.10, 0.555], np.float32)
    door.scale = np.array([0.18, 0.22, 0.02], np.float32)
    lh.add_child(door)

    for wy in [0.65, 0.95]:
        w = Node(f"win_{wy}")
        w.render_data["mesh"] = cube_mesh
        w.render_data["material"] = window_mat
        w.translation = np.array([0, wy, 0.555], np.float32)
        w.scale = np.array([0.10, 0.12, 0.02], np.float32)
        lh.add_child(w)

    # Small rocks at base
    for ri in range(5):
        a = 2 * np.pi * ri / 5 + 0.3
        r = 0.5 + 0.15 * np.sin(ri * 2.1)
        sr = Node(f"small_rock_{ri}")
        sr.render_data["mesh"] = sphere_mesh
        sr.render_data["material"] = dark_rock_mat
        sr.translation = np.array([r * np.cos(a), -0.08, r * np.sin(a)], np.float32)
        sr.scale = np.array([0.10, 0.06, 0.08], np.float32)
        lh.add_child(sr)

    # === WATER ===
    water_mesh = grid_mesh(16.0, 24)
    water = Node("water")
    water.render_data["mesh"] = water_mesh
    water.render_data["material"] = water_mat
    water.translation = np.array([0, -0.05, 0], np.float32)
    water._water_subdiv = 24
    water._water_size = 16.0
    water.callbacks = [update_water]
    scene_root.add_child(water)

    # === CLOUDS ===
    cloud_positions = [
        (-1.8, 1, -3.0, 0.9, 0.008),
        (0.3, 1, -3.8, 0.7, 0.012),
        (2.2, 1, -2.5, 0.8, 0.006),
        (-1.2, 1, -4.2, 0.6, 0.015),
        (1.5, 1, -4.0, 0.5, 0.010),
        (-2.5, 1, -1.5, 0.5, 0.004),
    ]

    for ci, (cx, cy, cz, cs, spd) in enumerate(cloud_positions):
        croot = Node(f"cloud_{ci}")
        croot.translation = np.array([cx, cy, cz], np.float32)
        croot._cloud_speed = spd
        croot.callbacks = [update_cloud]

        parts = [
            (0, 0, 0, 1.0),
            (0.35, 0.06, 0.15, 0.65),
            (-0.30, -0.04, -0.12, 0.60),
            (0.12, 0.10, -0.28, 0.50),
            (-0.18, -0.08, 0.30, 0.45),
        ]
        for pi, (ox, oy, oz, ps) in enumerate(parts):
            p = Node(f"c{ci}_p{pi}")
            p.render_data["mesh"] = sphere_mesh
            p.render_data["material"] = cloud_mat
            p.translation = np.array([ox * cs, oy * cs, oz * cs], np.float32)
            p.scale = np.array([ps * cs * 0.32, ps * cs * 0.18, ps * cs * 0.26], np.float32)
            croot.add_child(p)

        runtime.scene.add_child(croot)

    # === LIGHTS ===
    sun = urenderer.node.Light(urenderer.node.LightType.DIRECTIONAL)
    sun.rotation = np.array([15, -40, 0], np.float64)
    sun.light_color = np.array([1.0, 0.55, 0.2], np.float32)
    sun.light_intensity = 2.0
    runtime.scene.add_child(sun)

    fill_light = urenderer.node.Light(urenderer.node.LightType.DIRECTIONAL)
    fill_light.rotation = np.array([25, 110, 0], np.float64)
    fill_light.light_color = np.array([0.55, 0.65, 1.0], np.float32)
    fill_light.light_intensity = 0.8
    runtime.scene.add_child(fill_light)

    beacon = urenderer.node.Light(urenderer.node.LightType.POINT)
    beacon.light_color = np.array([1.0, 0.85, 0.5], np.float32)
    beacon.light_intensity = 10.0
    beacon.light_reference_distance = 2.5
    # lantern.add_child(beacon)

    # === RENDER ===
    video = True
    if video:
        runtime.loop(n=4000, capture=np.arange(0, 4000, 40, dtype=np.int32))
        urenderer.utils.image_to_video(NOME_DA_CENA, fps=30)
        urenderer.utils.clear_workdir(NOME_DA_CENA, image_only=True)
    else:
        runtime.loop(capture=[1])
