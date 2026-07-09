import numpy as np
from urenderer.renderer.opengl import Material, Shader, Texture
from OpenGL import GL


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


def create_materials(shader):
    return {
        "white_mat": solid_material(shader, (0.96, 0.96, 0.93), roughness=0.6),
        "red_mat": solid_material(shader, (0.85, 0.15, 0.10), roughness=0.5),
        "roof_mat": solid_material(shader, (0.65, 0.08, 0.04), roughness=0.4),
        "rock_mat": solid_material(shader, (0.55, 0.50, 0.44), roughness=0.9),
        "water_mat": solid_material(shader, (0.03, 0.08, 0.12), roughness=0.4, metallic=0.01),
        "door_mat": solid_material(shader, (0.28, 0.18, 0.08), roughness=0.7),
        "rail_mat": solid_material(shader, (0.25, 0.25, 0.25), roughness=0.3, metallic=0.5),
        "dark_rock_mat": solid_material(shader, (0.38, 0.34, 0.30), roughness=0.9),
        "wood_mat": solid_material(shader, (0.55, 0.33, 0.15), roughness=0.6),
    }