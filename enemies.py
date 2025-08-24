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


class Weapon:
    def __init__(self, name, damage, fire_rate, spread, projectile_speed, max_distance, color, projectile_count=1):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.spread = spread
        self.projectile_speed = projectile_speed
        self.max_distance = max_distance
        self.color = color
        self.projectile_count = projectile_count
        self.last_shot_time = 0

    def can_shoot(self, current_time):
        """Provjeri može li oružje pucati"""
        return current_time - self.last_shot_time >= 1000 / self.fire_rate

    def shoot(self, player_pos, player_angle, current_time):
        """Ispali projektile"""
        if not self.can_shoot(current_time):
            return []
        
        self.last_shot_time = current_time
        projectiles = []
        
        for i in range(self.projectile_count):
            spread_offset = 0
            if self.projectile_count > 1:
                spread_offset = (i - (self.projectile_count - 1) / 2) * self.spread
            
            angle = player_angle + spread_offset + np.random.uniform(-self.spread/2, self.spread/2)
            projectiles.append(Projectile(player_pos, angle, self.projectile_speed, self.max_distance, self.damage, self.color))
        
        return projectiles


class PowerUp:
    def __init__(self, pos, power_type, duration=20000):
        self.pos = np.array(pos, dtype=np.float32)
        self.power_type = power_type
        self.creation_time = pg.time.get_ticks()
        self.active = True
        
        power_configs = {
            'damage': {'color': (255, 0, 0)},
            'speed': {'color': (0, 255, 0)}
        }
        
        self.color = power_configs.get(power_type, {'color': (255, 255, 255)})['color']

    def update(self):
        """Provjeri je li power-up još aktivan"""
        now_ms = pg.time.get_ticks()
        if now_ms - self.creation_time >= 20000:  # 20 sekundi
            self.active = False

    def draw(self, screen, mode7):
        """Nacrtaj power-up s slikom"""
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            # Koristi sliku ako je dostupna, inače krug
            if hasattr(mode7.app, 'powerup_damage') and hasattr(mode7.app, 'powerup_speed'):
                if self.power_type == 'damage':
                    powerup_surface = mode7.app.powerup_damage
                else:  # speed
                    powerup_surface = mode7.app.powerup_speed
                
                # Skaliraj sliku prema udaljenosti (manje u igrici)
                size = max(4, int(scale * 3))
                scaled_surface = pg.transform.scale(powerup_surface, (size, size))
                powerup_rect = scaled_surface.get_rect(center=(int(screen_x), int(screen_y)))
                
                # Glow efekt uklonjen za čistiji izgled
                
                # Nacrtaj power-up sliku
                screen.blit(scaled_surface, powerup_rect)
            else:
                # Fallback na krugove
                size = max(4, int(scale * 0.4))
                glow_size = size + 2
                pg.draw.circle(screen, (*self.color, 100), (int(screen_x), int(screen_y)), glow_size)
                pg.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), size)
                pulse_size = size + int(np.sin(pg.time.get_ticks() * 0.01) * 1)
                pg.draw.circle(screen, (*self.color, 50), (int(screen_x), int(screen_y)), pulse_size, 1)


