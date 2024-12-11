import pygame
import math
import random

from scripts.particle import Particle
from scripts.spark import Spark


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        # Animation stuff
        self.action = ''
        self.animation = None
        self.last_movement = [0, 0]
        # Account for entity padding so that animations overflow over the hit box
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

    # Dynamically generate rect for collision
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    # Determine character animation
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    # Update player position
    def update(self, tilemap, movement=(0, 0)):
        # Reset Collisions every frame
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # Vector to determine how much an entity should move in a frame
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # Movement for x and y dimensions
        self.pos[0] += frame_movement[0]
        # Collision for x-axis
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        # Collision for y-axis
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        # Flip Character
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        # Player velocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Reset Velocity when player collide with something
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        # Update animation
        self.animation.update()

    # Render entity
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    # Player Update
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1

        # Falling death
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        # Particle bursts when dashing
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            # Particle stream when dashing
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(
                Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    # Make the player invisible during dashing
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    # Added a shoot button, lets see
    def shoot(self):
        if self.flip:
            self.game.sfx['shoot'].play()
            self.game.player_projectiles.append(
                [[self.rect().centerx - 7, self.rect().centery], -1.5, 0, self.game.assets['heart'], (255, 192, 203)])
            # Add Sparks when gun is shot (For left side)
            for i in range(4):
                self.game.sparks.append(Spark(self.game.player_projectiles[-1][0], random.random() - 0.5 + math.pi,
                                              2 + random.random(), (255, 192, 203)))
        if not self.flip:
            self.game.sfx['shoot'].play()
            self.game.player_projectiles.append(
                [[self.rect().centerx + 7, self.rect().centery], 1.5, 0, self.game.assets['heart'], (255, 192, 203)])
            # Add Sparks when gun is shot (For right side)
            for i in range(4):
                self.game.sparks.append(
                    Spark(self.game.player_projectiles[-1][0], random.random() - 0.5, 2 + random.random(),
                          (255, 192, 203)))

    # Player Jump
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                # Add sparks when jumping
                for i in range(3):
                    self.game.sparks.append(
                        Spark(self.pos, random.random() - 0.1 + (math.pi / 2 if self.pos[1] > 0 else 0),
                              2 + random.random(), (251, 198, 207)))
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                # Add sparks when jumping
                for i in range(3):
                    self.game.sparks.append(
                        Spark(self.pos, random.random() - 0.1 + (math.pi / 2 if self.pos[1] > 0 else 0),
                              2 + random.random(), (251, 198, 207)))
                return True

        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            # Add sparks when jumping
            for i in range(3):
                self.game.sparks.append(
                    Spark(self.pos, random.random() - 0.1 + (math.pi / 2 if self.pos[1] > 0 else 0),
                          2 + random.random(), (251, 198, 207)))
            return True

    # Player Dash
    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        # Enemy Pathing Logic
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1]) or abs(dis[0]) < 1000:
                    if self.flip and dis[0] < 0:
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx - 7, self.rect().centery], -1.5, 0, self.game.assets['projectile'],
                             (86, 68, 54)])
                        # Add Sparks when gun is shot (For left side)
                        for i in range(12):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                                                          2 + random.random(), (86, 68, 54)))
                    if not self.flip and dis[0] > 0:
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx + 7, self.rect().centery], 1.5, 0, self.game.assets['projectile'],
                             (86, 68, 54)])
                        # Add Sparks when gun is shot (For right side)
                        for i in range(12):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random(),
                                      (86, 68, 54)))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        # Set enemy animation
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # Add enemy killing
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.sfx['hit'].play()
                # Add screenshake when the enemy died
                self.game.screenshake = max(16, self.game.screenshake)
                # Visual effects when the enemy is killed
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))
                return True

        # Add enemy killing from projectiles
        for projectile in self.game.player_projectiles:
            if self.rect().collidepoint(projectile[0]):
                self.game.sfx['hit'].play()
                # Add screenshake when the enemy died
                self.game.screenshake = max(16, self.game.screenshake)
                # Visual effects when the enemy is killed
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))
                self.game.player_projectiles.remove(projectile)
                return True

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0] - 55,
                   self.pos[1] - offset[1] + self.anim_offset[1] - 65))


