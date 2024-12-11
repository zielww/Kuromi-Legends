import os
import sys

import pygame
import math
import random

from selenium.webdriver.common.devtools.v85.audits import disable

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark


class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        # Change window name
        pygame.display.set_caption('Onegai My Kuromi')

        # Change window resolution
        self.screen = pygame.display.set_mode((640, 480))

        # Initialize second surface for rendering (used for asset scaling)
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)

        # Display for outlines
        self.display_2 = pygame.Surface((320, 240))

        # initialize game clock
        self.clock = pygame.time.Clock()

        # Movement variable
        self.movement = [False, False]

        # Initialize Assets
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'enemy/idle': Animation(load_images('entities/enemy/idle')),
            'enemy/run': Animation(load_images('entities/enemy/run')),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        # Initialize Sound effects
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
            'victory': pygame.mixer.Sound('data/sfx/victory.wav'),
        }

        # Change volume of sounds
        self.sfx['jump'].set_volume(0.2)
        self.sfx['dash'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['shoot'].set_volume(0.3)
        self.sfx['ambience'].set_volume(0.7)
        self.sfx['victory'].set_volume(0.8)

        # Define Clouds
        self.clouds = Clouds(self.assets['clouds'], count=16)

        # Define Player
        self.player = Player(self, (50, 50), (8, 15))

        # Define Tile Map
        self.tilemap = Tilemap(self, tile_size=16)

        # Level variable for level transition
        self.level = 0
        self.load_level(self.level)

        # Screen shake values
        self.screenshake = 0

        # Mouse button
        self.clicking = False

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        # Add leaves to trees
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        # Player and enemy spawners
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        self.particles = []
        self.projectiles = []
        self.sparks = []

        # Add Camera
        self.scroll = [0, 0]

        # Allows the user to be dead
        self.dead = 0

        # Transition variable
        self.transition = -30

    def run(self):
        # Add music
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        while True:
            # Add transparency to display
            self.display.fill((0, 0, 0, 0))
            # Clear the Screen
            self.display_2.blit(self.assets['background'], (0, 0))

            # Add screenshake
            self.screenshake = max(0, self.screenshake - 1)

            # Handles level transition
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    # Added limit to levels
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
                    if self.level == len(os.listdir('data/maps')) - 3:
                        self.sfx['victory'].play()
            if self.transition < 0:
                self.transition += 1

            # Revives the player after 40 frames
            if self.dead:
                self.dead += 1
                if self.dead == 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)

            # Position the camera in the center of the screen (player)
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            # Remove jittery shit
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Spawn the leaf particles
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(
                        Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            # Render Clouds
            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

            # Render tile map
            self.tilemap.render(self.display, offset=render_scroll)

            # Render the enemies
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                # Update pos
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                # Render Player
                self.player.render(self.display, offset=render_scroll)

            # Render projectiles
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                        projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    # Spawn spark when a wall is hit
                    for i in range(4):
                        self.sparks.append(
                            Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                  2 + random.random(), ))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        # Player death logic
                        self.dead += 1
                        # Add sound when hit
                        self.sfx['hit'].play()
                        # Add screenshake when the player died
                        self.screenshake = max(16, self.screenshake)
                        # Sparks when the projectile hit the player
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(
                                Spark(self.player.rect().center, angle, 2 + random.random(), (255, 0, 0)))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                           velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                     math.sin(angle + math.pi) * speed * 0.5],
                                                           frame=random.randint(0, 7)))

            # Render the sparks
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            # Make a mask for game outline
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)

            # Render the particles and check if it needs to be removed
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # Loop for All type of Events
            for event in pygame.event.get():
                # Keyboard Controls
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = False

                #Mouse controls
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        self.player.dash()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False

            # Transition visuals
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                  random.random() * self.screenshake - self.screenshake / 2)
            # Blit the display into the screen
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            # Method to update the screen every frame
            pygame.display.update()
            self.clock.tick(60)


# Initialize the Game
Game().run()