class Enemy:
    def __init__(self, pos, speed=0.02, hp=3, enemy_type=1):
        self.pos = np.array(pos, dtype=np.float32)
        self.speed = speed
        self.hp = hp
        self.enemy_type = enemy_type
        
        texture_paths = {
            1: 'textures/airship_1.png',
            2: 'textures/enemy_2.png', 
            3: 'textures/enemy_3.png',
            4: 'textures/enemy_4.png',
            5: 'textures/enemy_5.png'
        }
        texture_path = texture_paths.get(enemy_type, 'textures/airship_1.png')
        self.texture = pg.image.load(texture_path).convert_alpha()
        
        # Kretanje
        self.strafe_bias = float(np.random.uniform(-1.0, 1.0))
        self.orbit_radius = float(np.random.uniform(1.5, 8.0))
        self.movement_pattern = np.random.randint(0, 4)
        self.retarget_interval_ms = int(np.random.randint(500, 3000))
        self.next_retarget_ms = int(pg.time.get_ticks() + self.retarget_interval_ms)
        self.target_pos = np.array(pos, dtype=np.float32)
        self.target_update_interval_ms = 500
        self.next_target_update_ms = int(pg.time.get_ticks() + self.target_update_interval_ms)
        self.chaos_factor = float(np.random.uniform(0.0, 0.8))
        self.direction_change_prob = float(np.random.uniform(0.1, 0.4))
        
        # Boss pucanje
        if enemy_type in [4, 5]:
            self.shoot_timer = 0
            self.shoot_cooldown = 5000
            self.is_shooting = False
            self.shoot_duration = 3000
            self.shoot_start_time = 0
            self.shots_fired = 0
            self.max_shots = 3

    def update(self, player_pos):
        now_ms = pg.time.get_ticks()
        
        # Ažuriraj target poziciju
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

        # Boss pucanje
        if self.enemy_type in [4, 5]:
            if not self.is_shooting:
                if self.shoot_timer == 0:
                    self.shoot_timer = now_ms
                
                if now_ms - self.shoot_timer >= self.shoot_cooldown:
                    self.is_shooting = True
                    self.shoot_start_time = now_ms
                    self.shots_fired = 0
                    self.shoot_timer = now_ms
            else:
                if now_ms - self.shoot_start_time >= self.shoot_duration:
                    self.is_shooting = False
                    self.shoot_timer = now_ms
                else:
                    return

        # Kretanje
        distance = np.linalg.norm(self.target_pos - self.pos)
        if distance > 1e-5:
            direction = self.target_pos - self.pos
            unit = direction / distance
            
            if np.random.random() < self.direction_change_prob:
                self.movement_pattern = np.random.randint(0, 4)
            
            # Različiti patterni kretanja
            if self.movement_pattern == 0:  # Ravno
                move_dir = unit
            elif self.movement_pattern == 1:  # Orbitiranje
                perp = np.array([-unit[1], unit[0]], dtype=np.float32)
                move_dir = unit if distance > self.orbit_radius else perp
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
            if self.enemy_type in [4, 5]:
                bar_width = max(20, scale * 1.5)
                bar_height = 6
            else:
                bar_width = max(10, scale)
                bar_height = 4
            
            max_hp_values = {1: 9, 2: 15, 3: 3, 4: 360, 5: 540}
            max_hp = max_hp_values.get(self.enemy_type, 9)
            hp_ratio = max(0.0, min(1.0, self.hp / max_hp))
            
            bar_x = int(screen_x) - bar_width // 2
            bar_y = int(screen_y) - scale // 2 - 8
            pg.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            pg.draw.rect(screen, (200, 60, 40), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
    
    def check_collision(self, projectile):
        collision_radii = {1: 0.8, 2: 1.0, 3: 0.9, 4: 1.0, 5: 1.0}
        collision_radius = collision_radii.get(self.enemy_type, 0.8)
        return np.linalg.norm(self.pos - projectile.pos) < collision_radius


class Projectile:
    def __init__(self, player_pos, player_angle, speed=0.6, max_distance=22, damage=1, color=(255, 220, 80), piercing=False, homing=False):
        direction_x = np.sin(player_angle)
        direction_y = np.cos(player_angle)
        self.direction = np.array([direction_x, direction_y], dtype=np.float32)
        
        offset_distance = 0.1
        self.pos = np.array(player_pos, dtype=np.float32) + np.array([offset_distance * direction_x, offset_distance * direction_y])
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True
        self.damage = damage
        self.color = color
        self.piercing = piercing
        self.homing = homing
        self.hit_enemies = set()

    def update(self, enemies=None):
        self.pos += self.direction * self.speed
        
        # Homing logika
        if self.homing and enemies:
            closest_enemy = None
            closest_distance = float('inf')
            for enemy in enemies:
                if enemy not in self.hit_enemies:
                    distance = np.linalg.norm(enemy.pos - self.pos)
                    if distance < closest_distance and distance < 5.0:
                        closest_enemy = enemy
                        closest_distance = distance
            
            if closest_enemy:
                direction_to_enemy = closest_enemy.pos - self.pos
                direction_to_enemy = direction_to_enemy / np.linalg.norm(direction_to_enemy)
                self.direction = self.direction * 0.9 + direction_to_enemy * 0.1
                self.direction = self.direction / np.linalg.norm(self.direction)
        
        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale <= 0:
            return
        
        size = max(2, min(4, int(scale * 0.2)))
        glow_size = size + 2
        glow_color = (*self.color, 100)
        pg.draw.circle(screen, glow_color, (int(screen_x), int(screen_y)), glow_size)
        pg.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), size)
        
        if self.piercing:
            pg.draw.circle(screen, (255, 255, 255, 50), (int(screen_x), int(screen_y)), size + 3, 1)


