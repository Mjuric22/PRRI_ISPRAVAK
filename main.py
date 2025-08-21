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

    title_font = pg.font.SysFont('consolas', 64)
    menu_font = pg.font.SysFont('consolas', 32)
    small_font = pg.font.SysFont('consolas', 20)

    def draw_button(text, center_y, hovered):
        w, h = 280, 64
        rect = pg.Rect(0, 0, w, h)
        rect.center = (WIDTH // 2, center_y)
        base_col = (40, 40, 40)
        hover_col = (80, 70, 50)
        border_col = (200, 170, 120)
        fill = hover_col if hovered else base_col
        pg.draw.rect(screen, fill, rect, border_radius=10)
        pg.draw.rect(screen, border_col, rect, width=2, border_radius=10)
        label = menu_font.render(text, True, (230, 220, 200))
        screen.blit(label, label.get_rect(center=rect.center))
        return rect

    def draw_overlay():
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

    in_about = False

    while True:
        screen.blit(background, (0, 0))
        draw_overlay()

        if not in_about:
            title = title_font.render('Airship Shoot \'Em Up', True, (230, 220, 200))
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160)))

            mx, my = pg.mouse.get_pos()
            play_rect = draw_button('Play', HEIGHT // 2 - 40, hovered=pg.Rect(WIDTH // 2 - 140, HEIGHT // 2 - 40 - 32, 280, 64).collidepoint(mx, my))
            about_rect = draw_button('About', HEIGHT // 2 + 40, hovered=pg.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 40 - 32, 280, 64).collidepoint(mx, my))
            exit_rect = draw_button('Exit', HEIGHT // 2 + 120, hovered=pg.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 120 - 32, 280, 64).collidepoint(mx, my))

            tip = small_font.render('WASD move | Arrows rotate | Space shoot | Esc exit', True, (210, 200, 180))
            screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if play_rect.collidepoint(pg.mouse.get_pos()):
                        return
                    elif about_rect.collidepoint(pg.mouse.get_pos()):
                        in_about = True
                    elif exit_rect.collidepoint(pg.mouse.get_pos()):
                        pg.quit()
                        sys.exit()
        else:
            header = title_font.render('About Game', True, (230, 220, 200))
            screen.blit(header, header.get_rect(center=(WIDTH // 2, 140)))

            about_lines = [
                "A fast-paced steampunk shoot 'em up with zeppelins and airship combat.",
                "Fly over Mode7-rendered landscapes, dodge enemy fire, and defeat bosses.",
                "Collect power-ups, upgrade your weapons, and survive increasingly", 
                "challenging enemy formations in the skies.",
            ]
            y = 220
            for line in about_lines:
                label = menu_font.render(line, True, (220, 210, 190))
                screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))
                y += 40

            mx, my = pg.mouse.get_pos()
            back_rect = draw_button('Back', HEIGHT - 120, hovered=pg.Rect(WIDTH // 2 - 140, HEIGHT - 120 - 32, 280, 64).collidepoint(mx, my))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    in_about = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if back_rect.collidepoint(pg.mouse.get_pos()):
                        in_about = False

        pg.display.flip()
        clock.tick(60)

class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(WIN_RES, pg.SCALED | pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.mode7 = Mode7(self)
        self.game = Game(self.mode7)
        self.font = pg.font.SysFont('consolas', 28)
        self.big_font = pg.font.SysFont('consolas', 64)
        self.running = True

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
            if event.type == pg.QUIT:
                print('QUIT event zaprimljen - izlazim iz glavne petlje')
                self.running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                print('ESC pritisnut - izlaz onemogućen radi debugiranja')
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
        while self.running:
            self.check_event()
            self.update()
            self.draw()
        pg.quit()

    def draw_hud(self):
        # Traka zdravlja (HP)
        max_w = 240
        hp_ratio = self.game.player_hp / self.game.player_max_hp
        bar_x, bar_y, bar_h = 20, 20, 18
        pg.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, max_w, bar_h))
        pg.draw.rect(self.screen, (200, 70, 50), (bar_x, bar_y, int(max_w * hp_ratio), bar_h))
        hp_text = self.font.render(f'HP: {self.game.player_hp}/{self.game.player_max_hp}', True, (230, 230, 230))
        self.screen.blit(hp_text, (bar_x, bar_y + 24))

        # Rezultat (Score)
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