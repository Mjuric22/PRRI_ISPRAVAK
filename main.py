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
    
    # Učitaj ikone zvuka
    try:
        speaker_on = pg.image.load("textures/zvucnik.png").convert_alpha()
        speaker_off = pg.image.load("textures/ugasen_zvucnik.png").convert_alpha()
        speaker_on = pg.transform.scale(speaker_on, (32, 32))
        speaker_off = pg.transform.scale(speaker_off, (32, 32))
    except:
        # Fallback ako slike ne postoje
        speaker_on = pg.Surface((32, 32))
        speaker_on.fill((255, 255, 255))
        speaker_off = pg.Surface((32, 32))
        speaker_off.fill((100, 100, 100))
    
    # Inicijaliziraj glazbu
    music_on = True
    try:
        pg.mixer.music.load("sounds/background.mp3")
        pg.mixer.music.play(-1)  # Loop glazbu
        pg.mixer.music.set_volume(0.5)
        # Učitaj UI zvukove
        ui_sound = pg.mixer.Sound("sounds/boop-417-mhz-39313.mp3")
        ui_sound.set_volume(0.3)
    except:
        music_on = False
        ui_sound = None
        print("Nije moguće učitati background glazbu")

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
            
            # Gumb za zvuk
            speaker_rect = pg.Rect(WIDTH // 2 - 16, HEIGHT // 2 + 180, 32, 32)
            speaker_hovered = speaker_rect.collidepoint(mx, my)
            
            # Pozadina gumba za zvuk
            if speaker_hovered:
                pg.draw.rect(screen, (80, 70, 50), speaker_rect, border_radius=5)
            pg.draw.rect(screen, (200, 170, 120), speaker_rect, width=2, border_radius=5)
            
            # Ikonica zvuka
            current_speaker = speaker_on if music_on else speaker_off
            screen.blit(current_speaker, speaker_rect)

            tip = small_font.render('WASD move | Arrows rotate | Space shoot | M mute | Esc exit', True, (210, 200, 180))
            screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.mixer.music.stop()
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if play_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_sound:
                            ui_sound.play()
                        pg.mixer.music.stop()
                        return
                    elif about_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_sound:
                            ui_sound.play()
                        in_about = True
                    elif exit_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_sound:
                            ui_sound.play()
                        pg.mixer.music.stop()
                        pg.quit()
                        sys.exit()
                    elif speaker_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_sound:
                            ui_sound.play()
                        # Promijeni glazbu
                        if music_on:
                            pg.mixer.music.pause()
                            music_on = False
                        else:
                            pg.mixer.music.unpause()
                            music_on = True
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
                    pg.mixer.music.stop()
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    in_about = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if back_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_sound:
                            ui_sound.play()
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
        
        # Parallax oblačke
        try:
            self.cloud1 = pg.image.load('textures/cloud1.png').convert_alpha()
            self.cloud2 = pg.image.load('textures/cloud2.png').convert_alpha()
            self.cloud3 = pg.image.load('textures/cloud3.png').convert_alpha()
            
            # Skaliraj oblačke na različite veličine (2x veće)
            self.cloud1 = pg.transform.scale(self.cloud1, (400, 200))
            self.cloud2 = pg.transform.scale(self.cloud2, (300, 150))
            self.cloud3 = pg.transform.scale(self.cloud3, (200, 100))
        except:
            # Fallback - kreiraj ljepše oblačke (2x veće)
            self.cloud1 = self.create_cloud_surface(400, 200, (255, 255, 255, 60))
            self.cloud2 = self.create_cloud_surface(300, 150, (255, 255, 255, 40))
            self.cloud3 = self.create_cloud_surface(200, 100, (255, 255, 255, 25))
        
        # Učitaj power-up slike
        try:
            self.powerup_damage = pg.image.load('textures/powerup_damage.png').convert_alpha()
            self.powerup_speed = pg.image.load('textures/powerup_speed.png').convert_alpha()
            # Power-up slike su već 64x64 piksela
        except:
            # Fallback - kreiraj power-up slike na 64px za bolju rezoluciju
            self.powerup_damage = self.create_powerup_surface(64, 64, (255, 0, 0))  # Crvena za damage
            self.powerup_speed = self.create_powerup_surface(64, 64, (0, 255, 0))   # Zelena za speed
        
        # Pozicije oblačaka (svjetske koordinate) - raspoređeno po cijeloj mapi
        self.cloud_positions = [
            # Dalji sloj (sporiji) - veliki prostor (20 oblačaka)
            [(20, 15), (-18, 25), (30, -10), (-25, -20), (40, 20), (15, -30), (-35, 10), (25, 35), (-40, -15), (35, -25),
             (45, 5), (-30, 30), (50, -20), (-45, -25), (60, 15), (25, -40), (-50, 5), (35, 45), (-55, -20), (45, -35)],
            # Srednji sloj - srednji prostor (24 oblačaka)
            [(10, 8), (-8, 15), (15, -5), (-12, -10), (20, 12), (8, -15), (-18, 5), (12, 18), (-20, -8), (18, -12), (5, 20), (-15, 18),
             (25, 3), (-25, 22), (30, -12), (-28, -18), (35, 8), (15, -25), (-32, 2), (22, 28), (-35, -12), (28, -22), (8, 30), (-22, 25)],
            # Bliski sloj (brži) - mali prostor (28 oblačaka)
            [(5, 3), (-3, 8), (8, -2), (-5, -5), (12, 6), (3, -8), (-8, 3), (6, 10), (-10, -3), (9, -6), (2, 12), (-6, 9), (4, -10), (-4, 12),
             (15, 1), (-12, 15), (18, -8), (-15, -12), (22, 4), (7, -18), (-18, 1), (12, 20), (-20, -8), (16, -15), (3, 25), (-10, 18), (8, -22), (-8, 20)]
        ]

    def create_cloud_surface(self, width, height, color):
        """Kreiraj ljepšu oblačku s više krugova i gradijentima"""
        surface = pg.Surface((width, height), pg.SRCALPHA)
        
        # Glavni krugovi oblačke
        circles = [
            (width//2, height//2, min(width, height)//3),  # Središnji
            (width//3, height//2, min(width, height)//4),  # Lijevi
            (2*width//3, height//2, min(width, height)//4),  # Desni
            (width//2, height//3, min(width, height)//5),  # Gornji
            (width//2, 2*height//3, min(width, height)//5),  # Donji
        ]
        
        # Nacrtaj glavne krugove s gradijentom
        for x, y, radius in circles:
            # Vanjski krug (svjetliji)
            pg.draw.circle(surface, (*color[:3], color[3]//2), (x, y), radius + 2)
            # Glavni krug
            pg.draw.circle(surface, color, (x, y), radius)
            # Unutarnji krug (tamniji)
            pg.draw.circle(surface, (*color[:3], color[3]//3), (x, y), radius - 2)
        
        # Dodaj male krugove za teksturu
        for _ in range(8):
            x = np.random.randint(5, width-5)
            y = np.random.randint(5, height-5)
            radius = np.random.randint(3, 8)
            alpha = np.random.randint(20, color[3])
            pg.draw.circle(surface, (*color[:3], alpha), (x, y), radius)
        
        return surface

    def create_powerup_surface(self, width, height, color):
        """Kreiraj ljepšu sliku za power-up s steampunk stilom"""
        surface = pg.Surface((width, height), pg.SRCALPHA)
        
        # Glavni krug
        center = (width//2, height//2)
        radius = min(width, height)//2 - 2
        
        # Vanjski glow
        pg.draw.circle(surface, (*color, 100), center, radius + 3)
        # Glavni krug
        pg.draw.circle(surface, color, center, radius)
        # Unutarnji highlight
        pg.draw.circle(surface, (*color, 200), center, radius - 2)
        
        # Dodaj steampunk detalje
        if color == (255, 0, 0):  # Damage power-up
            # Crveni križ za damage
            pg.draw.line(surface, (255, 255, 255), (center[0]-4, center[1]), (center[0]+4, center[1]), 2)
            pg.draw.line(surface, (255, 255, 255), (center[0], center[1]-4), (center[0], center[1]+4), 2)
        elif color == (0, 255, 0):  # Speed power-up
            # Zelena strelica za speed
            points = [(center[0]-3, center[1]), (center[0]+3, center[1]), (center[0], center[1]-3)]
            pg.draw.polygon(surface, (255, 255, 255), points)
        
        return surface

    def update(self):
        self.mode7.update()
        self.game.update(self.mode7.pos)
        self.game.handle_tutorial_input()
        self.clock.tick()
        pg.display.set_caption(f'{self.clock.get_fps():.1f}')

    def draw(self):
        self.mode7.draw()
        self.draw_parallax_clouds()  # Nacrtaj oblačke iznad mode7
        self.game.draw(self.screen)
        self.draw_hud()
        
        # Hit flash efekt
        now_ms = pg.time.get_ticks()
        if now_ms < getattr(self.game, 'hit_flash_end_ms', 0):
            flash = pg.Surface(WIN_RES, pg.SRCALPHA)
            flash.fill((220, 40, 40, 120))
            self.screen.blit(flash, (0, 0))
        
        # Wave timer (ako nema weapon unlock)
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
            # Promjena oružja (tipke 1-6)
            weapons = ['basic', 'heavy', 'rapid', 'sniper', 'shotgun', 'plasma']
            for i, weapon in enumerate(weapons, 1):
                if event.key == getattr(pg, f'K_{i}') and weapon in self.game.unlocked_weapons and not (self.game.game_over or self.game.game_won):
                    self.game.current_weapon = weapon
                    # Pusti zvuk promjene oružja
                    if self.game.weapon_switch_sound:
                        self.game.weapon_switch_sound.play()
                    break
            
            # Utisaj glazbu
            if event.key == pg.K_m and not (self.game.game_over or self.game.game_won):
                self.game.music_muted = not self.game.music_muted
                try:
                    if self.game.music_muted:
                        pg.mixer.music.pause()
                    else:
                        pg.mixer.music.unpause()
                except:
                    pass
            
            # Pucanje
            if event.key == pg.K_SPACE and not (self.game.game_over or self.game.game_won):
                self.game.start_auto_fire()
            
            # Ponovno pokretanje
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
        # HP bar (centar gore)
        hp_ratio = self.game.player_hp / self.game.player_max_hp
        bar_width, bar_height = 300, 25
        bar_x = (WIDTH - bar_width) // 2
        bar_y = 20
        
        pg.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        pg.draw.rect(self.screen, (200, 60, 40), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        hp_text = self.font.render(f'HP: {self.game.player_hp}/{self.game.player_max_hp}', True, (255, 255, 255))
        self.screen.blit(hp_text, hp_text.get_rect(center=(WIDTH//2, bar_y + bar_height//2)))
        
        # Wave (ispod HP)
        wave_text = f'Wave: {self.game.wave}' if self.game.wave < 5 else 'FINAL ROUND'
        wave_surface = self.font.render(wave_text, True, (255, 255, 255))
        self.screen.blit(wave_surface, wave_surface.get_rect(center=(WIDTH//2, bar_y + bar_height + 25)))
        
        # Trenutno oružje i sljedeći unlock (gore desno)
        weapon = self.game.weapons[self.game.current_weapon]
        weapon_text = self.font.render(f'Weapon: {weapon.name}', True, (255, 255, 255))
        self.screen.blit(weapon_text, (WIDTH - 350, 20))
        
        # Sljedeći unlock
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
        
        # Score, unlocked count, controls, power-ups (gore lijevo)
        y_pos = 20
        texts = [
            f'Score: {self.game.score}',
            f'Unlocked: {len(self.game.unlocked_weapons)}/{len(self.game.weapons)}',
            '1-6: Change Weapon | SPACE: Shoot | M: Mute'
        ]
        colors = [(255, 255, 255), (255, 255, 255), (200, 200, 200)]
        
        for text, color in zip(texts, colors):
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (20, y_pos))
            y_pos += 30
        
        # Aktivni power-ups
        now_ms = pg.time.get_ticks()
        y_pos = 110
        for power_type, end_time in self.game.active_power_ups.items():
            if now_ms < end_time:
                remaining_time = (end_time - now_ms) / 1000
                power_text = self.font.render(f'{power_type.title()}: {remaining_time:.1f}s', True, (255, 255, 0))
                self.screen.blit(power_text, (20, y_pos))
                y_pos += 25
        
        # Tutorial ili weapon unlock ekrani
        if self.game.tutorial_active:
            self.draw_tutorial_screen()
        elif self.game.last_unlocked_weapon and self.game.game_frozen:
            self.draw_weapon_unlock_screen()

    def draw_parallax_clouds(self):
        """Nacrtaj oblačne slojeve s naprednim parallax efektom"""
        # Poboljšani parallax faktori (više slojeva za veću dubinu)
        parallax_factors = [0.15, 0.3, 0.5, 0.7, 0.9, 1.0]  # 6 slojeva umjesto 3
        
        # Napredni drift efekti
        now_ms = pg.time.get_ticks()
        drift_offset_x = np.sin(now_ms * 0.0003) * 0.8
        drift_offset_y = np.cos(now_ms * 0.0004) * 0.6
        
        # Pulsirajući efekt za oblačke
        pulse = abs(np.sin(now_ms * 0.002)) * 0.2 + 0.8
        
        # Proširene pozicije oblačaka za više slojeva
        extended_cloud_positions = [
            # Dalji sloj 1 (najsporiji) - 15 oblačaka
            [(25, 20), (-22, 30), (35, -15), (-30, -25), (45, 25), (20, -35), (-40, 15), (30, 40), (-45, -20), (40, -30),
             (50, 10), (-35, 35), (55, -25), (-50, -30), (65, 20)],
            # Dalji sloj 2 - 18 oblačaka  
            [(18, 12), (-15, 22), (28, -8), (-22, -18), (38, 18), (15, -28), (-32, 12), (25, 32), (-38, -15), (32, -25),
             (42, 8), (-28, 28), (48, -18), (-42, -25), (58, 15), (22, -32), (-45, 8), (35, 38)],
            # Srednji sloj 1 - 20 oblačaka
            [(12, 8), (-10, 15), (20, -5), (-15, -12), (25, 12), (10, -20), (-25, 8), (18, 25), (-28, -10), (22, -18),
             (30, 5), (-20, 20), (35, -12), (-30, -18), (40, 10), (15, -25), (-35, 5), (25, 30), (-38, -12), (28, -22)],
            # Srednji sloj 2 - 22 oblačaka
            [(8, 5), (-6, 10), (15, -3), (-10, -8), (20, 8), (6, -15), (-18, 5), (12, 18), (-22, -6), (16, -12),
             (25, 3), (-15, 15), (28, -8), (-25, -12), (32, 6), (10, -18), (-28, 3), (18, 22), (-32, -8), (22, -15),
             (5, 25), (-12, 18)],
            # Bliski sloj 1 - 25 oblačaka
            [(5, 3), (-3, 6), (10, -2), (-6, -5), (15, 5), (3, -10), (-12, 3), (8, 12), (-15, -4), (10, -8),
             (18, 2), (-8, 10), (22, -5), (-18, -8), (25, 4), (6, -12), (-22, 2), (12, 15), (-25, -5), (15, -10),
             (3, 18), (-10, 12), (8, -15), (-8, 15), (5, -18)],
            # Bliski sloj 2 (najbrži) - 28 oblačaka
            [(3, 2), (-2, 4), (6, -1), (-4, -3), (8, 3), (2, -6), (-7, 2), (5, 8), (-9, -2), (6, -5),
             (10, 1), (-5, 6), (12, -3), (-8, -5), (14, 2), (4, -8), (-10, 1), (7, 10), (-12, -3), (8, -6),
             (2, 12), (-6, 8), (5, -10), (-5, 10), (3, -12), (-3, 12), (4, -8), (-4, 8)]
        ]
        
        # Proširene teksture oblačaka
        cloud_textures = [
            self.cloud1, self.cloud1,  # Dalji slojevi
            self.cloud2, self.cloud2,  # Srednji slojevi  
            self.cloud3, self.cloud3   # Bliski slojevi
        ]
        
        for layer_idx, (cloud_texture, positions, parallax_factor) in enumerate([
            (cloud_textures[0], extended_cloud_positions[0], parallax_factors[0]),
            (cloud_textures[1], extended_cloud_positions[1], parallax_factors[1]),
            (cloud_textures[2], extended_cloud_positions[2], parallax_factors[2]),
            (cloud_textures[3], extended_cloud_positions[3], parallax_factors[3]),
            (cloud_textures[4], extended_cloud_positions[4], parallax_factors[4]),
            (cloud_textures[5], extended_cloud_positions[5], parallax_factors[5])
        ]):
            for cloud_pos in positions:
                # Napredni drift efekt s različitim brzinama za svaki sloj
                layer_drift_x = drift_offset_x * parallax_factor * 0.5
                layer_drift_y = drift_offset_y * parallax_factor * 0.3
                
                # Izračunaj relativnu poziciju oblačke s drift efektom
                relative_x = cloud_pos[0] - self.mode7.pos[0] + layer_drift_x
                relative_y = cloud_pos[1] - self.mode7.pos[1] + layer_drift_y
                
                # Primijeni parallax faktor
                parallax_x = relative_x * parallax_factor
                parallax_y = relative_y * parallax_factor
                
                # Rotiraj poziciju prema kutu kamere
                rotated_x = parallax_x * np.cos(self.mode7.angle) - parallax_y * np.sin(self.mode7.angle)
                rotated_y = parallax_x * np.sin(self.mode7.angle) + parallax_y * np.cos(self.mode7.angle)
                
                # Projektiraj na ekran
                if rotated_y > 0.1:  # Izbjegni division by zero
                    screen_x = int(WIDTH // 2 + rotated_x / rotated_y * WIDTH // 3)
                    screen_y = int(HEIGHT // 2 - 50 / rotated_y)
                    
                    # Proširena vidljivost
                    if -400 < screen_x < WIDTH + 400 and -200 < screen_y < HEIGHT + 200:
                        # Napredno skaliranje s pulsiranjem
                        base_scale = max(0.05, min(2.5, 1.0 / rotated_y))
                        scale = base_scale * pulse
                        scaled_width = int(cloud_texture.get_width() * scale)
                        scaled_height = int(cloud_texture.get_height() * scale)
                        
                        if scaled_width > 0 and scaled_height > 0:
                            scaled_cloud = pg.transform.scale(cloud_texture, (scaled_width, scaled_height))
                            cloud_rect = scaled_cloud.get_rect(center=(screen_x, screen_y))
                            
                            # Glow efekt uklonjen za čistiji izgled
                            
                            # Dodaj blagi fade efekt za dalje slojeve
                            if layer_idx < 2:  # Dalji slojevi
                                fade_surface = pg.Surface((scaled_width, scaled_height), pg.SRCALPHA)
                                fade_alpha = int(255 * (0.6 + 0.2 * layer_idx))  # 60-80% alpha
                                fade_surface.fill((255, 255, 255, fade_alpha))
                                scaled_cloud.blit(fade_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
                            
                            # Nacrtaj oblačku
                            self.screen.blit(scaled_cloud, cloud_rect)
                            
                            # Dodaj male sparkle efekte za bliske slojeve
                            if layer_idx >= 4 and np.random.random() < 0.1:  # 10% šansa
                                sparkle_size = int(scale * 3)
                                sparkle_color = (255, 255, 255, int(100 * pulse))
                                sparkle_x = screen_x + np.random.randint(-scaled_width//2, scaled_width//2)
                                sparkle_y = screen_y + np.random.randint(-scaled_height//2, scaled_height//2)
                                pg.draw.circle(self.screen, sparkle_color, (sparkle_x, sparkle_y), sparkle_size)

    def draw_overlay_screen(self, title, subtitle, stats, border_color, line_color=None):
        """Generički overlay ekran za Game Over/Victory"""
        now_ms = pg.time.get_ticks()
        
        # Animirani overlay
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.003)) * 0.3 + 0.7
        
        for y in range(HEIGHT):
            if border_color == (150, 50, 50):  # Game Over
                alpha = int((180 + (y / HEIGHT) * 40) * pulse)
            else:  # Victory
                alpha = int((120 + (y / HEIGHT) * 60) * pulse)
            overlay.fill((0, 0, 0, alpha), (0, y, WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        # Naslov s sjenom
        title_shadow = self.big_font.render(title, True, (100, 0, 0) if border_color == (150, 50, 50) else (150, 150, 0))
        title_main = self.big_font.render(title, True, (255, 100, 100) if border_color == (150, 50, 50) else (255, 255, 100))
        
        title_offset = int(np.sin(now_ms * 0.005) * 3)
        title_rect = title_main.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + title_offset))
        shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 97 + title_offset))
        
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_main, title_rect)
        
        # Podnaslov
        if subtitle:
            subtitle_text = self.font.render(subtitle, True, (255, 255, 200))
            self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        
        # Statistike
        y_offset = 0 if not subtitle else 50
        for i, (text, color) in enumerate(stats):
            stat_text = self.font.render(text, True, color)
            self.screen.blit(stat_text, stat_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset + i * 40)))
        
        # Animirani okvir
        border_pulse = abs(np.sin(now_ms * 0.002)) * 0.5 + 0.5
        animated_border = tuple(int(c * border_pulse) for c in border_color)
        pg.draw.rect(self.screen, animated_border, (50, 50, WIDTH - 100, HEIGHT - 100), 4)
        

        
        # Instrukcija za ponovno pokretanje
        restart_pulse = abs(np.sin(now_ms * 0.005)) * 0.4 + 0.6
        restart_color = tuple(int(200 * restart_pulse) for _ in range(3))
        restart_text = self.font.render('Press R to restart', True, restart_color)
        self.screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

    def draw_tutorial_screen(self):
        """Nacrtaj tutorial ekran"""
        now_ms = pg.time.get_ticks()
        
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        page = self.game.tutorial_pages[self.game.tutorial_page]
        
        # Animirani naslov
        title_pulse = abs(np.sin(now_ms * 0.003)) * 0.3 + 0.7
        title_color = (int(255 * title_pulse), int(215 * title_pulse), 0)
        title_text = self.big_font.render(page['title'], True, title_color)
        self.screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 150)))
        
        # Podnaslov
        subtitle_text = self.font.render(page['subtitle'], True, (200, 200, 200))
        self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, 220)))
        
        # Sadržaj
        content_y = 300
        for line in page['content']:
            content_text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(content_text, content_text.get_rect(center=(WIDTH // 2, content_y)))
            content_y += 40
        
        # Animirani okvir
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
        
        # Animirani overlay
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.004)) * 0.4 + 0.6
        overlay.fill((0, 0, 0, int(180 * pulse)))
        self.screen.blit(overlay, (0, 0))
        
        # Izračunaj preostalo vrijeme
        remaining_ms = max(0, getattr(self.game, 'wave_start_timer_ms', 0) - now_ms)
        remaining_seconds = (remaining_ms // 1000) + 1
        
        # Odredi sljedeći wave
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
        
        # Wave naslov
        wave_text = self.big_font.render(wave_title, True, (255, 200, 100))
        self.screen.blit(wave_text, wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))
        
        # "starts in..." tekst
        tip_text = self.font.render('starts in...', True, (230, 230, 230))
        self.screen.blit(tip_text, tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
        
        # Animirani timer
        timer_pulse = abs(np.sin(now_ms * 0.01)) * 0.3 + 0.7
        timer_color = (int(255 * timer_pulse), int(255 * timer_pulse), int(100 * timer_pulse))
        timer_text = self.big_font.render(f'{remaining_seconds}', True, timer_color)
        
        timer_offset = int(np.sin(now_ms * 0.008) * 5)
        self.screen.blit(timer_text, timer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + timer_offset)))
        
        # Podnaslov
        if wave_subtitle:
            subtitle_alpha = abs(np.sin(now_ms * 0.006)) * 0.5 + 0.5
            subtitle_color = tuple(int(200 * subtitle_alpha) for _ in range(3))
            subtitle_text = self.font.render(wave_subtitle, True, subtitle_color)
            self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

    def draw_weapon_unlock_screen(self):
        """Prikaz ekrana za otključavanje oružja"""
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
        
        # Pozadina
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Naslov
        title_font = pg.font.Font(None, 72)
        title_text = title_font.render('WEAPON UNLOCKED!', True, (255, 215, 0))
        self.screen.blit(title_text, title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))
        
        # Ime oružja s tipkom
        weapon_font = pg.font.Font(None, 48)
        weapon_text = weapon_font.render(f'{weapon_name} (Key {key})', True, (255, 255, 255))
        self.screen.blit(weapon_text, weapon_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
        
        # Opis
        desc_font = pg.font.Font(None, 32)
        desc_text = desc_font.render(description, True, (200, 200, 200))
        self.screen.blit(desc_text, desc_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        
        # Timer
        now_ms = pg.time.get_ticks()
        remaining_time = (self.game.freeze_duration - (now_ms - self.game.freeze_start_time)) / 1000
        timer_text = desc_font.render(f'Resuming in {remaining_time:.1f}s...', True, (150, 150, 150))
        self.screen.blit(timer_text, timer_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
        
        # Animirani okvir
        pulse = int(np.sin(now_ms * 0.01) * 10)
        pg.draw.rect(self.screen, (255, 215, 0), (50 + pulse, 150 + pulse, WIDTH - 100 - 2*pulse, HEIGHT - 300 - 2*pulse), 4)


if __name__ == '__main__':
    app = App()
    app.run()