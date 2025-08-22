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
        self.mode7.update()
        player_pos = self.mode7.pos
        self.game.update(player_pos)
        self.clock.tick()
        pg.display.set_caption(f'{self.clock.get_fps():.1f}')

    def draw(self):
        self.mode7.draw()
        self.game.draw(self.screen)
        self.draw_hud()
        
        # Crveni flash kada igrač primi štetu
        now_ms = pg.time.get_ticks()
        if now_ms < getattr(self.game, 'hit_flash_end_ms', 0):
            alpha = 120
            flash = pg.Surface(WIN_RES, pg.SRCALPHA)
            flash.fill((220, 40, 40, alpha))
            self.screen.blit(flash, (0, 0))
        
        # Prikaz timera za početak novog wave-a
        if getattr(self.game, 'is_wave_starting', False):
            self.draw_wave_timer()
            
        if self.game.game_over:
            self.draw_game_over()
        elif getattr(self.game, 'game_won', False):
            self.draw_win_screen()
        pg.display.flip()

    def check_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                print('QUIT event zaprimljen - izlazim iz glavne petlje')
                self.running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                print('ESC pritisnut - izlaz onemogućen radi debugiranja')
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if not self.game.game_over:
                    self.game.shoot(self.mode7.pos, self.mode7.angle)
            elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                if self.game.game_over or getattr(self.game, 'game_won', False):
                    self.mode7.pos = np.array([0.0, 0.0])
                    self.mode7.angle = 0.0
                    self.mode7.alt = 1.0
                    self.game.reset()

    def run(self):
        show_menu(self.screen)
        while self.running:
            self.check_event()
            self.update()
            self.draw()
        pg.quit()

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

        # Wave
        if self.game.wave == 5:
            wave_text = self.font.render('FINAL ROUND', True, (230, 230, 230))
        else:
            wave_text = self.font.render(f'Wave: {self.game.wave}', True, (230, 230, 230))
        self.screen.blit(wave_text, (WIDTH // 2 - 50, 20))

    def draw_overlay_screen(self, title, subtitle, stats, border_color, line_color=None):
        """Generička metoda za crtanje overlay ekrana (Game Over/Victory)"""
        now_ms = pg.time.get_ticks()
        
        # Animirani overlay s gradijentom
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.003)) * 0.3 + 0.7  # Pulsirajući efekt
        
        for y in range(HEIGHT):
            if border_color == (150, 50, 50):  # Game Over - crveni
                alpha = int((180 + (y / HEIGHT) * 40) * pulse)
                overlay.fill((0, 0, 0, alpha), (0, y, WIDTH, 1))
            else:  # Victory - zlatni
                alpha = int((120 + (y / HEIGHT) * 60) * pulse)
                overlay.fill((0, 0, 0, alpha), (0, y, WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        # Glavni naslov s animiranim efektom
        title_shadow = self.big_font.render(title, True, (100, 0, 0) if border_color == (150, 50, 50) else (150, 150, 0))
        title_main = self.big_font.render(title, True, (255, 100, 100) if border_color == (150, 50, 50) else (255, 255, 100))
        
        # Animirana pozicija naslova
        title_offset = int(np.sin(now_ms * 0.005) * 3)  # Lagano ljuljanje
        title_rect = title_main.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + title_offset))  # Više razmaka
        shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 97 + title_offset))
        
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_main, title_rect)
        
        # Podnaslov (samo za Victory)
        if subtitle:
            subtitle_text = self.font.render(subtitle, True, (255, 255, 200))
            subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))  # Više razmaka
            self.screen.blit(subtitle_text, subtitle_rect)
        
        # Statistike s fade-in efektom
        y_offset = 0 if not subtitle else 50  # Više razmaka
        for i, (text, color) in enumerate(stats):
            stat_text = self.font.render(text, True, color)
            stat_rect = stat_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset + i * 40))  # Više razmaka
            self.screen.blit(stat_text, stat_rect)
        
        # Instrukcija s pulsirajućim efektom
        tip_alpha = int(200 + np.sin(now_ms * 0.008) * 55)  # Pulsirajući tekst
        tip = self.font.render('Pritisni R za restart', True, (200, 200, 200))
        tip_rect = tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))  # Više razmaka
        self.screen.blit(tip, tip_rect)
        
        # Animirani dekorativni okvir
        border_pulse = abs(np.sin(now_ms * 0.002)) * 0.5 + 0.5
        animated_border = tuple(int(c * border_pulse) for c in border_color)
        pg.draw.rect(self.screen, animated_border, (50, 50, WIDTH - 100, HEIGHT - 100), 4)
        
        # Dekorativne linije (samo za Victory)
        if line_color:
            for i in range(0, WIDTH, 50):
                line_offset = int(np.sin(now_ms * 0.001 + i * 0.1) * 2)
                pg.draw.line(self.screen, line_color, (i, 60 + line_offset), (i + 30, 60 + line_offset), 2)
                pg.draw.line(self.screen, line_color, (i, HEIGHT - 60 + line_offset), (i + 30, HEIGHT - 60 + line_offset), 2)

    def draw_game_over(self):
        stats = [
            (f'Final Score: {self.game.score}', (255, 255, 200)),
            (f'Waves Completed: {self.game.wave - 1}', (255, 255, 200))
        ]
        self.draw_overlay_screen('GAME OVER', None, stats, (150, 50, 50))

    def draw_win_screen(self):
        stats = [
            (f'Final Score: {self.game.score}', (255, 255, 200)),
            (f'All 5 Waves Completed!', (255, 255, 200))
        ]
        self.draw_overlay_screen('VICTORY!', 'You defeated all enemies!', stats, (255, 255, 100), (255, 255, 100, 100))

    def draw_wave_timer(self):
        now_ms = pg.time.get_ticks()
        
        # Animirani overlay
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.004)) * 0.4 + 0.6
        overlay.fill((0, 0, 0, int(180 * pulse)))
        self.screen.blit(overlay, (0, 0))
        
        # Izračunaj preostalo vrijeme
        remaining_ms = max(0, getattr(self.game, 'wave_start_timer_ms', 0) - now_ms)
        remaining_seconds = (remaining_ms // 1000) + 1
        
        # Odredi naziv wave-a
        next_wave = self.game.wave + 1
        wave_configs = {
            4: ("MINI BOSS FIGHT", "Watch out for fast bullets!"),
            5: ("BOSS FIGHT", "Watch out for slow but heavy bullets!")
        }
        wave_title, wave_subtitle = wave_configs.get(next_wave, (f"WAVE {next_wave}", ""))
        
        # Wave naslov s fade efektom
        wave_text = self.big_font.render(wave_title, True, (255, 200, 100))
        wave_rect = wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))  # Više razmaka
        
        # Tip tekst
        tip_text = self.font.render('počinje za...', True, (230, 230, 230))
        tip_rect = tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))  # Više razmaka
        
        # Animirani timer s pulsirajućim efektom
        timer_pulse = abs(np.sin(now_ms * 0.01)) * 0.3 + 0.7
        timer_color = (int(255 * timer_pulse), int(255 * timer_pulse), int(100 * timer_pulse))
        timer_text = self.big_font.render(f'{remaining_seconds}', True, timer_color)
        
        # Animirana pozicija timera
        timer_offset = int(np.sin(now_ms * 0.008) * 5)
        timer_rect = timer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + timer_offset))
        
        # Crtanje s redoslijedom
        self.screen.blit(wave_text, wave_rect)
        self.screen.blit(tip_text, tip_rect)
        self.screen.blit(timer_text, timer_rect)
        
        # Prikaži podnaslov ako postoji s fade efektom
        if wave_subtitle:
            subtitle_alpha = abs(np.sin(now_ms * 0.006)) * 0.5 + 0.5
            subtitle_color = (int(200 * subtitle_alpha), int(200 * subtitle_alpha), int(200 * subtitle_alpha))
            subtitle_text = self.font.render(wave_subtitle, True, subtitle_color)
            subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))  # Više razmaka
            self.screen.blit(subtitle_text, subtitle_rect)

if __name__ == '__main__':
    app = App()
    app.run()