import pygame as pg
import sys
import numpy as np
from settings import WIN_RES, WIDTH, HEIGHT
from mode7 import *
from enemies import Game

def show_menu(screen):
    pg.init()
    clock = pg.time.Clock()

    background = pg.image.load("textures/background.png")
    background = pg.transform.scale(background, WIN_RES)

    # Definiši klik-zones (moraš fino naštimati po slici)
    play_rect = pg.Rect(WIDTH // 2 - 120, 290, 240, 60)
    settings_rect = pg.Rect(WIDTH // 2 - 120, 410, 240, 60)
    quit_rect = pg.Rect(WIDTH // 2 - 120, 530, 240, 60)

    while True:
        screen.blit(background, (0, 0))
        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(pg.mouse.get_pos()):
                    return  # start game
                elif settings_rect.collidepoint(pg.mouse.get_pos()):
                    print("Settings clicked!")  # još nije implementirano
                elif quit_rect.collidepoint(pg.mouse.get_pos()):
                    pg.quit()
                    sys.exit()

        clock.tick(60)

class App:
    def __init__(self):
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.mode7 = Mode7(self)
        self.game = Game(self.mode7)
        self.font = pg.font.SysFont('consolas', 28)
        self.big_font = pg.font.SysFont('consolas', 64)

    def update(self):
        player_pos = self.mode7.pos
        self.mode7.update()
        self.game.update(player_pos)
        self.clock.tick()
        pg.display.set_caption(f'{self.clock.get_fps():.1f}')

    def draw(self):
        self.mode7.draw()
        self.game.draw(self.screen)
        self.draw_hud()
        if self.game.game_over:
            self.draw_game_over()
        pg.display.flip()

    def check_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                direction = np.array([np.cos(self.mode7.angle), np.sin(self.mode7.angle)])
                if not self.game.game_over:
                    self.game.shoot(self.mode7.pos, self.mode7.angle)
            elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                if self.game.game_over:
                    self.mode7.pos = np.array([0.0, 0.0])
                    self.mode7.angle = 0.0
                    self.mode7.alt = 1.0
                    self.game.reset()

    def run(self):
        show_menu(self.screen)  # Pokreni meni prije igre
        while True:
            self.check_event()
            self.update()
            self.draw()

    def draw_hud(self):
        # HP bar
        max_w = 240
        hp_ratio = self.game.player_hp / self.game.player_max_hp
        bar_x, bar_y, bar_h = 20, 20, 18
        pg.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, max_w, bar_h))
        pg.draw.rect(self.screen, (200, 70, 50), (bar_x, bar_y, int(max_w * hp_ratio), bar_h))
        hp_text = self.font.render(f'HP: {self.game.player_hp}/{self.game.player_max_hp}', True, (230, 230, 230))
        self.screen.blit(hp_text, (bar_x, bar_y + 24))

        # Score
        score_text = self.font.render(f'Score: {self.game.score}', True, (230, 230, 230))
        self.screen.blit(score_text, (WIDTH - 200, 20))

    def draw_game_over(self):
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render('GAME OVER', True, (230, 200, 180))
        tip = self.font.render('Pritisni R za restart', True, (230, 230, 230))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        tip_rect = tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.screen.blit(text, rect)
        self.screen.blit(tip, tip_rect)

if __name__ == '__main__':
    app = App()
    app.run()