class Goblin(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'goblin', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        # Enemy Pathing Logic
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1]) or abs(dis[0]) < 1000:
                    if self.flip and dis[0] < 0:
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx - 7, self.rect().centery], -1.5, 0, self.game.assets['bomb'],
                             (255, 255, 0)])
                        # Add Sparks when gun is shot (For left side)
                        for i in range(12):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                                                          2 + random.random(), (255, 255, 0)))
                    if not self.flip and dis[0] > 0:
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx + 7, self.rect().centery], 1.5, 0, self.game.assets['bomb'],
                             (255, 255, 0)])
                        # Add Sparks when gun is shot (For right side)
                        for i in range(12):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random(),
                                      (255, 255, 0)))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        # Set enemy animation
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # Add enemy killing
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.sfx['hit'].play()
                # Add screenshake when the enemy died
                self.game.screenshake = max(16, self.game.screenshake)
                # Visual effects when the enemy is killed
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))
                return True

        # Add enemy killing from projectiles
        for projectile in self.game.player_projectiles:
            if self.rect().collidepoint(projectile[0]):
                self.game.sfx['hit'].play()
                # Add screenshake when the enemy died
                self.game.screenshake = max(16, self.game.screenshake)
                # Visual effects when the enemy is killed
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))
                self.game.player_projectiles.remove(projectile)
                return True

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0] - 35,
                   self.pos[1] - offset[1] + self.anim_offset[1] - 45))


class Mushroom(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'mushroom', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        # Enemy Pathing Logic
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1]) or abs(dis[0]) < 1000:
                    if self.flip and dis[0] < 0:
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx - 7, self.rect().centery], -1.5, 0, self.game.assets['orb'],
                             (255, 0, 0)])
                        # Add Sparks when gun is shot (For left side)
                        for i in range(12):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                                                          2 + random.random(), (255, 0, 0)))
                    if not self.flip and dis[0] > 0:
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx + 7, self.rect().centery], 1.5, 0, self.game.assets['orb'],
                             (255, 0, 0)])
                        # Add Sparks when gun is shot (For right side)
                        for i in range(12):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random(),
                                      (255, 0, 0)))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        # Set enemy animation
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # Add enemy killing
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.sfx['hit'].play()
                # Add screenshake when the enemy died
                self.game.screenshake = max(16, self.game.screenshake)
                # Visual effects when the enemy is killed
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))
                return True

        # Add enemy killing from projectiles
        for projectile in self.game.player_projectiles:
            if self.rect().collidepoint(projectile[0]):
                self.game.sfx['hit'].play()
                # Add screenshake when the enemy died
                self.game.screenshake = max(16, self.game.screenshake)
                # Visual effects when the enemy is killed
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))
                self.game.player_projectiles.remove(projectile)
                return True

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0] - 35,
                   self.pos[1] - offset[1] + self.anim_offset[1] - 45))


class Skeleton(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'skeleton', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        # Enemy Pathing Logic
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        # Set enemy animation
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # The player die in this case
        if self.rect().colliderect(self.game.player.rect()):
            self.game.dead += 1
            self.game.sfx['hit'].play()
            # Add screenshake when the enemy died
            self.game.screenshake = max(16, self.game.screenshake)
            # Visual effects when the enemy is killed
            for i in range(10):
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                    velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                              math.sin(angle + math.pi) * speed * 0.5],
                                                    frame=random.randint(0, 7)))
            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))

        # Add enemy killing from projectiles
        for projectile in self.game.player_projectiles:
            if self.rect().collidepoint(projectile[0]):
                self.game.sfx['hit'].play()
                # Add screenshake when the enemy died
                self.game.screenshake = max(16, self.game.screenshake)
                # Visual effects when the enemy is killed
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255, 0, 0)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255, 0, 0)))
                self.game.player_projectiles.remove(projectile)
                return True

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0] - 25,
                   self.pos[1] - offset[1] + self.anim_offset[1] - 35))
