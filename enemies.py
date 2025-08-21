import pygame as pg
import numpy as np

class Enemy:
    def __init__(self, pos, speed=0.02, hp=3, enemy_type=1):
        self.pos = np.array(pos, dtype=np.float32)  # Pohrana pozicije kao [x, y]
        self.speed = speed
        self.alive = True
        self.hp = hp
        self.enemy_type = enemy_type
        # Učitaj teksturu ovisno o tipu neprijatelja
        if enemy_type == 1:
            self.texture = pg.image.load('textures/airship_1.png').convert_alpha()
        elif enemy_type == 2:
            self.texture = pg.image.load('textures/enemy_2.png').convert_alpha()
        elif enemy_type == 3:
            self.texture = pg.image.load('textures/enemy_3.png').convert_alpha()
        elif enemy_type == 4:
            self.texture = pg.image.load('textures/enemy_4.png').convert_alpha()
        elif enemy_type == 5:
            self.texture = pg.image.load('textures/enemy_5.png').convert_alpha()
        else:
            self.texture = pg.image.load('textures/airship_1.png').convert_alpha()
        # Nasumični faktori kretanja
        self.strafe_bias = float(np.random.uniform(-1.0, 1.0))  # Veći raspon za više varijacije
        self.orbit_radius = float(np.random.uniform(1.5, 8.0))  # Veći raspon radijusa
        self.movement_pattern = np.random.randint(0, 4)  # 0=ravno, 1=orbitiranje, 2=zigzag, 3=kaotik
        self.retarget_interval_ms = int(np.random.randint(500, 3000))  # Veći raspon vremena
        self.next_retarget_ms = int(pg.time.get_ticks() + self.retarget_interval_ms)
        # Dodaj target poziciju koja se ažurira svakih 0.5 sekundi
        self.target_pos = np.array(pos, dtype=np.float32)
        self.target_update_interval_ms = 500  # 0.5 sekundi
        self.next_target_update_ms = int(pg.time.get_ticks() + self.target_update_interval_ms)
        # Dodatni nasumični faktori
        self.chaos_factor = float(np.random.uniform(0.0, 0.8))  # Faktor kaosa
        self.direction_change_prob = float(np.random.uniform(0.1, 0.4))  # Vjerojatnost promjene smjera

    
    def update(self, player_pos):
        # Ažuriraj target poziciju svakih 0.5 sekundi
        now_ms = pg.time.get_ticks()
        if now_ms >= self.next_target_update_ms:
            self.target_pos = np.array(player_pos, dtype=np.float32)
            self.next_target_update_ms = now_ms + self.target_update_interval_ms
        
        # Nasumično mijenjanje patterna kretanja
        if now_ms >= self.next_retarget_ms:
            self.strafe_bias = float(np.random.uniform(-1.0, 1.0))
            self.movement_pattern = np.random.randint(0, 4)
            self.retarget_interval_ms = int(np.random.randint(500, 3000))
            self.next_retarget_ms = int(now_ms + self.retarget_interval_ms)
            # Nasumično mijenjanje dodatnih faktora
            self.chaos_factor = float(np.random.uniform(0.0, 0.8))
            self.direction_change_prob = float(np.random.uniform(0.1, 0.4))

        # Različiti patterni kretanja
        distance = np.linalg.norm(self.target_pos - self.pos)
        
        if distance > 1e-5:
            direction = self.target_pos - self.pos
            unit = direction / distance
            
            # Nasumična promjena smjera
            if np.random.random() < self.direction_change_prob:
                self.movement_pattern = np.random.randint(0, 4)
            
            if self.movement_pattern == 0:  # Ravno kretanje
                move_dir = unit
            elif self.movement_pattern == 1:  # Orbitiranje
                # Orbitiraj oko igrača
                perp = np.array([-unit[1], unit[0]], dtype=np.float32)
                if distance > self.orbit_radius:
                    move_dir = unit  # Približavaj se
                else:
                    move_dir = perp  # Orbitiraj
            elif self.movement_pattern == 2:  # Zigzag pattern
                # Kombinacija ravno + strafe
                perp = np.array([-unit[1], unit[0]], dtype=np.float32)
                move_dir = unit + perp * self.strafe_bias
                # Normalizacija
                norm = float(np.linalg.norm(move_dir))
                if norm > 1e-6:
                    move_dir = move_dir / norm
            else:  # Kaotik pattern
                # Potpuno nasumično kretanje s blagim trendom prema igraču
                random_dir = np.array([np.random.uniform(-1, 1), np.random.uniform(-1, 1)], dtype=np.float32)
                norm = float(np.linalg.norm(random_dir))
                if norm > 1e-6:
                    random_dir = random_dir / norm
                # Kombinacija nasumičnog + smjera prema igraču
                move_dir = random_dir * self.chaos_factor + unit * (1.0 - self.chaos_factor)
                norm = float(np.linalg.norm(move_dir))
                if norm > 1e-6:
                    move_dir = move_dir / norm
            
            # Osiguraj kretanje prema igraču (osim za kaotik pattern)
            if self.movement_pattern != 3 and np.dot(move_dir, unit) <= 0.0:
                move_dir = unit
            
            # Dinamička brzina ovisno o udaljenosti
            speed_multiplier = 1.0
            if distance > 8.0:  # Ako je igrač daleko
                speed_multiplier = 1.5  # Brže prema igraču
            elif distance < 3.0:  # Ako je igrač blizu
                speed_multiplier = 0.7  # Sporije, da ne bježe
            
            # Dodaj nasumičnu varijaciju brzine
            speed_multiplier *= np.random.uniform(0.8, 1.2)
            
            self.pos += move_dir * (self.speed * speed_multiplier)
    
    def draw(self, screen, mode7):
        # Projekcija svjetskih koordinata na ekran putem Mode7 projekcije
        screen_x, screen_y, scale = mode7.project(self.pos)
        
        if scale > 0:  # Prikaži neprijatelja samo ako je u vidnom polju
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale//2, int(screen_y) - scale//2))
            # Traka zdravlja neprijatelja
            bar_width = max(10, scale)
            bar_height = 4
            if self.enemy_type == 1:
                max_hp = 3
            elif self.enemy_type == 2:
                max_hp = 5
            elif self.enemy_type == 3:
                max_hp = 1
            elif self.enemy_type == 4:
                max_hp = 10 # HP za tip 4
            elif self.enemy_type == 5:
                max_hp = 30 # HP za tip 5
            else:
                max_hp = 3
            hp_ratio = max(0.0, min(1.0, self.hp / max_hp))
            bar_x = int(screen_x) - bar_width // 2
            bar_y = int(screen_y) - scale // 2 - 8
            pg.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            pg.draw.rect(screen, (200, 60, 40), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
    
    def check_collision(self, projectile):
        # Veći radijus kolizije za sve tipove neprijatelja
        if self.enemy_type == 1:
            collision_radius = 0.7
        elif self.enemy_type == 2:
            collision_radius = 0.9
        elif self.enemy_type == 3:
            collision_radius = 1.0
        elif self.enemy_type == 4:
            collision_radius = 1.1
        elif self.enemy_type == 5:
            collision_radius = 1.2
        else:
            collision_radius = 0.7
        return np.linalg.norm(self.pos - projectile.pos) < collision_radius


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
        # Nasumični spawn pozicije za prvi val
        def random_spawn_positions(count, min_dist=3, max_dist=8):
            positions = []
            for _ in range(count):
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(min_dist, max_dist)
                x = np.cos(angle) * distance
                y = np.sin(angle) * distance
                positions.append((x, y))
            return positions
        
        initial_positions = random_spawn_positions(4, 2, 4)
        self.enemies = [Enemy(pos, enemy_type=1) for pos in initial_positions]
        self.projectiles = []
        self.score = 0
        self.player_max_hp = 5
        self.player_hp = self.player_max_hp
        self.last_player_hit_ms = 0
        self.player_hit_cooldown_ms = 800
        self.game_over = False
        self.game_won = False # Dodaj varijablu za pobjedu
        # Sustav valova neprijatelja
        self.wave = 1
        self.enemies_killed_this_wave = 0
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
                        self.enemies_killed_this_wave += 1
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
                # Svaki kontakt odmah oduzima HP (bez cooldowna) - tip 1 radi 2 damage, tip 2 radi 3 damage, tip 4 radi 5 damage
                if enemy.enemy_type == 1:
                    damage = 2
                elif enemy.enemy_type == 2:
                    damage = 3
                elif enemy.enemy_type == 3:
                    damage = 1
                elif enemy.enemy_type == 4:
                    damage = 5
                elif enemy.enemy_type == 5:
                    damage = 10
                else:
                    damage = 1
                self.player_hp -= damage
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
            self.enemies_killed_this_wave += 1

        # Uklanjanje neaktivnih projektila
        self.projectiles = [p for p in self.projectiles if p.active]
        
        # Provjeri je li val završen i stvori novi (samo nakon što su svi mrtvi)
        if len(self.enemies) == 0:
            if self.wave >= 5:
                # Pobjeda nakon 5. vala
                self.game_won = True
            else:
                self.spawn_next_wave()
    
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen, self.mode7)
        for projectile in self.projectiles:
            projectile.draw(screen, self.mode7)
    
    def shoot(self, player_pos, player_angle):
        self.projectiles.append(Projectile(player_pos, player_angle))

    def reset(self):
        # Nasumični spawn pozicije za prvi val
        def random_spawn_positions(count, min_dist=3, max_dist=8):
            positions = []
            for _ in range(count):
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(min_dist, max_dist)
                x = np.cos(angle) * distance
                y = np.sin(angle) * distance
                positions.append((x, y))
            return positions
        
        initial_positions = random_spawn_positions(4, 2, 4)
        self.enemies = [Enemy(pos, enemy_type=1) for pos in initial_positions]
        self.projectiles = []
        self.score = 0
        self.player_hp = self.player_max_hp
        self.last_player_hit_ms = 0
        self.game_over = False
        self.game_won = False # Resetiraj varijablu za pobjedu
        self.hit_flash_end_ms = 0
        self.wave = 1
        self.enemies_killed_this_wave = 0

    def spawn_next_wave(self):
        """Stvara novi val neprijatelja s većim HP-om i drugom slikom"""
        self.wave += 1
        self.enemies_killed_this_wave = 0
        
        def random_spawn_positions(count, min_dist=3, max_dist=8):
            """Generira nasumične pozicije za spawn"""
            positions = []
            for _ in range(count):
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(min_dist, max_dist)
                x = np.cos(angle) * distance
                y = np.sin(angle) * distance
                positions.append((x, y))
            return positions
        
        if self.wave == 2:
            # Drugi val: 3 neprijatelja tipa 2 (5 HP)
            new_enemies = []
            positions = random_spawn_positions(3, 2, 4)
            for pos in positions:
                new_enemies.append(Enemy(pos, speed=0.025, hp=5, enemy_type=2))
        elif self.wave == 3:
            # Treći val: 3 neprijatelja tipa 3 (1 HP, duplo brži)
            new_enemies = []
            positions = random_spawn_positions(3, 2, 4)
            for pos in positions:
                new_enemies.append(Enemy(pos, speed=0.05, hp=1, enemy_type=3))
        elif self.wave == 4:
            # Četvrti val: 1 neprijatelj tipa 4 (10 HP) + 3 neprijatelja tipa 3 (1 HP, brži)
            new_enemies = []
            # Prvo dodaj 1 neprijatelja tipa 4 (spor, 10 HP) - još bliže spawn
            boss_pos = random_spawn_positions(1, 2, 5)[0]
            new_enemies.append(Enemy(boss_pos, speed=0.015, hp=10, enemy_type=4))
            # Zatim dodaj 3 neprijatelja tipa 3 (brži, 1 HP)
            positions = random_spawn_positions(3, 2, 4)
            for pos in positions:
                new_enemies.append(Enemy(pos, speed=0.05, hp=1, enemy_type=3))
        elif self.wave == 5:
            # Peti val: 1 neprijatelj tipa 5 (30 HP, brži) - još bliže spawn
            new_enemies = []
            positions = random_spawn_positions(1, 3, 6)
            for pos in positions:
                new_enemies.append(Enemy(pos, speed=0.07, hp=30, enemy_type=5))
        else:
            # Fallback za buduće valove
            new_enemies = []
            positions = random_spawn_positions(3, 2, 4)
            for pos in positions:
                new_enemies.append(Enemy(pos, speed=0.025, hp=5, enemy_type=2))
        
        self.enemies = new_enemies

