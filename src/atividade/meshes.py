from urenderer.geometry.mesh import Mesh
import numpy as np
from icosphere import icosphere

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