class BossProjectile:
    def __init__(self, boss_pos, target_pos, speed=0.1, max_distance=15, damage=3):
        direction = target_pos - boss_pos
        distance = np.linalg.norm(direction)
        self.direction = direction / distance if distance > 1e-6 else np.array([1.0, 0.0], dtype=np.float32)
        
        self.pos = np.array(boss_pos, dtype=np.float32) + self.direction * 1.5
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True
        self.lifetime = 2000
        self.creation_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.direction * self.speed
        now_ms = pg.time.get_ticks()
        if now_ms - self.creation_time >= self.lifetime or np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            size = max(4, int(scale * 0.4))
            pg.draw.circle(screen, (255, 50, 50), (int(screen_x), int(screen_y)), size)


class Game:
    def __init__(self, mode7):
        self.mode7 = mode7
        initial_positions = random_spawn_positions(5, 2, 4)
        self.enemies = [Enemy(pos, enemy_type=1, hp=9) for pos in initial_positions]
        self.projectiles = []
        self.boss_projectiles = []
        self.power_ups = []
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
        
        # Sustav oružja
        self.weapons = {
            'basic': Weapon('Basic Laser', 1, 2, 0.1, 0.6, 22, (255, 220, 80)),
            'heavy': Weapon('Heavy Cannon', 4, 0.5, 0.3, 0.4, 18, (255, 100, 100)),
            'rapid': Weapon('Rapid Fire', 1, 6, 0.05, 0.7, 20, (100, 255, 100)),
            'sniper': Weapon('Sniper Rifle', 6, 1.5, 0, 0.8, 30, (255, 255, 100)),
            'shotgun': Weapon('Shotgun', 3, 1.5, 0.4, 0.5, 15, (255, 150, 50), 3),
            'plasma': Weapon('Plasma Gun', 3, 2, 0.2, 0.6, 25, (100, 100, 255))
        }
        self.current_weapon = 'basic'
        self.weapon_unlock_requirements = {
            'basic': 0, 'heavy': 300, 'rapid': 600, 'sniper': 1000, 'shotgun': 1500, 'plasma': 2000
        }
        self.unlocked_weapons = ['basic']
        
        # Auto-pucanje
        self.auto_fire_active = False
        self.auto_fire_last_shot = 0
        
        # Zamrzavanje za otključavanje oružja
        self.game_frozen = False
        self.freeze_start_time = 0
        self.freeze_duration = 3000
        self.last_unlocked_weapon = None
        
        # Wave 4 faze
        self.wave4_phase = 1
        self.wave4_first_phase_complete = False
        
        # Power-upovi
        self.active_power_ups = {}
        self.power_up_durations = {'damage': 20000, 'speed': 15000}
        
        # Zvuk
        try:
            self.hit_sound = pg.mixer.Sound('sounds/player_hit.mp3')  # Koristi player_hit.mp3
            self.shoot_sound = pg.mixer.Sound('sounds/shoot.mp3')
            self.shoot_sound.set_volume(0.067)  # Smanjeno za 3x (0.2 / 3)
            self.enemy_death_sound = pg.mixer.Sound('sounds/enemy_death.mp3')
            self.player_hit_sound = pg.mixer.Sound('sounds/player_hit.mp3')
            self.powerup_sound = pg.mixer.Sound('sounds/powerup.mp3')
            self.weapon_switch_sound = pg.mixer.Sound('sounds/weapon_switch.mp3')
            self.boss_shoot_sound = pg.mixer.Sound('sounds/boss_shoot.mp3')
            self.boss_death_sound = pg.mixer.Sound('sounds/boss_death.mp3')
            self.weapon_unlock_sound = pg.mixer.Sound('sounds/weapon_unlock.mp3')
            self.game_over_sound = pg.mixer.Sound('sounds/game_over.mp3')
            self.victory_sound = pg.mixer.Sound('sounds/victory.mp3')
            self.tutorial_sound = pg.mixer.Sound('sounds/tutorial.mp3')
            self.tutorial_sound.set_volume(0.1)  # Smanjeno za tutorial navigaciju
            self.auto_fire_sound = pg.mixer.Sound('sounds/auto_shoot.mp3')  # Koristi auto_shoot.mp3
            self.auto_fire_sound.set_volume(0.067)  # Smanjeno za 3x (0.2 / 3)
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.hit_sound = None
            self.shoot_sound = None
            self.enemy_death_sound = None
            self.player_hit_sound = None
            self.powerup_sound = None
            self.weapon_switch_sound = None
            self.boss_shoot_sound = None
            self.boss_death_sound = None
            self.weapon_unlock_sound = None
            self.game_over_sound = None
            self.victory_sound = None
            self.tutorial_sound = None
            self.auto_fire_sound = None
            
        # Tutorial
        self.tutorial_active = True
        self.tutorial_page = 0
        self.tutorial_last_input = 0
        self.starting_wave_1 = False
        self.tutorial_pages = [
            {
                'title': 'WELCOME TO MODE7 SHOOTER!',
                'subtitle': 'A Steampunk Airship Combat Game',
                'content': [
                    'Use WASD to move your airship',
                    'Left/Right arrows to turn',
                    'Q/E to change altitude',
                    'HOLD SPACE to shoot',
                    'Press M to mute/unmute music',
                    'Press SPACE to continue...'
                ]
            },
            {
                'title': 'WEAPON SYSTEM',
                'subtitle': 'Unlock new weapons as you progress',
                'content': [
                    '• Basic Laser: Fast and accurate',
                    '• Heavy Cannon: Slow but powerful',
                    '• Rapid Fire: Automatic shooting',
                    '• Sniper Rifle: Long range precision',
                    '• Shotgun: Multiple projectiles',
                    '• Plasma Gun: Advanced weapon',
                    'Press SPACE to continue...'
                ]
            },
            {
                'title': 'ENEMY TYPES',
                'subtitle': 'Different enemies require different strategies',
                'content': [
                    '• Type 1: Basic enemies (100 XP)',
                    '• Type 2: Heavy enemies (200 XP)',
                    '• Type 3: Fast enemies (300 XP)',
                    '• Type 4: Mini Boss (400 XP)',
                    '• Type 5: Final Boss (500 XP)',
                    'Press SPACE to continue...'
                ]
            },
            {
                'title': 'POWER-UPS',
                'subtitle': 'Collect power-ups for temporary boosts',
                'content': [
                    '• Damage Boost: Double weapon damage',
                    '• Speed Boost: 50% faster fire rate',
                    'Power-ups spawn when enemies die',
                    'Press SPACE to continue...'
                ]
            },
            {
                'title': 'WAVE SYSTEM',
                'subtitle': 'Progressive difficulty with boss fights',
                'content': [
                    '• Wave 1-3: Regular enemies',
                    '• Wave 4: Mini Boss + enemies',
                    '• Wave 5: Final Boss',
                    'Complete all waves to win!',
                    'Press SPACE to start the game!'
                ]
            }
        ]
        
        # Zastavica za gameplay glazbu
        self.gameplay_music_started = False
        self.music_muted = False
    
    def update(self, player_pos):
        if self.game_over or self.tutorial_active:
            return

        now_ms = pg.time.get_ticks()
        
        # Zamrzavanje igre za otključavanje oružja
        if self.game_frozen:
            if now_ms - self.freeze_start_time >= self.freeze_duration:
                self.game_frozen = False
                self.last_unlocked_weapon = None
            else:
                return

        # Wave timer
        if self.is_wave_starting:
            if now_ms >= self.wave_start_timer_ms:
                self.is_wave_starting = False

                # Pokreni gameplay glazbu nakon tutoriala
                if self.tutorial_active == False and self.wave == 1 and not self.gameplay_music_started:
                    try:
                        pg.mixer.music.load("sounds/gameplay.mp3")
                        pg.mixer.music.set_volume(0.2)  # Tiša muzika
                        pg.mixer.music.play(-1)
                        self.gameplay_music_started = True
                    except:
                        pass
                if self.starting_wave_1:
                    self.starting_wave_1 = False
                else:
                    self.spawn_next_wave()
            else:
                return

        # Ažuriraj entitete
        for enemy in self.enemies:
            enemy.update(player_pos)
        for projectile in self.projectiles:
            projectile.update(self.enemies)
        for boss_projectile in self.boss_projectiles:
            boss_projectile.update()
        for power_up in self.power_ups:
            power_up.update()
        
        self.update_auto_fire(player_pos, self.mode7.angle)
        
        # Boss pucanje
        for enemy in self.enemies:
            if enemy.enemy_type in [4, 5] and enemy.is_shooting:
                if enemy.shots_fired < enemy.max_shots:
                    if now_ms - enemy.shoot_start_time >= enemy.shots_fired * 1000:
                        if enemy.enemy_type == 5:
                            for i in range(6):
                                random_angle = np.random.uniform(0, 2 * np.pi)
                                random_distance = np.random.uniform(5, 15)
                                random_target = np.array([
                                    enemy.pos[0] + np.cos(random_angle) * random_distance,
                                    enemy.pos[1] + np.sin(random_angle) * random_distance
                                ])
                                self.boss_projectiles.append(BossProjectile(enemy.pos, random_target, speed=0.025, damage=9))
                        else:
                            for i in range(3):
                                random_angle = np.random.uniform(0, 2 * np.pi)
                                random_distance = np.random.uniform(5, 15)
                                random_target = np.array([
                                    enemy.pos[0] + np.cos(random_angle) * random_distance,
                                    enemy.pos[1] + np.sin(random_angle) * random_distance
                                ])
                                self.boss_projectiles.append(BossProjectile(enemy.pos, random_target, damage=3))
                        enemy.shots_fired += 1
                        # Pusti zvuk boss pucanja
                        if self.boss_shoot_sound:
                            self.boss_shoot_sound.play()

        # Sudari
        self._handle_projectile_collisions()
        self._handle_player_collisions(player_pos, now_ms)
        self._handle_boss_projectile_collisions(player_pos, now_ms)
        self._handle_power_up_collisions(player_pos)

        # Čišćenje
        self.projectiles = [p for p in self.projectiles if p.active]
        self.boss_projectiles = [bp for bp in self.boss_projectiles if bp.active]
        self.power_ups = [pu for pu in self.power_ups if pu.active]
        
        self.check_weapon_unlocks()
        
        # Provjera kraja wave-a
        if len(self.enemies) == 0:
            if self.wave == 4 and self.wave4_phase == 1:
                self.wave4_phase = 2
                self.wave4_first_phase_complete = True
                self._spawn_wave4_second_phase()
            elif self.wave >= 5:
                self.game_won = True
                if self.victory_sound:
                    self.victory_sound.play()
                # Zaustavi gameplay glazbu
                try:
                    pg.mixer.music.stop()
                except:
                    pass
            else:
                self.is_wave_starting = True
                self.wave_start_timer_ms = pg.time.get_ticks() + 3000
    
    def _handle_projectile_collisions(self):
        enemies_to_remove = []
        for projectile in self.projectiles:
            if not projectile.active:
                continue
            for enemy in self.enemies:
                if enemy not in projectile.hit_enemies and enemy.check_collision(projectile):
                    enemy.hp -= projectile.damage
                    projectile.hit_enemies.add(enemy)
                    
                    if not projectile.piercing:
                        projectile.active = False
                    
                    if enemy.hp <= 0:
                        enemies_to_remove.append(enemy)
                        
                        # Pusti zvuk smrti neprijatelja
                        if enemy.enemy_type in [4, 5]:  # Boss death
                            if self.boss_death_sound:
                                self.boss_death_sound.play()
                        else:  # Regular enemy death
                            if self.enemy_death_sound:
                                self.enemy_death_sound.play()
                        
                        xp_rewards = {1: 100, 2: 200, 3: 300, 4: 400, 5: 500}
                        self.score += xp_rewards.get(enemy.enemy_type, 100)
                        self.enemies_killed_this_wave += 1
                        
                        # Spawn power-up-a
                        if np.random.random() < 0.25:
                            power_type = np.random.choice(['damage', 'speed'])
                            self.power_ups.append(PowerUp(enemy.pos, power_type))
                    
                    if not projectile.piercing:
                        break
        if enemies_to_remove:
            self.enemies = [e for e in self.enemies if e not in enemies_to_remove]

    def _handle_player_collisions(self, player_pos, now_ms):
        damage_values = {1: 2, 2: 3, 3: 1, 4: 2, 5: 3}
        
        for enemy in self.enemies:
            if np.linalg.norm(enemy.pos - player_pos) < 0.6:
                damage = damage_values.get(enemy.enemy_type, 1)
                self.player_hp -= damage
                self.hit_flash_end_ms = now_ms + 180
                
                if self.player_hit_sound:
                    self.player_hit_sound.play()
                
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.game_over = True
                    if self.game_over_sound:
                        self.game_over_sound.play()
                    # Zaustavi gameplay glazbu
                    try:
                        pg.mixer.music.stop()
                    except:
                        pass
                
                # Bossovi 4 i 5 ne umiru kada dodirnu igrača, ostali da
                if enemy.enemy_type not in [4, 5]:
                    self.enemies = [e for e in self.enemies if e is not enemy]
                    self.enemies_killed_this_wave += 1
                break

    def _handle_boss_projectile_collisions(self, player_pos, now_ms):
        boss_projectiles_to_remove = []
        for boss_projectile in self.boss_projectiles:
            if boss_projectile.active and np.linalg.norm(boss_projectile.pos - player_pos) < 0.8:
                boss_projectiles_to_remove.append(boss_projectile)
                self.player_hp -= boss_projectile.damage
                self.hit_flash_end_ms = now_ms + 180
                
                if self.player_hit_sound:
                    self.player_hit_sound.play()
                
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.game_over = True
                    if self.game_over_sound:
                        self.game_over_sound.play()
                    # Zaustavi gameplay glazbu
                    try:
                        pg.mixer.music.stop()
                    except:
                        pass
                break
        
        if boss_projectiles_to_remove:
            self.boss_projectiles = [bp for bp in self.boss_projectiles if bp not in boss_projectiles_to_remove]

    def _handle_power_up_collisions(self, player_pos):
        power_ups_to_remove = []
        for power_up in self.power_ups:
            if np.linalg.norm(power_up.pos - player_pos) < 0.8:
                power_ups_to_remove.append(power_up)
                self._apply_power_up(power_up.power_type)
                # Pusti zvuk power-up-a
                if self.powerup_sound:
                    self.powerup_sound.play()
        
        if power_ups_to_remove:
            self.power_ups = [pu for pu in self.power_ups if pu not in power_ups_to_remove]

    def _apply_power_up(self, power_type):
        """Primijeni power-up efekt"""
        now_ms = pg.time.get_ticks()
        duration = self.power_up_durations.get(power_type, 15000)
        self.active_power_ups[power_type] = now_ms + duration

    def get_modified_weapon(self):
        """Vrati trenutno oružje s primijenjenim power-up efektima"""
        weapon = self.weapons[self.current_weapon]
        now_ms = pg.time.get_ticks()
        
        modified_weapon = Weapon(
            weapon.name, weapon.damage, weapon.fire_rate, weapon.spread,
            weapon.projectile_speed, weapon.max_distance, weapon.color, weapon.projectile_count
        )
        
        for power_type, end_time in self.active_power_ups.items():
            if now_ms < end_time:
                if power_type == 'speed':
                    modified_weapon.fire_rate *= 1.5
                elif power_type == 'damage':
                    modified_weapon.damage *= 2
        
        return modified_weapon

    def check_weapon_unlocks(self):
        """Provjeri i otključaj nova oružja ovisno o score-u"""
        for weapon_name, required_score in self.weapon_unlock_requirements.items():
            if weapon_name not in self.unlocked_weapons and self.score >= required_score:
                self.unlocked_weapons.append(weapon_name)
                self.current_weapon = weapon_name
                self.game_frozen = True
                self.freeze_start_time = pg.time.get_ticks()
                self.last_unlocked_weapon = weapon_name
                # Pusti zvuk otključavanja oružja
                if self.weapon_unlock_sound:
                    self.weapon_unlock_sound.play()

    def start_auto_fire(self):
        """Započni automatsko pucanje"""
        self.auto_fire_active = True
        self.auto_fire_last_shot = 0
        # Pusti zvuk auto-pucanja
        if self.auto_fire_sound:
            self.auto_fire_sound.play()

    def stop_auto_fire(self):
        """Zaustavi automatsko pucanje"""
        self.auto_fire_active = False

    def update_auto_fire(self, player_pos, player_angle):
        """Ažuriraj automatsko pucanje"""
        if not self.auto_fire_active:
            return
        
        now_ms = pg.time.get_ticks()
        weapon = self.get_modified_weapon()
        fire_interval = 1000 / weapon.fire_rate
        
        if now_ms - self.auto_fire_last_shot >= fire_interval:
            self.shoot(player_pos, player_angle)
            self.auto_fire_last_shot = now_ms

    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen, self.mode7)
        for projectile in self.projectiles:
            projectile.draw(screen, self.mode7)
        for boss_projectile in self.boss_projectiles:
            boss_projectile.draw(screen, self.mode7)
        for power_up in self.power_ups:
            power_up.draw(screen, self.mode7)
    
    def shoot(self, player_pos, player_angle):
        """Ispali projektile s trenutnim oružjem"""
        now_ms = pg.time.get_ticks()
        weapon = self.get_modified_weapon()
        projectiles = weapon.shoot(player_pos, player_angle, now_ms)
        if projectiles:  # Ako su projektili ispaljeni
            if self.shoot_sound:
                self.shoot_sound.play()
        self.projectiles.extend(projectiles)

    def reset(self):
        initial_positions = random_spawn_positions(5, 2, 4)
        self.enemies = [Enemy(pos, enemy_type=1, hp=9) for pos in initial_positions]
        self.projectiles = []
        self.boss_projectiles = []
        self.power_ups = []
        self.score = 0
        self.player_hp = self.player_max_hp
        self.game_over = False
        self.game_won = False
        self.hit_flash_end_ms = 0
        self.wave_start_timer_ms = 0
        self.is_wave_starting = False
        self.wave = 1
        self.current_weapon = 'basic'
        self.active_power_ups = {}
        self.unlocked_weapons = ['basic']
        self.auto_fire_active = False
        self.auto_fire_last_shot = 0
        self.game_frozen = False
        self.freeze_start_time = 0
        self.last_unlocked_weapon = None
        self.tutorial_active = True
        self.tutorial_page = 0
        self.tutorial_last_input = 0
        self.starting_wave_1 = False
        self.wave4_phase = 1
        self.wave4_first_phase_complete = False
        
        # Reset zastavice za gameplay glazbu
        self.gameplay_music_started = False
        self.music_muted = False
        
    def handle_tutorial_input(self):
        """Handle tutorial navigation"""
        if not self.tutorial_active:
            return
            
        now_ms = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and now_ms - self.tutorial_last_input >= 300:
            self.tutorial_last_input = now_ms
            self.tutorial_page += 1
            # Pusti zvuk tutoriala
            if self.tutorial_sound:
                self.tutorial_sound.play()
            if self.tutorial_page >= len(self.tutorial_pages):
                self.tutorial_active = False
                self.is_wave_starting = True
                self.wave_start_timer_ms = now_ms + 3000
                self.starting_wave_1 = True
        
    def _spawn_wave4_second_phase(self):
        """Spawnaj drugu fazu Wave 4: 3x Tip 3 + 1x Boss 4"""
        tip3_positions = random_spawn_positions(3, 2, 4)
        for pos in tip3_positions:
            self.enemies.append(Enemy(pos, enemy_type=3, hp=3))
        
        boss_positions = random_spawn_positions(1, 2, 4)
        for pos in boss_positions:
            self.enemies.append(Enemy(pos, enemy_type=4, hp=360))
        
        self.enemies_killed_this_wave = 0

    def spawn_next_wave(self):
        self.wave += 1
        self.enemies_killed_this_wave = 0
        
        if self.wave == 4:
            self.wave4_phase = 1
            self.wave4_first_phase_complete = False
        
        wave_configs = {
            2: [(4, 0.025, 15, 2)],
            3: [(4, 0.05, 3, 3)],
            4: [(2, 0.025, 9, 1), (1, 0.025, 15, 2)],
            5: [(1, 0.035, 540, 5)]
        }
        
        config = wave_configs.get(self.wave, [(4, 0.025, 15, 2)])
        new_enemies = []
        
        for count, speed, hp, enemy_type in config:
            positions = random_spawn_positions(count, 2, 4)
            for pos in positions:
                new_enemies.append(Enemy(pos, speed=speed, hp=hp, enemy_type=enemy_type))
        
        self.enemies = new_enemies