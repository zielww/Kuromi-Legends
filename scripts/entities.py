import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]

    # Update player position
    def update(self, movement=(0, 0)):
        # Vector to determine how much an entity should move in a frame
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # Position for x and y dimensions
        self.pos[0] += frame_movement[0]
        self.pos[1] += frame_movement[1]



    # Render entity
    def render(self, surf):
        surf.blit(self.game.assets['player'], self.pos)
