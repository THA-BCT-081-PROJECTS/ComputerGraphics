import pygame



class Player:
    JUMPING_STRENGTH = 300
    SPEED = 5

    def __init__(self,x,y,radius):
        self.pos = pygame.Vector2(x,y)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.rect = pygame.Rect(self.pos.x, self.pos.y, radius,radius)

    def jump(self):
        if self.on_ground:
            self.velocity.y = -self.JUMPING_STRENGTH
            self.on_ground = False

    def move_left(self):
        self.pos.x -= self.SPEED

    def move_right(self):
        self.pos.x += self.SPEED


    def handle_horizontal_bounds(self):
        pass

    def handle_vertical_bounds(self):
        from main import HEIGHT

        if self.pos.y >= HEIGHT-30:
            self.pos.y = HEIGHT-30
            if self.velocity.y > 0:
                self.velocity.y=0
                self.on_ground = True
        if self.pos.y <= 0:
            self.pos.y = 0
            if self.velocity.y < 0:
                self.velocity.y = 0

    def update(self,dt,platforms):
        from main import GRAVITY

        self.velocity.y += GRAVITY*dt
        self.pos.y += self.velocity.y * dt

        self.handle_vertical_bounds()
        self.handle_horizontal_bounds()
        self.rect.center = self.pos
        self.platform_collision(platforms)

    def platform_collision(self,platforms):
        from main import RADIUS_OF_CIRCLE
        for platform in platforms:
            if self.rect.colliderect(platform):
                # falling → landing
                if self.velocity.y > 0:
                    self.rect.bottom = platform.top
                    self.pos.y = self.rect.y+RADIUS_OF_CIRCLE/2
                    self.velocity.y = 0
                    self.on_ground = True

                # jumping → hitting underside
                elif self.velocity.y < 0:
                    self.rect.top = platform.bottom
                    self.pos.y = self.rect.y
                    self.velocity.y = 0