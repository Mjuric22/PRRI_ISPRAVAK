import pygame as pg
import numpy as np

def random_spawn_positions(count, min_dist=3, max_dist=8):
    """Generira nasumične pozicije za spawn neprijatelja"""

    positions = []
    for _ in range(count):
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(min_dist, max_dist)
        x = np.cos(angle) * distance
        y = np.sin(angle) * distance
        positions.append((x, y))
    return positions

class Enemy:
    def __init__(self, pos, speed=0.02, hp=3, enemy_type=1):
        self.pos = np.array(pos, dtype=np.float32)
        self.speed = speed
        self.hp = hp
        self.enemy_type = enemy_type
        
        # Učitaj teksturu ovisno o tipu
        texture_paths = {
            1: 'textures/airship_1.png',
            2: 'textures/enemy_2.png', 
            3: 'textures/enemy_3.png',
            4: 'textures/enemy_4.png',
            5: 'textures/enemy_5.png'
        }
        texture_path = texture_paths.get(enemy_type, 'textures/airship_1.png')
        self.texture = pg.image.load(texture_path).convert_alpha()
        
        # Nasumični faktori kretanja
        self.strafe_bias = float(np.random.uniform(-1.0, 1.0))
        self.orbit_radius = float(np.random.uniform(1.5, 8.0))
        self.movement_pattern = np.random.randint(0, 4)
        self.retarget_interval_ms = int(np.random.randint(500, 3000))
        self.next_retarget_ms = int(pg.time.get_ticks() + self.retarget_interval_ms)
        
        # Target pozicija koja se ažurira svakih 0.5 sekundi
        self.target_pos = np.array(pos, dtype=np.float32)
        self.target_update_interval_ms = 500
        self.next_target_update_ms = int(pg.time.get_ticks() + self.target_update_interval_ms)
        
        # Dodatni nasumični faktori
        self.chaos_factor = float(np.random.uniform(0.0, 0.8))
        self.direction_change_prob = float(np.random.uniform(0.1, 0.4))
        
        # Varijable za pucanje boss-ova (tip 4 i 5)
        self.shoot_timer = 0
        self.shoot_cooldown = 5000
        self.is_shooting = False
        self.shoot_duration = 3000
        self.shoot_start_time = 0
        self.shots_fired = 0
        self.max_shots = 3
        self.target_player_pos = None

    def update(self, player_pos):
        now_ms = pg.time.get_ticks()
        
        # Ažuriraj target poziciju svakih 0.5 sekundi
        if now_ms >= self.next_target_update_ms:
            self.target_pos = np.array(player_pos, dtype=np.float32)
            self.next_target_update_ms = now_ms + self.target_update_interval_ms
        
        # Nasumično mijenjanje patterna kretanja
        if now_ms >= self.next_retarget_ms:
            self.strafe_bias = float(np.random.uniform(-1.0, 1.0))
            self.movement_pattern = np.random.randint(0, 4)
            self.retarget_interval_ms = int(np.random.randint(500, 3000))
            self.next_retarget_ms = int(now_ms + self.retarget_interval_ms)
            self.chaos_factor = float(np.random.uniform(0.0, 0.8))
            self.direction_change_prob = float(np.random.uniform(0.1, 0.4))

        # Logika za pucanje boss-ova
        if self.enemy_type in [4, 5]:
            if not self.is_shooting:
                if self.shoot_timer == 0:
                    self.shoot_timer = now_ms
                
                if now_ms - self.shoot_timer >= self.shoot_cooldown:
                    self.is_shooting = True
                    self.shoot_start_time = now_ms
                    self.shots_fired = 0
                    self.shoot_timer = now_ms
                    self.target_player_pos = np.array(player_pos, dtype=np.float32)
            else:
                if now_ms - self.shoot_start_time >= self.shoot_duration:
                    self.is_shooting = False
                    self.shoot_timer = now_ms
                    self.target_player_pos = None
                else:
                    return  # Ne kreći se dok puca

        # Kretanje
        distance = np.linalg.norm(self.target_pos - self.pos)
        if distance > 1e-5:
            direction = self.target_pos - self.pos
            unit = direction / distance
            
            # Nasumična promjena smjera
            if np.random.random() < self.direction_change_prob:
                self.movement_pattern = np.random.randint(0, 4)
            
            # Različiti patterni kretanja
            if self.movement_pattern == 0:  # Ravno
                move_dir = unit
            elif self.movement_pattern == 1:  # Orbitiranje
                perp = np.array([-unit[1], unit[0]], dtype=np.float32)
                if distance > self.orbit_radius:
                    move_dir = unit
                else:
                    move_dir = perp
            elif self.movement_pattern == 2:  # Zigzag
                perp = np.array([-unit[1], unit[0]], dtype=np.float32)
                move_dir = unit + perp * self.strafe_bias
                norm = float(np.linalg.norm(move_dir))
                if norm > 1e-6:
                    move_dir = move_dir / norm
            else:  # Kaotik
                random_dir = np.array([np.random.uniform(-1, 1), np.random.uniform(-1, 1)], dtype=np.float32)
                norm = float(np.linalg.norm(random_dir))
                if norm > 1e-6:
                    random_dir = random_dir / norm
                move_dir = random_dir * self.chaos_factor + unit * (1.0 - self.chaos_factor)
                norm = float(np.linalg.norm(move_dir))
                if norm > 1e-6:
                    move_dir = move_dir / norm
            
            # Osiguraj kretanje prema igraču
            if self.movement_pattern != 3 and np.dot(move_dir, unit) <= 0.0:
                move_dir = unit
            
            # Dinamička brzina
            speed_multiplier = 1.0
            if distance > 8.0:
                speed_multiplier = 1.5
            elif distance < 3.0:
                speed_multiplier = 0.7
            
            speed_multiplier *= np.random.uniform(0.8, 1.2)
            self.pos += move_dir * (self.speed * speed_multiplier)
    
    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        
        if scale > 0:
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale//2, int(screen_y) - scale//2))
            
            # HP bar
            bar_width = max(10, scale)
            bar_height = 4
            max_hp_values = {1: 3, 2: 5, 3: 1, 4: 10, 5: 30}
            max_hp = max_hp_values.get(self.enemy_type, 3)
            hp_ratio = max(0.0, min(1.0, self.hp / max_hp))
            
            bar_x = int(screen_x) - bar_width // 2
            bar_y = int(screen_y) - scale // 2 - 8
            pg.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            pg.draw.rect(screen, (200, 60, 40), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
    
    def check_collision(self, projectile):
        collision_radii = {1: 0.7, 2: 0.9, 3: 1.0, 4: 1.1, 5: 1.2}
        collision_radius = collision_radii.get(self.enemy_type, 0.7)
        return np.linalg.norm(self.pos - projectile.pos) < collision_radius


class Projectile:
    def __init__(self, player_pos, player_angle, speed=0.6, max_distance=22, damage=1):
        direction_x = np.sin(player_angle)
        direction_y = np.cos(player_angle)
        self.direction = np.array([direction_x, direction_y], dtype=np.float32)
        
        offset_distance = 0.4
        rotated_offset_x = offset_distance * direction_x
        rotated_offset_y = offset_distance * direction_y
        
        self.pos = np.array(player_pos, dtype=np.float32) + np.array([rotated_offset_x, rotated_offset_y])
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True
        self.damage = damage
        
        # Učitaj sliku projektila
        try:
            self.image = pg.image.load('textures/projectile.png')
        except:
            self.image = None

    def update(self):
        self.pos += self.direction * self.speed
        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale <= 0:
            return
        
        if self.image:
            size = max(12, min(25, int(scale * 1.2)))
            scaled_image = pg.transform.scale(self.image, (size, size))
            rect = scaled_image.get_rect(center=(int(screen_x), int(screen_y)))
            screen.blit(scaled_image, rect)
        else:
            size = max(5, min(15, int(scale * 0.6)))
            glow_size = size + 3
            pg.draw.circle(screen, (255, 255, 200, 100), (int(screen_x), int(screen_y)), glow_size)
            pg.draw.circle(screen, (255, 220, 80), (int(screen_x), int(screen_y)), size)


class BossProjectile:
    def __init__(self, boss_pos, target_pos, speed=0.1, max_distance=15):
        direction = target_pos - boss_pos
        distance = np.linalg.norm(direction)
        if distance > 1e-6:
            self.direction = direction / distance
        else:
            self.direction = np.array([1.0, 0.0], dtype=np.float32)
        
        offset_distance = 1.5
        self.pos = np.array(boss_pos, dtype=np.float32) + self.direction * offset_distance
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True
        self.lifetime = 2000
        self.creation_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.direction * self.speed
        now_ms = pg.time.get_ticks()
        if now_ms - self.creation_time >= self.lifetime:
            self.active = False
        elif np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            size = max(4, int(scale * 0.4))
            pg.draw.circle(screen, (255, 50, 50), (int(screen_x), int(screen_y)), size)


class Game:
    def __init__(self, mode7):
        self.mode7 = mode7
        initial_positions = random_spawn_positions(4, 2, 4)
        self.enemies = [Enemy(pos, enemy_type=1) for pos in initial_positions]
        self.projectiles = []
        self.boss_projectiles = []
        self.score = 0
        self.player_max_hp = 100
        self.player_hp = self.player_max_hp
        self.game_over = False
        self.game_won = False
        self.wave = 1
        self.enemies_killed_this_wave = 0
        self.hit_flash_end_ms = 0
        self.wave_start_timer_ms = 0
        self.is_wave_starting = False
        
        # Zvuk pogotka
        try:
            self.hit_sound = pg.mixer.Sound('sounds/hit.mp3')
        except Exception:
            self.hit_sound = None
    
    def update(self, player_pos):
        if self.game_over:
            return

        # Provjeri timer za novi wave
        now_ms = pg.time.get_ticks()
        if self.is_wave_starting:
            if now_ms >= self.wave_start_timer_ms:
                self.is_wave_starting = False
                self.spawn_next_wave()
            else:
                return

        # Update entiteta
        for enemy in self.enemies:
            enemy.update(player_pos)
        for projectile in self.projectiles:
            projectile.update()
        for boss_projectile in self.boss_projectiles:
            boss_projectile.update()
        
        # Stvaranje boss projektila
        for enemy in self.enemies:
            if enemy.enemy_type in [4, 5] and enemy.is_shooting:
                if enemy.shots_fired < enemy.max_shots:
                    if now_ms - enemy.shoot_start_time >= enemy.shots_fired * 1000:
                        if enemy.enemy_type == 5:
                            # Boss 5 puca 6 projektila
                            for i in range(6):
                                random_angle = np.random.uniform(0, 2 * np.pi)
                                random_distance = np.random.uniform(5, 15)
                                random_target_x = enemy.pos[0] + np.cos(random_angle) * random_distance
                                random_target_y = enemy.pos[1] + np.sin(random_angle) * random_distance
                                random_target = np.array([random_target_x, random_target_y])
                                self.boss_projectiles.append(BossProjectile(enemy.pos, random_target, speed=0.025))
                        else:
                            # Boss 4 puca 3 projektila
                            for i in range(3):
                                random_angle = np.random.uniform(0, 2 * np.pi)
                                random_distance = np.random.uniform(5, 15)
                                random_target_x = enemy.pos[0] + np.cos(random_angle) * random_distance
                                random_target_y = enemy.pos[1] + np.sin(random_angle) * random_distance
                                random_target = np.array([random_target_x, random_target_y])
                                self.boss_projectiles.append(BossProjectile(enemy.pos, random_target))
                        enemy.shots_fired += 1

        # Kolizije
        self._handle_projectile_collisions()
        self._handle_player_collisions(player_pos, now_ms)
        self._handle_boss_projectile_collisions(player_pos, now_ms)

        # Čišćenje neaktivnih projektila
        self.projectiles = [p for p in self.projectiles if p.active]
        self.boss_projectiles = [bp for bp in self.boss_projectiles if bp.active]
        
        # Provjeri kraj wave-a
        if len(self.enemies) == 0:
            if self.wave >= 5:
                self.game_won = True
            else:
                self.is_wave_starting = True
                self.wave_start_timer_ms = pg.time.get_ticks() + 3000
    
    def _handle_projectile_collisions(self):
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
                        self.enemies_killed_this_wave += 1
                    break
        if enemies_to_remove:
            self.enemies = [e for e in self.enemies if e not in enemies_to_remove]

    def _handle_player_collisions(self, player_pos, now_ms):
        damage_values = {1: 2, 2: 3, 3: 1, 4: 5, 5: 10}
        
        for enemy in self.enemies:
            if np.linalg.norm(enemy.pos - player_pos) < 0.6:
                damage = damage_values.get(enemy.enemy_type, 1)
                self.player_hp -= damage
                self.hit_flash_end_ms = now_ms + 180
                
                if self.hit_sound:
                    try:
                        self.hit_sound.play()
                    except Exception:
                        pass
                
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.game_over = True
                
                self.enemies = [e for e in self.enemies if e is not enemy]
                self.enemies_killed_this_wave += 1
                break

    def _handle_boss_projectile_collisions(self, player_pos, now_ms):
        boss_projectiles_to_remove = []
        for boss_projectile in self.boss_projectiles:
            if not boss_projectile.active:
                continue
            if np.linalg.norm(boss_projectile.pos - player_pos) < 0.8:
                boss_projectiles_to_remove.append(boss_projectile)
                self.player_hp -= 3
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
        
        if boss_projectiles_to_remove:
            self.boss_projectiles = [bp for bp in self.boss_projectiles if bp not in boss_projectiles_to_remove]
    
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen, self.mode7)
        for projectile in self.projectiles:
            projectile.draw(screen, self.mode7)
        for boss_projectile in self.boss_projectiles:
            boss_projectile.draw(screen, self.mode7)
    
    def shoot(self, player_pos, player_angle):
        self.projectiles.append(Projectile(player_pos, player_angle))

    def reset(self):
        initial_positions = random_spawn_positions(4, 2, 4)
        self.enemies = [Enemy(pos, enemy_type=1) for pos in initial_positions]
        self.projectiles = []
        self.boss_projectiles = []
        self.score = 0
        self.player_max_hp = 100
        self.player_hp = self.player_max_hp
        self.game_over = False
        self.game_won = False
        self.hit_flash_end_ms = 0
        self.wave_start_timer_ms = 0
        self.is_wave_starting = False
        self.wave = 1
        self.enemies_killed_this_wave = 0

    def spawn_next_wave(self):
        self.wave += 1
        self.enemies_killed_this_wave = 0
        
        wave_configs = {
            2: [(3, 0.025, 5, 2)],
            3: [(3, 0.05, 1, 3)],
            4: [(1, 0.015, 10, 4), (3, 0.05, 1, 3)],
            5: [(1, 0.035, 30, 5)]
        }
        
        config = wave_configs.get(self.wave, [(3, 0.025, 5, 2)])
        new_enemies = []
        
        for count, speed, hp, enemy_type in config:
            positions = random_spawn_positions(count, 2, 4)
            for pos in positions:
                new_enemies.append(Enemy(pos, speed=speed, hp=hp, enemy_type=enemy_type))
        
        self.enemies = new_enemies

