import pygame as pg
import numpy as np
from settings import *
from numba import njit, prange


class Mode7:
    def __init__(self, app):
        self.app = app
        self.floor_tex = pg.image.load('textures/ground_rail_lowres.png').convert()
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)

        self.ceil_tex = pg.image.load('textures/sky_night_fullres.png').convert()
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)

        self.screen_array = pg.surfarray.array3d(pg.Surface(WIN_RES))

        self.alt = 1.0
        self.angle = 0.0
        self.pos = np.array([0.0, 0.0])

    def update(self):
        self.movement()
        self.screen_array = self.render_frame(self.floor_array, self.ceil_array, self.screen_array,
                                              self.tex_size, self.angle, self.pos, self.alt)

    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def project(self, world_pos):
        """Pretvara svjetske koordinate (x, y) u zaslonske koordinate (screen_x, screen_y) uz skaliranje veličine"""
        relative_pos = world_pos - self.pos
        rotated_x = relative_pos[0] * np.cos(self.angle) - relative_pos[1] * np.sin(self.angle)
        rotated_y = relative_pos[0] * np.sin(self.angle) + relative_pos[1] * np.cos(self.angle)

        if rotated_y <= 0.1:  # Spriječi dijeljenje s nulom i potpuno nestajanje objekata
            return -1000, -1000, 0  # Vrati poziciju izvan ekrana

        screen_x = int(WIDTH / 2 + rotated_x / rotated_y * WIDTH / 4)
        screen_y = int(HEIGHT / 2 - self.alt * 50 / rotated_y)

        # Skaliranje veličine ovisno o udaljenosti (bliže = veće)
        scale = max(5, int(100 / rotated_y))  # Spriječi prenisku vrijednost skaliranja

        return screen_x, screen_y, scale

    @staticmethod
    @njit(fastmath=True, parallel=True)
    def render_frame(floor_array, ceil_array, screen_array, tex_size, angle, player_pos, alt):

        sin, cos = np.sin(angle), np.cos(angle)

        # Iteriranje kroz zaslonski niz
        for i in prange(WIDTH):
            new_alt = alt
            for j in range(HALF_HEIGHT, HEIGHT):
                x = HALF_WIDTH - i
                y = j + FOCAL_LEN
                z = j - HALF_HEIGHT + new_alt

                # Rotacija
                px = (x * cos - y * sin)
                py = (x * sin + y * cos)

                # Projekcija i transformacija poda
                floor_x = px / z - player_pos[1]
                floor_y = py / z + player_pos[0]

                # Pozicija i boja poda
                floor_pos = int(floor_x * SCALE % tex_size[0]), int(floor_y * SCALE % tex_size[1])
                floor_col = floor_array[floor_pos]

                # Projekcija i transformacija neba
                ceil_x = alt * px / z - player_pos[1] * 0.3
                ceil_y = alt * py / z + player_pos[0] * 0.3

                # Pozicija i boja neba
                ceil_pos = int(ceil_x * SCALE % tex_size[0]), int(ceil_y * SCALE % tex_size[1])
                ceil_col = ceil_array[ceil_pos]

                # Sjenčenje
                # depth = 4 * abs(z) / HALF_HEIGHT
                depth = min(max(2.5 * (abs(z) / HALF_HEIGHT), 0), 1)
                fog = (1 - depth) * 230

                floor_col = (floor_col[0] * depth + fog,
                             floor_col[1] * depth + fog,
                             floor_col[2] * depth + fog)

                ceil_col = (ceil_col[0] * depth + fog,
                            ceil_col[1] * depth + fog,
                            ceil_col[2] * depth + fog)

                # Ispunjavanje zaslonskog niza
                screen_array[i, j] = floor_col
                screen_array[i, -j] = ceil_col

                # Sljedeća dubina
                new_alt += alt

        return screen_array

    def movement(self):
        sin_a = np.sin(self.angle)
        cos_a = np.cos(self.angle)
        dx, dy = 0, 0
        speed_sin = SPEED * sin_a
        speed_cos = SPEED * cos_a

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            dx += -speed_sin
            dy += speed_cos
        self.pos[0] += dx
        self.pos[1] += dy

        if keys[pg.K_LEFT]:
            self.angle -= SPEED
        if keys[pg.K_RIGHT]:
            self.angle += SPEED

        if keys[pg.K_q]:
            self.alt += SPEED
        if keys[pg.K_e]:
            self.alt -= SPEED
        self.alt = min(max(self.alt, 0.3), 4.0)
