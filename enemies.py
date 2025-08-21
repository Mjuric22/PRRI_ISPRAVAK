import pygame as pg
import numpy as np

class Enemy:
    def __init__(self, pos, speed=0.02, hp=3):
        self.pos = np.array(pos, dtype=np.float32)  # Pohrana pozicije kao [x, y]
        self.speed = speed
        self.alive = True
        self.hp = hp
        self.texture = pg.image.load('textures/airship_1.png').convert_alpha()
    
    def update(self, player_pos):
        # Jednostavna AI logika: kretanje prema igraču
        direction = player_pos - self.pos
        distance = np.linalg.norm(direction)
        if distance > 0:
            self.pos += (direction / distance) * self.speed
    
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
    def __init__(self, player_pos, player_angle, speed=0.5, max_distance=20, damage=1):
        # Pretvaranje kuta u radijane (ako je potrebno)
        player_angle = np.radians(player_angle) if player_angle > np.pi * 2 else player_angle
        
        # Izračun smjera projektila (korekcija od 90°)
        direction_x = np.cos(player_angle - np.pi/2)
        direction_y = -np.sin(player_angle - np.pi/2)
        self.direction = np.array([direction_x, direction_y], dtype=np.float32)
        
        # Početni pomak projektila u smjeru kretanja
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
        
        # Veličina projektila ovisno o udaljenosti
        distance_traveled = np.linalg.norm(self.pos - self.start_pos)
        initial_size = 9  # Početna veličina
        min_size = 1  # Najmanja veličina kada je daleko
        size = max(min_size, initial_size - int(distance_traveled / self.max_distance * initial_size))
        
        pg.draw.circle(screen, (0, 0, 0), (int(screen_x), int(screen_y)), size)  # Crtanje projektila


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

        # Kolizija igrača i neprijatelja
        now_ms = pg.time.get_ticks()
        for enemy in self.enemies:
            if np.linalg.norm(enemy.pos - player_pos) < 1.2:
                if now_ms - self.last_player_hit_ms >= self.player_hit_cooldown_ms:
                    self.player_hp -= 1
                    self.last_player_hit_ms = now_ms
                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.game_over = True
                break

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

