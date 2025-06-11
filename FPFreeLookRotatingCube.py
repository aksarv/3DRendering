import pygame
import numpy as np
import math
from math import cos, sin
import copy

pygame.init()

f = 2


def project(x, y, z):
    x_proj = f * x / z
    y_proj = -f * y / z
    return [x_proj * 100 + scr_width // 2, y_proj * 100 + scr_height // 2]


scr_width, scr_height = 1280, 720
scr = pygame.display.set_mode((scr_width, scr_height))

vertices = [
    np.array([-1, -1, -1]),
    np.array([-1, -1, 1]),
    np.array([-1, 1, -1]),
    np.array([-1, 1, 1]),
    np.array([1, -1, -1]),
    np.array([1, -1, 1]),
    np.array([1, 1, -1]),
    np.array([1, 1, 1]),
]

edges = [
    (0, 1), (0, 2), (0, 4),
    (1, 3), (1, 5),
    (2, 3), (2, 6),
    (3, 7),
    (4, 5), (4, 6),
    (5, 7),
    (6, 7)
]

x_rot = math.radians(0.3)
y_rot = math.radians(0.5)
z_rot = math.radians(0.7)

SENSITIVITY = 0.002
SPEED = 0.1

F = np.array([0, 0, 1])
up = np.array([0, 1, 0])
R = np.cross(F, up)
U = np.cross(R, F)

C = np.array([0, 0, 0], dtype=float)

yaw = math.pi / 2
pitch = 0

clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    scr.fill((0, 0, 0))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        C += F * SPEED
    if keys[pygame.K_s]:
        C -= F * SPEED
    if keys[pygame.K_a]:
        C -= R * SPEED
    if keys[pygame.K_d]:
        C += R * SPEED

    x_mat = np.array(
        [
            [1, 0, 0],
            [0, cos(x_rot), -sin(x_rot)],
            [0, sin(x_rot), cos(x_rot)]
        ]
    )

    y_mat = np.array(
        [
            [cos(y_rot), 0, sin(y_rot)],
            [0, 1, 0],
            [-sin(y_rot), 0, cos(y_rot)]
        ]
    )

    z_mat = np.array(
        [
            [cos(z_rot), -sin(z_rot), 0],
            [sin(z_rot), cos(z_rot), 0],
            [0, 0, 1]
        ]
    )

    rotated_vertices = [(z_mat @ y_mat @ x_mat) @ v for v in vertices]
    translated_vertices = [v + np.array([0, 0, 5]) for v in rotated_vertices]

    mouse_x, mouse_y = pygame.mouse.get_pos()
    delta_x = mouse_x - scr_width // 2
    delta_y = mouse_y - scr_height // 2
    pygame.mouse.set_pos(scr_width // 2, scr_height // 2)

    yaw += delta_x * SENSITIVITY
    pitch -= delta_y * SENSITIVITY

    pitch = max(-math.radians(89), min(math.radians(89), pitch))

    F = np.array([cos(yaw) * cos(pitch),
                  sin(pitch),
                  sin(yaw) * cos(pitch)])
    F = F / np.linalg.norm(F)
    R = np.cross(F, up)
    R = R / np.linalg.norm(R)
    U = np.cross(R, F)
    U = U / np.linalg.norm(U)

    r_x, r_y, r_z = R
    u_x, u_y, u_z = U
    f_x, f_y, f_z = F

    V = np.array([
        [r_x, r_y, r_z, np.dot(-R, C)],
        [u_x, u_y, u_z, np.dot(-U, C)],
        [-f_x, -f_y, -f_z, np.dot(F, C)],
        [0, 0, 0, 1]
    ])

    new_vertices = []
    for v in translated_vertices:
        v_x, v_y, v_z = v
        new_vertices.append(V @ np.array([v_x, v_y, v_z, 1]))

    camera_vertices = []
    for v in new_vertices:
        v_x, v_y, v_z, _ = v
        camera_vertices.append(np.array([v_x, v_y, v_z]))

    proj = [project(*v.tolist()) for v in camera_vertices]
    x_rot += math.radians(0.3)
    y_rot += math.radians(0.5)
    z_rot += math.radians(0.7)

    for x, y in edges:
        pygame.draw.line(scr, (255, 255, 255), (proj[x][0], proj[x][1]), (proj[y][0], proj[y][1]), 2)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
