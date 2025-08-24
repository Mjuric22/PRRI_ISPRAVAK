import pygame as pg
import sys
import numpy as np
from settings import WIN_RES, WIDTH, HEIGHT
from mode7 import *
from enemies import Game

def prikazi_izbornik(ekran):
    """Prikazuje glavni izbornik igre"""
    pg.init()
    sat = pg.time.Clock()
    
    # Učitaj pozadinu
    pozadina = pg.image.load("textures/background.png")
    pozadina = pg.transform.scale(pozadina, WIN_RES)
    
    # Postavi fontove
    naslov_font = pg.font.SysFont('consolas', 64)
    izbornik_font = pg.font.SysFont('consolas', 32)
    mali_font = pg.font.SysFont('consolas', 20)
    
    # Učitaj ikone zvuka
    try:
        zvucnik_ukljucen = pg.image.load("textures/zvucnik.png").convert_alpha()
        zvucnik_iskljucen = pg.image.load("textures/ugasen_zvucnik.png").convert_alpha()
        zvucnik_ukljucen = pg.transform.scale(zvucnik_ukljucen, (32, 32))
        zvucnik_iskljucen = pg.transform.scale(zvucnik_iskljucen, (32, 32))
    except:
        # Fallback ako slike ne postoje
        zvucnik_ukljucen = pg.Surface((32, 32))
        zvucnik_ukljucen.fill((255, 255, 255))
        zvucnik_iskljucen = pg.Surface((32, 32))
        zvucnik_iskljucen.fill((100, 100, 100))
    
    # Inicijaliziraj glazbu
    glazba_ukljucena = True
    try:
        pg.mixer.music.load("sounds/background.mp3")
        pg.mixer.music.play(-1)  # Loop glazbu
        pg.mixer.music.set_volume(0.5)
        ui_zvuk = pg.mixer.Sound("sounds/boop-417-mhz-39313.mp3")
        ui_zvuk.set_volume(0.3)
    except:
        glazba_ukljucena = False
        ui_zvuk = None
        print("Nije moguće učitati background glazbu")

    def nacrtaj_gumb(tekst, centar_y, hover):
        """Nacrtaj gumb s hover efektom"""
        w, h = 280, 64
        pravokutnik = pg.Rect(0, 0, w, h)
        pravokutnik.center = (WIDTH // 2, centar_y)
        boja = (80, 70, 50) if hover else (40, 40, 40)
        pg.draw.rect(ekran, boja, pravokutnik, border_radius=10)
        pg.draw.rect(ekran, (200, 170, 120), pravokutnik, width=2, border_radius=10)
        label = izbornik_font.render(tekst, True, (230, 220, 200))
        ekran.blit(label, label.get_rect(center=pravokutnik.center))
        return pravokutnik

    u_o_igri = False
    while True:
        # Nacrtaj pozadinu s overlay-om
        ekran.blit(pozadina, (0, 0))
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        ekran.blit(overlay, (0, 0))

        if not u_o_igri:
            # Glavni izbornik
            naslov = naslov_font.render('Airship Shoot \'Em Up', True, (230, 220, 200))
            ekran.blit(naslov, naslov.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160)))

            mx, my = pg.mouse.get_pos()
            igraj_rect = nacrtaj_gumb('Play', HEIGHT // 2 - 40, 
                pg.Rect(WIDTH // 2 - 140, HEIGHT // 2 - 40 - 32, 280, 64).collidepoint(mx, my))
            o_igri_rect = nacrtaj_gumb('About', HEIGHT // 2 + 40, 
                pg.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 40 - 32, 280, 64).collidepoint(mx, my))
            izlaz_rect = nacrtaj_gumb('Exit', HEIGHT // 2 + 120, 
                pg.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 120 - 32, 280, 64).collidepoint(mx, my))
            
            # Gumb za zvuk
            zvucnik_rect = pg.Rect(WIDTH // 2 - 16, HEIGHT // 2 + 180, 32, 32)
            zvucnik_hover = zvucnik_rect.collidepoint(mx, my)
            
            if zvucnik_hover:
                pg.draw.rect(ekran, (80, 70, 50), zvucnik_rect, border_radius=5)
            pg.draw.rect(ekran, (200, 170, 120), zvucnik_rect, width=2, border_radius=5)
            
            trenutni_zvucnik = zvucnik_ukljucen if glazba_ukljucena else zvucnik_iskljucen
            ekran.blit(trenutni_zvucnik, zvucnik_rect)

            # Prikaži kontrole
            savjet = mali_font.render('WASD move | Arrows rotate | Space shoot | M mute | Esc exit', True, (210, 200, 180))
            ekran.blit(savjet, savjet.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

            # Obrađuj događaje
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.mixer.music.stop()
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if igraj_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_zvuk: ui_zvuk.play()
                        pg.mixer.music.stop()
                        return
                    elif o_igri_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_zvuk: ui_zvuk.play()
                        u_o_igri = True
                    elif izlaz_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_zvuk: ui_zvuk.play()
                        pg.mixer.music.stop()
                        pg.quit()
                        sys.exit()
                    elif zvucnik_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_zvuk: ui_zvuk.play()
                        if glazba_ukljucena:
                            pg.mixer.music.pause()
                            glazba_ukljucena = False
                        else:
                            pg.mixer.music.unpause()
                            glazba_ukljucena = True
        else:
            # O igri ekran
            header = naslov_font.render('About Game', True, (230, 220, 200))
            ekran.blit(header, header.get_rect(center=(WIDTH // 2, 140)))

            o_igri_linije = [
                "A fast-paced steampunk shoot 'em up with zeppelins and airship combat.",
                "Fly over Mode7-rendered landscapes, dodge enemy fire, and defeat bosses.",
                "Collect power-ups, upgrade your weapons, and survive increasingly", 
                "challenging enemy formations in the skies.",
            ]
            y = 220
            for linija in o_igri_linije:
                label = izbornik_font.render(linija, True, (220, 210, 190))
                ekran.blit(label, label.get_rect(center=(WIDTH // 2, y)))
                y += 40

            mx, my = pg.mouse.get_pos()
            nazad_rect = nacrtaj_gumb('Back', HEIGHT - 120, 
                pg.Rect(WIDTH // 2 - 140, HEIGHT - 120 - 32, 280, 64).collidepoint(mx, my))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.mixer.music.stop()
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    u_o_igri = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if nazad_rect.collidepoint(pg.mouse.get_pos()):
                        if ui_zvuk: ui_zvuk.play()
                        u_o_igri = False

        pg.display.flip()
        sat.tick(60)


class App:
    def __init__(self):
        """Inicijaliziraj glavnu aplikaciju"""
        pg.init()
        self.ekran = pg.display.set_mode(WIN_RES, pg.FULLSCREEN | pg.SCALED)
        self.sat = pg.time.Clock()
        self.mode7 = Mode7(self)
        self.igra = Game(self.mode7)
        self.font = pg.font.SysFont('consolas', 28)
        self.veliki_font = pg.font.SysFont('consolas', 64)
        self.running = True
        
        # Učitaj parallax oblačke
        try:
            self.oblak1 = pg.image.load('textures/cloud1.png').convert_alpha()
            self.oblak2 = pg.image.load('textures/cloud2.png').convert_alpha()
            self.oblak3 = pg.image.load('textures/cloud3.png').convert_alpha()
            
            # Skaliraj oblačke na različite veličine
            self.oblak1 = pg.transform.scale(self.oblak1, (200, 100))
            self.oblak2 = pg.transform.scale(self.oblak2, (150, 75))
            self.oblak3 = pg.transform.scale(self.oblak3, (100, 50))
        except:
            # Fallback - kreiraj ljepše oblačke
            self.oblak1 = self.kreiraj_oblak_surface(200, 100, (255, 255, 255, 60))
            self.oblak2 = self.kreiraj_oblak_surface(150, 75, (255, 255, 255, 40))
            self.oblak3 = self.kreiraj_oblak_surface(100, 50, (255, 255, 255, 25))
        
        # Pozicije oblačaka (svjetske koordinate) - raspoređeno po cijeloj mapi
        self.oblak_pozicije = [
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

    def kreiraj_oblak_surface(self, sirina, visina, boja):
        """Kreiraj ljepšu oblačku s više krugova i gradijentima"""
        surface = pg.Surface((sirina, visina), pg.SRCALPHA)
        
        # Glavni krugovi oblačke
        krugovi = [
            (sirina//2, visina//2, min(sirina, visina)//3),  # Središnji
            (sirina//3, visina//2, min(sirina, visina)//4),  # Lijevi
            (2*sirina//3, visina//2, min(sirina, visina)//4),  # Desni
            (sirina//2, visina//3, min(sirina, visina)//5),  # Gornji
            (sirina//2, 2*visina//3, min(sirina, visina)//5),  # Donji
        ]
        
        # Nacrtaj glavne krugove s gradijentom
        for x, y, radius in krugovi:
            # Vanjski krug (svjetliji)
            pg.draw.circle(surface, (*boja[:3], boja[3]//2), (x, y), radius + 2)
            # Glavni krug
            pg.draw.circle(surface, boja, (x, y), radius)
            # Unutarnji krug (tamniji)
            pg.draw.circle(surface, (*boja[:3], boja[3]//3), (x, y), radius - 2)
        
        # Dodaj male krugove za teksturu
        for _ in range(8):
            x = np.random.randint(5, sirina-5)
            y = np.random.randint(5, visina-5)
            radius = np.random.randint(3, 8)
            alpha = np.random.randint(20, boja[3])
            pg.draw.circle(surface, (*boja[:3], alpha), (x, y), radius)
        
        return surface

    def update(self):
        """Ažuriraj stanje igre"""
        self.mode7.update()
        self.igra.update(self.mode7.pos)
        self.igra.handle_tutorial_input()
        self.sat.tick()
        pg.display.set_caption(f'{self.sat.get_fps():.1f}')

    def draw(self):
        """Nacrtaj sve elemente igre"""
        self.mode7.draw()
        self.nacrtaj_parallax_oblake()  # Nacrtaj oblačke iznad mode7
        self.igra.draw(self.ekran)
        self.nacrtaj_hud()
        
        # Hit flash efekt
        now_ms = pg.time.get_ticks()
        if now_ms < getattr(self.igra, 'hit_flash_end_ms', 0):
            flash = pg.Surface(WIN_RES, pg.SRCALPHA)
            flash.fill((220, 40, 40, 120))
            self.ekran.blit(flash, (0, 0))
        
        # Wave timer (ako nema weapon unlock)
        if getattr(self.igra, 'is_wave_starting', False) and not (self.igra.last_unlocked_weapon and self.igra.game_frozen):
            self.nacrtaj_wave_timer()
            
        if self.igra.game_over:
            self.nacrtaj_game_over()
        elif getattr(self.igra, 'game_won', False):
            self.nacrtaj_win_screen()
        pg.display.flip()

    def check_event(self, event):
        """Obrađuje događaje tipkovnice i miša"""
        if self.igra.tutorial_active:
            return True
            
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            return False
        
        if event.type == pg.KEYDOWN:
            # Promjena oružja (tipke 1-6)
            oruzja = ['basic', 'heavy', 'rapid', 'sniper', 'shotgun', 'plasma']
            for i, oruzje in enumerate(oruzja, 1):
                if event.key == getattr(pg, f'K_{i}') and oruzje in self.igra.unlocked_weapons and not (self.igra.game_over or self.igra.game_won):
                    self.igra.current_weapon = oruzje
                    if self.igra.weapon_switch_sound:
                        self.igra.weapon_switch_sound.play()
                    break
            
            # Mute glazba
            if event.key == pg.K_m and not (self.igra.game_over or self.igra.game_won):
                self.igra.music_muted = not self.igra.music_muted
                try:
                    if self.igra.music_muted:
                        pg.mixer.music.pause()
                    else:
                        pg.mixer.music.unpause()
                except:
                    pass
            
            # Pucanje
            if event.key == pg.K_SPACE and not (self.igra.game_over or self.igra.game_won):
                self.igra.start_auto_fire()
            
            # Restart
            if event.key == pg.K_r and (self.igra.game_over or self.igra.game_won):
                self.igra.reset()
        
        elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
            self.igra.stop_auto_fire()
        
        return True

    def run(self):
        """Glavna petlja igre"""
        prikazi_izbornik(self.ekran)
        while self.running:
            for event in pg.event.get():
                if not self.check_event(event):
                    self.running = False
            self.update()
            self.draw()
        pg.quit()

    def nacrtaj_hud(self):
        """Nacrtaj HUD (heads-up display)"""
        # HP bar (centar gore)
        hp_ratio = self.igra.player_hp / self.igra.player_max_hp
        bar_sirina, bar_visina = 300, 25
        bar_x = (WIDTH - bar_sirina) // 2
        bar_y = 20
        
        pg.draw.rect(self.ekran, (60, 60, 60), (bar_x, bar_y, bar_sirina, bar_visina))
        pg.draw.rect(self.ekran, (200, 60, 40), (bar_x, bar_y, int(bar_sirina * hp_ratio), bar_visina))
        hp_tekst = self.font.render(f'HP: {self.igra.player_hp}/{self.igra.player_max_hp}', True, (255, 255, 255))
        self.ekran.blit(hp_tekst, hp_tekst.get_rect(center=(WIDTH//2, bar_y + bar_visina//2)))
        
        # Wave (ispod HP)
        wave_tekst = f'Wave: {self.igra.wave}' if self.igra.wave < 5 else 'FINAL ROUND'
        wave_surface = self.font.render(wave_tekst, True, (255, 255, 255))
        self.ekran.blit(wave_surface, wave_surface.get_rect(center=(WIDTH//2, bar_y + bar_visina + 25)))
        
        # Trenutno oružje i sljedeći unlock (gore desno)
        oruzje = self.igra.weapons[self.igra.current_weapon]
        oruzje_tekst = self.font.render(f'Weapon: {oruzje.name}', True, (255, 255, 255))
        self.ekran.blit(oruzje_tekst, (WIDTH - 350, 20))
        
        # Sljedeći unlock
        sljedeci_unlock_score = float('inf')
        sljedeci_unlock = None
        for ime_oruzja, potreban_score in self.igra.weapon_unlock_requirements.items():
            if ime_oruzja not in self.igra.unlocked_weapons and potreban_score < sljedeci_unlock_score:
                sljedeci_unlock = ime_oruzja
                sljedeci_unlock_score = potreban_score
        
        if sljedeci_unlock:
            preostali_score = sljedeci_unlock_score - self.igra.score
            sljedece_oruzje_ime = self.igra.weapons[sljedeci_unlock].name
            unlock_tekst = self.font.render(f'Next: {sljedece_oruzje_ime} ({preostali_score} XP)', True, (255, 255, 0))
            self.ekran.blit(unlock_tekst, (WIDTH - 350, 50))
        
        # Score, unlocked count, controls, power-ups (gore lijevo)
        y_pos = 20
        tekstovi = [
            f'Score: {self.igra.score}',
            f'Unlocked: {len(self.igra.unlocked_weapons)}/{len(self.igra.weapons)}',
            '1-6: Change Weapon | SPACE: Shoot | M: Mute'
        ]
        boje = [(255, 255, 255), (255, 255, 255), (200, 200, 200)]
        
        for tekst, boja in zip(tekstovi, boje):
            tekst_surface = self.font.render(tekst, True, boja)
            self.ekran.blit(tekst_surface, (20, y_pos))
            y_pos += 30
        
        # Aktivni power-ups
        now_ms = pg.time.get_ticks()
        y_pos = 110
        for power_tip, kraj_vrijeme in self.igra.active_power_ups.items():
            if now_ms < kraj_vrijeme:
                preostalo_vrijeme = (kraj_vrijeme - now_ms) / 1000
                power_tekst = self.font.render(f'{power_tip.title()}: {preostalo_vrijeme:.1f}s', True, (255, 255, 0))
                self.ekran.blit(power_tekst, (20, y_pos))
                y_pos += 25
        
        # Tutorial ili weapon unlock ekrani
        if self.igra.tutorial_active:
            self.nacrtaj_tutorial_ekran()
        elif self.igra.last_unlocked_weapon and self.igra.game_frozen:
            self.nacrtaj_weapon_unlock_ekran()

    def nacrtaj_parallax_oblake(self):
        """Nacrtaj oblačne slojeve s parallax efektom"""
        # Parallax faktori (sporiji dalji sloj, brži bliski sloj)
        parallax_faktori = [0.3, 0.6, 1.0]  # Dalji, srednji, bliski
        
        # Dodaj blagi drift efekt
        now_ms = pg.time.get_ticks()
        drift_offset = np.sin(now_ms * 0.0005) * 0.5
        
        for layer_idx, (oblak_textura, pozicije, parallax_faktor) in enumerate([
            (self.oblak1, self.oblak_pozicije[0], parallax_faktori[0]),
            (self.oblak2, self.oblak_pozicije[1], parallax_faktori[1]),
            (self.oblak3, self.oblak_pozicije[2], parallax_faktori[2])
        ]):
            for oblak_pos in pozicije:
                # Izračunaj relativnu poziciju oblačke
                relative_x = oblak_pos[0] - self.mode7.pos[0] + drift_offset * parallax_faktor
                relative_y = oblak_pos[1] - self.mode7.pos[1]
                
                # Primijeni parallax faktor
                parallax_x = relative_x * parallax_faktor
                parallax_y = relative_y * parallax_faktor
                
                # Rotiraj poziciju prema kutu kamere
                rotated_x = parallax_x * np.cos(self.mode7.angle) - parallax_y * np.sin(self.mode7.angle)
                rotated_y = parallax_x * np.sin(self.mode7.angle) + parallax_y * np.cos(self.mode7.angle)
                
                # Projektiraj na ekran
                if rotated_y > 0.1:  # Izbjegni division by zero
                    screen_x = int(WIDTH // 2 + rotated_x / rotated_y * WIDTH // 3)  # Veći prostor
                    screen_y = int(HEIGHT // 2 - 50 / rotated_y)  # Fiksna visina za oblačke
                    
                    # Provjeri je li oblačka vidljiva na ekranu (veći prostor)
                    if -300 < screen_x < WIDTH + 300 and -150 < screen_y < HEIGHT + 150:
                        # Scale oblačku prema udaljenosti
                        scale = max(0.1, min(2.0, 1.0 / rotated_y))
                        scaled_sirina = int(oblak_textura.get_width() * scale)
                        scaled_visina = int(oblak_textura.get_height() * scale)
                        
                        if scaled_sirina > 0 and scaled_visina > 0:
                            scaled_oblak = pg.transform.scale(oblak_textura, (scaled_sirina, scaled_visina))
                            oblak_rect = scaled_oblak.get_rect(center=(screen_x, screen_y))
                            
                            # Dodaj blagi glow efekt
                            glow_surface = pg.Surface((scaled_sirina + 4, scaled_visina + 4), pg.SRCALPHA)
                            glow_surface.fill((255, 255, 255, 10))
                            glow_rect = glow_surface.get_rect(center=(screen_x, screen_y))
                            self.ekran.blit(glow_surface, glow_rect)
                            
                            # Nacrtaj oblačku
                            self.ekran.blit(scaled_oblak, oblak_rect)

    def nacrtaj_overlay_ekran(self, naslov, podnaslov, statistike, boja_okvira):
        """Generički overlay ekran za Game Over/Victory"""
        now_ms = pg.time.get_ticks()
        
        # Animirani overlay
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.003)) * 0.3 + 0.7
        
        for y in range(HEIGHT):
            if boja_okvira == (150, 50, 50):  # Game Over
                alpha = int((180 + (y / HEIGHT) * 40) * pulse)
            else:  # Victory
                alpha = int((120 + (y / HEIGHT) * 60) * pulse)
            overlay.fill((0, 0, 0, alpha), (0, y, WIDTH, 1))
        self.ekran.blit(overlay, (0, 0))
        
        # Naslov s sjenom
        naslov_sjena = self.veliki_font.render(naslov, True, (100, 0, 0) if boja_okvira == (150, 50, 50) else (150, 150, 0))
        naslov_glavni = self.veliki_font.render(naslov, True, (255, 100, 100) if boja_okvira == (150, 50, 50) else (255, 255, 100))
        
        naslov_offset = int(np.sin(now_ms * 0.005) * 3)
        naslov_rect = naslov_glavni.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + naslov_offset))
        sjena_rect = naslov_sjena.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 97 + naslov_offset))
        
        self.ekran.blit(naslov_sjena, sjena_rect)
        self.ekran.blit(naslov_glavni, naslov_rect)
        
        # Podnaslov
        if podnaslov:
            podnaslov_tekst = self.font.render(podnaslov, True, (255, 255, 200))
            self.ekran.blit(podnaslov_tekst, podnaslov_tekst.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        
        # Statistike
        y_offset = 0 if not podnaslov else 50
        for i, (tekst, boja) in enumerate(statistike):
            stat_tekst = self.font.render(tekst, True, boja)
            self.ekran.blit(stat_tekst, stat_tekst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset + i * 40)))
        
        # Animirani okvir
        border_pulse = abs(np.sin(now_ms * 0.002)) * 0.5 + 0.5
        animirani_okvir = tuple(int(c * border_pulse) for c in boja_okvira)
        pg.draw.rect(self.ekran, animirani_okvir, (50, 50, WIDTH - 100, HEIGHT - 100), 4)
        
        # Restart instrukcija
        restart_pulse = abs(np.sin(now_ms * 0.005)) * 0.4 + 0.6
        restart_boja = tuple(int(200 * restart_pulse) for _ in range(3))
        restart_tekst = self.font.render('Press R to restart', True, restart_boja)
        self.ekran.blit(restart_tekst, restart_tekst.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

    def nacrtaj_tutorial_ekran(self):
        """Nacrtaj tutorial ekran"""
        now_ms = pg.time.get_ticks()
        
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.ekran.blit(overlay, (0, 0))
        
        stranica = self.igra.tutorial_pages[self.igra.tutorial_page]
        
        # Animirani naslov
        naslov_pulse = abs(np.sin(now_ms * 0.003)) * 0.3 + 0.7
        naslov_boja = (int(255 * naslov_pulse), int(215 * naslov_pulse), 0)
        naslov_tekst = self.veliki_font.render(stranica['title'], True, naslov_boja)
        self.ekran.blit(naslov_tekst, naslov_tekst.get_rect(center=(WIDTH // 2, 150)))
        
        # Podnaslov
        podnaslov_tekst = self.font.render(stranica['subtitle'], True, (200, 200, 200))
        self.ekran.blit(podnaslov_tekst, podnaslov_tekst.get_rect(center=(WIDTH // 2, 220)))
        
        # Sadržaj
        sadrzaj_y = 300
        for linija in stranica['content']:
            sadrzaj_tekst = self.font.render(linija, True, (255, 255, 255))
            self.ekran.blit(sadrzaj_tekst, sadrzaj_tekst.get_rect(center=(WIDTH // 2, sadrzaj_y)))
            sadrzaj_y += 40
        
        # Animirani okvir
        pulse = int(np.sin(now_ms * 0.01) * 10)
        pg.draw.rect(self.ekran, (255, 215, 0), (50 + pulse, 100 + pulse, WIDTH - 100 - 2*pulse, HEIGHT - 200 - 2*pulse), 4)

    def nacrtaj_game_over(self):
        """Nacrtaj game over ekran"""
        statistike = [
            (f'Final Score: {self.igra.score}', (255, 255, 200)),
            (f'Waves Completed: {self.igra.wave - 1}', (255, 255, 200))
        ]
        self.nacrtaj_overlay_ekran('GAME OVER', None, statistike, (150, 50, 50))

    def nacrtaj_win_screen(self):
        """Nacrtaj victory ekran"""
        statistike = [
            (f'Final Score: {self.igra.score}', (255, 255, 200)),
            (f'All 5 Waves Completed!', (255, 255, 200))
        ]
        self.nacrtaj_overlay_ekran('VICTORY!', 'You defeated all enemies!', statistike, (255, 255, 100))

    def nacrtaj_wave_timer(self):
        """Nacrtaj wave timer ekran"""
        now_ms = pg.time.get_ticks()
        
        # Animirani overlay
        overlay = pg.Surface(WIN_RES, pg.SRCALPHA)
        pulse = abs(np.sin(now_ms * 0.004)) * 0.4 + 0.6
        overlay.fill((0, 0, 0, int(180 * pulse)))
        self.ekran.blit(overlay, (0, 0))
        
        # Izračunaj preostalo vrijeme
        preostalo_ms = max(0, getattr(self.igra, 'wave_start_timer_ms', 0) - now_ms)
        preostalo_sekundi = (preostalo_ms // 1000) + 1
        
        # Odredi sljedeći wave
        if getattr(self.igra, 'starting_wave_1', False):
            sljedeci_wave = 1
        else:
            sljedeci_wave = self.igra.wave + 1
        
        # Konfiguracija za svaki wave
        wave_configs = {
            1: ("WAVE 1", "Destroy the basic enemies!"),
            2: ("WAVE 2", "Heavy enemies incoming!"),
            3: ("WAVE 3", "Fast enemies attack!"),
            4: ("MINI BOSS FIGHT", "WARNING: Boss deals massive damage on contact & Watch out for fast bullets!"),
            5: ("BOSS FIGHT", "WARNING: Boss deals massive damage on contact & Watch out for slow but heavy bullets!")
        }
        wave_naslov, wave_podnaslov = wave_configs.get(sljedeci_wave, (f"WAVE {sljedeci_wave}", ""))
        
        # Wave naslov
        wave_tekst = self.veliki_font.render(wave_naslov, True, (255, 200, 100))
        self.ekran.blit(wave_tekst, wave_tekst.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))
        
        # "starts in..." tekst
        tip_tekst = self.font.render('starts in...', True, (230, 230, 230))
        self.ekran.blit(tip_tekst, tip_tekst.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
        
        # Animirani timer
        timer_pulse = abs(np.sin(now_ms * 0.01)) * 0.3 + 0.7
        timer_boja = (int(255 * timer_pulse), int(255 * timer_pulse), int(100 * timer_pulse))
        timer_tekst = self.veliki_font.render(f'{preostalo_sekundi}', True, timer_boja)
        
        timer_offset = int(np.sin(now_ms * 0.008) * 5)
        self.ekran.blit(timer_tekst, timer_tekst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + timer_offset)))
        
        # Podnaslov
        if wave_podnaslov:
            podnaslov_alpha = abs(np.sin(now_ms * 0.006)) * 0.5 + 0.5
            podnaslov_boja = tuple(int(200 * podnaslov_alpha) for _ in range(3))
            podnaslov_tekst = self.font.render(wave_podnaslov, True, podnaslov_boja)
            self.ekran.blit(podnaslov_tekst, podnaslov_tekst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

    def nacrtaj_weapon_unlock_ekran(self):
        """Prikaz ekrana za otključavanje oružja"""
        ime_oruzja = self.igra.weapons[self.igra.last_unlocked_weapon].name
        
        # Opisi oružja
        opisi_oruzja = {
            'basic': 'Basic laser - fast and accurate (2 shots/sec)',
            'heavy': 'Heavy cannon - powerful but slow (1 shot/2 sec)',
            'rapid': 'Rapid fire - automatic shooting (6 shots/sec)',
            'sniper': 'Sniper rifle - precise and long range (1.5 shots/sec)',
            'shotgun': 'Shotgun - 3 projectiles at once (1.5 shots/sec)',
            'plasma': 'Plasma gun - advanced weapon (2 shots/sec)'
        }
        
        tipke_oruzja = ['1', '2', '3', '4', '5', '6']
        oruzja = ['basic', 'heavy', 'rapid', 'sniper', 'shotgun', 'plasma']
        tipka = tipke_oruzja[oruzja.index(self.igra.last_unlocked_weapon)] if self.igra.last_unlocked_weapon in oruzja else '?'
        
        opis = opisi_oruzja.get(self.igra.last_unlocked_weapon, 'New weapon!')
        
        # Pozadina
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.ekran.blit(overlay, (0, 0))
        
        # Naslov
        naslov_font = pg.font.Font(None, 72)
        naslov_tekst = naslov_font.render('WEAPON UNLOCKED!', True, (255, 215, 0))
        self.ekran.blit(naslov_tekst, naslov_tekst.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))
        
        # Ime oružja s tipkom
        oruzje_font = pg.font.Font(None, 48)
        oruzje_tekst = oruzje_font.render(f'{ime_oruzja} (Key {tipka})', True, (255, 255, 255))
        self.ekran.blit(oruzje_tekst, oruzje_tekst.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
        
        # Opis
        opis_font = pg.font.Font(None, 32)
        opis_tekst = opis_font.render(opis, True, (200, 200, 200))
        self.ekran.blit(opis_tekst, opis_tekst.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        
        # Timer
        now_ms = pg.time.get_ticks()
        preostalo_vrijeme = (self.igra.freeze_duration - (now_ms - self.igra.freeze_start_time)) / 1000
        timer_tekst = opis_font.render(f'Resuming in {preostalo_vrijeme:.1f}s...', True, (150, 150, 150))
        self.ekran.blit(timer_tekst, timer_tekst.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
        
        # Animirani okvir
        pulse = int(np.sin(now_ms * 0.01) * 10)
        pg.draw.rect(self.ekran, (255, 215, 0), (50 + pulse, 150 + pulse, WIDTH - 100 - 2*pulse, HEIGHT - 300 - 2*pulse), 4)


if __name__ == '__main__':
    app = App()
    app.run()