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
        fill = (80, 70, 50) if hovered else (40, 40, 40)
        pg.draw.rect(screen, fill, rect, border_radius=10)
        pg.draw.rect(screen, (200, 170, 120), rect, width=2, border_radius=10)
        label = menu_font.render(text, True, (230, 220, 200))
        screen.blit(label, label.get_rect(center=rect.center))
        return rect

    in_about = False
    while True:
        screen.blit(background, (0, 0))
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

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
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
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
        self.screen = pg.display.set_mode(WIN_RES, pg.FULLSCREEN | pg.SCALED)
        self.clock = pg.time.Clock()
        self.mode7 = Mode7(self)
        self.game = Game(self.mode7)
        self.font = pg.font.SysFont('consolas', 28)
        self.big_font = pg.font.SysFont('consolas', 64)
        self.running = True

    def update(self):
        self.mode7.update()
        self.game.update(self.mode7.pos)
        self.game.handle_tutorial_input()
        self.clock.tick()
        pg.display.set_caption(f'{self.clock.get_fps():.1f}')

    def draw(self):
        self.mode7.draw()
        self.game.draw(self.screen)
        self.draw_hud()
        
        # Hit flash
        now_ms = pg.time.get_ticks()
        if now_ms < getattr(self.game, 'hit_flash_end_ms', 0):
            flash = pg.Surface(WIN_RES, pg.SRCALPHA)
            flash.fill((220, 40, 40, 120))
            self.screen.blit(flash, (0, 0))
        
        # Wave timer (if no weapon unlock)
        if getattr(self.game, 'is_wave_starting', False) and not (self.game.last_unlocked_weapon and self.game.game_frozen):
            self.draw_wave_timer()
            
        if self.game.game_over:
            self.draw_game_over()
        elif getattr(self.game, 'game_won', False):
            self.draw_win_screen()
        pg.display.flip()

    def check_event(self, event):
        if self.game.tutorial_active:
            return True
            
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            return False
        
        if event.type == pg.KEYDOWN:
            # Weapon switching (1-6 keys)
            weapons = ['basic', 'heavy', 'rapid', 'sniper', 'shotgun', 'plasma']
            for i, weapon in enumerate(weapons, 1):
                if event.key == getattr(pg, f'K_{i}') and weapon in self.game.unlocked_weapons and not (self.game.game_over or self.game.game_won):
                    self.game.current_weapon = weapon
                    break
            
            # Shooting
            if event.key == pg.K_SPACE and not (self.game.game_over or self.game.game_won):
                self.game.start_auto_fire()
            
            # Restart
            if event.key == pg.K_r and (self.game.game_over or self.game.game_won):
                self.game.reset()
        
        elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
            self.game.stop_auto_fire()
        
        return True

    def run(self):
        show_menu(self.screen)
        while self.running:
            for event in pg.event.get():
                if not self.check_event(event):
                    self.running = False
            self.update()
            self.draw()
        pg.quit()

    def draw_hud(self):
        # HP bar (center top)
        hp_ratio = self.game.player_hp / self.game.player_max_hp
        bar_width, bar_height = 300, 25
        bar_x = (WIDTH - bar_width) // 2
        bar_y = 20
        
        pg.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        pg.draw.rect(self.screen, (200, 60, 40), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        hp_text = self.font.render(f'HP: {self.game.player_hp}/{self.game.player_max_hp}', True, (255, 255, 255))
        self.screen.blit(hp_text, hp_text.get_rect(center=(WIDTH//2, bar_y + bar_height//2)))
        
        # Wave (below HP)
        wave_text = f'Wave: {self.game.wave}' if self.game.wave < 5 else 'FINAL ROUND'
        wave_surface = self.font.render(wave_text, True, (255, 255, 255))
        self.screen.blit(wave_surface, wave_surface.get_rect(center=(WIDTH//2, bar_y + bar_height + 25)))
        
        # Current weapon and next unlock (top right)
        weapon = self.game.weapons[self.game.current_weapon]
        weapon_text = self.font.render(f'Weapon: {weapon.name}', True, (255, 255, 255))
        self.screen.blit(weapon_text, (WIDTH - 350, 20))
        
        # Next unlock
        next_unlock_score = float('inf')
        next_unlock = None
        for weapon_name, required_score in self.game.weapon_unlock_requirements.items():
            if weapon_name not in self.game.unlocked_weapons and required_score < next_unlock_score:
                next_unlock = weapon_name
                next_unlock_score = required_score
        
        if next_unlock:
            remaining_score = next_unlock_score - self.game.score
            next_weapon_name = self.game.weapons[next_unlock].name
            unlock_text = self.font.render(f'Next: {next_weapon_name} ({remaining_score} XP)', True, (255, 255, 0))
            self.screen.blit(unlock_text, (WIDTH - 350, 50))
        
        # Score, unlocked count, controls, power-ups (top left)
        y_pos = 20
        texts = [
            f'Score: {self.game.score}',
            f'Unlocked: {len(self.game.unlocked_weapons)}/{len(self.game.weapons)}',
            '1-6: Change Weapon | SPACE: Shoot'
        ]
        colors = [(255, 255, 255), (255, 255, 255), (200, 200, 200)]
        
        for text, color in zip(texts, colors):
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (20, y_pos))
            y_pos += 30
        
        # Active power-ups
        now_ms = pg.time.get_ticks()
        y_pos = 110
        for power_type, end_time in self.game.active_power_ups.items():
            if now_ms < end_time:
                remaining_time = (end_time - now_ms) / 1000
                power_text = self.font.render(f'{power_type.title()}: {remaining_time:.1f}s', True, (255, 255, 0))
                self.screen.blit(power_text, (20, y_pos))
                y_pos += 25
        
        # Tutorial or weapon unlock screens
        if self.game.tutorial_active:
            self.draw_tutorial_screen()
        elif self.game.last_unlocked_weapon and self.game.game_frozen:
            self.draw_weapon_unlock_screen()

    def draw_overlay_screen(self, title, subtitle, stats, border_color, line_color=None):
        """Generic overlay screen for Game Over/Victory"""
        now_ms = pg.time.get_ticks()
        
        # Animated overlay
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.003)) * 0.3 + 0.7
        
        for y in range(HEIGHT):
            if border_color == (150, 50, 50):  # Game Over
                alpha = int((180 + (y / HEIGHT) * 40) * pulse)
            else:  # Victory
                alpha = int((120 + (y / HEIGHT) * 60) * pulse)
            overlay.fill((0, 0, 0, alpha), (0, y, WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        # Title with shadow
        title_shadow = self.big_font.render(title, True, (100, 0, 0) if border_color == (150, 50, 50) else (150, 150, 0))
        title_main = self.big_font.render(title, True, (255, 100, 100) if border_color == (150, 50, 50) else (255, 255, 100))
        
        title_offset = int(np.sin(now_ms * 0.005) * 3)
        title_rect = title_main.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + title_offset))
        shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 97 + title_offset))
        
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_main, title_rect)
        
        # Subtitle
        if subtitle:
            subtitle_text = self.font.render(subtitle, True, (255, 255, 200))
            self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        
        # Stats
        y_offset = 0 if not subtitle else 50
        for i, (text, color) in enumerate(stats):
            stat_text = self.font.render(text, True, color)
            self.screen.blit(stat_text, stat_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset + i * 40)))
        
        # Animated border
        border_pulse = abs(np.sin(now_ms * 0.002)) * 0.5 + 0.5
        animated_border = tuple(int(c * border_pulse) for c in border_color)
        pg.draw.rect(self.screen, animated_border, (50, 50, WIDTH - 100, HEIGHT - 100), 4)
        
        # Victory decorative lines
        if line_color:
            for i in range(0, WIDTH, 50):
                line_offset = int(np.sin(now_ms * 0.001 + i * 0.1) * 2)
                pg.draw.line(self.screen, line_color, (i, 60 + line_offset), (i + 30, 60 + line_offset), 2)
                pg.draw.line(self.screen, line_color, (i, HEIGHT - 60 + line_offset), (i + 30, HEIGHT - 60 + line_offset), 2)
        
        # Restart instruction
        restart_pulse = abs(np.sin(now_ms * 0.005)) * 0.4 + 0.6
        restart_color = tuple(int(200 * restart_pulse) for _ in range(3))
        restart_text = self.font.render('Press R to restart', True, restart_color)
        self.screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

    def draw_tutorial_screen(self):
        """Draw tutorial screen"""
        now_ms = pg.time.get_ticks()
        
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        page = self.game.tutorial_pages[self.game.tutorial_page]
        
        # Animated title
        title_pulse = abs(np.sin(now_ms * 0.003)) * 0.3 + 0.7
        title_color = (int(255 * title_pulse), int(215 * title_pulse), 0)
        title_text = self.big_font.render(page['title'], True, title_color)
        self.screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 150)))
        
        # Subtitle
        subtitle_text = self.font.render(page['subtitle'], True, (200, 200, 200))
        self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, 220)))
        
        # Content
        content_y = 300
        for line in page['content']:
            content_text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(content_text, content_text.get_rect(center=(WIDTH // 2, content_y)))
            content_y += 40
        
        # Animated border
        pulse = int(np.sin(now_ms * 0.01) * 10)
        pg.draw.rect(self.screen, (255, 215, 0), (50 + pulse, 100 + pulse, WIDTH - 100 - 2*pulse, HEIGHT - 200 - 2*pulse), 4)

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
        self.draw_overlay_screen('VICTORY!', 'You defeated all enemies!', stats, (255, 255, 100), (255, 255, 100))

    def draw_wave_timer(self):
        now_ms = pg.time.get_ticks()
        
        # Animated overlay
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.004)) * 0.4 + 0.6
        overlay.fill((0, 0, 0, int(180 * pulse)))
        self.screen.blit(overlay, (0, 0))
        
        # Calculate remaining time
        remaining_ms = max(0, getattr(self.game, 'wave_start_timer_ms', 0) - now_ms)
        remaining_seconds = (remaining_ms // 1000) + 1
        
        # Determine next wave
        if getattr(self.game, 'starting_wave_1', False):
            next_wave = 1
        else:
            next_wave = self.game.wave + 1
        
        wave_configs = {
            1: ("WAVE 1", "Destroy the basic enemies!"),
            2: ("WAVE 2", "Heavy enemies incoming!"),
            3: ("WAVE 3", "Fast enemies attack!"),
            4: ("MINI BOSS FIGHT", "WARNING: Boss deals massive damage on contact & Watch out for fast bullets!"),
            5: ("BOSS FIGHT", "WARNING: Boss deals massive damage on contact & Watch out for slow but heavy bullets!")
        }
        wave_title, wave_subtitle = wave_configs.get(next_wave, (f"WAVE {next_wave}", ""))
        
        # Wave title
        wave_text = self.big_font.render(wave_title, True, (255, 200, 100))
        self.screen.blit(wave_text, wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))
        
        # "starts in..." text
        tip_text = self.font.render('starts in...', True, (230, 230, 230))
        self.screen.blit(tip_text, tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
        
        # Animated timer
        timer_pulse = abs(np.sin(now_ms * 0.01)) * 0.3 + 0.7
        timer_color = (int(255 * timer_pulse), int(255 * timer_pulse), int(100 * timer_pulse))
        timer_text = self.big_font.render(f'{remaining_seconds}', True, timer_color)
        
        timer_offset = int(np.sin(now_ms * 0.008) * 5)
        self.screen.blit(timer_text, timer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + timer_offset)))
        
        # Subtitle
        if wave_subtitle:
            subtitle_alpha = abs(np.sin(now_ms * 0.006)) * 0.5 + 0.5
            subtitle_color = tuple(int(200 * subtitle_alpha) for _ in range(3))
            subtitle_text = self.font.render(wave_subtitle, True, subtitle_color)
            self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

    def draw_weapon_unlock_screen(self):
        """Display weapon unlock screen"""
        weapon_name = self.game.weapons[self.game.last_unlocked_weapon].name
        
        weapon_descriptions = {
            'basic': 'Basic laser - fast and accurate (2 shots/sec)',
            'heavy': 'Heavy cannon - powerful but slow (1 shot/2 sec)',
            'rapid': 'Rapid fire - automatic shooting (6 shots/sec)',
            'sniper': 'Sniper rifle - precise and long range (1.5 shots/sec)',
            'shotgun': 'Shotgun - 3 projectiles at once (1.5 shots/sec)',
            'plasma': 'Plasma gun - advanced weapon (2 shots/sec)'
        }
        
        weapon_keys = ['1', '2', '3', '4', '5', '6']
        weapons = ['basic', 'heavy', 'rapid', 'sniper', 'shotgun', 'plasma']
        key = weapon_keys[weapons.index(self.game.last_unlocked_weapon)] if self.game.last_unlocked_weapon in weapons else '?'
        
        description = weapon_descriptions.get(self.game.last_unlocked_weapon, 'New weapon!')
        
        # Background
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pg.font.Font(None, 72)
        title_text = title_font.render('WEAPON UNLOCKED!', True, (255, 215, 0))
        self.screen.blit(title_text, title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))
        
        # Weapon name with key
        weapon_font = pg.font.Font(None, 48)
        weapon_text = weapon_font.render(f'{weapon_name} (Key {key})', True, (255, 255, 255))
        self.screen.blit(weapon_text, weapon_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
        
        # Description
        desc_font = pg.font.Font(None, 32)
        desc_text = desc_font.render(description, True, (200, 200, 200))
        self.screen.blit(desc_text, desc_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        
        # Timer
        now_ms = pg.time.get_ticks()
        remaining_time = (self.game.freeze_duration - (now_ms - self.game.freeze_start_time)) / 1000
        timer_text = desc_font.render(f'Resuming in {remaining_time:.1f}s...', True, (150, 150, 150))
        self.screen.blit(timer_text, timer_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
        
        # Animated border
        pulse = int(np.sin(now_ms * 0.01) * 10)
        pg.draw.rect(self.screen, (255, 215, 0), (50 + pulse, 150 + pulse, WIDTH - 100 - 2*pulse, HEIGHT - 300 - 2*pulse), 4)


if __name__ == '__main__':
    app = App()
    app.run()