import pygame
import numpy as np
import math
from math import cos, sin

pygame.init()

SCR_WIDTH, SCR_HEIGHT = 1280, 720
F = 2


class Camera:
    def __init__(self, pos=np.array([0, 0, 0], dtype=float), yaw=math.pi / 2, pitch=0,
                 sensitivity=0.002, speed=0.1, screen_center=(SCR_WIDTH // 2, SCR_HEIGHT // 2)):
        self.pos = pos
        self.yaw = yaw
        self.pitch = pitch
        self.sensitivity = sensitivity
        self.speed = speed
        self.screen_center = screen_center
        self.up = np.array([0, 1, 0])
        self._update_vectors()

    def _update_vectors(self):
        self.front = np.array([
            cos(self.yaw) * cos(self.pitch),
            sin(self.pitch),
            sin(self.yaw) * cos(self.pitch)
        ])
        self.front /= np.linalg.norm(self.front)
        self.right = np.cross(self.front, self.up)
        self.right /= np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)
        self.up /= np.linalg.norm(self.up)

    def handle_mouse_motion(self, mouse_pos):
        delta_x = mouse_pos[0] - self.screen_center[0]
        delta_y = mouse_pos[1] - self.screen_center[1]
        self.yaw += delta_x * self.sensitivity
        self.pitch -= delta_y * self.sensitivity
        max_pitch = math.radians(89)
        self.pitch = max(-max_pitch, min(max_pitch, self.pitch))
        self._update_vectors()

    def handle_keyboard(self, keys):
        if keys[pygame.K_w]:
            self.pos += self.front * self.speed
        if keys[pygame.K_s]:
            self.pos -= self.front * self.speed
        if keys[pygame.K_a]:
            self.pos -= self.right * self.speed
        if keys[pygame.K_d]:
            self.pos += self.right * self.speed
        if keys[pygame.K_SPACE] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.pos += self.up * self.speed
        if keys[pygame.K_SPACE] and not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.pos -= self.up * self.speed

    def get_view_matrix(self):
        r = self.right
        u = self.up
        f = self.front
        c = self.pos
        return np.array([
            [r[0], r[1], r[2], -np.dot(r, c)],
            [u[0], u[1], u[2], -np.dot(u, c)],
            [-f[0], -f[1], -f[2], np.dot(f, c)],
            [0, 0, 0, 1]
        ])


class Cube:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges
        self.x_rot = math.radians(0.3)
        self.y_rot = math.radians(0.5)
        self.z_rot = math.radians(0.7)

    def rotate(self):
        x_mat = np.array([
            [1, 0, 0],
            [0, cos(self.x_rot), -sin(self.x_rot)],
            [0, sin(self.x_rot), cos(self.x_rot)]
        ])

        y_mat = np.array([
            [cos(self.y_rot), 0, sin(self.y_rot)],
            [0, 1, 0],
            [-sin(self.y_rot), 0, cos(self.y_rot)]
        ])

        z_mat = np.array([
            [cos(self.z_rot), -sin(self.z_rot), 0],
            [sin(self.z_rot), cos(self.z_rot), 0],
            [0, 0, 1]
        ])

        rotated = [(z_mat @ y_mat @ x_mat) @ v for v in self.vertices]
        translated = [v + np.array([0, 0, 5]) for v in rotated]

        self.x_rot += math.radians(0.3)
        self.y_rot += math.radians(0.5)
        self.z_rot += math.radians(0.7)

        return translated


def project(x, y, z, scr_width=SCR_WIDTH, scr_height=SCR_HEIGHT, f=F):
    x_proj = f * x / z
    y_proj = -f * y / z
    return [x_proj * 100 + scr_width // 2, y_proj * 100 + scr_height // 2]


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
        pygame.display.set_caption("3D Rotating Cube")

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

        self.cube = Cube(vertices, edges)
        self.camera = Camera()

        self.clock = pygame.time.Clock()
        pygame.mouse.set_pos(self.camera.screen_center)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            self.screen.fill((0, 0, 0))

            keys = pygame.key.get_pressed()
            self.camera.handle_keyboard(keys)

            mouse_pos = pygame.mouse.get_pos()
            self.camera.handle_mouse_motion(mouse_pos)
            pygame.mouse.set_pos(self.camera.screen_center)

            translated_vertices = self.cube.rotate()

            V = self.camera.get_view_matrix()

            camera_vertices = []
            for v in translated_vertices:
                v_x, v_y, v_z = v
                v_camera = V @ np.array([v_x, v_y, v_z, 1])
                camera_vertices.append(v_camera[:3])

            projected = [project(*v.tolist()) for v in camera_vertices]

            for edge in self.cube.edges:
                start, end = edge
                pygame.draw.line(
                    self.screen,
                    (255, 255, 255),
                    (projected[start][0], projected[start][1]),
                    (projected[end][0], projected[end][1]),
                    2
                )

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    app = App()
    app.run()
