import sys

import pygame

from scripts.utils import load_image, load_images
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap


class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        # Change window name
        pygame.display.set_caption('Kuromi Legends')

        # Change window resolution
        self.screen = pygame.display.set_mode((640, 480))

        # Initialize second surface for rendering (used for asset scaling)
        self.display = pygame.Surface((320, 240))

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
            'player': load_image('entities/player.png')
        }

        # Define Player
        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))

        # Define Tile Map
        self.tilemap = Tilemap(self, tile_size=16)

    def run(self):
        while True:
            # Clear the Screen
            self.display.fill((14, 219, 248))

            # Render tile map
            self.tilemap.render(self.display)

            # Update pos
            self.player.update((self.movement[1] - self.movement[0], 0))
            # Render Player
            self.player.render(self.display)

            # Loop for All type of Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            # Blit the display into the screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            # Method to update the screen every frame
            pygame.display.update()
            self.clock.tick(60)


# Initialize the Game
Game().run()
