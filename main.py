import numpy as np
import pygame
import os
import math
import sys
import random
import neat

screen_width = 1500
screen_height = 800
generation = 0

class Criatura:
    def __init__(self,screen,clock,id):
        self.id = id
        self.radius = int(random.randint(1, 60))
        self.pos = [int(random.randint(1, screen_width - self.radius)), int(random.randint(1,screen_height - self.radius))]
        self.rect = pygame.draw.circle(screen, (255,0,0), (self.pos[0], self.pos[1]), self.radius, 3)
        self.angle = 0
        self.speed = 0
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.time = clock
        self.hungry = 100


    def update(self,cars,screen):
        # check speed
        self.speed = 4

        #move
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed

        self.rect = pygame.draw.circle(screen, (0,0,0), (self.pos[0], self.pos[1]), self.radius, 3)
        self.rect = pygame.draw.circle(screen, (255,0,0), (self.pos[0], self.pos[1]), self.radius, 3)

        self.check_collision(cars)
        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d, screen)

        self.check_hungry()

    def check_collision(self, cars):
        self.is_alive = True

        for car in cars:
            if not (self.id == car.id):
                dist = math.dist([self.pos[0], self.pos[1]], [car.pos[0], car.pos[1]]) #https://stackoverflow.com/questions/22135712/pygame-collision-detection-with-two-circles
                #dist  = math.hypot(car.pos[0] - self.pos[0], car.pos[1] - self.pos[1])
                if dist < (self.radius + car.radius):
                    if (self.radius < car.radius):
                        self.is_alive = False
                    else:
                        self.hungry = self.hungry + 200

    def check_radar(self, degree, map):
        len = 0
        x = int(self.pos[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.pos[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        if x < screen_width or y < screen_height:
            while map.get_at((x, y)) == (25, 25, 25, 255) and len < 300:
                len = len + 1
                x = int(self.pos[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.pos[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
                if x >= screen_width or y >= screen_height:
                    break

        dist = int(math.sqrt(math.pow(x - self.pos[0], 2) + math.pow(y - self.pos[1], 2)))
        self.radars.append([(x, y), dist])

    def draw_radar(self, screen):
        for r in self.radars:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def draw(self):
        pygame.display.flip()

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        return self.time / 50.0

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 30)

        return ret

    def check_hungry(self):
        self.hungry = self.hungry - 1

        if self.hungry <= 0:
            self.is_alive = False


def run_car(genomes, config):

    # Init NEAT
    nets = []
    cars = []

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    i = 0
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # Init my cars
        cars.append(Criatura(screen,clock.tick(),i))
        i = i + 1


    generation_font = pygame.font.SysFont("Arial", 70)
    font = pygame.font.SysFont("Arial", 30)
    bg = 25, 25, 25
    screen.fill(bg)

    # Main loop
    global generation
    generation += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)


        # Input my data and get result from network
        for index, car in enumerate(cars):
            output = nets[index].activate(car.get_data())
            i = output.index(max(output))
            if i == 0:
                car.angle += 10
            else:
                car.angle -= 10

        # Update car and fitness
        remain_cars = 0
        cars_aux = np.copy(cars)
        for i, car in enumerate(cars):
            if car.get_alive():
                remain_cars += 1
                car.update(cars_aux,screen)
                genomes[i][1].fitness += car.get_reward()

        # check
        if remain_cars == 0:
            break

        # Drawing
        for car in cars:
            if car.get_alive():
                car.draw()

        text = generation_font.render("Generation : " + str(generation), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        screen.blit(text, text_rect)

        text = font.render("remain cars : " + str(remain_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)

if __name__ == "__main__":
    # Set configuration file
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(run_car, 1000)