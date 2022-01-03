import numpy as np
import pygame
import os
import math
import sys
import random
import neat
import time

screen_width = 1500
screen_height = 800
generation = 0

class Criatura:
    def __init__(self,screen,clock,id,rad,r,g,b):
        self.id = id
        self.radius = rad
        self.pos = [int(random.randint(1, screen_width - self.radius)), int(random.randint(1,screen_height - self.radius))]
        self.angle = 0
        self.speed = 0
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.time = clock
        self.hungry = 100
        self.color = [r,g,b]


    def update(self,cars,screen):
        # check speed
        self.speed = 5

        #move
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed

        self.check_collision(cars)
        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d, screen)

        self.check_hungry()

    def check_collision(self, cars):
        self.is_alive = True

        for car in cars:
            if (not (self.id == car.id)) and (car.get_alive()):
                dist = math.dist([self.pos[0], self.pos[1]], [car.pos[0], car.pos[1]]) #https://stackoverflow.com/questions/22135712/pygame-collision-detection-with-two-circles
                #dist  = math.hypot(car.pos[0] - self.pos[0], car.pos[1] - self.pos[1])
                if dist < (self.radius + car.radius):
                    if (self.radius < car.radius):
                        self.is_alive = False
                    elif self.radius > car.radius:
                        print("Eat")
                        print(self.id)
                        self.hungry = self.hungry + 100


    def check_radar(self, degree, map):
        len = 0
        x = int(self.pos[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.pos[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while len < 300 and (x < (screen_width - self.radius) and y < (screen_height - self.radius)) and (x > 0 and y > 0):

            if x >= (screen_width - self.radius) or y >= (screen_height - self.radius):
                break

            if map.get_at((x, y)) != (25, 25, 25, 255):
                break
            else:
                len = len + 1
                x = int(self.pos[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.pos[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)




        dist = int(math.sqrt(math.pow(x - self.pos[0], 2) + math.pow(y - self.pos[1], 2)))
        self.radars.append([(x, y), dist])

    def draw_radar(self, screen):
        for r in self.radars:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.pos, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def draw(self,screen):
        pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2]), (self.pos[0], self.pos[1]), self.radius, self.radius)

        generation_font = pygame.font.SysFont("Arial", 10)
        text = generation_font.render(str(self.id), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.pos)
        screen.blit(text, text_rect)

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
    nets1 = []
    cars1 = []

    nets2 = []
    cars2 = []

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    i = 0
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets1.append(net)
        g.fitness = 0

        # Init my cars
        cars1.append(Criatura(screen,clock.tick(),i,30,255,0,0))
        i = i + 1

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets2.append(net)
        g.fitness = 0

        # Init my cars
        cars2.append(Criatura(screen, clock.tick(),i,10,0,0,255))
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
        for index, car in enumerate(cars1):
            output = nets1[index].activate(car.get_data())
            i = output.index(max(output))
            if i == 0:
                car.angle += 10
            else:
                car.angle -= 10

        # Input my data and get result from network
        for index, car in enumerate(cars2):
            output = nets2[index].activate(car.get_data())
            i = output.index(max(output))
            if i == 0:
                car.angle += 10
            else:
                car.angle -= 10

        # Update car and fitness
        remain_cars1 = 0
        total_cars = cars1 + cars2
        for i, car in enumerate(cars1):
            if car.get_alive():
                remain_cars1 += 1
                car.update(total_cars,screen)
                genomes[i][1].fitness += car.get_reward()

        # Update car and fitness
        remain_cars2 = 0
        for i, car in enumerate(cars2):
            if car.get_alive():
                remain_cars2 += 1
                car.update(total_cars, screen)
                genomes[i][1].fitness += car.get_reward()

        # check
        if remain_cars1 == 0 and remain_cars2 == 0:
            break

        screen.fill(bg)
        # Drawing
        time.sleep(0.01)
        for car in cars1:
            if car.get_alive():
                car.draw(screen)

        for car in cars2:
            if car.get_alive():
                car.draw(screen)

        text = generation_font.render("Generation : " + str(generation), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        screen.blit(text, text_rect)

        text = font.render("remain cars : " + str(remain_cars1+remain_cars2), True, (0, 0, 0))
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