import pygame
import os
import random

# screen sizing
screen_width = 500
screen_height = 800

# load imagePath paths
img_pipe = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'pipe.png')))
img_floor = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'base.png')))
img_background = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bg.png')))
img_bird = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird3.png')))]

pygame.font.init()
font_p = pygame.font.SysFont('comic sans', 50)


class Bird:
    imagePath = img_bird
    max_rotation = 25
    rotation_spd = 20
    time_animation = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.image_count = 0
        self.bird_image = self.imagePath[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        # moving
        self.time += 1
        moving = 1.5 * (self.time ** 2) + self.speed * self.time

        # restricting move in case of loop or complete fall
        if moving > 16:
            moving = 16
        elif moving < 0:
            moving -= 2

        self.y += moving

        # moving angle
        if moving < 0 or self.y < (self.height + 50):
            if self.angle < self.max_rotation:
                self.angle = self.max_rotation
            else:
                if self.angle > -90:
                    self.angle -= self.rotation_spd

    def drawbird(self, screen):
        # define bird img
        self.image_count += 1

        if self.image_count < self.time_animation:
            self.bird_image = self.imagePath[0]
        elif self.image_count < self.time_animation * 2:
            self.bird_image = self.imagePath[1]
        elif self.image_count < self.time_animation * 3:
            self.bird_image = self.imagePath[2]
        elif self.image_count < self.time_animation * 4:
            self.bird_image = self.imagePath[1]
        elif self.image_count >= self.time_animation * 4 + 1:
            self.bird_image = self.imagePath[0]
            self.image_count = 0

        # not flap if defined to fall
        if self.angle <= -80:
            self.bird_image = self.imagePath[1]
            self.image_count = self.time_animation * 2
        # draw
        imageroll = pygame.transform.rotate(self.bird_image, self.angle)
        imagecenterposition = self.bird_image.get_rect(topleft=(self.x, self.y)).center
        rectangle = imageroll.get_rect(center=imagecenterposition)
        screen.blit(imageroll, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.bird_image)


class Pipe:
    distance = 200
    speed = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_position = 0
        self.base_position = 0
        self.top_pipe_image = pygame.transform.flip(img_pipe, False, True)
        self.base_pipe_image = img_pipe
        self.pass_ = False
        self.height_definition()

    def height_definition(self):
        self.height = random.randrange(50, 450)
        self.top_position = self.height - self.top_pipe_image.get_height()
        self.base_position = self.height + self.distance

    def movingpipe(self):
        self.x -= self.speed

    def drawpipe(self, screen):
        screen.blit(self.top_pipe_image, (self.x, self.top_position))
        screen.blit(self.base_pipe_image, (self.x, self.base_position))

    def colision(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top_pipe_image)
        base_mask = pygame.mask.from_surface(self.base_pipe_image)

        topodistance = (self.x - bird.x, self.top_position - round(bird.y))
        basedistance = (self.x - bird.x, self.base_position - round(bird.y))

        topcolisionpoint = bird_mask.overlap(top_mask, topodistance)
        basecolisionpoint = bird_mask.overlap(base_mask, basedistance)

        if basecolisionpoint or topcolisionpoint:
            return True
        else:
            return False


class Floor:
    speed = 5
    width = img_floor.get_width()
    image = img_floor

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.width

    def movefloor(self):
        self.x0 -= self.speed
        self.x1 -= self.speed

        if self.x0 + self.width < 0:
            self.x0 = self.x1 + self.width
        if self.x1 + self.width < 0:
            self.x1 = self.x0 + self.width

    def drawfloor(self, screen):
        screen.blit(self.image, (self.x0, self.y))
        screen.blit(self.image, (self.x1, self.y))


def screendraw(screen, birds, pipes, floor, score):
    screen.blit(img_background, (0, 0))
    for bird in birds:
        bird.drawbird(screen)
    for pipe in pipes:
        pipe.drawpipe(screen)

    text = font_p.render(f'Score: {score}', 1, (255, 255, 255))
    screen.blit(text, (screen_width - 10 - text.get_width(), 10))
    floor.drawfloor(screen)
    pygame.display.update()


def main():
    birds = [Bird(200, 300)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((screen_width, screen_height))
    score = 0
    gameclock = pygame.time.Clock()
    game_running = True

    while game_running:
        gameclock.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                game_running = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        def respawn():
            main()

        # moving things
        for bird in birds:
            bird.move()
        floor.movefloor()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.colision(bird):
                    respawn()
                if not pipe.pass_ and bird.x > pipe.x:
                    pipe.pass_ = True
                    add_pipe = True
            pipe.movingpipe()
            if pipe.x + pipe.top_pipe_image.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.bird_image.get_height()) > floor.y or bird.y < 0:
                respawn()

        screendraw(screen, birds, pipes, floor, score)


if __name__ == '__main__':
    main()
