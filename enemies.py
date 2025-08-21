import pygame as pg
import numpy as np

class Enemy:
    def __init__(self, pos, speed=0.02, hp=3):
        self.pos = np.array(pos, dtype=np.float32)  # Pohrana pozicije kao [x, y]
        self.speed = speed
        self.alive = True
        self.hp = hp
        self.texture = pg.image.load('textures/airship_1.png').convert_alpha()
        # Svaki neprijatelj dobiva blagi nasumični "strafe" faktor (ne idu svi u istu liniju)
        self.strafe_bias = float(np.random.uniform(-0.4, 0.4))
        self.retarget_interval_ms = int(np.random.randint(1400, 2600))
        self.next_retarget_ms = int(pg.time.get_ticks() + self.retarget_interval_ms)
    
    def update(self, player_pos):
        # Uvijek juri prema igraču, ali s blagim "strafe" skretanjem da se ne skupljaju
        now_ms = pg.time.get_ticks()
        if now_ms >= self.next_retarget_ms:
            self.strafe_bias = float(np.random.uniform(-0.4, 0.4))
            self.retarget_interval_ms = int(np.random.randint(1200, 2600))
            self.next_retarget_ms = int(now_ms + self.retarget_interval_ms)

        direction = player_pos - self.pos
        distance = np.linalg.norm(direction)
        if distance > 1e-5:
            unit = direction / distance
            # Vektor okomit na smjer prema igraču
            perp = np.array([-unit[1], unit[0]], dtype=np.float32)
            biased_dir = unit + perp * self.strafe_bias
            # Normalizacija kako bismo zadržali konstantnu brzinu
            norm = float(np.linalg.norm(biased_dir))
            if norm > 1e-6:
                biased_dir = biased_dir / norm
            # Osiguraj kretanje naprijed (prema igraču), ne od igrača
            if np.dot(biased_dir, unit) <= 0.0:
                biased_dir = unit
            self.pos += biased_dir * self.speed
    
    def draw(self, screen, mode7):
        # Projekcija svjetskih koordinata na ekran putem Mode7 projekcije
        screen_x, screen_y, scale = mode7.project(self.pos)
        
        if scale > 0:  # Prikaži neprijatelja samo ako je u vidnom polju
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale//2, int(screen_y) - scale//2))
            # Traka zdravlja neprijatelja
            bar_width = max(10, scale)
            bar_height = 4
            hp_ratio = max(0.0, min(1.0, self.hp / 3.0))
            bar_x = int(screen_x) - bar_width // 2
            bar_y = int(screen_y) - scale // 2 - 8
            pg.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            pg.draw.rect(screen, (200, 60, 40), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
    
    def check_collision(self, projectile):
        return np.linalg.norm(self.pos - projectile.pos) < 0.6  # Provjera sudara na temelju udaljenosti


class Projectile:
    def __init__(self, player_pos, player_angle, speed=0.6, max_distance=22, damage=1):
        # Smjer projektila točno prema smjeru pogleda (Mode7 forward = [sin(a), cos(a)])
        direction_x = np.sin(player_angle)
        direction_y = np.cos(player_angle)
        self.direction = np.array([direction_x, direction_y], dtype=np.float32)
        
        # Početni pomak projektila u smjeru kretanja (ispred igrača)
        offset_distance = 2.0
        rotated_offset_x = offset_distance * direction_x
        rotated_offset_y = offset_distance * direction_y
        
        self.pos = np.array(player_pos, dtype=np.float32) + np.array([rotated_offset_x, rotated_offset_y])
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True
        self.damage = damage

    def update(self):
        self.pos += self.direction * self.speed

        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    
    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale <= 0:
            return
        # Veličinu vežemo uz perspektivu (Mode7 scale) i garantiramo vidljivost
        size = max(3, min(10, int(scale * 0.4)))
        # Kontrastna boja da se jasno vidi na tamnoj pozadini
        pg.draw.circle(screen, (255, 220, 80), (int(screen_x), int(screen_y)), size)


class Game:
    def __init__(self, mode7):
        self.mode7 = mode7
        self.enemies = [Enemy((5, 5)), Enemy((-5, 2)), Enemy((5, -5)), Enemy((-5, -2))]
        self.projectiles = []
        self.score = 0
        self.player_max_hp = 5
        self.player_hp = self.player_max_hp
        self.last_player_hit_ms = 0
        self.player_hit_cooldown_ms = 800
        self.game_over = False
        # Vizualni efekt pri pogotku (trajanje u ms)
        self.hit_flash_end_ms = 0
        # Opcionalni zvuk pogotka (spremi datoteku u sounds/hit.wav)
        self.hit_sound = None
        try:
            self.hit_sound = pg.mixer.Sound('sounds/hit.mp3')
        except Exception:
            self.hit_sound = None
    
    def update(self, player_pos):
        if self.game_over:
            return

        for enemy in self.enemies:
            enemy.update(player_pos)
        for projectile in self.projectiles:
            projectile.update()

        # Kolizija projektila i neprijatelja
        enemies_to_remove = []
        for projectile in self.projectiles:
            if not projectile.active:
                continue
            for enemy in self.enemies:
                if enemy.check_collision(projectile):
                    enemy.hp -= projectile.damage
                    projectile.active = False
                    if enemy.hp <= 0:
                        enemies_to_remove.append(enemy)
                        self.score += 100
                    break

        # Uklanjanje uništenih neprijatelja
        if enemies_to_remove:
            self.enemies = [e for e in self.enemies if e not in enemies_to_remove]

        # Kolizija igrača i neprijatelja (samo jako blizu) — neprijatelj nestaje na kontakt, bez cooldowna
        now_ms = pg.time.get_ticks()
        enemy_to_remove_on_contact = None
        for enemy in self.enemies:
            if np.linalg.norm(enemy.pos - player_pos) < 0.6:
                enemy_to_remove_on_contact = enemy
                # Svaki kontakt odmah oduzima HP (bez cooldowna)
                self.player_hp -= 1
                # Postavi flash efekt i pusti zvuk (ako postoji)
                self.hit_flash_end_ms = now_ms + 180
                if self.hit_sound:
                    try:
                        self.hit_sound.play()
                    except Exception:
                        pass
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.game_over = True
                break
        if enemy_to_remove_on_contact is not None:
            self.enemies = [e for e in self.enemies if e is not enemy_to_remove_on_contact]

        # Uklanjanje neaktivnih projektila
        self.projectiles = [p for p in self.projectiles if p.active]
    
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen, self.mode7)
        for projectile in self.projectiles:
            projectile.draw(screen, self.mode7)
    
    def shoot(self, player_pos, player_angle):
        self.projectiles.append(Projectile(player_pos, player_angle))

    def reset(self):
        self.enemies = [Enemy((5, 5)), Enemy((-5, 2)), Enemy((5, -5)), Enemy((-5, -2))]
        self.projectiles = []
        self.score = 0
        self.player_hp = self.player_max_hp
        self.last_player_hit_ms = 0
        self.game_over = False
        self.hit_flash_end_ms = 0

