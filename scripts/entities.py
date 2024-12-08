import pygame


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

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
